from flask import Flask, render_template, request
import sqlite3

app = Flask(__name__)


# Error handler for 404 (Not Found),
# reroutes the user to a 404 page when an error occurs with the URL
@app.errorhandler(404)
def page_not_found(e):
    return render_template("404.html"), 404


# Error handler for 414 (Request-URI Too Long),
# reroutes the user to a 414 page when the URL is too long
@app.errorhandler(414)
def url_too_long(e):
    return render_template("414.html"), 414


# Error handler for 500 (Internal Server Error)
# reroutes the user to a 500 page when an error occurs with the server
@app.errorhandler(500)
def internal_server_error(e):
    return render_template("500.html"), 500


@app.route("/")
def homepage():
    return render_template("home.html")


# A function to connect to the database and execute a query,
def db_query(query_string, params=(), single=True, commit=False):
    
    # Set a timeout of 5 seconds to wait for the lock to release
    with sqlite3.connect("database.db", timeout=5) as conn:
        cur = conn.cursor()
        cur.execute(query_string, params)

        if single:
            result = cur.fetchone()
        else:
            result = cur.fetchall()

        if commit:
            conn.commit()

        return result


# funtion to delete gymnasts or/and scores
def delete_gymnast(delete_id, delete_gymnast=False):

    if delete_gymnast:
        db_query("DELETE FROM score "
                 "WHERE gymnast_id = ?", (delete_id,), commit=True)

        db_query("DELETE FROM gymnast "
                 "WHERE gymnast_id = ?", (delete_id,), commit=True)

    else:
        db_query("DELETE FROM score "
                 "WHERE score_id = ?", (delete_id,), commit=True)
    return None


# route for the gymnast page
@app.route("/addgymnast")
def gymnast():

    if request.args:
        name = request.args.get("registorname")
        level = request.args.get("registorlevel")

        if name and level:
            result = db_query("INSERT INTO gymnast (gymnast_name, level) "
                              "VALUES (?, ?)", (name, level), commit=True)

    delete_id = request.args.get("deleteid")
    if delete_id:
        delete_gymnast(delete_id, delete_gymnast=True)

    name = None
    level = None
    error_message = None

    if request.args:
        gymnast_id = request.args.get("id")
        name = request.args.get("newname")
        level = request.args.get("newlevel")

        if gymnast_id and name and level:

            # checking if gymnast_ID exists
            result = db_query("SELECT * FROM gymnast "
                              "WHERE gymnast_id = ?",
                              (gymnast_id,), single=True)

            if result is None:
                error_message = "Error: ID does not exist."

            else:
                result = db_query("UPDATE gymnast "
                                  "SET gymnast_name = ?, level = ? "
                                  "WHERE gymnast_id = ?",
                                  (name, level, gymnast_id),
                                  single=False, commit=True)

    all_gymnasts = db_query("SELECT * FROM gymnast", single=False)

    return render_template("gymnast.html", result=all_gymnasts,
                           error_message=error_message,)


# route for the score page
@app.route("/addscores")
def scores():

    error_msg = None

    if request.args:
        gymnast_id = request.args.get("addgymnastid")
        apparatus = request.args.get("app")
        execution = request.args.get("add-escore")
        difficulty = request.args.get("add-dscore")

        if gymnast_id and apparatus and execution and difficulty:

            # checking if gymnast_ID exists
            result = db_query("SELECT * FROM gymnast "
                              "WHERE gymnast_id = ?",
                              (gymnast_id,), single=True)

            if result is None:
                error_msg = "Error: ID does not exist."
            else:
                result = db_query("INSERT INTO score "
                                  "(gymnast_id, apparatus_id, "
                                  "escore, dscore) "
                                  "VALUES (?, ?, ?, ?)",
                                  (gymnast_id, apparatus,
                                   execution, difficulty),
                                  single=False, commit=True)

    delete_score_id = request.args.get("deleteid")
    delete_gymnast_id = request.args.get("delete_gymnast")

    if delete_score_id:
        delete_gymnast(delete_score_id,
                       delete_gymnast=(delete_gymnast_id == 'true'))

    apparatus = None
    execution = None
    difficulty = None
    msg = None

    if request.args:
        score_id = request.args.get("scoreid")
        apparatus = request.args.get("appid")
        execution = request.args.get("newescore")
        difficulty = request.args.get("newdscore")

        if score_id and apparatus and execution and difficulty:

            # checking if score_ID exists
            result = db_query("SELECT * FROM score WHERE score_id = ?",
                              (score_id,), single=True)

            if result is None:
                msg = "Error: Score ID does not exist."

            else:
                result = db_query("UPDATE score "
                                  "SET apparatus_id = ?, "
                                  "escore = ?, dscore = ? "
                                  "WHERE score_id = ?",
                                  (apparatus, execution,
                                   difficulty, score_id),
                                  single=False, commit=True)

    # Selecting all scores with name and apparatus
    all_scores = db_query("SELECT score_id, score.gymnast_id, "
                          "gymnast.gymnast_name, "
                          "apparatus.apparatus_name, escore, dscore "
                          "FROM score "
                          "INNER JOIN gymnast "
                          "ON score.gymnast_id=gymnast.gymnast_id "
                          "INNER JOIN apparatus "
                          "ON score.apparatus_id=apparatus.apparatus_id",
                          single=False)

    all_gymnasts = db_query("SELECT * FROM gymnast", single=False)

    # using dictionary to store the results
    result = {
        "gymnasts": all_gymnasts,
        "scores": all_scores
    }

    return render_template("score.html", result=result,
                           scoredata=scoredata,
                           msg=msg, error_msg=error_msg)


