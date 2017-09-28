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
ENV=<indicate production or development>
```
Finally as superuser use the command:
```
docker-compose up --build
```
The service should now be running
