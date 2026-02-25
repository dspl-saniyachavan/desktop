from flask import Flask, redirect, request, jsonify, make_response, render_template, session, flash, url_for
import jwt
from datetime import datetime, timedelta
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = 'KEEP_IT_A_SECRET'

@app.route('/public')
def public():
 return 'Anyone can access this'

def token_required(func):
    @wraps(func)
    def decorated(*args, **kwargs):
        token = request.args.get('token')
        if not token:
            return jsonify({'message': 'Token is missing!'}), 401

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Invalid token'}), 403

        return func(*args, **kwargs)

    return decorated

@app.route('/private')
@token_required
def private():
 return 'Only token can access'

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == "GET":
        return render_template("index.html")
    
    if request.form['username'] and request.form['password'] == '123456':
        session['logged_in'] = True
        token = jwt.encode({
            'user': request.form['username'],
            'expiration': str(datetime.utcnow() + timedelta(minutes=50))
        }, app.config['SECRET_KEY'])

        return jsonify({'token': token})
    else:
        return make_response('Unable to verify', 403, {'WWW-Authenticate': 'Basic realm: "Authentication Failed"'})
    
@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

    
