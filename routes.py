from flask import Flask, render_template, request
import sqlite3, time


app = Flask(__name__)

#creating a hompage
@app.route('/')
def homepage():
    return render_template("home.html")

#creating a page to add gymnasts
@app.route('/addgymnast')
def gymnast():

    #adding gymnasts to the database
    form1 = None
    form2 = None
    if len(request.args) > 0:
        #getting the gymnast name from the websites input
        form1 = request.args.get('registorname')
        form2 = request.args.get('registorlevel')
        if form1 is not None and form2 is not None:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            sql = ("INSERT INTO gymnast (gymnast_name, level) VALUES(?,?)")
            cur.execute(sql, (form1, form2))
            conn.commit()
            conn.close()

    #viewing registered gymnasts
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM gymnast")
    regdata = cur.fetchall()
    conn.close()

    #delete registered gymnasts
    delete = None
    delete_error = None
    if len(request.args) > 0:
        delete = request.args.get('deleteid')
        if delete is not None:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()

            # Check if ID exists
            cur.execute("SELECT * FROM gymnast WHERE gymnast_id = ?", (delete,))
            if not cur.fetchone():
                delete_error = "Error: id does not exist."

            time.sleep(1)
            sql = ("DELETE FROM gymnast WHERE gymnast_id = ?")
            cur.execute(sql, (delete,))
            conn.commit()
            conn.close()
    
    #Editing registered gymnasts
    id = None
    name = None
    level = None
    error_message = None
    if len(request.args) > 0:
        #getting the registered gymnasts id and new name
        id = request.args.get('id')
        name = request.args.get('newname')
        level = request.args.get('newlevel')
        if id is not None and name is not None and level is not None: 
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            sql = ("UPDATE gymnast SET gymnast_name = ?, level = ? WHERE gymnast_id = ?")
            cur.execute(sql, (name, level, id))
            conn.commit()

            # Check if ID exists
            cur.execute("SELECT * FROM gymnast WHERE gymnast_id = ?", (id,))
            if not cur.fetchone():
                error_message = "Error: id does not exist."


            conn.close()

    return render_template('gymnast.html', regdata=regdata, error_message=error_message, delete_error=delete_error)


#creating a page to add scores
@app.route('/addscores')
def scores():

    #viewing gymnasts that are in the database
    conn = sqlite3.connect('database.db')  
    cur = conn.cursor()
    cur.execute("SELECT * FROM gymnast")
    gymdata = cur.fetchall()
    conn.close()

    #Adding Scores
    form1 = None
    form2 = None
    form3 = None
    form4 = None
    if len(request.args) > 0:
        #getting the data needed from the users input
        form1 = request.args.get('addgymnastid')
        form2 = request.args.get('app')
        form3 = request.args.get('add-escore')
        form4 = request.args.get('add-dscore')
        if form1 is not None and form2 is not None and form3 is not None and form4 is not None:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            sql = ("INSERT INTO score (gymnast_id, apparatus_id, escore, dscore) VALUES (?,?,?,?)")
            cur.execute(sql, (form1, form2, form3, form4))
            conn.commit()
            conn.close()

    #Viewing the registered scores
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score_id, score.gymnast_id, gymnast.gymnast_name, apparatus.apparatus_name, escore, dscore FROM score INNER JOIN gymnast ON score.gymnast_id=gymnast.gymnast_id INNER JOIN apparatus ON score.apparatus_id=apparatus.apparatus_id ")
    scoredata = cur.fetchall()
    conn.close()

    #delete registered scores
    delete = None
    delete_error = None
    if len(request.args) > 0:
        delete = request.args.get('deleteid')
        if delete is not None:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            # Check if ID exists
            cur.execute("SELECT * FROM score WHERE score_id = ?", (delete,))
            if not cur.fetchone():
                delete_error = "Error: id does not exist."
            
            time.sleep(1)
            sql = ("DELETE FROM score WHERE score_id = ?")
            cur.execute(sql, (delete,))
            conn.commit()
            conn.close()

    #Editing the registered scores
    newform1 = None
    newform2 = None
    newform3 = None
    newform4 = None
    msg = None
    if len(request.args) > 0:
        #Getting the data needed from the users input
        newform1 = request.args.get('scoreid')
        newform2 = request.args.get('appid')
        newform3 = request.args.get('newescore')
        newform4 = request.args.get('newdscore')
        if newform1 is not None and newform2 is not None and newform3 is not None and newform4 is not None:
            conn = sqlite3.connect('database.db')
            cur = conn.cursor()
            sql = ("UPDATE score SET apparatus_id = ?, escore = ?, dscore = ? WHERE score_id = ?")
            cur.execute(sql, (newform2, newform3, newform4, newform1))
            conn.commit()
            
            # Check if ID exists
            cur.execute("SELECT * FROM score WHERE score_id = ?", (newform1,))
            if not cur.fetchone():
                msg = "Error: Score id does not exist."
            conn.close()

    return render_template("score.html", gymdata=gymdata, scoredata=scoredata, msg=msg, delete_error=delete_error)

   

    

#get and order the gymnasts levels in descending order
@app.route('/scoredata')
def scoredata():
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT * FROM ( SELECT *, ROW_NUMBER() OVER(PARTITION BY level ORDER BY gymnast_id) AS num FROM gymnast ) AS ranked_gymnasts WHERE num = 1 ORDER BY level;")
    levels = cur.fetchall()
    conn.close() 
    
    return render_template("scoredata.html", levels=levels)

#get the levels in decending order
@app.route('/scorelead/<level>')
def level_leaderboard(level):
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.* FROM score JOIN gymnast ON score.gymnast_id = gymnast.gymnast_id WHERE gymnast.level = ?", (level,))
    levels = cur.fetchall()  

     # viewing overall leaderboard
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, SUM(score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE gymnast.level = ? GROUP BY score.gymnast_id, gymnast.gymnast_name ORDER BY total DESC  ", (level,))
    overalldata = cur.fetchall()
    conn.close()
    
    #viewing floor leaderboard
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 6 and gymnast.level = ? ORDER BY total DESC ", (level,))
    floordata = cur.fetchall()
    conn.close()

    #viewing pommel leaderboard
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 5 and gymnast.level = ? ORDER BY total DESC ", (level,))
    pommeldata = cur.fetchall()
    conn.close()

    #viewing rings leaderboard
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 4 and gymnast.level = ? ORDER BY total DESC ", (level,))
    ringsdata = cur.fetchall()
    conn.close()

    #viewing vault leaderboard
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore, score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 3 and gymnast.level = ? ORDER BY total DESC ", (level,))
    vaultdata = cur.fetchall()
    conn.close()

    #viewing parellel bar leaderboard
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 2 and gymnast.level = ? ORDER BY total DESC ", (level,))
    pbardata = cur.fetchall()
    conn.close()

    #viewing high bars leaderboard
    conn = sqlite3.connect('database.db')
    cur = conn.cursor()
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore, score.escore, (score.dscore + score.escore) AS total FROM gymnast JOIN score ON score.gymnast_id = gymnast.gymnast_id JOIN apparatus ON score.apparatus_id = apparatus.apparatus_id WHERE apparatus.apparatus_id = 1 and gymnast.level = ? ORDER BY total DESC ", (level,))
    highbardata = cur.fetchall()
    conn.close()

    return render_template("scorelead.html", levels=levels, overalldata=overalldata, floordata=floordata, pommeldata=pommeldata, ringsdata=ringsdata, vaultdata=vaultdata, pbardata=pbardata, highbardata=highbardata )


if __name__ == "__main__":
    app.run(debug=True)