from flask import Flask, render_template, request, url_for, flash, redirect
import sqlite3

app = Flask(__name__)
app.secret_key = 'your_secret_key'

def init_db():
    conn = sqlite3.connect('./baking_info.db')
    curr = conn.cursor()


#Create the Baking_Info table
    curr.execute('''
    CREATE TABLE IF NOT EXISTS Baking_Info(
        Name TEXT NOT NULL,
        Age INTEGER NOT NULL,
        Phone_Number TEXT NOT NULL,
        Security_Level INTEGER NOT NULL,
        Login_Password TEXT NOT NULL
        
        
    )
    ''')
    conn.commit()  # Commit changes
    conn.close()


@app.route('/')  #first page
def home():
    return render_template('home.html')

@app.route('/add_baker', methods=['GET', 'POST'])
def add_baker():
    if request.method == 'POST':
        # Retrieve form data
        name = request.form.get('Name', '').strip()
        age = request.form.get('Age', '').strip()
        phone_number = request.form.get('PhoneNumber', '').strip()
        security_level = request.form.get('SecurityLevel', '').strip()
        password = request.form.get('Password', '').strip()
        print("name, age, phone, sec, password")
        print(f"{name}, {age}, {phone_number}, {security_level}, {password}")


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
        ''', (name, int(age), phone_number, int(security_level), password)) 
        conn.commit()
        conn.close()
        flash("Record Successfully added")
        return render_template('success.html')

    return render_template('add_baker.html')

@app.route('/success')
def success():
    return render_template('success.html')

def get_users_list():
    conn = sqlite3.connect('./baking_info.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT Name, Age, Phone_Number, Security_Level, Login_Password FROM Baking_Info")
    users = cursor.fetchall()
    conn.close()
    return users


def init_resultDB():
    conn = sqlite3.connect('./baking_result.db')
    curr = conn.cursor()

    curr.execute('''
        CREATE TABLE IF NOT EXISTS Baking_Results(
            Entry_Id INTEGER NOT NULL,
            User_Id INTEGER NOT NULL,
            Name TEXT NOT NULL,
            ExcellentV INTEGER NOT NULL,
            OkV INTEGER NOT NULL,
            BadV INT NOT NULL
                 )
                 ''')
    conn.commit()

    curr.execute("SELECT COUNT(*) FROM Baking_Results")
    if curr.fetchone()[0] == 0:  # If the table is empty
        curr.executescript('''
        INSERT INTO Baking_Results VALUES
        (1, 1, 'Whoot Whoot Brownies', 1, 2, 4),
        (2, 2, 'Cho Chip Cookies', 4, 1, 2),
        (3, 3, 'Cho Cake', 2, 4, 1),
        (4, 1, 'Sugar Cookies', 2, 2, 1);
        ''')
        conn.commit()
    else:
        conn.close()
    

def get_results():
    conn = sqlite3.connect('./baking_result.db')
    conn.row_factory = sqlite3.Row 
    cursor = conn.cursor()
    
    cursor.execute("SELECT Entry_Id, User_Id, Name, ExcellentV, OKV, BadV FROM Baking_Results")
    users = cursor.fetchall()
    conn.close()
    return users
    
@app.route('/tableview')
def list():
    users = get_users_list()
    print(users)
    print("HELLOLOKOKOFODFODOFDOFODO")
    return render_template('list.html', users=users)

@app.route('/results')
def show_results():
    users = get_results()
    print(users)
    return render_template('results.html', Entrys=users)


if __name__ == '__main__':
    init_db()
    init_resultDB()
    app.run(debug=True)

