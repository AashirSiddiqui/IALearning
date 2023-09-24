from flask import Flask, render_template, request, session
from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv

app_path = os.path.join(os.path.dirname(__file__), '.')
dotenv_path = os.path.join(app_path, '.env')
load_dotenv(dotenv_path)

client = MongoClient(os.environ.get("MONGODB_URI"))
db = client.IALearning

accounts = db.Accounts
lessons = db.Lessons

print(accounts, lessons)

app = Flask((__name__))

app.secret_key = os.environ.get("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/", methods=["POST", "GET"])
def mainpage():
    if request.method == "GET":
        return render_template("index.html")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        print(request.form)
        return {"success":True}

@app.route("/home")
def accountpage():
    return render_template("account.html")

@app.route("/signup", methods=["POST", "GET"])
def signuppage():
    if request.method == "GET":
        return render_template("signup.html", message="")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if accounts.count_documents({"username":username}, limit = 1) > 0:
            print("exists")
            return {"success":False, "message":"An account with that username already exists- please choose another username."}
        if " " in username:
            return {"success":False, "message":"Spaces aren't allowed in usernames."}
        else:
            accounts.insert_one({"username":username, "password":password})
        # return render_template("account-created.html")
        session["username"] = username
        print(session["username"])
        return {"success":True}
    
@app.route("/signin", methods=["POST"])
def signin():
    username = request.form["username"]
    password = request.form["password"]
    doc = accounts.find_one({"username":username})
    if doc is not None:
        if doc["password"] == password:
            session["username"] = username
            return {"success":True}
        else:
            return {"success":False, "message":"Incorrect password."}
    else:
        return {"sucess":False, "message":"An account with that username doesn't exist."}
        

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