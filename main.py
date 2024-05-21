from flask import Flask

app = Flask(__name__)

@app.post("/create")
def createJob():
    pass

@app.post("/install")
def installDependencies():
    pass

@app.post("/reboot")
def reboot():
    pass

@app.post("/stow")
def stow():
    pass