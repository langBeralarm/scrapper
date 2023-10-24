from scrapper import app


@app.task(name="tasks.tasks.add")
def add(x: int, y: int) -> int:
    return x + y
