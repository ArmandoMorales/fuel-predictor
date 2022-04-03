from crypt import methods
import re
import time
from urllib.request import Request
from flask import Flask, redirect, render_template, request , flash, session, url_for

# adding database connection
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password123",
  database="FuelDatabase"
)
mycursor = mydb.cursor()

CURRENT_USER = -1

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

            # inserting into database client info corresponding to logged in user
            sql = "INSERT INTO ClientInformation (Client_ID, Client_User_ID, Client_Name, Client_AddressOne, Client_AddressTwo, Client_City, Client_State, Client_Zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            val = (0, CURRENT_USER, name, add1, add2, city, state, zip)
            mycursor.execute(sql, val)
            mydb.commit()

    
    return render_template("client.html")

######################################################### IGNORE
def client_test(name, add1, add2, city, zip):
    if (len(name) <=0 or len(name) >50): 
        name_len = "invalid"
    if (len(add1)<=0 or len(add1)> 100):
        add1_len = "invalid"
    if (len(add2)> 100):
        add2_len = "invalid"
    if(len(city)<=0 or len(city)>100):
        city_len = "invalid"
    if(len(zip)<5 or len(zip)>9):
        zip_len = "invalid"

    return (name_len, add1_len, add2_len, city_len, zip_len)
#########################################################


@app.route('/history.html')
def history():
    return render_template("history.html")

@app.route('/login.html', methods=["GET", "POST"])
def login():
    global CURRENT_USER
    if request.method=="POST":
        session.pop("user_id", None)

        l_name=request.form["loginid"]
        l_pass=request.form["loginpw"]
        
        # user = [x for x in users if x.loginID == l_name]
        # authenticating and grabbing user who's password matches
        sql = "SELECT * FROM UserCredentials WHERE User_Password = %s"
        passw = (l_pass, )
        mycursor.execute(sql, passw)
        myresult = mycursor.fetchall()        
        '''
        if (len(user)!=0):
            user = user[0]
            if user and user.password == l_pass:
                session["user_id"] = user.id
                return redirect(url_for("history"))
            else:
                flash("Incorrect Credentials! Please try again", "error")
        else:
            flash("User name doesnt exist! Please try again", "error")
        '''

        if (len(myresult) != 0):
            db_user = myresult[0]
            session["user_id"] = db_user[0]
            print('db_user: ')
            print(db_user)
            CURRENT_USER = db_user[0]
            print('CURRENT USER: ')
            print(CURRENT_USER)
            return redirect(url_for("history"))
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
            # TODO: for final demo cross check user ids
            flash("User successfully registered, Please go to login page to login.", "success")
            # adding new user to the database
            sql = "INSERT INTO UserCredentials (User_ID, User_Name, User_Password) VALUES (%s, %s, %s)"
            val = (0, s_name, s_pw)
            mycursor.execute(sql, val)
            mydb.commit()
               
    return render_template("signup.html")

######################################################### IGNORE
def signup_test(s_name, s_pw, s_c_pw, match=False):
    if(len(s_name)<=0):
        s_name_len = -1
    if(len(s_pw)<=0):
        s_pw_len = -1
    if(len(s_c_pw)<=0):
        s_c_pw_len = -1
    if(s_c_pw==s_pw):
        match = True

    return (s_name_len, s_pw_len, s_c_pw_len, match)
######################################################### 

@app.route('/quote.html', methods=["GET","POST"])
def quote():
    # TODO: For demo, add redirection to client profile
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
            
            # adding quote to the database
            sql = "INSERT INTO FuelQuote2 (Fuel_ID, Gallons, Fuel_User_ID, Delivery_Date, Suggested_Price, Total_Due) VALUES (%s, %s, %s, %s, %s, %s)"
            val = (0, quantity, CURRENT_USER, date, sug_price, total)
            mycursor.execute(sql, val)
            mydb.commit()     
    return render_template("quote.html")

######################################################### IGNORE
def quote_test(quantity, add, date, sug_price, total):
    if(quantity.isnumeric()== False):
        quantity_status = "invalid"
    if (len(add) <= 0):
        add_status = "invalid"
    if (len(date) <= 0):
        date_status = "invalid"
    if (sug_price.isnumeric()== False):
        sug_price_status = "invalid"
    if (total.isnumeric()== False):
        total_status = "invalid"

    return (quantity_status, add_status, date_status, sug_price_status, total_status)
#########################################################


@app.route('/index.html')
def home():
    return render_template("index.html")


