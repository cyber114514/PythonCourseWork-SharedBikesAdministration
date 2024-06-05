import pymysql
import threading
from datetime import datetime, timedelta

lock = threading.Lock()

class IsRentingError(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
class PositionError(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
class BikeError(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
class WrongUserError(Exception):
    def __init__(self,msg):
        self.msg = msg
        super().__init__(self.msg)
def testconnect():
    lock.acquire()
    conn = pymysql.connect(
        host='localhost',
            port=3306,
            user='flaskuser',
            password='123456',
            charset='utf8mb4',
            db='bike'
    )
    print(conn.get_server_info())
    cursor = conn.cursor()
    cursor.close()
    conn.close()
    lock.release()

class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host='localhost',
            port=3306,
            user='flaskuser',
            password='123456',
            charset='utf8mb4',
            db='bike'
        )
        self.cursor = self.conn.cursor()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.conn.commit()
        self.cursor.close()
        self.conn.close()

    def query(self, sql, fetchall=True):
        self.cursor.execute(sql)
        if fetchall:
            return self.cursor.fetchall()
        else:
            return self.cursor.fetchone()

    def set(self,sql):
        self.cursor.execute(sql)

def query_for_position(uname):
    lock.acquire()
    with Database() as db:
        message = f"select position from user where username = '{uname}'"
        try:
            result = db.query(message)
            print(result[0][0])
            return result[0][0]
        except Exception as e:
            print(f'error:{e}')
        finally:
            lock.release()


def query_for_rent(bikeid, userid):
    lock.acquire()
    with Database() as db:
        userposition = 'select position,isrenting from user where userid=' + str(userid)
        BikeState = 'select rentable from bike where bikeid=' + str(bikeid)
        try:
            result = db.query(userposition)
            bs = db.query(BikeState)
            if bs[0][0] == 0:
                raise BikeError('Bike is being rented')
            if (result[0][0] != 'customer'):
                raise PositionError('wrong position')
            if (result[0][1] == True):
                raise IsRentingError("You're renting a bike!")
            renting = "UPDATE bike SET rentable = False, userid = {} WHERE bikeid = {}".format(userid, bikeid)
            db.set(renting)
            updateuser = "update user set isrenting=True where userid=" + str(userid)
            db.set(updateuser)
            start_time = get_mock_now().strftime('%Y-%m-%d %H:%M:%S')
            insert_order = "INSERT INTO orders (userid, bikeid, start_time) VALUES ({}, {}, '{}')".format(userid, bikeid,
                                                                                                      start_time)
            db.set(insert_order)
            print('Successfully rented the bike!')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            lock.release()


def query_for_return(bikeid, userid):
    lock.acquire()
    with Database() as db:
        userposition = 'SELECT position, isrenting, userid FROM user WHERE userid = {}'.format(userid)
        result = db.query(userposition)
        BikeState = 'SELECT rentable, userid FROM bike WHERE bikeid = {}'.format(bikeid)
        bs = db.query(BikeState)

        try:
            if bs[0][0] == 1:
                raise BikeError('Bike is not available for return')
            if result[0][0] != 'customer':
                raise PositionError('Wrong position')
            if result[0][1] == False:
                raise IsRentingError("You're not renting a bike!")
            if int(result[0][2]) != int(bs[0][1]):
                raise WrongUserError('Wrong userid')

            # Update bike and user status
            returning = "UPDATE bike SET rentable = True, userid = NULL WHERE bikeid = {}".format(bikeid)
            db.set(returning)
            updateuser = "UPDATE user SET isrenting = False WHERE userid = {}".format(userid)
            db.set(updateuser)

            # Calculate end time, total time, and total cost
            end_time = get_mock_now()
            start_time_query = "SELECT start_time FROM orders WHERE userid = {} AND bikeid = {} ORDER BY orderid DESC LIMIT 1".format(userid, bikeid)
            start_time = db.query(start_time_query, fetchall=False)[0]
            total_time = (end_time - start_time).total_seconds() / 3600  # Convert seconds to hours
            total_time = max(total_time, 1)  # Minimum charge is for one hour
            total_cost = total_time * 1.5  # Charge rate per hour

            update_order = "UPDATE orders SET end_time = '{}', total_time = {}, total_cost = {} WHERE userid = {} AND bikeid = {} AND end_time IS NULL".format(
                end_time.strftime('%Y-%m-%d %H:%M:%S'), total_time, total_cost, userid, bikeid)
            db.set(update_order)

            print('Successfully returned the bike!')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            lock.release()

def query_for_add(userid):
    lock.acquire()
    with Database() as db:
        userposition = 'SELECT position, isrenting, userid FROM user WHERE userid = {}'.format(userid)
        result = db.query(userposition)
        try:
            if result[0][0] != 'staff':
                raise PositionError('Wrong position')
            add = 'INSERT INTO bike(rentable) VALUES (1)'
            db.set(add)
            print('Successfully added the bike!')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            lock.release()

def delete_max_bike(userid):
    lock.acquire()
    with Database() as db:
        userposition = 'SELECT position, isrenting, userid FROM user WHERE userid = {}'.format(userid)
        result = db.query(userposition)
        try:
            if result[0][0] != 'staff':
                raise PositionError('Wrong position')
            max_bikeid_query = 'SELECT MAX(bikeid) FROM bike'
            max_bikeid = db.query(max_bikeid_query, fetchall=False)[0]
            delete_query = 'DELETE FROM bike WHERE bikeid = {}'.format(max_bikeid)
            db.set(delete_query)
            print('Successfully deleted the bike with the highest bikeid!')
        except Exception as e:
            print(f'Error: {e}')
        finally:
            lock.release()

def register(p, uname, pwd):
    lock.acquire()
    if len(uname) == 0 or len(pwd) == 0:
        print("empty username or password!")
        return False
    with Database() as db:
        try:
            insert = f'INSERT INTO user(position, username, password) VALUES ("{p}", "{uname}", "{pwd}")'
            db.query(insert)
            print('Successfully registered!')
            return True
        except Exception as e:
            print(f'Error: {e}')
            return False
        finally:
            lock.release()

def login(uname, pwd):
    lock.acquire()
    if len(uname) == 0 or len(pwd) == 0:
        print("empty username or password!")
        return False
    with Database() as db:
        try:
            select = f'SELECT * FROM user WHERE username = "{uname}" AND password = "{pwd}"'
            result = db.query(select)
            if result:
                print('Successfully logged in!')
                return True
            else:
                print('Wrong username or password!')
                return False
        except Exception as e:
            print(f'Error: {e}')
            return False
        finally:
            lock.release()

def availablebikes():
    lock.acquire()
    with Database() as db:
        try:
            query = 'SELECT COUNT(*) FROM bike WHERE rentable = True'
            result = db.query(query)
            available_bikes = int(result[0][0])
            print(available_bikes)
            return available_bikes
        except Exception as e:
            print(f'Error: {e}')
        finally:
            lock.release()
    

def rent(username):
    lock.acquire()
    with Database() as db:
        try:
            select_user = f'SELECT userid FROM user WHERE username = "{username}"'
            result1 = db.query(select_user)
            query = 'SELECT bikeid FROM bike WHERE rentable = True'
            result2 = db.query(query)
            query_for_rent(result2[0][0], result1[0][0])
            return True
        except Exception as e:
            print(f'Error: {e}')
            return False
        finally:
            lock.release()

def returnbike(username):
    lock.acquire()
    with Database() as db:
        try:
            select_user = f'SELECT userid FROM user WHERE username = "{username}"'
            result1 = db.query(select_user)
            query = f'SELECT bikeid FROM bike WHERE userid = "{result1[0][0]}"'
            result2 = db.query(query)
            query_for_return(result2[0][0], result1[0][0])
            return True
        except Exception as e:
            print(f'Error: {e}')
            return False
        finally:
            lock.release()

def add_del(username, mode):
    lock.acquire()
    with Database() as db:
        try:
            select_user = f'SELECT userid FROM user WHERE username = "{username}"'
            result1 = db.query(select_user)
            if mode == 1:
                query_for_add(result1[0][0])
                return True
            elif mode == 2:
                delete_max_bike(result1[0][0])
                return True
        except Exception as e:
            print(f'Error: {e}')
            return False
        finally:
            lock.release()

def get_mock_now():
    return mock_now

def get_data_options():
    # 从数据库获取数据选项
    data_options = [
        {'id': 1, 'name': '订单的费用分布'},
        {'id': 2, 'name': '订单的租赁时间分布'},
        {'id': 3, 'name': '每天的订单数量'}
    ]
    return data_options

def get_data_for_image(data_id):
    lock.acquire()
    with Database() as db:# 根据选择的数据ID从数据库获取数据
        try:
            if data_id == '1': 
                query = f'SELECT orderid, total_cost FROM orders'
                result = db.query(query)
                data = {'x': [row[0] for row in result], 'y': [row[1] for row in result]}
                x_label = '订单ID'
                y_label = '费用'
                title = '订单的费用分布'
                chart_type = 'scatter'

            elif data_id == '2':
                query = f'SELECT orderid, total_time FROM orders'
                result = db.query(query)
                data = {'x': [row[0] for row in result], 'y': [row[1] for row in result]}
                x_label = '订单ID'
                y_label = '租赁时间'
                title = '订单的租赁时间分布'
                chart_type = 'scatter'

            elif data_id == '3':
                query = f'SELECT DATE(start_time) as order_date, COUNT(*) as order_count FROM orders GROUP BY DATE(start_time)'
                result = db.query(query)
                data = {'x': [row[0] for row in result], 'y': [row[1] for row in result]}
                x_label = '日期'
                y_label = '订单数量'
                title = '每天的订单数量'
                chart_type = 'line'

            else:
                data = {'x': [], 'y': []}
            return data, x_label, y_label, title, chart_type
        except Exception as e:
            print(f'Error: {e}')
        finally:
            lock.release()

def get_data_for_predict():
    lock.acquire()
    with Database() as db:
        try:
            query = '''
                SELECT DATE(start_time) AS order_date, COUNT(*) AS order_count 
                FROM orders 
                GROUP BY DATE(start_time) 
                ORDER BY order_date
            '''
            result = db.query(query)
            data = {'x': [row[0] for row in result], 'y': [row[1] for row in result]}
            return data
        except Exception as e:
            print(f'Error: {e}')
        finally:
            lock.release()

mock_now = datetime.now()