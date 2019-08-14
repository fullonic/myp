# base image
FROM postgres:11.2-alpine

# run create.db on init
ADD create.sql /docker-entrypoint-initdb.d
