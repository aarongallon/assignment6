from flask import Flask, render_template, request, url_for, flash, redirect, session
import sqlite3
from cryptography.fernet import Fernet
import os
import pandas as pd


app = Flask(__name__)
app.secret_key = 'your_secret_key'

from cryptography.fernet import Fernet

if not os.path.exists("key.key"):
    key = Fernet.generate_key()
    with open("key.key", "wb") as key_file:
        key_file.write(key)
else:
    with open("key.key", "rb") as key_file:
        key = key_file.read()
cipher = Fernet(key)

def init_db():
    conn = sqlite3.connect('./baking_info.db')
    curr = conn.cursor()

    curr.execute('''Drop table IF EXISTS Baking_Info''')
    #curr.execute('''Select * from Baking_Info;''')
#Create the Baking_Info table
    curr.execute('''
    CREATE TABLE IF NOT EXISTS Baking_Info(
        UserId INTEGER PRIMARY KEY AUTOINCREMENT,
        Name TEXT NOT NULL,
        Age INTEGER NOT NULL,
        Phone_Number TEXT NOT NULL,
        Security_Level INTEGER NOT NULL,
        Login_Password TEXT NOT NULL
        
        
    )
    ''')
    conn.commit()  # Commit changes
    name3 = 'Admin3'
    name2 = 'Admin2'
    name1 = 'Admin1'
    age = 21
    Phone_Number = '1234567890'
    Security_Level3 = 3
    Security_Level2 = 2
    Security_Level1 = 1
    Login_Password = '12345'
    nm3 = str(cipher.encrypt(name3.encode()).decode('utf-8'))
    nm2 = str(cipher.encrypt(name2.encode()).decode('utf-8'))
    nm1 = str(cipher.encrypt(name1.encode()).decode('utf-8'))
    lp = str(cipher.encrypt(Login_Password.encode()).decode('utf-8'))
    pn = str(cipher.encrypt(Phone_Number.encode()).decode('utf-8'))
    curr.execute('''INSERT INTO Baking_Info(Name, Age, Phone_Number, Security_Level, Login_Password)
                 VALUES(?,?,?,?,?)''', (nm3,age,pn,Security_Level3,lp)
                 )
    conn.commit()
    curr.execute('''INSERT INTO Baking_Info(Name, Age, Phone_Number, Security_Level, Login_Password)
                 VALUES(?,?,?,?,?)''', (nm2,age,pn,Security_Level2,lp)
                 )
    conn.commit()
    curr.execute('''INSERT INTO Baking_Info(Name, Age, Phone_Number, Security_Level, Login_Password)
                 VALUES(?,?,?,?,?)''', (nm1,age,pn,Security_Level1,lp)
                 )
    conn.commit()
    conn.close()


