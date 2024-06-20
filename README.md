Some of the projects and work I have done with data, including visualizations, machine learning, and more, mostly in Python. A summary of each file follows.

- "Taylor Swift Visualizations.ipynb" is a project I did to find the most common words across Taylor Swift's discography per album as well as compare statistics between albums, as it provides insight into the vibes of each album, and many people say Taylor Swift is very one-dimensional in her songs (i.e. always talking about love and heartbreak). To show the most common words in each album, I employed the use of word clouds, and made the shape and color of each word cloud match the cover of the album. This project involved scraping data from the Spotify API for track names and statistics, such as acousticness and length of the songs, as well as the Genius API for the lyrics to each song. The findings from this project surprised me, as only 4 of the 10 albums had a significant presence of the word "love", but each album does address the topics of love and heartbreak from a different angle (e.g. 1989 does so from a more lighthearted perspective), as also demonstrated with the word choices in other albums. Overall, this was a very fun project to do, and I learned a lot about webscraping as well as creating visualizations based on text data. 

- "Dashboard_TEST.py" is part of my Senior Design project, in which I worked with a company to create a production tracking dashboard so management could know where any product was in the assembly process. The goal of this dashboard was to reduce manual data entry by 50%, as a lot of the tracking was done manually before (Excel files, paper schedules, etc.). This dashboard was built using the Streamlit package in Python, which allows for the use of a web-based dashboard for ease of access, and also makes the dashboard very modular, as every part of it is easily modifiable. In addition to the Python used for the dashboard, this project also involved SQL as a database was created so that any information updated through the dashboard was sent to the database and then could be used by the ERP system the client already had in place. The end product was an easily usable dashboard with an overview page, a details page to see specific information about a singular product and update this information, as well as a page to see a subset of the assembly process and the products within each stage. The image "Dashboard.png" shows some of the main page, including the graph with the number of products in each stage of assembly as well as a big table showing information about all of the products in assembly. This was a very extensive project, and with only having about 3 months to do it, there were some features that were not able to be implemented, but I am still proud of the final product, and this project introduced me to dashboard creation, which I enjoyed doing.

- "Genre Classification by Lyrics.ipynb" is another project in a similar vein to that of the Taylor Swift one, as this focuses on prediction of song genre by the song's lyrics. I listen to a lot of music, so I enjoy working with data concerning music, and in this project, I wanted to challenge myself and learn about neural networks, especially recursive neural networks (RNNs), which are particularly useful for text data such as song lyrics. There were some NLP techniques applied within this project as well, as the data needed lots of cleaning, and to be put into a format readable by the machine for predicting - in this case, a simple dictionary in which each word was assigned an integer based on its frequency. The model employed for prediction was a relatively simple RNN consisting of an embedding layer, an LSTM layer, a fully connected layer, and a dropout layer. In the end, the model did not perform too well, having only 40% accuracy, but there were many limitations, such as only focusing on only lyrics and the simple vectorization method I used which may have simplified the data too much. However, for my first attempts at NLP and neural networks in general, it is not bad at all, and I am glad to have some exposure to neural networks.

- [In Progress] "Group Chat Dashboard.py" follows suit from the dashboard I built for my Senior Design project, as I realized how much I enjoy visualizing data and the format of a dashboard. This dashboard focuses on data from a group chat I have with my friends over 3 years, as I wanted to see how our vocabulary and activity has changed over this time using visualizations and statistics. In addition, I wanted to learn Dash, which is another Python framework for creating interactive dashboards. This project consists of the Group Chat Dashboard.py file, as well as the three page files for the dashboard (home.py, page2.py, page3.py).

- [In Progress] "spotify_analysis.pbix" is an exploration of my Spotify listening history, as I love listening to music and obsess over statistics and data pertaining to my listening. Since I have always used Python for data exploration, as shown with the previous projects, I wanted to try something different and get some exposure to Power BI. In this project, I am looking to generate a comprehensive report with data visuals to answer some burning questions I have about the music I listen to, such as which songs I skip the most or how my music taste has changed over 2 years, since I seem to find a new obsession every two weeks.
