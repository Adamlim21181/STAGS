from flask import Flask, render_template, request
import sqlite3


app = Flask(__name__)

#creating a hompage
@app.route('/')
def homepage():
    return render_template("home.html")

#creating a page to add gymnasts
@app.route('/addgymnast')
def gymnast():     
    return render_template('gymnast.html')

#creating a page to add scores
@app.route('/addscores')
def scores():
    return render_template("score.html")

#creating a page to view leaderboards
@app.route('/leaderboard')
def leaderboard():
    return render_template("leaderboard.html")

#creating a page to edit gymnasts or/and scores
@app.route('/edit')
def edit():
    return render_template("edit.html")


if __name__ == "__main__":
    app.run(debug=True)