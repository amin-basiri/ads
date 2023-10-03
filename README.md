# Installation

Make sure you have python and pip packages manager installed on your device
and you are in root of project in your terminal.

You need to install required packages to run service:

```shell
pip install -r requirements.txt
```


### Initialize Database
Make sure postgresql is up on port `5432` of localhost
```shell
python manage.py makemigrations
```
Then:
```shell
python manage.py migrate
```


### Create Admin User
```shell
python manage.py createsuperuser
```
Fill username and password of admin user


### Launch
```shell
python manage.py runserver
```


Now you can access admin panel in `http://localhost/admin/` and enter admin username and password.


Enjoy :)


# Test

```shell
python manage.py test
```