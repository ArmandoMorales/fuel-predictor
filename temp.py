from crypt import methods
import re
import time
from urllib.request import Request
from flask import Flask, redirect, render_template, request , flash, session, url_for, g
import os

# adding database connection
import mysql.connector
mydb = mysql.connector.connect(
  host="localhost",
  user="root",
  password="password123",
  database="FuelDatabase"
)
mycursor = mydb.cursor()

# CURRENT_USER = -1
LAST_INSERTED_ID = -1

class person:
    def __init__(self):
        self.name = "dan"
        self.id = 123

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

class price_module:
    def __init__(self, gallons_requested, delivery_address, delivery_date, isTexas, hasHistory, current_price=1.50, company_profit=0.1):
        self.gallons_requested = float(gallons_requested)
        self.delivery_address = delivery_address
        self.delivery_date = delivery_date
        self.current_price = current_price
        self.isTexas = isTexas
        self.hasHistory = hasHistory
        self.company_profit = company_profit

    def get_quote(self):
        if self.isTexas:
            self.location_factor = 0.02
        else:
            self.location_factor = 0.04

        if self.hasHistory:
            self.rate_history_factor = 0.01
        else:
            self.rate_history_factor = 0.00

        gallons_requested_factor = 0.02
        if self.gallons_requested < 1000:
            gallons_requested_factor = 0.03

        print(str(self.current_price) + " " + str(self.location_factor) + " " + str(self.rate_history_factor) + " " + str(gallons_requested_factor) + " " + str(self.company_profit))
        margin = self.current_price * (self.location_factor - self.rate_history_factor + gallons_requested_factor + self.company_profit)
        print(margin)
        suggested_price = self.current_price + margin
        total_amt_due = self.gallons_requested * suggested_price

        return (suggested_price, total_amt_due)

'''
Create a pricing module that should calculate the price per gallon based on this formula.

Suggested Price = Current Price + Margin

Where,

Current price per gallon = $1.50 (this is the price what distributor gets from refinery and it varies based upon crude price. But we are keeping it constant for simplicity)
Margin =  Current Price * (Location Factor - Rate History Factor + Gallons Requested Factor + Company Profit Factor)

Consider these factors:
Location Factor = 2% for Texas, 4% for out of state.
Rate History Factor = 1% if client requested fuel before, 0% if no history (you can query fuel quote table to check if there are any rows for the client)
Gallons Requested Factor = 2% if more than 1000 Gallons, 3% if less
Company Profit Factor = 10% always

Example:
1500 gallons requested, in state, does have history (i.e. quote history data exist in DB for this client)

Margin => (.02 - .01 + .02 + .1) * 1.50 = .195
Suggested Price/gallon => 1.50 + .195 = $1.695
Total Amount Due => 1500 * 1.695 = $2542.50
'''

users = []
users.append(user(id =1, loginID = "adam", password = "abc123" ))
users.append(user(id =2, loginID = "jacob", password = "xyz000" ))


quotes = []
quotes.append(fule_quote_module(date='01-01-2022', gallons_requested=20, suggested_price=2000, total_amt_due=40000, first_order=True))
quotes.append(fule_quote_module(date='02-02-2023', gallons_requested=40, suggested_price=4000, total_amt_due=80000, first_order=False))

app = Flask(__name__)
app.secret_key="123abc"

