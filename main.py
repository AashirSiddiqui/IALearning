from flask import Flask, render_template
import pymongo
import json

app = Flask((__name__))

@app.route("/")
def mainpage():
    return render_template("index.html")

@app.route("/home")
def accountpage():
    return render_template("account.html")

@app.route("/lesson.html")
def redirectToLesson():
    return render_template("redirect.html", page="lesson")

@app.route("/lesson")
def lessonpage():
    return render_template("lesson.html", lesson=["ID01Learntest", "ID02", "ID00Welcome to this text","ID03Try rereading the text.", "ID00You will learn here"])

@app.route("/submitlesson", methods=["POST", "GET"])
def submitlesson():
    return json.dumps("hello")

app.debug = True 

if __name__ == "__main__":
    app.run()