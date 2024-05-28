Some of the projects and work I have done with data, including visualizations, machine learning, and more in Python. A summary of each file follows.

"Taylor Swift Visualizations.ipynb" is a project I did to find the most common words across Taylor Swift's discography per album as well as compare statistics between albums, as it provides insight into the vibes of each album, and many people say Taylor Swift is very one-dimensional in her songs (i.e. always talking about love and heartbreak). To show the most common words in each album, I employed the use of word clouds, and made the shape and color of each word cloud match the cover of the album. This project involved scraping data from the Spotify API for track names and statistics, such as acousticness and length of the songs, as well as the Genius API for the lyrics to each song. The findings from this project surprised me, as only 4 of the 10 albums had a significant presence of the word "love", but each album does address the topics of love and heartbreak from a different angle (e.g. 1989 does so from a more lighthearted perspective), as also demonstrated with the word choices in other albums. Overall, this was a very fun project to do, and I learned a lot about webscraping as well as creating visualizations based on text data. 

"Dashboard_TEST.py" is part of my Senior Design project, in which I worked with a company to create a production tracking dashboard so management could know where any product was in the assembly process. The goal of this dashboard was to reduce manual data entry by 50%, as a lot of the tracking was done manually before (Excel files, paper schedules, etc.). This dashboard was built using the Streamlit package in Python, which allows for the use of a web-based dashboard for ease of access, and also makes the dashboard very modular, as every part of it is easily modifiable. In addition to the Python used for the dashboard, this project also involved SQL as a database was created so that any information updated through the dashboard was sent to the database and then could be used by the ERP system the client already had in place. The end product was an easily usable dashboard with an overview page, a details page to see specific information about a singular product and update this information, as well as a page to see a subset of the assembly process and the products within each stage. This was a very extensive project, and with only having about 3 months to do it, there were some features that were not able to be implemented, but I am still proud of the final product, and this project showed me a new love for data analysis and presentation of data within a dashboard format. The image "Dashboard.png" shows some of the main page, including the graph with the number of products in each stage of assembly as well as a big table showing information about all of the products in assembly. All data shown in the image was generated randomly and it does show a static version of the dashboard.

"Genre Classification by Lyrics.ipynb" is another project in a similar vein to that of the Taylor Swift one, as this focuses on prediction of song genre by the song's lyrics. I listen to a lot of music, so I enjoy working with data concerning music, and in this project, I wanted to challenge myself and learn about neural networks, especially recursive neural networks (RNNs), which are particularly useful for text data such as song lyrics. There were some NLP techniques applied within this project as well, as the data needed lots of cleaning, and to be put into a format readable by the machine for predicting - in this case, a simple dictionary in which each word was assigned an integer based on its frequency. The model employed for prediction was a relatively simple RNN consisting of an embedding layer, an LSTM layer, a fully connected layer, and a dropout layer. In the end, the model did not perform too well, having only 40% accuracy, but there were many limitations, such as only focusing on only lyrics and the simple vectorization method I used which may have simplified the data too much. However, for my first attempts at NLP and neural networks in general, it is not bad at all, and I am glad to have done some work with neural networks.

[In Progress] "Group Chat Dashboard.py" follows suit from the dashboard I built for my Senior Design project, as I realized how much I enjoy visualizing data and the format of a dashboard. This dashboard focuses on statistics from a group chat I have with my friends over almost 3 years. In creating this dashboard and dataset, I want to figure out some other things as well, such as the most/least frequent interactions and most active times, so that I have a basis for further exploration with this data, including creating a model to predict the author of a given message. 