# Route for level selection page
@app.route("/scoredata")
def scoredata():

    # Getting all the levels
    result = db_query("SELECT * FROM "
                      "(SELECT gymnast.*, ROW_NUMBER() OVER "
                      "(PARTITION BY gymnast.level "
                      "ORDER BY gymnast.gymnast_id) "
                      "AS num FROM gymnast "
                      "JOIN score ON gymnast.gymnast_id = score.gymnast_id) "
                      "AS ranked_gymnasts "
                      "WHERE num = 1 ORDER BY level", single=False)

    return render_template("scoredata.html", result=result)


# Route for displaying leaderboard by level
@app.route("/scorelead/<int:level>")
def level_leaderboard(level):

    if level < 1 or level > 9:
        return render_template("404.html"), 404

    # Get apparatuses that have a score
    apparatus = db_query("SELECT DISTINCT apparatus.apparatus_id, "
                         "apparatus.apparatus_name FROM apparatus "
                         "JOIN score ON "
                         "apparatus.apparatus_id = score.apparatus_id "
                         "JOIN gymnast "
                         "ON score.gymnast_id = gymnast.gymnast_id "
                         "WHERE gymnast.level = ? "
                         "ORDER BY apparatus.apparatus_id",
                         (level,), single=False)

    # Get scores for all around leaderboard
    all_leaderboard = db_query("SELECT score.gymnast_id, "
                               "gymnast.gymnast_name, "
                               "SUM(score.dscore + score.escore) AS total "
                               "FROM gymnast JOIN score "
                               "ON score.gymnast_id = gymnast.gymnast_id "
                               "WHERE gymnast.level = ? "
                               "GROUP BY score.gymnast_id, "
                               "gymnast.gymnast_name "
                               "ORDER BY total DESC", (level,), single=False)

    # Using dictionary to store the results
    result = {
        "apparatus": apparatus,
        "all_leaderboard": all_leaderboard
    }

    return render_template("scorelead.html", level=level,
                           result=result)


# Route for the apparatus leaderboards pages.
@app.route("/apparatuslead/<int:level>/<int:apparatus_id>")
def apparatus_leaderboard(level, apparatus_id):

    # Get scores for each apparatus
    scores = db_query("SELECT score.gymnast_id, "
                      "gymnast.gymnast_name, score.dscore,"
                      "score.escore, (score.dscore + score.escore) "
                      "AS total FROM gymnast "
                      "JOIN score ON score.gymnast_id = gymnast.gymnast_id "
                      "WHERE score.apparatus_id = ? AND gymnast.level = ? "
                      "ORDER BY total DESC",
                      (apparatus_id, level), single=False)

    # Get the name of each apparatus
    apparatus_name = db_query("SELECT apparatus_name FROM apparatus "
                              "WHERE apparatus_id = ?",
                              (apparatus_id,), single=True)

    if apparatus_name is not None:
        apparatus_name = apparatus_name[0]
    else:
        return render_template("404.html"), 404

    # Get all apparatuses that have a score
    apparatus = db_query("SELECT DISTINCT apparatus.apparatus_id, "
                         "apparatus.apparatus_name FROM apparatus "
                         "JOIN score "
                         "ON apparatus.apparatus_id = score.apparatus_id "
                         "JOIN gymnast "
                         "ON score.gymnast_id = gymnast.gymnast_id "
                         "WHERE gymnast.level = ? "
                         "ORDER BY apparatus.apparatus_id",
                         (level,), single=False)

    # Using dictionary to store the results
    result = {
        "scores": scores,
        "apparatus_name": apparatus_name,
        "apparatus": apparatus
    }

    return render_template("apparatuslead.html", level=level,
                           apparatus_id=apparatus_id, result=result)


if __name__ == "__main__":
    app.run(debug=True)