# GOOD
@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == 'POST':
        session.pop('user', None)

        username_from_form = request.form['loginid']

        sql = "SELECT * FROM UserCredentials WHERE User_Name = %s"
        adr = (username_from_form, )

        mycursor.execute(sql, adr)
        myresult = mycursor.fetchall()

        if len(myresult) > 0:
            database_password = myresult[0][2]
            database_user_id = myresult[0][0]

        else:
            database_password = None

        if request.form['loginpw'] == database_password:
            session['User_Name'] = username_from_form
            session['User_ID'] = database_user_id

            return redirect(url_for('home'))

    return render_template("login.html")


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
            # check if user already exists / has a entry in ClientInformation table
            Client_User_ID = session['User_ID'] 
            sql = "SELECT * FROM ClientInformation WHERE Client_User_ID = %s"
            adr = (Client_User_ID, )
            mycursor.execute(sql, adr)
            myresult = mycursor.fetchall()
            # if the user does not exist
            if len(myresult) <= 0:
                # inserting into database client info corresponding to logged in user
                sql = "INSERT INTO ClientInformation (Client_ID, Client_User_ID, Client_Name, Client_AddressOne, Client_AddressTwo, Client_City, Client_State, Client_Zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                val = (0, Client_User_ID, name, add1, add2, city, state, zip)
                mycursor.execute(sql, val)
                mydb.commit()
                flash("User Profile Successfully Created", "success")
            else:
                # update the users info based on what they typed into the form
                # sql = "INSERT INTO ClientInformation (Client_ID, Client_User_ID, Client_Name, Client_AddressOne, Client_AddressTwo, Client_City, Client_State, Client_Zipcode) VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                sql = "UPDATE ClientInformation SET Client_Name = %s, Client_AddressOne = %s, Client_AddressTwo = %s, Client_City = %s, Client_State = %s, Client_Zipcode = %s WHERE Client_User_ID = %s;"
                val = (name, add1, add2, city, state, zip, session['User_ID'])
                mycursor.execute(sql, val)
                mydb.commit()
                flash("User Profile Successfully Saved", "success")


    # DISPLAY USER's INFO
    sql = "SELECT * FROM ClientInformation WHERE Client_User_ID = %s"
    adr = (session['User_ID'], )

    mycursor.execute(sql, adr)

    myresult = mycursor.fetchall()

    #for x in myresult:
    #    print(x)

    if len(myresult) > 0:
        name = myresult[0][2]
        add1 = myresult[0][3]
        add2 = myresult[0][4]
        city = myresult[0][5]
        state = myresult[0][6]
        zip = myresult[0][7]
    else:
        name = ''
        add1 = ''
        add2 = ''
        city = ''
        state = ''
        zip = ''

    return render_template("client.html", name=name, add1=add1, add2=add2, city=city, state=state, zip=zip)

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
    # get session for who's logged in, and do a query to find the user with Fuel_User_ID.
    # then pass variables to be rendered.

    # sql = "SELECT * FROM FuelQuote2 WHERE Fuel_User_ID = %s"

    sql = "SELECT Gallons, Delivery_Date, Suggested_Price, Total_Due, Client_AddressOne, Client_City, Client_State, Client_Zipcode FROM FuelQuote2 LEFT JOIN ClientInformation ON FuelQuote2.Fuel_User_ID = ClientInformation.Client_User_ID WHERE FuelQuote2.Fuel_User_ID = %s"
    adr = (session['User_ID'], )
    mycursor.execute(sql, adr)
    myresult = mycursor.fetchall()

    return render_template("history.html", myresult=myresult)


