from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, make_response
from flask_session import Session
from helpers import  apology, login_required

import pypyodbc as odbc

server = 'hospitaljugueton.database.windows.net'
database = 'HospitalJuguetonDB'
username  = 'juanmarenco'
password  = 'juangabriel123$'

connection_string = 'Driver={ODBC Driver 18 for SQL Server};Server=tcp:hospitaljugueton.database.windows.net,1433;Database=HospitalJuguetonDB;Uid=juanmarenco;Pwd=juangabriel123$;Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;'

conn = odbc.connect(connection_string)

db = conn.cursor()


app = Flask(__name__)
if __name__ == '__main__':
    app.run(debug=True)

app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

Session(app)

@app.route("/",methods=["GET", "POST"])
def index():
    if request.method == "GET":
        return render_template("index.html")



@app.route("/login",methods=["GET", "POST"])
def login():
    if request.method == "GET":
        return render_template("login.html")
    else:
        if not request.form.get("username"):
            return apology("must provide username", 403)

        # Ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password", 403)

        # Query database for username
        username = request.form.get("username")
        password = request.form.get("password")

        # Execute the SQL query with a parameter

        rows_query  = db.execute("SELECT * FROM users WHERE name = ? AND password = ?", (username, password))
        rows = rows_query.fetchall()

        # Ensure username exists and password is correct
        if len(rows) != 1:
            return apology("invalid username and/or password", 403)

        # Remember which user has logged in
        session["user_id"] = rows[0]["id"]

        query_alias =  db.execute("SELECT alias FROM users WHERE name = ? AND password = ?", (username, password))
        result_alias = query_alias.fetchall()

        alias = result_alias[0]["alias"]

        # Redirect user to home page
        return render_template("pregame.html", alias = alias)


@app.route("/logout")
def logout():
    """Log user out"""
    # Forget any user_id
    session.clear()
    # Redirect user to login form
    return redirect("/")



@app.route("/pregame",methods=["GET", "POST"])
@login_required
def pregame():
    if request.method == "GET":
        
        return render_template("pregame.html")


@app.route("/verstats",methods=["GET", "POST"])
def verstats():
    if request.method == "GET":
        user_id = session["user_id"]
        query_stats =  db.execute("SELECT * FROM stats WHERE dr_id = ? ", (user_id,))
        query_results = query_stats.fetchall()
        agarres = query_results[0]["agarres"]
        bodycount = query_results[0]["bodies"]

        query_alias =  db.execute("SELECT alias FROM users WHERE id = ?", (user_id,))
        result_alias = query_alias.fetchall()

        alias = result_alias[0]["alias"]

        return render_template("verstats.html", agarres= agarres, bodycount = bodycount, alias =alias)

@app.route("/updatestats",methods=["GET", "POST"])
def updatestats():
    if request.method == "GET":  
        user_id = session["user_id"]
        query_alias =  db.execute("SELECT alias FROM users WHERE id = ?", (user_id,))
        result_alias = query_alias.fetchall()
        alias = result_alias[0]["alias"]
        return render_template("updatestats.html", alias= alias)
    
@app.route("/hospitalstats",methods=["GET", "POST"])
def hospitalstats():
    if request.method == "GET":
        return render_template("hospitalstats.html")

@app.route("/agarres",methods=["GET", "POST"])
def agarres():
    if request.method == "GET":
        agarres_query = db.execute("SELECT users.name, a.agarres FROM stats AS a JOIN users ON users.id = a.dr_id ORDER BY a.agarres DESC")
        agarres_result = agarres_query.fetchall()
        return render_template("agarres.html", agarres_list = agarres_result)
    
@app.route("/bodies",methods=["GET", "POST"])
def bodies():
    if request.method == "GET":
        bodies_query = db.execute("SELECT users.name, a.bodies FROM stats AS a JOIN users ON users.id = a.dr_id ORDER BY a.bodies DESC")
        bodies_result = bodies_query.fetchall()
        return render_template("bodies.html", bodies_list = bodies_result)

@app.route("/updateagarres",methods=["GET", "POST"])
def updateagarres():
    if request.method == "GET":
        return render_template("updateagarres.html")
    else:
        user_id = session["user_id"]
        number =  request.form.get("number")
        
        numberint = int(number)

        if numberint < 1: 
            return apology("Ingresa un numero entero mayor que 1", 403)

        agarres_query = db.execute("SELECT agarres FROM stats WHERE dr_id = ?",(user_id,))
        agarres_result = agarres_query.fetchall()

        agarres_now = int(agarres_result[0]["agarres"])

        new_agarres =  agarres_now + numberint

        db.execute("UPDATE stats SET agarres = ? WHERE dr_id = ?",(new_agarres,user_id,))

        return render_template("pregame.html")

    
@app.route("/updatebodies",methods=["GET", "POST"])
def updatebodies():
    if request.method == "GET":
        return render_template("updatebodies.html")
    else:
        user_id = session["user_id"]
        number =  request.form.get("number")
        
        numberint = int(number)

        if numberint < 1: 
            return apology("Ingresa un numero entero mayor que 1", 403)

        bodies_query = db.execute("SELECT bodies FROM stats WHERE dr_id = ?",(user_id,))
        bodies_result = bodies_query.fetchall()

        bodies_now = int(bodies_result[0]["bodies"])

        new_bodies =  bodies_now + numberint

        db.execute("UPDATE stats SET bodies = ? WHERE dr_id = ?",(new_bodies,user_id,))

        return render_template("pregame.html")

