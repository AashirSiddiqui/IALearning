from flask import Flask, render_template, request, session
from pymongo import MongoClient
import json
import os
from dotenv import load_dotenv
import bson.objectid

app_path = os.path.join(os.path.dirname(__file__), '.')
dotenv_path = os.path.join(app_path, '.env')
load_dotenv(dotenv_path)

client = MongoClient(os.environ.get("MONGODB_URI"))
db = client.IALearning

accounts = db.Accounts
lessons = db.Lessons

app = Flask((__name__))

app.secret_key = os.environ.get("SECRET_KEY")
app.config["SESSION_TYPE"] = "filesystem"

@app.route("/landing", methods=["GET"])
def lander():
    return render_template("landing.html")

@app.route("/", methods=["POST", "GET"])
def mainpage():
    if request.method == "GET":
        completedIds = []
        if "lessonCompleted" in request.args and request.args["lessonCompleted"].strip() == "true":
            lesson_id = request.args["lessonId"]
            accounts.update_one({"username":session.get("username")}, {"$addToSet":{"lessons_completed_ids":lesson_id}})
        account_exists = False
        account_username = ""
        if session.get("username"):
            account_username = session.get("username")
            completedIds = accounts.find_one({"username":session.get("username")})["lessons_completed_ids"]
            account_exists = True
            return render_template("index.html", lessons=lessons.find({"published":True}), username=account_username, isAccount = account_exists, completedIds = list(completedIds))
        else:
            return render_template("redirect.html", page="/landing")
    elif request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        return {"success":True}

@app.route("/syntax")
def syntaxpage():
    return render_template("lesson-syntax.html")

@app.route("/home")
def accountpage():
    return render_template("redirect.html", page="/")

@app.route("/makelesson", methods=["POST"])
def makeLesson():
    if session.get("username"):
        lessonName = request.form["lesson-name"]
        creatorId = request.form["lesson-creatorId"]
        newLsn = lessons.insert_one({
            "name":lessonName,
            "creator_id":bson.objectid.ObjectId(creatorId),
            "content":[],
            "rating":0,
            "verified":False,
            "published":False
        })
        return str(newLsn.inserted_id)
    else:
        return "error"

@app.route("/signup", methods=["POST", "GET"])
def signuppage():
    if request.method == "GET":
        return render_template("signup.html", message="")
    else:
        username = request.form["username"]
        password = request.form["password"]
        if accounts.count_documents({"username":username}, limit = 1) > 0:
            #print("exists")
            return {"success":False, "message":"An account with that username already exists- please choose another username."}
        if " " in username:
            return {"success":False, "message":"Spaces aren't allowed in usernames."}
        else:
            accounts.insert_one({"username":username, "password":password, "lessons_liked_ids":[], "lessons_completed_ids":[]})
        # return render_template("account-created.html")
        session["username"] = username
        #print(session["username"])
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
        
@app.route("/your-lessons")
def yourLessons():
    if session.get("username"):
        account = accounts.find_one({"username":session.get("username")})
        ownedLessons = list(lessons.find({"creator_id":account["_id"]}))
        makerID = account["_id"]
        #print(ownedLessons)
        return render_template("your-lessons.html", lessons=ownedLessons, makerId = makerID)
    else:
        return(render_template("redirect.html", page="signup"))

@app.route("/lesson-editor", methods=["POST", "GET"])
def lessonEditor():
    if request.method == "GET":
        if session.get("username"):
            lessonId = request.args["id"]
            lesson = lessons.find_one({"_id":bson.objectid.ObjectId(lessonId)})
            #print(lesson)
            return render_template("lesson-editor.html", lesson=lesson["content"], lessonID=lessonId)
        else:
            return(render_template("redirect.html", page="signup"))
    else:
        #print(request.form.items)
        if session.get("username"):
            lessonID = request.form["lessonID"]
            lessonContent = request.form["lessonContent"]
            lesson = lessons.find_one({"_id":bson.objectid.ObjectId(lessonID)})
            lesson["content"] = eval(lessonContent)
            lessons.update_one({"_id":lesson["_id"]}, {"$set": {"content":eval(lessonContent)}})
            return "success"
        else:
            return "error"

@app.route("/lesson.html")
def redirectToLesson():
    return render_template("redirect.html", page="lesson")

@app.route("/lesson")
def lessonpage():
    if session.get("username"):
        lessonId = request.args.get("id")
        isPreview = request.args.get("preview")
        lesson = lessons.find_one({"_id":bson.objectid.ObjectId(lessonId)})
        return render_template("lesson.html", lesson=json.dumps({"list":lesson["content"]}), lesson_name=lesson["name"], preview=isPreview, lessonID = lessonId)
    else:
        return render_template("redirect.html", page="/signup")
    
@app.route("/submitlesson", methods=["POST", "GET"])
def submitlesson():
    return json.dumps("hello")

@app.route("/likelesson", methods=["POST"])
def likeLesson():
    if session.get("username"):
        lessonId = request.form["lessonID"]
        if lessonId in accounts.find_one({"username":session.get("username")})["lessons_liked_ids"]:
            return "already liked"
        else:
            lessons.update_one({"_id":bson.objectid.ObjectId(lessonId)}, 
                                        {"$inc":{"rating":1}})
            accounts.update_one({"username":session.get("username")}, {"$addToSet":{"lessons_liked_ids":lessonId}})
            return "success"
    else:
        return "error"

@app.route("/deletelesson", methods=["POST"])
def deletelesson():
    if session.get("username"):
        lessonId = request.form["lessonID"]
        lessons.delete_one({"_id":bson.objectid.ObjectId(lessonId)})
        return "success"
    else:
        return "error"

@app.route("/publish-lesson", methods=["POST"])
def publishlesson():
    if session.get("username"):
        lessonId = request.form["lessonID"]
        publishLesson = lessons.update_one({"_id":bson.objectid.ObjectId(lessonId)}, {"$set":{"published":True}})
        return "success"
    else:
        return "error"

app.debug = True

if __name__ == "__main__":
    app.run(host="0.0.0.0")