from flask import Flask, render_template, request, redirect, url_for
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

    #viewing gymnasts that are in the database
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT * FROM gymnast")
    data = cur.fetchall()
    conn.close()


    #viewing apparatus with their id's
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT * FROM apparatus")
    appdata = cur.fetchall()
    conn.close()


    #getting the gymnast id, apparatus id, their e-score and their d-score
    form1 = None
    form2 = None
    form3 = None
    form4 = None
    if len(request.args) > 0:
        form1 = request.args.get('addgymnastid')
        form2 = request.args.get('app')
        form3 = request.args.get('add-escore')
        form4 = request.args.get('add-dscore')
        

    #adding the new scores
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    sql = ("INSERT INTO score (gymnast_id, apparatus_id, escore, dscore) VALUES (?,?,?,?)")
    cur.execute(sql, (form1, form2, form3, form4))
    conn.commit()
    conn.close()

    return render_template("score.html", appdata=appdata, data=data)


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