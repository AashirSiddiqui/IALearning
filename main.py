from flask import Flask, render_template

app = Flask((__name__))

@app.route("/")
def mainpage():
    return render_template("index.html")

@app.route("/lesson.html")
def lessonpage():
    return render_template("lesson.html", lesson=["ID01Learntest", "ID02", "ID00Welcome to this text","ID03Try rereading the text.", "ID00You will learn here"])

@app.route("/style.css")
def css():
    return render_template("style.css")

app.debug = True 

if __name__ == "__main__":
    app.run()