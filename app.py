from flask import Flask, request, render_template, redirect

import test

app = Flask(__name__)


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

@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    print(f'账号: {username}')
    print(f'密码: {password}')
    test.testconnect()
    if test.login(username, password):
        available_bikes = test.availablebikes()
        return render_template('main.html', data=available_bikes)
    else:
        return f'登录失败！'


@app.route('/main')
def main():
    available_bikes = test.availablebikes()
    print(available_bikes)
    # 渲染 main.html 模板，并传递可用车辆数量
    return render_template('main.html', data=available_bikes)


if __name__ == '__main__':
    app.run(debug=True)
