from scrapper import app


@app.task
def alert(message: str):
    print(f"Alert: {message}")
    return message.capitalize()


@app.task
def notify(message: str, recipient: str):
    print(f"Notification {message} for: {recipient}")
