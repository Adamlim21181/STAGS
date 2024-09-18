from flask import Flask, render_template, request
import sqlite3
import time

app = Flask(__name__)


# Error handler for 404 (Not Found)
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Error handler for 500 (Internal Server Error)
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


# Route for the homepage
@app.route("/")
def homepage():
    return render_template("home.html")


# Route for adding and managing gymnasts
@app.route("/addgymnast")
def gymnast():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Variables to hold form data
    form1 = None
    form2 = None

    # Handle form submission for adding gymnasts
    if request.args:
        form1 = request.args.get("registorname")
        form2 = request.args.get("registorlevel")

        if form1 and form2:
            cur.execute("INSERT INTO gymnast "
                        "(gymnast_name, level) VALUES (?, ?)", (form1, form2))
            conn.commit()

    # Fetch all gymnasts for display
    cur.execute("SELECT * FROM gymnast")
    regdata = cur.fetchall()
    # Explanation: Retrieves all rows from the 'gymnast' table.

    # Handle deletion of a gymnast
    delete = None
    delete_error = None

    if request.args:
        delete = request.args.get("deleteid")

        if delete:
            cur.execute("SELECT * FROM gymnast "
                        "WHERE gymnast_id = ?", (delete,))
            result = cur.fetchone()

            if result is None:
                delete_error = "Error: ID does not exist."

            else:
                time.sleep(1)  # Simulate processing delay
                cur.execute("DELETE FROM score "
                            "WHERE gymnast_id = ?", (delete,))

                cur.execute("DELETE FROM gymnast "
                            "WHERE gymnast_id = ?", (delete,))
                conn.commit()

    # Explanation:
    '''
        Checks if a gymnast with the given ID exists.
        If it does, deletes the gymnast from the 'gymnast' table.
    '''

    # Handle updating gymnast details
    gymnastid = None
    name = None
    level = None
    error_message = None

    if request.args:
        gymnastid = request.args.get("id")
        name = request.args.get("newname")
        level = request.args.get("newlevel")

        if gymnastid and name and level:

            cur.execute("SELECT * FROM gymnast "
                        "WHERE gymnast_id = ?", (gymnastid,))
            result2 = cur.fetchone()

            if result2 is None:
                error_message = "Error: ID does not exist."

            else:
                cur.execute("UPDATE gymnast SET gymnast_name = ?, level = ? "
                            "WHERE gymnast_id = ?", (name, level, gymnastid))

                conn.commit()

    # Explanation:
    '''
        Updates the name and level of a
        gymnast identified by 'gymnast_id'.
        Checks if the update wass
        successful by checking if the ID still exists.
    '''

    conn.close()

    return render_template("gymnast.html", regdata=regdata,
                           error_message=error_message,
                           delete_error=delete_error)


# Route for adding and managing scores
@app.route("/addscores")
def scores():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Fetch all gymnasts for display in the scores form
    cur.execute("SELECT * FROM gymnast")
    gymdata = cur.fetchall()

    # Variables to hold form data
    form1 = None
    form2 = None
    form3 = None
    form4 = None
    error_msg = None

    # Handle form submission for adding scores
    if request.args:
        form1 = request.args.get("addgymnastid")
        form2 = request.args.get("app")
        form3 = request.args.get("add-escore")
        form4 = request.args.get("add-dscore")

        if form1 and form2 and form3 and form4:

            cur.execute("SELECT * FROM gymnast WHERE gymnast_id = ?", (form1,))
            result = cur.fetchone()

            if result is None:
                error_msg = "Error: ID does not exist."

            else:
                cur.execute("INSERT INTO score "
                            "(gymnast_id, apparatus_id, escore, dscore) "
                            "VALUES (?, ?, ?, ?)",
                            (form1, form2, form3, form4))
                conn.commit()

    # Explanation:
    '''
        Inserts a new score into the 'score' table
        if all required form fields filled out.
        Checks if the gymnast ID exists.
    '''

    # Fetch all scores with detailed information
    cur.execute("SELECT score_id, score.gymnast_id, gymnast.gymnast_name, "
                "apparatus.apparatus_name, escore, dscore "
                "FROM score "
                "INNER JOIN gymnast ON score.gymnast_id=gymnast.gymnast_id "
                "INNER JOIN apparatus "
                "ON score.apparatus_id=apparatus.apparatus_id")
    scoredata = cur.fetchall()

    # Explanation:
    '''
        Gets scores from the 'score' table, joining with
        'gymnast' to get gymnast names
        and with 'apparatus' to get apparatus names.
    '''

    # Handle deletion of a score
    delete = None
    delete_error = None

    if request.args:
        delete = request.args.get("deleteid")

        if delete:
            cur.execute("SELECT * FROM score WHERE score_id = ?", (delete,))
            results2 = cur.fetchone()

            if results2 is None:
                delete_error = "Error: ID does not exist."

            else:
                time.sleep(1)  # Simulate processing delay
                cur.execute("DELETE FROM score WHERE score_id = ?", (delete,))
                conn.commit()

    # Explanation:
    '''
        Checks if a score with the given ID exists.
        If it does, deletes it from the 'score' table.
    '''

    # Handle updating scores
    newform1 = None
    newform2 = None
    newform3 = None
    newform4 = None
    msg = None

    if request.args:
        newform1 = request.args.get("scoreid")
        newform2 = request.args.get("appid")
        newform3 = request.args.get("newescore")
        newform4 = request.args.get("newdscore")

        if newform1 and newform2 and newform3 and newform4:

            cur.execute("SELECT * FROM score WHERE score_id = ?", (newform1,))
            results3 = cur.fetchone()

            if results3 is None:
                msg = "Error: Score ID does not exist."

            else:
                cur.execute("UPDATE score "
                            "SET apparatus_id = ?, escore = ?, dscore = ? "
                            "WHERE score_id = ?",
                            (newform2, newform3, newform4, newform1))
                conn.commit()

    # Explanation:
    '''
        Updates the details of a score identified by 'score_id'.
        Verifies if the update was
        successful by checking if the ID still exists.
    '''

    conn.close()

    return render_template("score.html", gymdata=gymdata, scoredata=scoredata,
                           msg=msg, delete_error=delete_error,
                           error_msg=error_msg)


