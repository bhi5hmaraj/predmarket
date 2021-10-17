# This repository contains code for the prediction market POC  
  
Project structure  
|---- project  
|----------- init.py  
|----------- auth.py  
|----------- main.py  
|----------- models.py  
|----------- static  
|----------- templates  
|---- README.md  
  
To recreate this website, first create a virtual environment using the requirements.txt. You will need to replace the facebook login with a seperate login feature and link a new database. Recommend following this https://www.digitalocean.com/community/tutorials/how-to-add-authentication-to-your-app-with-flask-login.  
  
In order for the bets to placed you wil also need a kakfa engine. Repo for this coming soon..  
  
init.py helps creates the app  
auth.py helps the login for users  
main.py is a driver  
models.py is sqlite database  
templates has the html code  
static should have any js code but ignore that for now
