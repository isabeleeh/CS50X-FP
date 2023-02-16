# HERBS INVENTORY MANAGEMENT
#### Video Demo:  <https://youtu.be/XjD9Tl5qczI>
#### Description:
This project is based on the daily requirements of myself. As people who are under Chinese medicine conditioning, instead of manually check out our herbs inventory, we are anxious to build up such a system that can record each herb's remaining amount, automatically read doctor's prescription and minus the amount from inventory, replenish, as well as some other basic operations to the data. It is a web-based application using JavaScript, Python, and SQL. Part of the style inherits one of CS50x Problem Sets *Finance* (hereinafter called *Finance*).

#### Requirements:
1. By default, the homepage will display all the herbs recorded in database, ordered by Chinese pinyin. 
   - The homepage will provide a quick way to update the 'Amount' field by clicking the 'Change' button designed for each line. 
   - The homepage will provide '-' button for each herb to remove it permanently. 
   - The homepage will also provide the feature to delete all records from database by clicking 'Remove All' button.

2. The project will read the prescription like below, resolve the listed herbs together with the amount, and minus the amount accordingly from inventory. It will be listed out if certain herbs are not in stock or the amount is not sufficient. 

   One example of doctor's prescription is as follows:
   > 白芍12克，枳实10克，苍术10克，丹参12克，菟丝子15克，楮实子12克，茺蔚子12克，枸杞子10克，寒水石10克先煎，木瓜10克，五味子6克，桑寄生12克，茯苓12克，三副，每副冲服三七粉2克

3. The project will provide a 'replenish' feature, with which the 'amount' information can be updated for existing herbs and new herbs with amount information can be added.

4. The project will import .csv file and record the data into database. The .csv file is supposed to have two fields: 'Name' and 'Amount'. If certain herb already exists in database, the feature will only update the 'amount' field.

5. The project will allow users to export one .csv file to local computer. Currently only 'Name' and 'Amount' fields are provided.

6. Please be noted that above is just phase I requirements. Moving forward, more feaures might be added, such as replenish price record, usage record, herbs usage trending analysis, etc.

#### Files Usage And Explaination:
1. Python files

   - 'app.py': the major python file under Flask framework. It includes following functions:

     - 'index': the homepage's default display page, listing all herbs and fundamental information stored in database.

     - 'importfile': uploads .csv file, resolves it and writes into database correspondingly. Currently the supported format is fixed being 'Name' and 'Amount'. 'Name' field supports string of both Chinese character and pinyin as follows:

        > ba ji tian 巴戟天
     
     - 'prescription': resolves the prescription, automatically minus the amount of listed herbs from database, lists those that are not in database yet or the amount is not sufficient for users' further action.

     - 'manage': allows users to quickly update the amount of certain herb listed on homepage.

     - 'replenish': allows users to update the amount of existing herbs or add new herbs and its amount.

     - 'remove': a quick way from homepage for users to remove herbs from database one at a time.

     - 'removeall': allows users to remove all herbs from database.

     - 'export': allows users to export data to local disk. Currently only two fields will be shown being 'Name' and 'Amount'. 

   - 'helpers.py': defines some internally invoked functions.
   
     - 'apology'. Notice how it ultimately renders a template, 'apology.html'. It also happens to define within itself another function, 'escape', that it simply uses to replace special characters in apologies. By defining 'escape' inside of 'apology', we’ve scoped the former to the latter alone; no other functions will be able (or need) to call it. This part herits from *Finance*.

     - 'allowed_file': check if the extension is valid based on the set of allowed file extensions ALLOWED_EXTENSIONS. Currently only .csv is supported.

     - 'preprocess: handles some "irregular" usages in prescription based the doctor's habit. For example, the doctor likes to use "赤白芍各6克" instead of "赤芍6克，白芍6克". This function is to change the former to the latter.

     - 'split_herbs': takes the whole prescrition as the input and return a set of dict type data with the fields 'Chinese_ch' and 'amount'.

     - 'is_all_chinese': checks out whether the string is all Chinese character.

     - 'generate_download_headers': generates download headers for the 'export' function.

   - 'requirements.txt': This file simply prescribes the packages on which this app will depend.

   - 'static/': This folder contains two files being 'styles.css' with some CSS lives partly inheriting from that of *Finance*, as well as 'sqlite3_creation.txt' that records the code to create tables in 'sqlite3'.

   - 'templates/': contains all the '.html' files.

     - 'layout.html': partly inherits the style of *Finance*, using "navbar" based on Bootstrap.

     - 'apology.html': a template for an apology, inheriting from *Finance*.

     - 'index.html': what the homepage displays by default.

     - 'importfile.html': the page from which the users can import '.csv' file from local disk and store data into server.

     - 'replenish.html': the page users can update herbs' amount or insert new herbs.

     - 'export.html': the page users can download '.csv' file that lists all herbs' names and amount information. Currently no download path can be chosen.

     - 'prescription.html': the page users can input the doctor's prescription.

   - 'uploads/': folder for 'importfile' function to tempororily store .csv file.

#### Further Action:
More features could be implemented after using the app for some time. That would be a phase II project.

        
