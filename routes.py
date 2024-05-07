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
    form = None
    if len(request.args) > 0:
        #getting the gymnast name from the websites input
        form = request.args.get('registorname')

        #adding the gymnast name to the database
        conn = sqlite3.connect('database')
        cur = conn.cursor()
        sql = ("INSERT INTO gymnast (gymnast_name) VALUES(?)")
        cur.execute(sql, (form,))
        conn.commit()
        conn.close()
    return render_template('gymnast.html', form=form)

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