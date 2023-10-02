# Installation

Make sure you are in root of project in your terminal.


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
python manage.py runserver
```