Follow steps in the link below to install and configure postgres sql with Django

https://www.digitalocean.com/community/tutorials/how-to-use-postgresql-with-your-django-application-on-ubuntu-20-04

Note: In addition to premissions granted above, you also need to grand permission to SCHEMA Public. Do it by executing below command in postgres cli
GRANT ALL ON SCHEMA public TO sai_user;
GRANT USAGE ON SCHEMA public TO sai_user;
GRANT CREATE ON SCHEMA public TO sai_user;

#For some reason giving all the permissions of superuser (postgres) to the desired user will fix error [django.db.utils.ProgrammingError: permission denied for schema public]

GRANT postgres TO sai_user;
