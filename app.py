from flask import Flask, request, render_template, redirect, url_for, session, flash, abort
from stats import generate_img, do_predict
from multiprocessing import Process, Pipe

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
        elif action == 'select':
            return redirect(url_for('select_data'))
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
        elif action == 'select':
            return redirect(url_for('select_data'))
    available_bikes = test.availablebikes()
    print(available_bikes)
    return render_template('main2.html', data=available_bikes)

@app.route('/select', methods=['GET', 'POST'])
def select_data():
    if request.method == 'POST':
        return redirect(url_for('img', data_selection=request.form['data_selection']))
    else:
        return render_template('select.html', data_options=test.get_data_options())

@app.route('/img', methods=['GET'])
def img():
    allowed_referers = {
    url_for('predict', _external=True),
    url_for('select_data', _external=True)
    }
    referer = request.headers.get('Referer')

    data, x_label, y_label, title, chart_type = test.get_data_for_image(request.args.get('data_selection'))

    parent_conn, child_conn = Pipe()
    
    p_img = Process(target=generate_img, args=(child_conn, data, x_label, y_label, title, chart_type))
    p_img.start()
    img_base64 = parent_conn.recv()
    p_img.join()

    if not img_base64:
        return "Failed to receive image data"
    
    if referer in allowed_referers:
        return render_template('img.html', img_data=img_base64)
    else:
        abort(403)

@app.route('/predict')
def predict():
    data = do_predict(test.get_data_for_predict())

    parent_conn, child_conn = Pipe()
    p_img = Process(target=generate_img, args=(child_conn, data, '日期', '订单数', '未来30天订单数预测', 'line'))
    p_img.start()
    img_base64 = parent_conn.recv()
    p_img.join()

    if not img_base64:
        return "Failed to receive image data"

    return render_template('img.html', img_data=img_base64)

@app.errorhandler(403)
def handle_bad_request(e):
    return '错误请求', 403   #返回错误信息

if __name__ == '__main__':
    app.run(debug=True)