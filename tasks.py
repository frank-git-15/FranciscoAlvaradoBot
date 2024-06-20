from robocorp.tasks import task


class Article:
    def __init__(self,header,description,imgeUrl) -> None:
        pass



@task
def minimal_task():
    message = "Hello"
    message = message + " World!"
