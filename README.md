# 381chatbot
 
How to add a Paramiko skill to 381chatbot:

1) Make a Paramiko script and convert it into a python function using the key word "def" with a parameter "incoming_msg" (the message that the bot will read in from Webex)

![SS1-step 1](https://user-images.githubusercontent.com/93939453/144773987-66c3cf6d-f8b5-4a54-84ee-c7820cbf7db1.PNG)


2) Also make sure to change the router Ip address, username, and password to the correct ones as needed.

3) Edit the Paramiko script to return the output so our bot can read it and output it to webex.

![SS2-step 3](https://user-images.githubusercontent.com/93939453/144774373-7e04a577-f42d-460b-959f-bc8ef4a68a9b.PNG)


4) Import the Paramiko script to the 381Bot.py file

![SS3 step 4](https://user-images.githubusercontent.com/93939453/144774576-96b27ec8-a3a6-4457-a621-49d2f5f1d47b.PNG)


5) Add the bot command to the 381Bot.py file

![SS4 step 5](https://user-images.githubusercontent.com/93939453/144774807-27f19085-7959-4b0b-abaf-d4da48a5769c.PNG)

6) Now we can test our Bot's new Paramiko skill by running the 381Bot.py file and typing in "show ip int brief" on Webex


![SS5 step 6](https://user-images.githubusercontent.com/93939453/144775185-cfed36d1-ac6f-43dc-a59d-faaeb5c11278.PNG)
