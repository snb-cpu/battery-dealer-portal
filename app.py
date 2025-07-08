from flask import Flask, request, redirect, render_template, session, url_for
from firebase_admin import credentials, initialize_app, db, auth
from dotenv import load_dotenv
import os, uuid
from encrypt_util import encrypt, decrypt

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)

cred = credentials.Certificate(os.getenv("FIREBASE_CRED_PATH"))
initialize_app(cred, {'databaseURL': os.getenv("DATABASE_URL")})

@app.route('/')
def home():
    return redirect('/login')

@app.route('/register', methods=['GET','POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        company_code = request.form['company_code']
        try:
            user = auth.create_user(email=email, password=password)
            db.reference('dealers').child(user.uid).set({
                'email': email, 'company_code': company_code
            })
            return redirect('/login')
        except Exception as e:
            return f"Error: {e}"
    return render_template('register_dealer.html')

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        all_users = db.reference('dealers').get() or {}
        for uid, u in all_users.items():
            if u['email'] == email:
                session['user'] = u
                return redirect('/dashboard')
        return "Invalid login"
    return render_template('login.html')

@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')
    code = session['user']['company_code']
    customers = db.reference('customers') \
        .order_by_child('company_code').equal_to(code).get() or {}
    data = []
    for cid, c in customers.items():
        data.append({
            'id': cid,
            'name': decrypt(c['name']),
            'phone': decrypt(c['phone']),
            'battery': decrypt(c['battery']),
            'method': c['method'],
            'purchase_date': c['purchase_date']
        })
    return render_template('dashboard.html', customers=data)

@app.route('/add_customer', methods=['GET','POST'])
def add_customer():
    if 'user' not in session:
        return redirect('/login')
    if request.method == 'POST':
        db.reference('customers').child(str(uuid.uuid4())).set({
            'name': encrypt(request.form['name']),
            'phone': encrypt(request.form['phone']),
            'battery': encrypt(request.form['battery']),
            'method': request.form['method'],
            'purchase_date': request.form['purchase_date'],
            'company_code': session['user']['company_code']
        })
        return redirect('/dashboard')
    return render_template('customer_entry.html')

@app.route('/delete_customer', methods=['POST'])
def delete_customer():
    if 'user' not in session:
        return redirect('/login')
    db.reference('customers').child(request.form['customer_id']).delete()
    return redirect('/dashboard')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    app.run(debug=True)
