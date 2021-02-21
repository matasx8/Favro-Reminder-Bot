How to use program:
1. configure settings.json
	"mailer" "email" must be gmail
	"mailer" "psw" gmail api password
	you don't have to change these, will work with my email for testing

	"favroInfo" "email" favro users email
	"favroInfo" "token" favro users token
	you don't have to change these, will work with my email for testing

2. IMPORTANT!!!! If you don't want to send emails to users on selected widget go to dataHandler.py and uncomment
lines 50, 51 and comment lines 52, 53 and enter your email instead of "YOUREMAIL"

3. If you dont want to wait for 8 am, go to main.py comment lines 60, 61, uncomment lines 62, 63

3. Run main.py and each work day this service will remind people about their stuck tasks


---------------------------------
To make a get request, in cmd type curl -X GET localhost:5000/json
