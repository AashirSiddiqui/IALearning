from flask import Flask, render_template, request, session
from pymongo import MongoClient
import json, os

os.environ['MONGODB_URI'] = "mongodb://ialearning:programmer-of-databases-MGDB@cluster0-shard-00-00.dc1ys.mongodb.net:27017,cluster0-shard-00-01.dc1ys.mongodb.net:27017,cluster0-shard-00-02.dc1ys.mongodb.net:27017/?ssl=true&replicaSet=atlas-54vvqc-shard-0&authSource=admin&retryWrites=true&w=majority" # only if not deployed

client = MongoClient(os.getenv("MONGODB_URI"))
db = client.IALearning

accounts = db.Accounts
lessons = db.Lessons

print(db.list_collection_names())

app = Flask((__name__))

@app.route("/")
def mainpage():
    return render_template("index.html")

@app.route("/home")
def accountpage():
    return render_template("account.html")

@app.route("/signup", methods=["POST", "GET"])
def signuppage():
    if request.method == "GET":
        return render_template("signup.html")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if accounts.count_documents({"username":username}, limit = 1) > 0:
            print("exists")
        else:
            accounts.insert_one({"username":username, "password":password})
        # return render_template("account-created.html")
        session["username"] = username
        return "200"

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
    app.run(host="0.0.0.0")