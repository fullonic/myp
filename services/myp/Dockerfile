# base python image
FROM python:3.7.3-alpine

# install dependencies
RUN apk update && \
    apk add --virtual build-deps gcc python-dev musl-dev && \
    apk add postgresql-dev && \
    apk add netcat-openbsd libffi-dev
# SET WORKING DIR

WORKDIR /home/myp/app

# ADD AND INSTALL REQUIREMENTS
COPY ./requirements.txt /home/myp/app/requirements.txt
RUN pip install -r requirements.txt

# ADD ENTREYPOINT AND MAKE IT EXEC
COPY ./entrypoint.sh /home/myp/app/entrypoint.sh
RUN chmod +x /home/myp/app/entrypoint.sh

# ADD THE APP
COPY . /home/myp/app


# RUN SERVER
CMD ["/home/myp/app/entrypoint.sh"]
