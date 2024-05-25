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
        if form is not None:
            #adding the gymnast name to the database
            conn = sqlite3.connect('database')
            cur = conn.cursor()
            sql = ("INSERT INTO gymnast (gymnast_name) VALUES(?)")
            cur.execute(sql, (form,))
            conn.commit()
            conn.close()

    #viewing registerd gymnasts
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT * FROM gymnast")
    regdata = cur.fetchall()
    conn.close()

    
    id = None
    name = None
    if len(request.args) > 0:
        #getting the registered gymnasts id and new name
        id = request.args.get('id')
        name = request.args.get('newname')

        if id is not None and name is not None: 
            #replacing the old gymnast name with the new gymast name
            conn = sqlite3.connect('database')
            cur = conn.cursor()
            sql = ("UPDATE gymnast SET gymnast_name = ? WHERE gymnast_id = ?")
            cur.execute(sql, (name, id))
            conn.commit()
            conn.close()

    return render_template('gymnast.html', regdata=regdata)

#creating a page to add scores
@app.route('/addscores')
def scores():

    #viewing gymnasts that are in the database
    conn = sqlite3.connect('database')  
    cur = conn.cursor()
    cur.execute("SELECT * FROM gymnast")
    gymdata = cur.fetchall()
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

    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score_id, score.gymnast_id, gymnast.gymnast_name, apparatus.apparatus_name, escore, dscore FROM score INNER JOIN gymnast ON score.gymnast_id=gymnast.gymnast_id INNER JOIN apparatus ON score.apparatus_id=apparatus.apparatus_id ")
    scoredata = cur.fetchall()
    conn.close()

    return render_template("score.html", appdata=appdata, gymdata=gymdata, scoredata=scoredata)

#creating a page to view leaderboards
@app.route('/leaderboard')
def leaderboard():

    # viewing overall leaderboard
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, SUM(score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id GROUP BY score.gymnast_id, gymnast.gymnast_name ORDER BY total DESC ")
    overalldata = cur.fetchall()
    conn.close()
    
    #viewing floor leaderboard
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 6 ORDER BY total DESC ")
    floordata = cur.fetchall()
    conn.close()

    #viewing pommel leaderboard
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 5 ORDER BY total DESC ")
    pommeldata = cur.fetchall()
    conn.close()

    #viewing rings leaderboard
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 4 ORDER BY total DESC ")
    ringsdata = cur.fetchall()
    conn.close()

    #viewing vault leaderboard
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 3 ORDER BY total DESC ")
    vaultdata = cur.fetchall()
    conn.close()

    #viewing parellel bar leaderboard
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 2 ORDER BY total DESC ")
    pbardata = cur.fetchall()
    conn.close()

    #viewing high bars leaderboard
    conn = sqlite3.connect('database')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore, score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 1 ORDER BY total DESC ")
    highbardata = cur.fetchall()
    conn.close()

    return render_template("leaderboard.html", overalldata=overalldata, floordata=floordata, pommeldata=pommeldata, ringsdata=ringsdata, vaultdata=vaultdata, pbardata=pbardata, highbardata=highbardata)

if __name__ == "__main__":
    app.run(debug=True)