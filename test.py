from crypt import methods
import re
import time
from urllib.request import Request
from flask import Flask, redirect, render_template, request , flash, session, url_for


class user:
    def __init__(self, id, loginID, password):
        self.id = id
        self.loginID = loginID
        self.password = password


class fule_quote_module:
    def __init__(self, date, gallons_requested, suggested_price, total_amt_due, first_order=False):
        self.date = date
        self.gallons_requested = gallons_requested
        self.suggested_price = suggested_price
        self.total_amt_due = total_amt_due


class price_quote_module:
    pass


users = []
users.append(user(id =1, loginID = "adam", password = "abc123" ))
users.append(user(id =2, loginID = "jacob", password = "xyz000" ))

quotes = []
quotes.append(fule_quote_module(date='01-01-2022', gallons_requested=20, suggested_price=2000, total_amt_due=40000, first_order=True))
quotes.append(fule_quote_module(date='02-02-2023', gallons_requested=40, suggested_price=4000, total_amt_due=80000, first_order=False))

app = Flask(__name__)
app.secret_key="123abc"

@app.route("/")
def index():
    return render_template("index.html")


@app.route('/client.html', methods=["GET", "POST"])
def client():
    if request.method=="POST":
        name=request.form["FullName"]   
        add1=request.form["address"]    
        add2=request.form["address-2"] 
        city=request.form["city"]       
        state=request.form["state"]     
        zip=request.form["zipcode"]        

        if (len(name) <=0): 
            flash(" Fullname cannot be blank!", "error")
        elif(len(name) >50 ):
            flash(" Fullname cannot be exceed 50 characters!", "error")

        if (len(add1)<=0):
            flash("Address1 cannot be blank!", "error")
        elif(len(add1)> 100):
            flash("Address1 cannot exceed 100 characters!", "error")

        if (len(add2)> 100):
            flash("Cannot exceed 100 characters!", "error")

        if(len(city)<=0):
            flash("City cannot be blank!", "error")
        elif(len(city)>100):
            flash("City cannot exceed 100 characters!", "error")
        
        if(len(zip)<5):
            flash("Zipcode needs to be atleast 5 characters!", "error")
        elif(len(zip)>9):
            flash("Zipcode cannot exceed 9 characters!", "error")
        
        else:    
            flash("User Profile Successfully Saved!", "success")              
    
    return render_template("client.html")


@app.route('/history.html')
def history():
    return render_template("history.html")

@app.route('/login.html', methods=["GET", "POST"])
def login():
    if request.method=="POST":
        session.pop("user_id", None)

        l_name=request.form["loginid"]
        l_pass=request.form["loginpw"]
        
        user = [x for x in users if x.loginID == l_name]
        if (len(user)!=0):
            user = user[0]
            if user and user.password == l_pass:
                session["user_id"] = user.id
                return redirect(url_for("history"))
            else:
                flash("Incorrect Credentials! Please try again", "error")
        else:
            flash("User name doesnt exist! Please try again", "error")
        
    return render_template("login.html")


@app.route('/signup.html', methods=["GET", "POST"])
def signup():
    if request.method=="POST":
        s_name=request.form["username"]         
        s_pw=request.form["password"]           
        s_c_pw=request.form["confirmpassword"]

        if(len(s_name)<=0):
            flash("User name cannot be blank!" , "error")

        if(len(s_pw)<=0):
            flash("Password cannot be blank!", "error")

        if(len(s_c_pw)<=0):
            flash("Password cannot be blank!", "error")

        if(s_c_pw!=s_pw):
            flash("Passwords did not match!", "error")

        else:
            flash("User successfully registered, Please go to login page to login.", "success")
               
    return render_template("signup.html")


@app.route('/quote.html', methods=["GET","POST"])
def quote():
    if request.method=="POST":
        session.pop("user_id", None)
        quantity = request.form["gallon"]   
        add = request.form["delivery"]       
        date = request.form["datetime"]     
        sug_price = request.form["price"]   
        total = request.form["totalamt"]

        if(quantity.isnumeric()== False):
            flash("Number of gallons must be a number!", "error")
        else:
            flash("Order submitted successfully","success")     
    return render_template("quote.html")


@app.route('/index.html')
def home():
    return render_template("index.html")


