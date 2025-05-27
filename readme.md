# Personal finance manager
This is a personal finance manager, which reads your gmail, parses statements and pushes structured finance data into google sheets.

# Setup steps. 

## Step 0: Clone the github repo in your machine. 

## Step 1: Create a GCP project and configure an outh2.0 client in that project. 
- create a new project in gcp.
- enable gmail api access for this project. 
- in the credintials page create an oauth 2.0 client.
- fill in the app name like gmail-desktop and select external for personal use. 
- add your email id as a test user.
- Download the credentials.json file from that project and keep it in the working directory of your github repo.
(This is already added to your .gitignore of the project)

- while running the script for the first time it would redirect to chrome and ask for permissions. From second time onwards the inbuilt token.json would be used for such work. Also make sure to use the same gmail account everywhere. 


