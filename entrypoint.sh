#!/bin/sh

echo "Connection to DB"

while ! nc -z ${SQL_HOST} ${SQL_PORT}; do
  sleep .2s
done

echo "Connected!"

if [ $CELERY -eq 1 ]
then
  bash -c "cd ./medweb && python -m celery -A medweb worker"
else
  python ./medweb/manage.py makemigrations
  echo "MIGRATION BASE!"

  python ./medweb/manage.py makemigrations medml
  echo "MIGRATION MEDML!"
  python ./medweb/manage.py makemigrations medemail
  echo "MIGRATION MEDEMAIL!"
  python ./medweb/manage.py makemigrations inner_mail
  echo "MIGRATION inner_mail!"
  python ./medweb/manage.py migrate auth
  python ./medweb/manage.py migrate medml
  python ./medweb/manage.py migrate medemail
  python ./medweb/manage.py migrate inner_mail
  python ./medweb/manage.py migrate

  python ./medweb/manage.py base_configuration
  python ./medweb/manage.py collectstatic --noinput

  # python ./medweb/manage.py runserver 0.0.0.0:8000

fi

exec "$@"