from flask import Flask, request, render_template, redirect, url_for
from stats import generate_img
from multiprocessing import Process, Pipe
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

@app.route('/select', methods=['GET', 'POST'])
def select_data():
    if request.method == 'POST':
        return redirect(url_for('img', data_selection=request.form['data_selection']))
    else:
        return render_template('select.html', data_options=test.get_data_options())

@app.route('/img')
def img():
    data, x_label, y_label, title, chart_type = test.get_data_for_image(request.args.get('data_selection'))

    parent_conn, child_conn = Pipe()
    p_img = Process(target=generate_img, args=(child_conn, data, x_label, y_label, title, chart_type))

    p_img.start()
    img_base64 = parent_conn.recv()
    p_img.join()

    if not img_base64:
        return "Failed to receive image data"
    
    return render_template('img.html', img_data=img_base64)

if __name__ == '__main__':
    app.run(debug=True)