'''
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

        if (len(myresult) != 0):
            db_user = myresult[0]
            session["user_id"] = db_user[0]
            print('db_user: ')
            print(db_user)
            CURRENT_USER = db_user[0]
            print('CURRENT USER: ')
            print(CURRENT_USER)
            return redirect(url_for("index"))
        else:
            flash("User name doesnt exist! Please try again", "error")

    return render_template("login.html")
'''


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
            # return redirect(url_for('index'))  
               
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
    global LAST_INSERTED_ID
    # TODO: For demo, add redirection to client profile
    if request.method=="POST":
        # session.pop("user_id", None)
        quantity = request.form["gallon"]   
        # add = request.form["delivery"]       
        date = request.form["datetime"]     
        # sug_price = request.form["price"]   
        # total = request.form["totalamt"]

        if(quantity.isnumeric()== False):
            # flash("Number of gallons must be a number!", "error")
            pass
        elif date == "":
            # flash("Date cannot be empty", "error")
            pass
        else:
            # check which button was clicked
            if request.form['get-quote-btn'] == 'GetQuote':
                # flash("Order submitted successfully","success")
                '''
                # adding quote to the database
                sql = "INSERT INTO FuelQuote2 (Fuel_ID, Gallons, Fuel_User_ID, Delivery_Date, Suggested_Price, Total_Due) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (0, quantity, CURRENT_USER, date, sug_price, total)
                mycursor.execute(sql, val)
                mydb.commit() 
                '''

                

                sql = "SELECT * FROM ClientInformation WHERE Client_User_ID = %s"
                adr = (session['User_ID'], )
                mycursor.execute(sql, adr)
                myresult = mycursor.fetchall()

                if len(myresult) > 0:
                    # name = myresult[0][2]
                    add1 = myresult[0][3]
                    add2 = myresult[0][4]
                    city = myresult[0][5]
                    state = myresult[0][6]
                    zip = myresult[0][7]
                    delivery_address = add1 + " " + city + ", " + state + " " + str(zip)
                else:
                    # name = myresult[0][2]
                    add1 = ""
                    add2 = ""
                    city = ""
                    state = ""
                    zip = ""
                    delivery_address = add1 + " " + city + ", " + state + " " + str(zip)

                # calculate the suggested and total price, and pass it down as a variable
                isTexas = True
                if state != 'TX':
                    isTexas = False

                hasHistory = False
                sql = "SELECT * FROM FuelQuote2 WHERE Fuel_User_ID = %s"
                adr = (session['User_ID'], )
                print ('seddion id', session['User_ID'])
                mycursor.execute(sql, adr)
                myresult = mycursor.fetchall()
                if len(myresult) > 0:
                    hasHistory = True
                
                priceObj = price_module(quantity, delivery_address, date, isTexas, hasHistory, current_price=1.50, company_profit=0.1)
                suggested_price, total_amt_due = priceObj.get_quote()

                # insert into temp
                sql = "INSERT INTO TEMP (Fuel_ID, Gallons, Delivery_Date, Suggested_Price, Total_Due) VALUES (%s, %s, %s, %s, %s)"
                val = (0, quantity, date, suggested_price, total_amt_due)
                mycursor.execute(sql, val)
                mydb.commit()

                # print("LAST INSERTED ID: ")
                # print(mycursor.lastrowid)

                LAST_INSERTED_ID = mycursor.lastrowid
                # print("LSSDLFKJSDLFKJD:")
                # print(LAST_INSERTED_ID)

                return render_template("quote.html", delivery_address=delivery_address, add2=add2, suggested_price=suggested_price,  total_amt_due=total_amt_due)
            elif request.form['submit-quote-btn'] == 'Submit':
                # presssed submit button
                sql = "SELECT * FROM TEMP WHERE Fuel_ID = %s"
                adr = (LAST_INSERTED_ID, )
                # print ('seddion id', session['User_ID'])
                mycursor.execute(sql, adr)
                myresult = mycursor.fetchall()
                if len(myresult) > 0:
                    gals_from_temp = myresult[0][1]
                    delivery_date_from_temp = myresult[0][2]
                    suggested_from_temp = myresult[0][3]
                    total_from_temp = myresult[0][4]

                # insert into FuelQuote2
                sql = "INSERT INTO TEMP (Fuel_ID, Gallons, Fuel_User_ID, Delivery_Date, Suggested_Price, Total_Due) VALUES (%s, %s, %s, %s, %s, %s)"
                val = (0, gals_from_temp, session['User_ID'], delivery_date_from_temp, suggested_from_temp, total_from_temp)
                mycursor.execute(sql, val)
                mydb.commit()

    sql = "SELECT * FROM ClientInformation WHERE Client_User_ID = %s"
    adr = (session['User_ID'], )
    mycursor.execute(sql, adr)
    myresult = mycursor.fetchall()

    if len(myresult) > 0:
        # name = myresult[0][2]
        add1 = myresult[0][3]
        add2 = myresult[0][4]
        city = myresult[0][5]
        state = myresult[0][6]
        zip = myresult[0][7]
        delivery_address = add1 + " " + city + ", " + state + " " + str(zip)
    else:
        # name = myresult[0][2]
        add1 = ""
        add2 = ""
        city = ""
        state = ""
        zip = ""
        delivery_address = add1 + " " + city + ", " + state + " " + str(zip)

    '''
    # calculate the suggested and total price, and pass it down as a variable
    isTexas = True
    if state != 'Texas' or state != 'texas' or state != 'TX' or state != 'tx':
        isTexas = False

    hasHistory = True
    sql = "SELECT * FROM FuelQuote2 WHERE Fuel_User_ID = %s"
    adr = (session['User_ID'], )
    mycursor.execute(sql, adr)
    myresult = mycursor.fetchall()
    if len(myresult) <= 0:
        hasHistory = False
    
    priceObj = price_module(quantity, delivery_address, date, isTexas, hasHistory, current_price=1.50, company_profit=0.1)
    suggested_price, total_amt_due = priceObj.get_quote()
    '''

    return render_template("quote.html", delivery_address=delivery_address, add2=add2)

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


@app.route('/logout.html', methods=["GET","POST"])
def logout():
    return render_template("logout.html")


@app.route('/index.html')
def home():
    if g.User_Name:
        return render_template("index.html", User_Name=session['User_Name'])
    return redirect(url_for(index))

@app.before_request
def before_request():
    g.User_Name = None

    if 'User_Name' in session:
        g.User_Name = session['User_Name']

@app.route('/dropsession')
def dropsession():
    session.pop('User_Name', None)
    session.pop('User_ID', None)

    # return render_template('login.html')
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)