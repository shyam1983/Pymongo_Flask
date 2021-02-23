from flask import Flask, render_template, url_for, request, session, redirect, flash,jsonify
from flask_pymongo import PyMongo
import json, random, string, hashlib, binascii
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
import os
from functools import wraps




app = Flask(__name__)


app.config['MONGO_DBNAME'] = 'admin'
app.config['MONGO_URI'] = "mongodb://localhost:27017/admin"

# connect to MongoDB with the defaults
mongo1 = PyMongo(app, uri ="mongodb://localhost:27017/Laeyes")


mongo = PyMongo(app)

    
@app.route('/login', methods=['POST', 'GET'])
def login():
    daat = request.get_json()
    data = mongo.db.data
    login_user = data.find_one({'EmailID' : daat['EmailID']})

    if login_user:
        check_password_hash(login_user['Password'], daat['password'])
      
    if daat['EmailID'] == login_user['EmailID']:
        session['Loggedin'] = True
        session[daat['EmailID']] = "username"
        #print(mongo.db.authenticate(daat['EmailID'], daat['password'], mechanism='SCRAM-SHA-256'))
    
    if daat['EmailID'] in session:
        print(session)
        session['Loggedin'] = True
        print("Loggedin"  +" " + "as" + " "+ login_user['Name'])
        return("Loggedin") 
    else:
        print("Password or User name is wrong.")
        return "Password or User name is wrong."


def login_required(f):
    @wraps(f)
    def wrap(*args, **kwargs):
        if "Loggedin" in session:
            print(session)
            return f(*args, **kwargs)
        else:
            print(session)
            print("You need to login first")
            return "You need to login first"
    return wrap


@app.route('/register', methods=['POST', 'GET'])
def register():
    dat = request.get_json()
    special_char = {'#', '@', '%'}
    email_char = {'.com', '@'}
   
   
    if(len(dat['Name']) < 5):
        print("User name has to be longer than 4.")
        return "User name has to be longer than 4."

    if not all(character in dat['EmailID'] for character in email_char):
        print("Email-id should be in correct format.")
        return "Email-id should be in correct format."        

    if(len(dat['Password']) < 6):
        print('the length of password should be at least 6 char long')
        return 'the length of password should be at least 6 char long'

    if(len(dat['Password']) > 10):
        print('the length of password should be not be greater than 10')
        return 'the length of password should be not be greater than 10'    

    if not any(char.isupper() for char in dat['Password']):
        print('the password should have at least one uppercase letter')
        return 'the password should have at least one uppercase letter'
    
    if not any(char.islower() for char in dat['Password']):
        print('the password should have at least one lowercase letter')
        return 'the password should have at least one lowercase letter'

    if not any(character in dat['Password'] for character in special_char):
        print('the password should have at least one of the symbols $@#')
        return 'the password should have at least one of the symbols $@#'    

    if not any(char.isdigit() for char in dat['Password']):
        print('the password should have at least one numeral.')
        return 'the password should have at least one numeral.'


    if request.method == 'POST':
        data = mongo.db.data
        existing_user = data.find_one({'EmailID' : dat['EmailID']})

        if existing_user is None:
            print(mongo.db.command("createUser", dat['EmailID'], pwd=dat['Password'], roles=[{"role" : "read", "db" : "Laeyes"}]))
            #print(mongo.db.authenticate(dat['EmailID'], dat['Password'], mechanism='SCRAM-SHA-256'))
            password = generate_password_hash(dat["Password"])
            session['EmailID'] =  dat['EmailID']
            session['logged_in'] = True
            dat["Password"] = password
            data.insert_one(dat).inserted_id
            print("Registered")
            return "Registered"
        else:
            print("The Email-ID already exists.")
            return "The Email-ID already exists."    
       

@app.route('/find/', methods=['GET'])
@login_required
def show():
    query = mongo.db.data.find()
    output = {} 
    i = 0
    for x in query: 
        output[i] = x 
        output[i].pop('_id') 
        i += 1
    return jsonify(output) 


APP_ROOT = os.path.dirname(os.path.abspath(__file__))    
    
@app.route('/face_upload', methods=['POST','GET'])
#@login_required
def face_upload():
    if request.method == 'POST':
        name = str(request.form['Name'])
        model = int(request.form['Model'])
        price = int(request.form['Price'])
        After_Discount = int(request.form['After_Discount'])
        f1 = request.files["admin-images1"]
        f2 = request.files["admin-images2"]
        f3 = request.files["admin-images3"]
        f1 = secure_filename(f1.filename)
        f2 = secure_filename(f2.filename)
        f3 = secure_filename(f3.filename)
        mongo1.db.jpeg.insert_one({'front':f1,
                                    'left':f2,
                                    'right':f3,
                                    'Name':name,
                                    'Model':model,
                                    'Price':price,
                                    'After_Discount':After_Discount})
        flash('Details successfully Submitted')
        return render_template('upload.html')
    return render_template('upload.html')


@app.route('/logout', methods=['POST','GET'])
def logout():
    datg = request.get_json()
    print(datg)
    session['logged_in'] = False
    session.clear()
    print("You have been logged out!")
    return "You have been logged out!"


if __name__ == '__main__':
    app.secret_key = '\x0c\x8eZ\x86\x13\x1e\x0f\xcb\xc3\xb8\xaeY'
    app.run(host='0.0.0.0', port=5000, debug=True)

    