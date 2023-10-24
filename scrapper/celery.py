from celery import Celery  # type:ignore

# The include option is necessary to list the modules every worker should import
app = Celery("scrapper", broker="amqp://localhost", include=["tasks"])
