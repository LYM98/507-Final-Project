Required Packages
    requests
    pandas
    BeautifulSoup


To property run the program, please use the following command:
    
    python .\final_project.py

Interaction with program

    To interact the program, users only need to follow the instructions in the command prompt. Here is a brief description of the processs. When user first launchs the program, user will be asked to scrape data from the website or load the data from the cache. After that, users will be asked whether they want to save the data for later use or not. Once it is done, users will be asked to choose the preferable price, brand, age, and mileage of the car. If there are matched results in the scraped data, system will show all attributes of the results in a tabular format. 

Data Structure

    For this project, scraped data is organized into a tree structure. Nodes in each level are corresponding to options of each decision users can make. For used car matching system I implemented, users are allowed to chooce the brand, year, mileage, and price. As a result, the tree has four levels. System will iterate through the tree based on users decisions and present the matching results in the leaf node. 


