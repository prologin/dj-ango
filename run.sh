#! /bin/sh

gunicorn -b :1234 wsgi:application -t 99999
