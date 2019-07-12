# SalesforceIoT

Setup Steps:

1. Open terminal and use command: sudo pip install packagename
   Run command for each of the following packages, replacing 'packagename' with the name of the package
      a. simple-salesforce
      b. datetime
      c. serial
      d. threading

2. Create a credentials.py file with 2 variables: username and password
   These variables should contain your username and password of your Salesforce org

3. Ensure Python script (line 21) and Arduino settings are set to stream and read from the same USB port

4. Push the .ino file onto an Arduino
