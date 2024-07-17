import mysql.connector
from flask import Flask, render_template, request, redirect
from datetime import datetime

app = Flask(__name__)

def get_db_connection():
    connection = mysql.connector.connect(
        host="localhost",
        user="root",
        password="trabs123",
        database="funcionarios"
    )
    return connection

#mycursor.execute("CREATE DATABASE funcionarios")
#mycursor.execute("CREATE TABLE person(id INT AUTO_INCREMENT PRIMARY KEY, name VARCHAR(50) NOT NULL, checkedat datetime NOT NULL)")

@app.route('/')
def index():
    db = get_db_connection()
    mycursor = db.cursor()

    mycursor.execute(''' SELECT person.id, person.name, person.checkedat AS checked_in, po.checkedat AS checked_out
                     FROM person
                     LEFT JOIN person_out po ON person.id = po.id ''')
    persons = mycursor.fetchall()

    mycursor.close()
    db.close()
    return render_template('index.html', persons=persons)

@app.route('/check_in', methods=['POST'])
def check_in():
    name = request.form.get('name')
    if name:
        db = get_db_connection()
        mycursor = db.cursor()

        mycursor.execute("SELECT * FROM person WHERE name = %s", (name,))
        person_exists = mycursor.fetchone()

        if not person_exists:
            mycursor.execute("INSERT INTO person (name, checkedat) VALUES(%s,%s)", (name, datetime.now()))
            db.commit()
            message = None
        else:
            message = "Worker already Checked In."    

        mycursor.execute(''' SELECT p.id, p.name, p.checkedat AS checked_in, po.checkedat AS checked_out
                         FROM person p
                         LEFT JOIN person_out po ON p.id = po.id ''')
        persons = mycursor.fetchall()


        mycursor.close()
        db.close()

        if message:
            return render_template('index.html', persons=persons, message=message)
    return redirect('/') 

@app.route('/check_out', methods=['POST'])
def check_out():
    name = request.form.get('name')
    warn_chkout_msg = None
    if name:
        db = get_db_connection()
        mycursor = db.cursor()

        mycursor.execute("SELECT * FROM person WHERE name=%s", (name,))
        person = mycursor.fetchone()
        
        mycursor.fetchall()

        if person:
            person_id = person[0]

            mycursor.execute("SELECT * FROM person_out WHERE id=%s", (person_id,))
            person_out_exists = mycursor.fetchone()
            
            mycursor.fetchall()

            if not person_out_exists:
                mycursor.execute("INSERT INTO person_out (id,name,checkedat) SELECT id,name,%s FROM person WHERE name = %s", (datetime.now(), name))
                db.commit()
            else:
                warn_chkout_msg = "Person not checked in or already checked out."
        else:
            warn_chkout_msg = "Person not checked in or already checked out."            

        mycursor.execute(''' SELECT p.id, p.name, p.checkedat AS checked_in, po.checkedat AS checked_out
                             FROM person p
                             LEFT JOIN person_out po ON p.id = po.id ''')
        persons = mycursor.fetchall()

        mycursor.close()
        db.close()

        return render_template('index.html', persons=persons, warn_chkout_msg=warn_chkout_msg)
    return redirect('/')    

if __name__ == '__main__':
    app.run(debug=True)