# Route for displaying score data by level
@app.route("/scoredata")
def scoredata():
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Fetch the top gymnast by level
    cur.execute("SELECT * FROM "
                "(SELECT gymnast.*, ROW_NUMBER() OVER "
                "(PARTITION BY gymnast.level ORDER BY gymnast.gymnast_id) "
                "AS num FROM gymnast "
                "JOIN score ON gymnast.gymnast_id = score.gymnast_id) "
                "AS ranked_gymnasts WHERE num = 1 ORDER BY level")
    levels = cur.fetchall()

    # Explanation:
    '''
        Uses a subquery with ROW_NUMBER()
        to rank gymnasts within each level, then selects
        the top-ranked gymnast (num = 1) for each level.
        Orders the results by level.
    '''

    conn.close()
    return render_template("scoredata.html", levels=levels)


# Route for displaying leaderboard by level
@app.route("/scorelead/<int:level>")
def level_leaderboard(level):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Fetch all apparatus for the given level
    cur.execute("SELECT DISTINCT apparatus.apparatus_id, "
                "apparatus.apparatus_name FROM apparatus JOIN score ON "
                "apparatus.apparatus_id = score.apparatus_id "
                "JOIN gymnast ON score.gymnast_id = gymnast.gymnast_id "
                "WHERE gymnast.level = ? "
                "ORDER BY apparatus.apparatus_id", (level,))
    apps = cur.fetchall()

    # Explanation:
    '''
        Gets distinct apparatus for the given level,
        joining with 'score' and 'gymnast' to make sure the
        apparatus is used by gymnasts at that level.
    '''

    # Fetch leaderboard data for the given level
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, "
                "SUM(score.dscore + score.escore) AS total "
                "FROM gymnast JOIN score "
                "ON score.gymnast_id = gymnast.gymnast_id "
                "WHERE gymnast.level = ? "
                "GROUP BY score.gymnast_id, gymnast.gymnast_name "
                "ORDER BY total DESC", (level,))
    overalldata = cur.fetchall()

    # Explanation:
    '''
        Calculates the total score
        (dscore + escore) for each gymnast at the given level.
        Groups by gymnast ID and name, and orders the
        results by total score in descending order.
    '''

    conn.close()
    return render_template("scorelead.html", level=level,
                           apps=apps, overalldata=overalldata)


# Route for displaying leaderboard by apparatus
@app.route("/apparatuslead/<int:level>/<int:apparatus_id>")
def apparatus_leaderboard(level, apparatus_id):
    conn = sqlite3.connect("database.db")
    cur = conn.cursor()

    # Fetch scores for the given apparatus and level
    cur.execute("SELECT score.gymnast_id, gymnast.gymnast_name, score.dscore,"
                "score.escore, (score.dscore + score.escore) "
                "AS total FROM gymnast "
                "JOIN score ON score.gymnast_id = gymnast.gymnast_id "
                "WHERE score.apparatus_id = ? AND gymnast.level = ? "
                "ORDER BY total DESC", (apparatus_id, level))
    data = cur.fetchall()

    # Explanation:
    '''
        Gets scores for an apparatus and level,
        calculating the total score for each gymnast.
        Orders the results by total score in descending order.
    '''

    # Fetch the name of the apparatus
    cur.execute("SELECT apparatus_name FROM apparatus "
                "WHERE apparatus_id = ?", (apparatus_id,))
    apparatus_name = cur.fetchone()[0]

    # Explanation:
    '''
        Gets the name of the
        apparatus based on the given apparatus ID.
    '''

    # Fetch all apparatus for the given level
    cur.execute("SELECT DISTINCT apparatus.apparatus_id, "
                "apparatus.apparatus_name FROM apparatus "
                "JOIN score ON apparatus.apparatus_id = score.apparatus_id "
                "JOIN gymnast ON score.gymnast_id = gymnast.gymnast_id "
                "WHERE gymnast.level = ? "
                "ORDER BY apparatus.apparatus_id", (level,))
    apps = cur.fetchall()

    # Explanation:
    '''
        Gets all apparatus used by
        gymnasts at thier level, making sure the apparatus is
        associated with scores and gymnasts at that level.
    '''

    conn.close()
    return render_template("apparatuslead.html", level=level,
                           apparatus_id=apparatus_id, data=data,
                           apps=apps, apparatus_name=apparatus_name)


if __name__ == "__main__":
    app.run(debug=True)
