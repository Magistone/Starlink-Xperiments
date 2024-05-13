from flask import Flask

app = Flask(__name__)

@app.post("/create")
def createJob():
    pass