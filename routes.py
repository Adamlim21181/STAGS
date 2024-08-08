from flask import Flask, render_template, request
import sqlite3
import time

app = Flask(__name__)


@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


@app.route("/")
def homepage():
    return render_template("home.html")


@app.route("/addgymnast")
def gymnast():

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    form1 = None
    form2 = None
    if request.args:
        form1 = request.args.get("registorname")
        form2 = request.args.get("registorlevel")
        if form1 and form2:
            cur.execute(
                "INSERT INTO gymnast (gymnast_name, level) VALUES (?, ?)",
                (form1, form2),
                )
            conn.commit()

    cur.execute("SELECT * FROM gymnast")
    regdata = cur.fetchall()

    delete = delete_error = None
    if request.args:
        delete = request.args.get("deleteid")
        if delete:
            cur.execute(
                "SELECT * FROM gymnast WHERE gymnast_id = ?",
                (delete,)
                )
            if not cur.fetchone():
                delete_error = "Error: ID does not exist."
            else:
                time.sleep(1)
                cur.execute(
                    "DELETE FROM gymnast WHERE gymnast_id = ?", (delete,)
                )
                conn.commit()

    id = None
    name = None
    level = None
    error_message = None
    if request.args:
        id = request.args.get("id")
        name = request.args.get("newname")
        level = request.args.get("newlevel")
        if id and name and level:
            cur.execute(
                "UPDATE gymnast SET "
                "gymnast_name = ?, "
                "level = ? "
                "WHERE gymnast_id = ?",
                (name, level, id),
                )

            conn.commit()
            cur.execute(
                "SELECT * FROM gymnast WHERE gymnast_id = ?", (id,)
            )
            if not cur.fetchone():
                error_message = "Error: ID does not exist."

            conn.close()

    return render_template(
        "gymnast.html", regdata=regdata,
        error_message=error_message, delete_error=delete_error
    )


@app.route("/addscores")
def scores():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute("SELECT * FROM gymnast")
    gymdata = cur.fetchall()
    conn.close()

    form1 = form2 = form3 = form4 = None
    if request.args:
        form1 = request.args.get("addgymnastid")
        form2 = request.args.get("app")
        form3 = request.args.get("add-escore")
        form4 = request.args.get("add-dscore")
        if form1 and form2 and form3 and form4:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            cur.execute(
                "INSERT INTO score (gymnast_id, apparatus_id, escore, dscore) "
                "VALUES (?, ?, ?, ?)",
                (form1, form2, form3, form4),
            )
            conn.commit()
            conn.close()

    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT score_id, score.gymnast_id, gymnast.gymnast_name, "
        "apparatus.apparatus_name, escore, dscore FROM score "
        "INNER JOIN gymnast ON score.gymnast_id=gymnast.gymnast_id "
        "INNER JOIN apparatus ON score.apparatus_id=apparatus.apparatus_id"
    )
    scoredata = cur.fetchall()
    conn.close()

    delete = delete_error = None
    if request.args:
        delete = request.args.get("deleteid")
        if delete:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            cur.execute("SELECT * FROM score WHERE score_id = ?", (delete,))
            if not cur.fetchone():
                delete_error = "Error: ID does not exist."
            else:
                time.sleep(1)
                cur.execute("DELETE FROM score WHERE score_id = ?", (delete,))
                conn.commit()
            conn.close()

    newform1 = newform2 = newform3 = newform4 = msg = None
    if request.args:
        newform1 = request.args.get("scoreid")
        newform2 = request.args.get("appid")
        newform3 = request.args.get("newescore")
        newform4 = request.args.get("newdscore")
        if newform1 and newform2 and newform3 and newform4:
            conn = sqlite3.connect("database.db")
            cur = conn.cursor()
            cur.execute(
                "UPDATE score SET apparatus_id = ?, escore = ?, dscore = ? "
                "WHERE score_id = ?",
                (newform2, newform3, newform4, newform1),
            )
            conn.commit()
            cur.execute("SELECT * FROM score WHERE score_id = ?", (newform1,))
            if not cur.fetchone():
                msg = "Error: Score ID does not exist."
            conn.close()

    return render_template(
        "score.html",
        gymdata=gymdata,
        scoredata=scoredata,
        msg=msg,
        delete_error=delete_error
    )


@app.route("/scoredata")
def scoredata():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()
    cur.execute(
        "SELECT * FROM ( "
        "SELECT *, ROW_NUMBER() OVER(PARTITION BY level ORDER BY gymnast_id) "
        "AS num "
        "FROM gymnast "
        ") AS ranked_gymnasts "
        "WHERE num = 1 "
        "ORDER BY level;"
    )

    levels = cur.fetchall()
    conn.close()
    return render_template("scoredata.html", levels=levels)


@app.route("/scorelead/<int:level>")
def level_leaderboard(level):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT DISTINCT apparatus.apparatus_id, apparatus.apparatus_name "
        "FROM apparatus "
        "JOIN score ON apparatus.apparatus_id = score.apparatus_id "
        "JOIN gymnast ON score.gymnast_id = gymnast.gymnast_id "
        "WHERE gymnast.level = ? "
        "ORDER BY apparatus.apparatus_id",
        (level,)
    )
    apps = cur.fetchall()

    cur.execute(
        "SELECT score.gymnast_id, gymnast.gymnast_name, "
        "SUM(score.dscore + score.escore) AS total "
        "FROM gymnast "
        "JOIN score ON score.gymnast_id = gymnast.gymnast_id "
        "WHERE gymnast.level = ? "
        "GROUP BY score.gymnast_id, gymnast.gymnast_name "
        "ORDER BY total DESC",
        (level,)
    )
    overalldata = cur.fetchall()

    conn.close()
    return render_template("scorelead.html",
                           level=level,
                           apps=apps,
                           overalldata=overalldata)


@app.route("/apparatuslead/<int:level>/<int:apparatus_id>")
def apparatus_leaderboard(level, apparatus_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    cur.execute(
        "SELECT score.gymnast_id, gymnast.gymnast_name, "
        "score.dscore, score.escore, "
        "(score.dscore + score.escore) AS total "
        "FROM gymnast "
        "JOIN score ON score.gymnast_id = gymnast.gymnast_id "
        "WHERE score.apparatus_id = ? AND gymnast.level = ? "
        "ORDER BY total DESC",
        (apparatus_id, level)
    )
    data = cur.fetchall()

    cur.execute(
        "SELECT apparatus_name FROM apparatus WHERE apparatus_id = ?",
        (apparatus_id,)
    )
    apparatus_name = cur.fetchone()[0]

    cur.execute(
        "SELECT DISTINCT apparatus.apparatus_id, apparatus.apparatus_name "
        "FROM apparatus "
        "JOIN score ON apparatus.apparatus_id = score.apparatus_id "
        "JOIN gymnast ON score.gymnast_id = gymnast.gymnast_id "
        "WHERE gymnast.level = ? "
        "ORDER BY apparatus.apparatus_id",
        (level,)
    )
    apps = cur.fetchall()

    conn.close()
    return render_template("apparatuslead.html",
                           level=level,
                           apparatus_id=apparatus_id,
                           data=data,
                           apps=apps,
                           apparatus_name=apparatus_name)


if __name__ == "__main__":
    app.run(debug=True)
