# ServiceConnect
ServiceConnect is a web app that aims to connect those in need with services that can help them via SMS.

## Deployment
The site is hosted on Docker containers and can be built from the project root using docker-compose.  
### Setup Env
Before deployment certain environmental variables need to be set.  In the project root create a folder called .env and inside create two files .dbenv and .appenv:
```
mkdir env && cd .env
touch .dbenv .appenv
```
In the two files the following environmental variables need to be set:
.dbenv
```
POSTGRES_DB=<database_name>
POSTGRES_USER=<database_user>
POSTGRES_PASSWORD=<database_password>
```
.appenv
```
DATABASE_HOST=<dataase url>
TWILIO_SID=<SID>
TWILIO_AUTH=<AUTH>
ENV=<indicate production or development>
```
### Running with Docker
As superuser use the command:
```
docker-compose up --build
```
The service should now be running
### Running without Docker
To run the serice without Docker is possible although not suggested.  First a Postgres database needs to be running at the specified DATABASE_HOST, then an virtualenv needs to setup I use virtualenvwrapper
```
mkvirtualenv ServiceConnect
```
Then install the required packages using:
```
pip install -r requirements.txt
```
The environment variable from appenv need to be set on the local enviroment (Note: the variables will persist after the virtualenv is deactivated):
```
DATABASE_HOST=<dataase url>
TWILIO_SID=<SID>
TWILIO_AUTH=<AUTH>
ENV=<indicate production or development>
```
The server is now ready to be run locally using while in the project root:
```
python3 run.py
```
