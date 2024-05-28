import streamlit as st
import pandas as pd
#import cv2 (for QR codes)
import pyodbc
import urllib
import numpy as np
import datetime
from st_aggrid import AgGrid, GridOptionsBuilder
import matplotlib
import matplotlib.pyplot as plt
import plotly.express as px
import plotly.graph_objects as go
from st_aggrid import JsCode
from streamlit_option_menu import option_menu
from sqlalchemy import create_engine


# Main app
def main():
        
    pd.set_option('display.notebook_repr_html', False)

    st.set_page_config(
        page_title = "Nautique Production Dashboard",
        page_icon = "🛥️",
        layout = "wide"
    )

    # Importing data
    df = pd.read_csv('output.csv')
    df.drop(['Unnamed: 0', 'Order Number', 'Order Date', 'Actual Gel Date', 'Issue Details'], axis = 1, inplace = True)
    
    # Vertical menu on the left side of the page (option_menu did not take updates to its value very well)
    # Need to beautify the sidebar since its just an ugly dropdown now :(
    with st.sidebar:
        options = {'Home': 0, 'Details': 1, 'Departments': 2, 'Settings': 3}
        if 'selected' not in st.session_state:
            st.session_state.selected = st.selectbox("Main Menu", list(options.keys()), index = 0)

    # Important to check if boat has been selected before
    if 'hin_history' not in st.session_state:
        st.session_state.hin_history = []

    # Creating dictionary for each boat's list of issues (key: HIN, value: list of dictionaries corresponding to issues)
    if 'issue_details' not in st.session_state:
        st.session_state.issue_details = {}
    
    # Color function for dataframe based on status
    def color_status(row):
        if row.Status == 'Offline':
            return pd.Series('background-color: red', row.index)
        elif row.Status == 'Delayed':
            return pd.Series('background-color: orange', row.index)
        else:
            return pd.Series('background-color: green', row.index)
        
    def set_details_state(hin):
            st.session_state.details = 'Y'
            st.session_state.HIN = hin
            st.session_state.selected = 'Details'

    # Display content based on selected page
    if st.session_state.selected == "Home":
        # Logo and Dashboard title
        col1, col2, col3 = st.columns([1,3,1])
        with col1:
            st.image("logo.jpg", width=100)

        with col2:
            # Use a full-width markdown container to center the title
            st.markdown("""
                <style>
                .centered {
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    font-size: 32px;
                    font-family: 'Bahnschrift';
                    font-weight: bold;
                    height: 80px; 
                }
            </style>
            <div class="centered">
                <b>Production Overview</b>
            </div>
        """, unsafe_allow_html=True)
            
        # Creating buttons for toggle between SPF/NPF/both
        if 'facility' not in st.session_state:
            st.session_state.facility = 'All'

        def set_state(x):
            st.session_state.facility = x

        spf_depts = ['Lamination', 'Post Pulling Buffer', 'Grinding', 'Post Grinding Buffer', 'Patch QC', 'Post Patch QC Buffer', 'Patch and Polish', 'Post Patch and Polish Buffer', 
                 'Underwater Gear', 'Post Underwater Gear Buffer', 'Dry Capping', 'Post Dry Capping Buffer', 'Water Test', 'Post Water Test Buffer', 'Final Finish']
        
        npf_depts = ['Assembly', 'Post Assembly Buffer', 'Post Final Finish Buffer', 'Final Assembly']

        if st.session_state.facility == 'SPF':
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                st.button('NPF Departments', use_container_width = True, on_click = set_state, args = ['NPF'])
            with button_col2:
                st.button('All Departments', use_container_width = True, on_click = set_state, args = ['All'])

            df = df[df['Department'].isin(spf_depts)]

            # Dominos tracker style chart (still needs some refining - shape, etc)
            chartcol, datacol = st.columns([9.5, 2])
            dept_order = ['Lamination', 'Post Pulling Buffer', 'Grinding',  'Post Grinding Buffer', 'Patch QC', 'Post Patch QC Buffer', 'Patch and Polish', 
                     'Post Patch and Polish Buffer', 'Underwater Gear', 'Post Underwater Gear Buffer', 'Dry Capping', 'Post Dry Capping Buffer', 
                     'Assembly', 'Post Assembly Buffer', 'Water Test', 'Post Water Test Buffer', 'Final Finish', 'Post Final Finish Buffer', 'Final Assembly']
            
            dept_counts = df['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            dept_counts['Total'] = dept_counts['Count'].sum()
            dept_counts['x'] = dept_counts['Department'].nunique() / dept_counts['Total']

            fig2 = px.bar(dept_counts, x = 'x', y = 'Total', orientation = 'h', color = 'Department', text = 'Department', barmode = 'stack', category_orders = {'Department': dept_order},
                         height = 350, hover_name = 'Count')
            fig2.update_traces(marker = dict(line = dict(width = 2, color = 'black')))
            fig2.update_layout(showlegend = False, yaxis = dict(showticklabels = False), xaxis = dict(showticklabels = False), bargap = 0.2, bargroupgap = 0.5)
            fig2.update_xaxes(title_text = '')
            fig2.update_yaxes(title_text = '')
            
            with chartcol:
                st.plotly_chart(fig2, use_container_width = True)

            with datacol:
                dept_counts2 = dept_counts
                dept_counts2.drop('Total', axis = 1, inplace = True)
                dept_counts2['Department'] = pd.Categorical(dept_counts2.Department, categories = dept_order, ordered = True)
                dept_counts2.sort_values(by = 'Department', inplace = True)
                df_table = dept_counts2[['Department', 'Count']]
                st.dataframe(df_table, hide_index = True, use_container_width = True)

            if st.button('Department View', use_container_width = True):
                st.session_state.selected = 'Departments'
        
            # Multiselect filter for df
            df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date
            df['Sched Finish Date'] = pd.to_datetime(df['Sched Finish Date']).dt.date

            # Filter functionality for df
            random_key_base = pd.util.hash_pandas_object(df)

            # Trying to make datetime columns correct format/type
            for col in df.columns:
                if pd.api.types.is_object_dtype(df[col]):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass
            
            modification_container = st.container()

            with modification_container:
                to_filter_columns = st.multiselect("Filter options", df.columns, key = f"{random_key_base}_multiselect")
                filters: pd.Dict[str, pd.Any] = dict()

                for column in to_filter_columns:
                    left, right = st.columns((1, 20))

                    if pd.api.types.is_categorical_dtype(df[column]) or df[column].nunique() <= 10 or column == 'Department':
                        left.write("↳")
                        filters[column] = right.multiselect(f"Values for {column}", df[column].unique(), default = list(df[column].unique()), key = f"{random_key_base}_{column}")
                        df = df[df[column].isin(filters[column])]

                    elif pd.api.types.is_numeric_dtype(df[column]):
                        left.write("↳")
                        _min = float(df[column].min())
                        _max = float(df[column].max())
                        step = (_max - _min) / 100
                        filters[column] = right.slider(f"Values for {column}", _min, _max, (_min, _max), step = step, key = f"{random_key_base}_{column}")                           
                        df = df[df[column].between(*filters[column])]

                    elif pd.api.types.is_datetime64_any_dtype(df[column]):
                        left.write("↳")
                        filters[column] = right.date_input(f"Values for {column}", value=(df[column].min(), df[column].max()), key = f"{random_key_base}_{column}")
                        if len(filters[column]) == 2:
                            filters[column] = tuple(map(pd.to_datetime, filters[column]))
                            start_date, end_date = filters[column]
                            df = df.loc[df[column].between(start_date, end_date)]

                    else:
                        left.write("↳")
                        filters[column] = right.text_input(f"Pattern in {column}", key = f"{random_key_base}_{column}")
                        df = df[df[column].str.contains(filters[column], case = True)]

            grid_options = {"rowSelection": "single",
                            "rowMultiSelectWithClick": False,
                            "suppressRowDeselection": False,
                            "suppressRowClickSelection": True,
                            "groupSelectsChildren": False,
                            "groupSelectsFiltered": True,
                            "preSelectAllRows": False,
                            'columnDefs': [
                                            {
                                                'field': 'Model Part',
                                                'checkboxSelection': True
                                            },
                                            {'field': 'HIN'},
                                            {'field': 'Start Date'},
                                            {'field': 'Sched Finish Date'},
                                            {
                                                'field': 'Status',
                                                'cellStyle': JsCode("""
                                                    function(params) {
                                                        switch(params.value) {
                                                            case 'Offline':
                                                                  return {backgroundColor: 'red'};
                                                            case 'Delayed':
                                                                 return {backgroundColor: 'orange'};
                                                            default:
                                                                  return {backgroundColor: 'green'};
                                                        }
                                                    }
                                                """)
                                            },
                                            {'field': 'Department'}]
            }

            aggrid_ALL = AgGrid(
                    df,
                    gridOptions = grid_options,
                    enable_enterprise_modules=True,
                    height=600,
                    fit_columns_on_grid_load=True,
                    search=True,
                    allow_unsafe_jscode=True
            ) 

            if aggrid_ALL.selected_rows:
                set_details_state(aggrid_ALL.selected_rows[0]['HIN'])
            else:
                st.write('No boat selected.')
            
        if st.session_state.facility == 'NPF':
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                st.button('SPF Departments', use_container_width = True, on_click = set_state, args = ['SPF'])
            with button_col2:
                st.button('All Departments', use_container_width = True, on_click = set_state, args = ['All'])

            df = df[df['Department'].isin(npf_depts)]

            # Dominos tracker style chart (still needs some refining - shape, etc)
            chartcol, datacol = st.columns([9.5, 2])
            dept_order = ['Lamination', 'Post Pulling Buffer', 'Grinding',  'Post Grinding Buffer', 'Patch QC', 'Post Patch QC Buffer', 'Patch and Polish', 
                     'Post Patch and Polish Buffer', 'Underwater Gear', 'Post Underwater Gear Buffer', 'Dry Capping', 'Post Dry Capping Buffer', 
                     'Assembly', 'Post Assembly Buffer', 'Water Test', 'Post Water Test Buffer', 'Final Finish', 'Post Final Finish Buffer', 'Final Assembly']
            
            dept_counts = df['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            dept_counts['Total'] = dept_counts['Count'].sum()
            dept_counts['x'] = dept_counts['Department'].nunique() / dept_counts['Total']

            fig2 = px.bar(dept_counts, x = 'x', y = 'Total', orientation = 'h', color = 'Department', text = 'Department', barmode = 'stack', category_orders = {'Department': dept_order},
                         height = 350, hover_name = 'Count')
            fig2.update_traces(marker = dict(line = dict(width = 2, color = 'black')))
            fig2.update_layout(showlegend = False, yaxis = dict(showticklabels = False), xaxis = dict(showticklabels = False), bargap = 0.2, bargroupgap = 0.5)
            fig2.update_xaxes(title_text = '')
            fig2.update_yaxes(title_text = '')
            
            with chartcol:
                st.plotly_chart(fig2, use_container_width = True)

            with datacol:
                dept_counts2 = dept_counts
                dept_counts2.drop('Total', axis = 1, inplace = True)
                dept_counts2['Department'] = pd.Categorical(dept_counts2.Department, categories = dept_order, ordered = True)
                dept_counts2.sort_values(by = 'Department', inplace = True)
                df_table = dept_counts2[['Department', 'Count']]
                st.dataframe(df_table, hide_index = True, use_container_width = True)

            if st.button('Department View', use_container_width = True):
                st.session_state.selected = 'Departments'
        
            # Multiselect filter for df
            df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date
            df['Sched Finish Date'] = pd.to_datetime(df['Sched Finish Date']).dt.date

            # Filter functionality for df
            random_key_base = pd.util.hash_pandas_object(df)

            # Trying to make datetime columns correct format/type
            for col in df.columns:
                if pd.api.types.is_object_dtype(df[col]):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass
            
            modification_container = st.container()

            with modification_container:
                to_filter_columns = st.multiselect("Filter options", df.columns, key = f"{random_key_base}_multiselect")
                filters: pd.Dict[str, pd.Any] = dict()

                for column in to_filter_columns:
                    left, right = st.columns((1, 20))

                    if pd.api.types.is_categorical_dtype(df[column]) or df[column].nunique() <= 10 or column == 'Department':
                        left.write("↳")
                        filters[column] = right.multiselect(f"Values for {column}", df[column].unique(), default = list(df[column].unique()), key = f"{random_key_base}_{column}")
                        df = df[df[column].isin(filters[column])]

                    elif pd.api.types.is_numeric_dtype(df[column]):
                        left.write("↳")
                        _min = float(df[column].min())
                        _max = float(df[column].max())
                        step = (_max - _min) / 100
                        filters[column] = right.slider(f"Values for {column}", _min, _max, (_min, _max), step = step, key = f"{random_key_base}_{column}")                           
                        df = df[df[column].between(*filters[column])]

                    elif pd.api.types.is_datetime64_any_dtype(df[column]):
                        left.write("↳")
                        filters[column] = right.date_input(f"Values for {column}", value=(df[column].min(), df[column].max()), key = f"{random_key_base}_{column}")
                        if len(filters[column]) == 2:
                            filters[column] = tuple(map(pd.to_datetime, filters[column]))
                            start_date, end_date = filters[column]
                            df = df.loc[df[column].between(start_date, end_date)]

                    else:
                        left.write("↳")
                        filters[column] = right.text_input(f"Pattern in {column}", key = f"{random_key_base}_{column}")
                        df = df[df[column].str.contains(filters[column], case = True)]

            grid_options = {"rowSelection": "single",
                            "rowMultiSelectWithClick": False,
                            "suppressRowDeselection": False,
                            "suppressRowClickSelection": True,
                            "groupSelectsChildren": False,
                            "groupSelectsFiltered": True,
                            "preSelectAllRows": False,
                            'columnDefs': [
                                            {
                                                'field': 'Model Part',
                                                'checkboxSelection': True
                                            },
                                            {'field': 'HIN'},
                                            {'field': 'Start Date'},
                                            {'field': 'Sched Finish Date'},
                                            {
                                                'field': 'Status',
                                                'cellStyle': JsCode("""
                                                    function(params) {
                                                        switch(params.value) {
                                                            case 'Offline':
                                                                  return {backgroundColor: 'red'};
                                                            case 'Delayed':
                                                                 return {backgroundColor: 'orange'};
                                                            default:
                                                                  return {backgroundColor: 'green'};
                                                        }
                                                    }
                                                """)
                                            },
                                            {'field': 'Department'}]
            }

            aggrid_ALL = AgGrid(
                    df,
                    gridOptions = grid_options,
                    enable_enterprise_modules=True,
                    height=600,
                    fit_columns_on_grid_load=True,
                    search=True,
                    allow_unsafe_jscode=True
            ) 

            if aggrid_ALL.selected_rows:
                set_details_state(aggrid_ALL.selected_rows[0]['HIN'])
            else:
                st.write('No boat selected.')

        if st.session_state.facility == 'All':
            button_col1, button_col2 = st.columns(2)
            with button_col1:
                st.button('NPF Departments', use_container_width = True, on_click = set_state, args = ['NPF'])
            with button_col2:
                st.button('SPF Departments', use_container_width = True, on_click = set_state, args = ['SPF'])
            
            # Dominos tracker style chart (still needs some refining - shape, etc)
            chartcol, datacol = st.columns([9.5, 2])
            dept_order = ['Lamination', 'Post Pulling Buffer', 'Grinding',  'Post Grinding Buffer', 'Patch QC', 'Post Patch QC Buffer', 'Patch and Polish', 
                     'Post Patch and Polish Buffer', 'Underwater Gear', 'Post Underwater Gear Buffer', 'Dry Capping', 'Post Dry Capping Buffer', 
                     'Assembly', 'Post Assembly Buffer', 'Water Test', 'Post Water Test Buffer', 'Final Finish', 'Post Final Finish Buffer', 'Final Assembly']
            
            dept_counts = df['Department'].value_counts().reset_index()
            dept_counts.columns = ['Department', 'Count']
            dept_counts['Total'] = dept_counts['Count'].sum()
            dept_counts['x'] = dept_counts['Department'].nunique() / dept_counts['Total']

            fig2 = px.bar(dept_counts, x = 'x', y = 'Total', orientation = 'h', color = 'Department', text = 'Department', barmode = 'stack', category_orders = {'Department': dept_order},
                         height = 350, hover_name = 'Count')
            fig2.update_traces(marker = dict(line = dict(width = 2, color = 'black')))
            fig2.update_layout(showlegend = False, yaxis = dict(showticklabels = False), xaxis = dict(showticklabels = False), bargap = 0.2, bargroupgap = 0.5)
            fig2.update_xaxes(title_text = '')
            fig2.update_yaxes(title_text = '')
            
            with chartcol:
                st.plotly_chart(fig2, use_container_width = True)

            with datacol:
                dept_counts2 = dept_counts
                dept_counts2.drop('Total', axis = 1, inplace = True)
                dept_counts2['Department'] = pd.Categorical(dept_counts2.Department, categories = dept_order, ordered = True)
                dept_counts2.sort_values(by = 'Department', inplace = True)
                df_table = dept_counts2[['Department', 'Count']]
                st.dataframe(df_table, hide_index = True, use_container_width = True)

            if st.button('Department View', use_container_width = True):
                st.session_state.selected = 'Departments'
        
            # Multiselect filter for df
            df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date
            df['Sched Finish Date'] = pd.to_datetime(df['Sched Finish Date']).dt.date

            # Filter functionality for df
            random_key_base = pd.util.hash_pandas_object(df)

            # Trying to make datetime columns correct format/type
            for col in df.columns:
                if pd.api.types.is_object_dtype(df[col]):
                    try:
                        df[col] = pd.to_datetime(df[col])
                    except Exception:
                        pass
            
            modification_container = st.container()

            with modification_container:
                to_filter_columns = st.multiselect("Filter options", df.columns, key = f"{random_key_base}_multiselect")
                filters: pd.Dict[str, pd.Any] = dict()

                for column in to_filter_columns:
                    left, right = st.columns((1, 20))

                    if pd.api.types.is_categorical_dtype(df[column]) or df[column].nunique() <= 10 or column == 'Department':
                        left.write("↳")
                        filters[column] = right.multiselect(f"Values for {column}", df[column].unique(), default = list(df[column].unique()), key = f"{random_key_base}_{column}")
                        df = df[df[column].isin(filters[column])]

                    elif pd.api.types.is_numeric_dtype(df[column]):
                        left.write("↳")
                        _min = float(df[column].min())
                        _max = float(df[column].max())
                        step = (_max - _min) / 100
                        filters[column] = right.slider(f"Values for {column}", _min, _max, (_min, _max), step = step, key = f"{random_key_base}_{column}")                           
                        df = df[df[column].between(*filters[column])]

                    elif pd.api.types.is_datetime64_any_dtype(df[column]):
                        left.write("↳")
                        filters[column] = right.date_input(f"Values for {column}", value=(df[column].min(), df[column].max()), key = f"{random_key_base}_{column}")
                        if len(filters[column]) == 2:
                            filters[column] = tuple(map(pd.to_datetime, filters[column]))
                            start_date, end_date = filters[column]
                            df = df.loc[df[column].between(start_date, end_date)]

                    else:
                        left.write("↳")
                        filters[column] = right.text_input(f"Pattern in {column}", key = f"{random_key_base}_{column}")
                        df = df[df[column].str.contains(filters[column], case = True)]

            grid_options = {"rowSelection": "single",
                            "rowMultiSelectWithClick": False,
                            "suppressRowDeselection": False,
                            "suppressRowClickSelection": True,
                            "groupSelectsChildren": False,
                            "groupSelectsFiltered": True,
                            "preSelectAllRows": False,
                            'columnDefs': [
                                            {
                                                'field': 'Model Part',
                                                'checkboxSelection': True
                                            },
                                            {'field': 'HIN'},
                                            {'field': 'Start Date'},
                                            {'field': 'Sched Finish Date'},
                                            {
                                                'field': 'Status',
                                                'cellStyle': JsCode("""
                                                    function(params) {
                                                        switch(params.value) {
                                                            case 'Offline':
                                                                  return {backgroundColor: 'red'};
                                                            case 'Delayed':
                                                                 return {backgroundColor: 'orange'};
                                                            default:
                                                                  return {backgroundColor: 'green'};
                                                        }
                                                    }
                                                """)
                                            },
                                            {'field': 'Department'}]
            }

            aggrid_ALL = AgGrid(
                    df,
                    gridOptions = grid_options,
                    enable_enterprise_modules=True,
                    height=600,
                    fit_columns_on_grid_load=True,
                    search=True,
                    allow_unsafe_jscode=True
            ) 

            if aggrid_ALL.selected_rows:
                set_details_state(aggrid_ALL.selected_rows[0]['HIN'])

            else:
                st.write('No boat selected.')
















          




    elif st.session_state.selected == 'Details':
        if st.session_state.details == 'N':
            st.warning('Please select a boat first.')

        else:
            current_hin = st.session_state.HIN
            st.session_state.hin_history.append(current_hin)
            
            if len(st.session_state.hin_history) == 1:
                st.session_state.issues = []
            
            else:
                if current_hin in st.session_state.hin_history:
                    if current_hin in st.session_state.issue_details:
                        st.session_state.issues = st.session_state.issue_details[current_hin]
                    else:
                        st.session_state.issues = []
                else:
                    st.session_state.issues = []

            st.title('Details')

            location = df.loc[df['HIN'] == st.session_state.HIN, 'Department'].values[0]
            st.metric('Current Location', location, '9:40 AM')
            
            grid_options = {
                'columnDefs': [{'field': 'Model Part'},{'field': 'HIN'},{'field': 'Start Date'},{'field': 'Sched Finish Date'},{
                    'field': 'Status',
                    'cellStyle': JsCode("""
                        function(params) {
                            switch(params.value) {
                                case 'Offline':
                                    return {backgroundColor: 'red'};
                                case 'Delayed':
                                    return {backgroundColor: 'orange'};
                                default:
                                    return {backgroundColor: 'green'};
                            }
                        }
                    """)
                },{'field': 'Department'}]
            }

            grid_response = AgGrid(
                df[df['HIN'] == st.session_state.HIN],
                gridOptions = grid_options,
                enable_enterprise_modules=True,
                height=93,
                fit_columns_on_grid_load=True,
                search=True,
                allow_unsafe_jscode=True
            )

            no_issues = st.checkbox('No issues')
            if not no_issues:
                issue_type = st.selectbox('Issue Type', ['', 'Missing Part', 'Defective Part', 'Delay', 'Other'])
                if issue_type == 'Other':
                    st.warning('Please describe issue below.')
                issue_description = st.text_input('Issue Description', '')
                issue_severity = st.selectbox('Severity', ['', 'High', 'Medium', 'Low'])
                issue_priority = st.selectbox('Priority', ['', 'High', 'Medium', 'Low'])
                # ... (any other fields you want to include)

            elif no_issues:
                issue_description = 'No issues reported.'
                timenow = datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S %p")
                issue_type = 'NA'
                issue_severity = 'NA'
                issue_priority = 'NA'
                # ... (any other fields you want to include)

            if st.button('Add entry'):
                # Check that all fields have been filled
                if not no_issues and (not issue_description or not issue_type or not issue_severity):  # adjust this line as needed
                    st.warning('Please fill in all fields.')
                else:
                    timenow = datetime.datetime.now().strftime("%m-%d-%Y %I:%M:%S %p")
                    entry = {
                        'Type': issue_type,
                        'Severity': issue_severity,
                        'Priority': issue_priority,
                        'Description': issue_description,
                        'Time': timenow
                    # ... (any other fields you want to include)
                    }
                    
                    st.session_state.issues.append(entry)  # Append the new entry to the list
                    st.session_state.issue_details[current_hin] = st.session_state.issues # adding new entry to encompassing issue dictionary for each boat

    
            if 'issues' in st.session_state and st.session_state.issues:
                # Reverse the list of issues so the newest entries are at the top
                reversed_issues = st.session_state.issue_details[current_hin][::-1]
                # Convert the reversed list of issues to a DataFrame
                issues_df = pd.DataFrame(reversed_issues)

            # Display existing issues
            if st.session_state.issues:
                issues_df = pd.DataFrame(st.session_state.issues[::-1])
                st.table(issues_df.assign(hack='').set_index('hack'))

                # Select entry to edit
                entry_to_edit = st.selectbox('Select entry to edit:', issues_df.index[::-1])

                if entry_to_edit is not None:
                    # Display editable form for selected entry
                    with st.form(key='edit_form'):
                        #st.write(f'Editing entry {entry_to_edit}')
                        edited_description = st.text_input('Description', issues_df.loc[entry_to_edit, 'Description'])
                        edited_type = st.text_input('Type', issues_df.loc[entry_to_edit, 'Type'])
                        edited_severity = st.text_input('Severity', issues_df.loc[entry_to_edit, 'Severity'])
                        edited_priority = st.text_input('Priority', issues_df.loc[entry_to_edit, 'Priority'])

                        if st.form_submit_button('Submit Changes'):
                            # Update the selected entry with new values
                            st.session_state.issues[entry_to_edit] = {
                                'Time': issues_df.loc[entry_to_edit, 'Time'],  # keep the original time
                                'Description': edited_description,
                                'Type': edited_type,
                                'Severity': edited_severity,
                                'Priority': edited_priority
                            }
            else:
                st.write("No entries yet.")

        if st.button('Return to Home Page', use_container_width = True):
            st.session_state.selected = 'Home'





























    elif st.session_state.selected == 'Departments':
        st.title('Department View')

        depts = ['Lamination', 'Post Pulling Buffer', 'Grinding',  'Post Grinding Buffer', 'Patch QC', 'Post Patch QC Buffer', 'Patch and Polish', 
                 'Post Patch and Polish Buffer', 'Underwater Gear', 'Post Underwater Gear Buffer', 'Dry Capping', 'Post Dry Capping Buffer', 
                 'Assembly', 'Post Assembly Buffer', 'Water Test', 'Post Water Test Buffer', 'Final Finish', 'Post Final Finish Buffer', 'Final Assembly']
        
        buffers = ['Post Grinding Buffer', 'Post Patch QC Buffer', 'Post Patch and Polish Buffer', 'Post Underwater Gear Buffer', 'Post Dry Capping Buffer', 'Post Assembly Buffer', 
                   'Post Water Test Buffer', 'Post Final Finish Buffer']
        
        dept = st.selectbox('Department', ['', 'Lamination',  'Post Pulling Buffer', 'Grinding',  'Post Grinding Buffer', 'Patch QC', 'Post Patch QC Buffer', 'Patch and Polish', 
                                           'Post Patch and Polish Buffer', 'Underwater Gear', 'Post Underwater Gear Buffer', 'Dry Capping', 'Post Dry Capping Buffer', 
                                           'Assembly', 'Post Assembly Buffer', 'Water Test', 'Post Water Test Buffer', 'Final Finish', 'Post Final Finish Buffer', 'Final Assembly'])
        
        if dept == '':
            st.warning('Please select a department.')

        else:
            # probably better way to do this - open to improvements/suggestions
            ind_dept = depts.index(dept)
            prev_dept = depts[ind_dept - 1] if ind_dept > 0 else 'N'
            prev2_dept = depts[ind_dept - 2] if ind_dept > 1 else 'N'
            next_dept = depts[ind_dept + 1] if ind_dept < len(depts) - 1 else 'N'
            next2_dept = depts[ind_dept + 2] if ind_dept < len(depts) - 2 else 'N'

            five_depts = [prev2_dept, prev_dept, dept, next_dept, next2_dept]
            
            # Casting Start Date as datetime type so sort works properly
            df['Start Date'] = pd.to_datetime(df['Start Date']).dt.date

            c1, c2, c3, c4, c5 = st.columns(5)

            # Looping through dept list and writing dataframe into corresponding column
            # Third column is the department selected by user
            aggrids = {}

            for i, x in enumerate(five_depts):
                col_list = [c1, c2, c3, c4, c5]
                with col_list[i]:
                    if x == 'N': # no department exists in this position (e.g. no department before lamination)
                        st.write('')
                    else:
                        st.write(x)
                        dept_df = df.loc[df['Department'] == x][['HIN', 'Status', 'Start Date']]
                        if len(dept_df) != 0:
                            # Sorting boats in department by start date
                            srt_idx = np.argsort(df[df['Department'] == x]['Start Date'])
                            dept_df_srt = pd.DataFrame(dept_df.iloc[srt_idx][['HIN', 'Start Date', 'Status']])
                
                            grid_options = {"rowSelection": "single",
                            "rowMultiSelectWithClick": False,
                            "suppressRowDeselection": False,
                            "suppressRowClickSelection": True,
                            "groupSelectsChildren": False,
                            "groupSelectsFiltered": True,
                            "preSelectAllRows": False,
                            'columnDefs': [
                                            {
                                                'field': 'HIN',
                                                'checkboxSelection': True
                                            },
                                            {'field': 'Start Date'},
                                            {
                                                'field': 'Status',
                                                'cellStyle': JsCode("""
                                                    function(params) {
                                                        switch(params.value) {
                                                            case 'Offline':
                                                                  return {backgroundColor: 'red'};
                                                            case 'Delayed':
                                                                 return {backgroundColor: 'orange'};
                                                            default:
                                                                  return {backgroundColor: 'green'};
                                                        }
                                                    }
                                                """)
                                            }]
                            }

                            grid_name = f"aggrid_{x.replace(' ', '_')}_{i}"

                            aggrids[grid_name] = AgGrid(
                                                dept_df_srt,
                                                gridOptions = grid_options,
                                                enable_enterprise_modules=True,
                                                height=600,
                                                fit_columns_on_grid_load=True,
                                                search=True,
                                                allow_unsafe_jscode=True
                            ) 

                        else:
                            st.write('No boats in this department.')

            for grid in aggrids.values():
                if grid.selected_rows:
                    set_details_state(grid.selected_rows[0]['HIN'])

            button_states = [False] * 5
            for i, col in enumerate(col_list):
                with col:
                    if five_depts[i] == 'N':
                        button_states[i] = False
                    
                    else:
                        button_states[i] = st.button(five_depts[i] + ' Detailed View')

            
            for i, state in enumerate(button_states):
                if state:
                    dept_select = five_depts[i]
                    df_dept = df.loc[df['Department'] == dept_select]
                    
                    st.title(f'Boats in {dept_select}')
                    for idx, row in df_dept.iterrows():
                        current_hin = row['HIN']
                        st.session_state.hin_history.append(current_hin)
                        
                        if len(st.session_state.hin_history) == 1:
                            st.session_state.issues = []
                        
                        else:
                            if current_hin in st.session_state.hin_history:
                                if current_hin in st.session_state.issue_details:
                                    st.session_state.issues = st.session_state.issue_details[current_hin]
                                else:
                                    st.session_state.issues = []
                            else:
                                st.session_state.issues = []

                        st.write('')
                        st.write('')
                        st.subheader(f"Boat {row['HIN']}")

                        location = row['Department']
                        st.metric('Current Location', location, '9:40 AM')
                        
                        grid_options = {
                            'columnDefs': [{'field': 'Model Part'},{'field': 'HIN'},{'field': 'Start Date'},{'field': 'Sched Finish Date'},{
                                'field': 'Status',
                                'cellStyle': JsCode("""
                                    function(params) {
                                        switch(params.value) {
                                            case 'Offline':
                                                return {backgroundColor: 'red'};
                                            case 'Delayed':
                                                return {backgroundColor: 'orange'};
                                            default:
                                                return {backgroundColor: 'green'};
                                        }
                                    }
                                """)
                            },{'field': 'Department'}]
                        }

                        grid_response = AgGrid(
                            df[df['HIN'] == current_hin],
                            gridOptions = grid_options,
                            enable_enterprise_modules=True,
                            height=93,
                            fit_columns_on_grid_load=True,
                            search=True,
                            allow_unsafe_jscode=True
                        )

                        if 'issues' in st.session_state and st.session_state.issues:
                            # Reverse the list of issues so the newest entries are at the top
                            reversed_issues = st.session_state.issue_details[row['HIN']][::-1]
                            # Convert the reversed list of issues to a DataFrame
                            issues_df = pd.DataFrame(reversed_issues)
                            issues_df = pd.DataFrame(st.session_state.issues[::-1])
                            st.table(issues_df.assign(hack = '').set_index('hack'))
                        
                        else:
                            st.write('No issues yet.')

        if st.button('Return to Home Page', use_container_width = True):
            st.session_state.selected = 'Home'

if __name__ == "__main__":
    main()