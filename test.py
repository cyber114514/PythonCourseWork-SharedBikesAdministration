import pymysql
from datetime import datetime, timedelta
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
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    print(conn.get_server_info())
    cursor = conn.cursor()
    cursor.close()
    conn.close()

def query_for_bike(bikeid):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    message = 'select *from bike where bikeid='+str(bikeid)
    cursor.execute(message)
    result = cursor.fetchall()

    print(result)
    cursor.close()
    conn.close()

def query_for_position(uname):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    message = f"select position from user where username = '{uname}'"
    try:
        cursor.execute(message)
        result = cursor.fetchall()
        print(result[0][0])
        return result[0][0]
    except Exception as e:
        print(f'error:{e}')
    finally:
        cursor.close()
        conn.close()


def query_for_rent(bikeid, userid):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    userposition = 'select position,isrenting from user where userid=' + str(userid)
    BikeState = 'select rentable from bike where bikeid=' + str(bikeid)
    try:
        cursor.execute(userposition)
        result = cursor.fetchall()
        cursor.execute(BikeState)
        bs = cursor.fetchall()
        if bs[0][0] == 0:
            raise BikeError('Bike is being rented')
        if (result[0][0] != 'customer'):
            raise PositionError('wrong position')
        if (result[0][1] == True):
            raise IsRentingError("You're renting a bike!")
        renting = "UPDATE bike SET rentable = False, userid = {} WHERE bikeid = {}".format(userid, bikeid)
        cursor.execute(renting)
        updateuser = "update user set isrenting=True where userid=" + str(userid)
        cursor.execute(updateuser)
        start_time = get_mock_now().strftime('%Y-%m-%d %H:%M:%S')
        insert_order = "INSERT INTO orders (userid, bikeid, start_time) VALUES ({}, {}, '{}')".format(userid, bikeid,
                                                                                                      start_time)
        cursor.execute(insert_order)
        conn.commit()
        print('Successfully rented the bike!')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()


def query_for_return(bikeid, userid):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    userposition = 'SELECT position, isrenting, userid FROM user WHERE userid = {}'.format(userid)
    cursor.execute(userposition)
    result = cursor.fetchall()
    BikeState = 'SELECT rentable, userid FROM bike WHERE bikeid = {}'.format(bikeid)
    cursor.execute(BikeState)
    bs = cursor.fetchall()

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
        cursor.execute(returning)
        updateuser = "UPDATE user SET isrenting = False WHERE userid = {}".format(userid)
        cursor.execute(updateuser)

        # Calculate end time, total time, and total cost
        end_time = get_mock_now()
        cursor.execute(
            "SELECT start_time FROM orders WHERE userid = {} AND bikeid = {} ORDER BY orderid DESC LIMIT 1".format(
                userid, bikeid))
        start_time = cursor.fetchone()[0]
        total_time = (end_time - start_time).total_seconds() / 3600  # Convert seconds to hours
        total_time = max(total_time, 1)  # Minimum charge is for one hour
        total_cost = total_time * 1.5  # Charge rate per hour

        update_order = "UPDATE orders SET end_time = '{}', total_time = {}, total_cost = {} WHERE userid = {} AND bikeid = {} AND end_time IS NULL".format(
            end_time.strftime('%Y-%m-%d %H:%M:%S'), total_time, total_cost, userid, bikeid)
        cursor.execute(update_order)

        conn.commit()
        print('Successfully returned the bike!')
    except Exception as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()


def query_for_add(userid):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    userposition = 'SELECT position, isrenting,userid FROM user WHERE userid = {}'.format(userid)
    cursor.execute(userposition)
    result = cursor.fetchall()
    try:
        if result[0][0] != 'staff':
            raise PositionError('Wrong position')
        add = 'insert into bike(rentable) values(1)'
        cursor.execute(add)
        print('Successfully added the bike!')
        conn.commit()
    except Exception as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()


def delete_max_bike(userid):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')

    try:
        userposition = 'SELECT position, isrenting,userid FROM user WHERE userid = {}'.format(userid)
        cursor.execute(userposition)
        result = cursor.fetchall()
        if result[0][0] != 'staff':
            raise PositionError('Wrong position')
        max_bikeid_query = 'SELECT MAX(bikeid) FROM bike'
        cursor.execute(max_bikeid_query)
        max_bikeid = cursor.fetchone()[0]

        delete_query = f'DELETE FROM bike WHERE bikeid = {max_bikeid}'
        cursor.execute(delete_query)
        print('Successfully deleted the bike with the highest bikeid!')
        conn.commit()
    except Exception as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

def register(p,uname,pwd):
    if len(uname) == 0 or len(pwd) == 0:
        print("empty username or password!")
        return False
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    try:
        insert = f'insert into user(position,username,password) values("{p}","{uname}","{pwd}")'
        print(insert)
        cursor.execute(insert)
        conn.commit()
        print('Successfully registered!')
        return True
    except Exception as e:
        print(f'Error: {e}')
        return False
    finally:
        cursor.close()
        conn.close()


def login(uname,pwd):
    if len(uname) == 0 or len(pwd) == 0:
        print("empty username or password!")
        return
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    try:
        select = f'select *from user where username = "{uname}" and password = "{pwd}"'
        cursor.execute(select)
        result = cursor.fetchall()
        if result[0][0]:
            print('Successfully logged in!')
            conn.commit()
            return True
        else:
            print('Wrong username or password!')
            return False
    except Exception as e:
        print(f'Error: {e}')
        return False
    finally:
        cursor.close()
        conn.close()

def availablebikes():
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    query = f'select count(*) from bike where rentable = True'
    cursor.execute(query)
    result = cursor.fetchall()
    available_bikes = int(result[0][0])
    print(available_bikes)
    return available_bikes

def rent(username):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    try:
        select_user = f'select userid from user where username = "{username}"'
        cursor.execute(select_user)
        result1 = cursor.fetchall()
        print(result1[0][0])
        query = f'select bikeid from bike where rentable = True'
        cursor.execute(query)
        result2 = cursor.fetchall()
        print(result2[0][0])
        query_for_rent(result2[0][0], result1[0][0])
        return True
    except Exception as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

def returnbike(username):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    try:
        select_user = f'select userid from user where username = "{username}"'
        cursor.execute(select_user)
        result1 = cursor.fetchall()
        print(result1[0][0])
        query = f'select bikeid from bike where userid = "{result1[0][0]}"'
        cursor.execute(query)
        result2 = cursor.fetchall()
        print(result2[0][0])
        query_for_return(result2[0][0], result1[0][0])
        return True
    except Exception as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

def add_del(username,mode):
    conn = pymysql.connect(
        host='localhost',
        port=3306,
        user='root',
        password='123456',
        charset='utf8mb4'
    )
    cursor = conn.cursor()
    conn.select_db('bike')
    try:
        select_user = f'select userid from user where username = "{username}"'
        cursor.execute(select_user)
        result1 = cursor.fetchall()
        print(result1[0][0])
        if mode == 1:
            query_for_add(result1[0][0])
            return True
        elif mode == 2:
            delete_max_bike(result1[0][0])
            return True
    except Exception as e:
        print(f'Error: {e}')
    finally:
        cursor.close()
        conn.close()

def get_mock_now():
    return mock_now

mock_now = datetime.now()
