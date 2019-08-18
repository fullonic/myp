from .. import celery

@celery.task()
def multiply(x, y):
    return x * y

@celery.task()
def log(msg):
    return msg