@app.route('/')  #first page
def home():
    return render_template('home.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        # Retrieve form data
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '').strip()
        try:

            conn = sqlite3.connect('./baking_info.db')
            conn.row_factory = sqlite3.Row
            curr = conn.cursor()

            curr.execute("SELECT UserId, Name, Age, Phone_Number, Security_Level, Login_Password FROM Baking_Info")
            rows = curr.fetchall()

            df = pd.DataFrame(rows, columns=["UserId", "Name", "Age", "Phone_Number", "Security_Level", "Login_Password"])
            df["Name"] = df["Name"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
            df["Phone_Number"] = df["Phone_Number"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
            df["Login_Password"] = df["Login_Password"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
            securitylevel = 0
            filtered_row = df[(df['Name'] == username) & (df['Login_Password'] == password)]

            if not filtered_row.empty:
                securitylevel = filtered_row.iloc[0]['Security_Level']
                userId = filtered_row.iloc[0]['UserId']
                session['username'] = username
                session['security_level'] = int(securitylevel)
                session['user_id'] = int(userId)
            else:
                flash("Invalid Username or Password")
            if securitylevel == 1:
                return render_template('homepagelvl1.html', username=username)
            elif securitylevel == 2: 
                return render_template('homepagelvl2.html', username=username)
            elif securitylevel == 3:
                return render_template('homepagelvl3.html', username=username)
            else:
                return render_template('login.html')
    
        except Exception as e:
            flash("Incorrect Username or Password")
            return render_template('login.html')
        finally:
            conn.close()
    return render_template('login.html')

@app.route('/logout')
def logout():
    session['username'] = False
    session['security_level'] = False
    session['user_id'] = False

    return home()

@app.route('/pagenotfound')
def pagenotfound():
    session['username'] = False
    session['security_level'] = False
    session['user_id'] = False
    return render_template('pagenotfound.html')

@app.route('/add_baker', methods=['GET', 'POST'])
def add_baker():
    if session['security_level'] != 3:
        logout()
        return render_template('pagenotfound.html')
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('Name', '').strip()
        age = request.form.get('Age', '').strip()
        phone_number = request.form.get('PhoneNumber', '').strip()
        security_level = request.form.get('SecurityLevel', '').strip()
        password = request.form.get('Password', '').strip()

        #encrypt the name and password and phone number 
        nm = str(cipher.encrypt(name.encode()).decode('utf-8'))
        pwd = str(cipher.encrypt(password.encode()).decode('utf-8'))
        phn_num = str(cipher.encrypt(phone_number.encode()).decode('utf-8'))


        decrypted_name = cipher.decrypt(nm.encode('utf-8')).decode('utf-8')
        decrypted_password = cipher.decrypt(pwd.encode('utf-8')).decode('utf-8')
        decrypted_phone_number = cipher.decrypt(phn_num.encode('utf-8')).decode('utf-8')
        errors = False
        if not name:
            flash("You cannot enter an empty name.")
            errors = True
        
        if not phone_number:
            flash("You cannot enter an empty phone number")
            errors = True
        
        if not age.isdigit() or not (0 < int(age) < 121):
            flash("The age must be a whole number greater than 0 and less than 121.")
            errors = True
        
        if not security_level.isdigit() or int(security_level) not in [1,2,3]:
            flash("The SecurityLevel must be a numeric value between 1 and 3")
            errors = True
        
        if not password:
            flash("You cannot enter an empty password")
            errors = True

        if errors:
            return redirect(url_for('success'))
        
        conn = sqlite3.connect('./baking_info.db')
        curr = conn.cursor()
        curr.execute('''
            INSERT INTO Baking_info (Name, Age, Phone_Number, Security_Level, Login_Password)
            VALUES (?, ?, ?, ?, ?)
        ''', (nm, int(age), phn_num, int(security_level), pwd)) 
        conn.commit()
        conn.close()
        flash("Record Successfully added")
        return render_template('success.html')

    return render_template('add_baker.html')

@app.route('/add_entry', methods=['GET', 'POST'])
def add_entry():
    if session['security_level'] == False:
        logout()
        return render_template('pagenotfound.html')
    if request.method == 'POST':
        # Retrieve form data
        user_id = session['user_id']
        username = session['username']
        entry = request.form.get('Entry', '').strip()
        e_votes = request.form.get('e_votes', '').strip()
        ok_votes = request.form.get('ok_votes', '').strip()
        b_votes = request.form.get('b_votes', '').strip()

        errors = False
        if not entry:
            flash("You cannot enter an empty entry.")
            errors = True
        
        if int(e_votes) < 0:
            flash("You cannot enter an excellent vote less than 0")
            errors = True
        
        if int(ok_votes) < 0:
            flash("You cannot enter an excellent vote less than 0")
            errors = True
        
        if int(b_votes) < 0:
            flash("You cannot enter an excellent vote less than 0")
            errors = True
        

        if errors:
            return redirect(url_for('successEntry'))
        
        conn = sqlite3.connect('./baking_result.db')
        curr = conn.cursor()
        curr.execute('''
            INSERT INTO Baking_Results (User_Id, Entry_Id, Name, ExcellentV, OkV, BadV)
            VALUES (?, ?, ?, ?, ?,?)
        ''', (user_id, 2, entry, int(e_votes), int(ok_votes), int(b_votes))) 
        conn.commit()
        conn.close()
        flash("Record Successfully added")
        return render_template('successEntry.html')

    return render_template('add_entry.html')

@app.route('/success')
def success():
    return render_template('success.html')

@app.route('/successEntry')
def successEntry():
    return render_template('successEntry')



@app.route('/homepagelvl1')
def homepagelvl1():
    if session['security_level'] != 1:
        return render_template('pagenotfound.html')
    return render_template('homepagelvl1.html',username=session['username'])

@app.route('/homepagelvl2')
def homepagelvl2():
    if session['security_level'] != 2:
        return render_template('pagenotfound.html')
    return render_template('homepagelvl2.html',username=session['username'])

@app.route('/homepagelvl3')
def homepagelvl3():
    if session['security_level'] != 3:
        return render_template('pagenotfound.html')
    return render_template('homepagelvl3.html',username=session['username'])

@app.route('/go_home')
def go_home():
    if session['security_level'] == 1:
        return homepagelvl1()
    elif session['security_level'] == 2:
        return homepagelvl2()
    elif session['security_level'] == 3:
        return homepagelvl3()
    else:
        return render_template('home.html')



def get_users_list():
    conn = sqlite3.connect('./baking_info.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT Name, Age, Phone_Number, Security_Level, Login_Password FROM Baking_Info")

    rows = cursor.fetchall()

    df = pd.DataFrame(rows, columns=["Name", "Age", "Phone_Number", "Security_Level", "Login_Password"])
    
    # Decrypt fields
    df["Name"] = df["Name"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
    df["Phone_Number"] = df["Phone_Number"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
    df["Login_Password"] = df["Login_Password"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))

    users = df.to_dict(orient="records")
    
    conn.close()
    return users


def init_resultDB():
    conn = sqlite3.connect('./baking_result.db')
    curr = conn.cursor()

    
    curr.execute('''Drop table IF EXISTS Baking_Results''')
    #curr.execute('''Select * from Baking_Results;''')
    conn.commit()

    curr.execute('''
        CREATE TABLE IF NOT EXISTS Baking_Results(
            User_Id INTEGER NOT NULL,
            Entry_Id INTEGER NOT NULL,
            Name TEXT NOT NULL,
            ExcellentV INTEGER NOT NULL,
            OkV INTEGER NOT NULL,
            BadV INT NOT NULL
                 )
                 ''')
    conn.commit()

    conn.close()
    

def get_results():
    conn = sqlite3.connect('./baking_result.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT Entry_Id, User_Id, Name, ExcellentV, OKV, BadV FROM Baking_Results")
    users = cursor.fetchall()
    conn.close()
    return users

def get_my_results():
    conn = sqlite3.connect('./baking_result.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute('''SELECT User_Id, Entry_Id,  Name, ExcellentV, OKV, BadV FROM Baking_Results WHERE User_Id=?
                    ''', (session['user_id'],))
    users = cursor.fetchall()
    conn.close()
    return users
    
    
@app.route('/tableview')
def list():
    if session['security_level'] == False or session['security_level'] == 1:
        return render_template('pagenotfound.html')
    users = get_users_list()
    return render_template('list.html', users=users)

@app.route('/my_results')
def my_results():
    if session['security_level'] == False:
        return render_template('pagenotfound.html')
    results = get_my_results()
    return render_template('my_results.html', Entrys=results)


@app.route('/results')
def show_results():
    if session['security_level'] != 3:
        return render_template('pagenotfound.html')
    users = get_results()
    return render_template('results.html', Entrys=users)

def printscript():
    conn = sqlite3.connect('./baking_info.db')
    conn.row_factory = sqlite3.Row
    curr = conn.cursor()

    curr.execute("SELECT UserId, Name, Age, Phone_Number, Security_Level, Login_Password FROM Baking_Info")
    rows = curr.fetchall()

    df = pd.DataFrame(rows, columns=["UserId", "Name", "Age", "Phone_Number", "Security_Level", "Login_Password"])
    df["Name"] = df["Name"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
    df["Phone_Number"] = df["Phone_Number"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
    df["Login_Password"] = df["Login_Password"].apply(lambda x: cipher.decrypt(x.encode()).decode('utf-8'))
    print(df)
    print("Sign in using Admin1 Admin2 or Admin3 for the respective security levels to test")
    conn.close()





if __name__ == '__main__':
    if os.environ.get('WERKZEUG_RUN_MAIN') == 'true':
        init_db()
        init_resultDB()
        printscript()

    app.run(debug=True)

