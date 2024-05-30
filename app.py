from flask import Flask, request, render_template, redirect, url_for, session, flash

import test

app = Flask(__name__)
app.secret_key = 'aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa'

@app.route('/')
def index():
    return render_template('login.html')

@app.route('/jump', methods=['GET'])
def jump():
    return render_template('register.html')

@app.route('/register', methods=['POST'])
def register():
    username = request.form['username']
    password = request.form['password']
    is_admin = 'staff' if 'option1' in request.form else 'customer'
    print(is_admin)
    print(f'账号: {username}')
    print(f'密码: {password}')
    test.testconnect()
    if test.register(is_admin, username, password):
        return render_template('login.html')
    else:
        return f'注册失败！'

@app.route('/login', methods=['POST','GET'])
def login():
    username = request.form['username']
    password = request.form['password']
    print(f'账号: {username}')
    print(f'密码: {password}')
    test.testconnect()
    if test.login(username, password):
        session['username'] = username
        if test.query_for_position(username) == 'customer':
            return redirect(url_for('main'))
        else:
            return redirect(url_for('main2'))
    else:
        return f'登录失败！'

@app.route('/main', methods=['GET','POST'])
def main():
    username = session.get('username')
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'rent':
            if test.rent(username):
                return redirect(url_for('main'))
        elif action == 'return':
            if test.returnbike(username):
                return redirect(url_for('main'))
    available_bikes = test.availablebikes()
    print(available_bikes)
    return render_template('main.html', data=available_bikes)

@app.route('/main2', methods=['GET','POST'])
def main2():
    username = session.get('username')
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'add':
            if test.add_del(username,1):
                return redirect(url_for('main2'))
        elif action == 'del':
            if test.add_del(username,2):
                return redirect(url_for('main2'))
    available_bikes = test.availablebikes()
    print(available_bikes)
    return render_template('main2.html', data=available_bikes)

if __name__ == '__main__':
    app.run(debug=True)

