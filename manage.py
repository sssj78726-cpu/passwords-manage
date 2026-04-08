import sqlite3
import hashlib
import datetime
import requests
from bs4 import BeautifulSoup


conn = sqlite3.connect('datete.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,login UNIQUE,password_hash TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS passwords(
id INTEGER PRIMARY KEY,user_id INTEGER,site TEXT,login TEXT,password TEXT)''')

cursor.execute("CREATE TABLE IF NOT EXISTS habits(id INTEGER PRIMARY KEY,user_id INTEGER,name TEXT,goal TEXT, created DATE)")

cursor.execute("CREATE TABLE IF NOT EXISTS habits_logs(id INTEGER PRIMARY KEY,habit_id INTEGER,date DATE,complete TEXT)")

cursor.execute("SELECT habits.id,habits_logs.habit_id FROM habits_logs JOIN habits ON habits.id = habits_logs.habit_id")

cursor.execute("SELECT users.id,passwords.user_id FROM passwords JOIN users ON users.id = passwords.user_id")

cursor.execute("SELECT users.id,habits.user_id FROM habits JOIN users ON users.id = habits.user_id")

cursor.execute("CREATE TABLE IF NOT EXISTS weather_hist (id INTEGER PRIMARY KEY,user_id INTEGER,feel TEXT,temp TEXT,city TEXT)")

cursor.execute("SELECT users.id, weather_hist.user_id FROM weather_hist JOIN users ON users.id = weather_hist.user_id ")
conn.commit()
conn.close()

def registr(login,password):
    print("WELCOME")
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    hash_obj = hashlib.sha256(password.encode())
    hash_hex = hash_obj.hexdigest()
    try:
        cursor.execute("INSERT INTO users (login,password_hash) VALUES (?,?)",(login,hash_hex))
        conn.commit()
        print('secssuseful')
        return True
    except sqlite3.IntegrityError:
        print('login in base')
        return False
    finally:
        conn.close()


def Login(password,login):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    hash_obj = hashlib.sha256(password.encode())
    hash_hex = hash_obj.hexdigest()
    cursor.execute("SELECT id FROM users WHERE login = ? AND password_hash = ?",(login,hash_hex))
    user = cursor.fetchone()
    conn.close()
    if user:
        print('sucsesseful log in')
        return user[0]
    else:
        print('bad login or password')
        return None

def add_password(user_id):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    login = input('login: ')
    site = input('site: ')
    password = input('password: ')
    cursor.execute("INSERT INTO passwords (user_id,site,login,password) VALUES (?,?,?,?)",(user_id,site,login,password))
    conn.commit()
    conn.close()
    print('password save!')

def show_passwords(user_id):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    cursor.execute("SELECT site,login,password FROM passwords WHERE user_id = ?",(user_id,))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print('none password')
    else:
        for site,login,password in rows:
            print(f'site: {site},login: {login},password: {password}')

def add_habits(user_id):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    name = input('print habits name: ')
    goal = input('yout goal: ')
    created = datetime.date.today().isoformat()
    cursor.execute("INSERT INTO habits (user_id,name,goal,created) VALUES (?,?,?,?)",(user_id,name,goal,created,))
    conn.commit()
    conn.close()

def mark_complete(user_id):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    date = datetime.date.today().isoformat()
    cursor.execute("SELECT id,name FROM habits WHERE user_id = ?",(user_id,))
    habits = cursor.fetchall()
    if not habits:
        print("you dont have habits!")
        conn.close()
        return
    print('your habits')
    for habit_id,name in habits:
        print(habit_id,name)
    try:
        habit_id = int(input('ID habit: '))
    except ValueError:
        print('error,print number')
        conn.close()
        return
    cursor.execute("SELECT complete FROM habits_logs WHERE habit_id = ? AND date = ?",(habit_id,date,))
    if cursor.fetchone():
        print('today you mark this habt!')
        conn.close()
        return
    cursor.execute("INSERT INTO habits_logs (habit_id,date,complete) VALUES (?,?,'Yes')",(habit_id,date,))
    conn.commit()
    conn.close()
    print('you mark habit!')

def show_habits(user_id):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name,goal FROM habits WHERE user_id =?",(user_id,))
    fst = cursor.fetchall()
    cursor.execute("SELECT complete FROM habits_logs")
    scnd = cursor.fetchall()
    for f in fst:
        print(f)
    for s in scnd:
        print(f'completed:{s}')
    conn.close()

def get_weather(user_id):

    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()

    city = input('city: ').lower()
    url = f'https://yandex.ru/pogoda/ru/{city}'
    if url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text,'html.parser')
        temp = soup.find('span', class_="AppFactTemperature_value__2qhsG")
        simvl = soup.find('span', class_="AppFactTemperature_sign__1MeN4 AppFactTemperature_attr__8pcxc")
        feel_today = soup.find('span', class_="AppFact_feels__base__bw86b")
        predict = soup.find('div' ,class_="AppFact_warning__second__BMdKC")
        full_temp =simvl.text+temp.text
        print('temperature:',full_temp)
        print(feel_today.text)
        print(predict.text)
        cursor.execute("INSERT INTO weather_hist (user_id,temp,city) VALUES (?,?,?)",(user_id,full_temp,city,))
        conn.commit()
        conn.close()
    else:
        print('unknown city!')

def Show_weather(user_id):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()

    cursor.execute("SELECT temp,city FROM weather_hist WHERE user_id = ?",(user_id,))
    weather = cursor.fetchall()
    if weather:
        for weat in weather:
            print(weat)
    else:
        print('history not detected')
    conn.close()

def Main():
    while True:
        try:
            print('1-registr')
            print('2- log in')
            print('3- exit')
            choice = int(input('your choice: '))
            if choice == 1:
                login = input('login: ')
                password = input('password: ')
                registr(login,password)
            elif choice == 2: 
                login = input('login: ')
                password = input('password: ')
                user_id = Login(password,login)
                if user_id:
                    while True:
                        print('1 -> add password')
                        print('2 -> show passwords')
                        print('3 -> leave from account')
                        print('4 -> exit')
                        print('5 -> add habits')
                        print('6 -> mark a habits')
                        print('7 -> show habits')
                        print('8 -> get weather')
                        print('9 -> show weather history')
                        actions ={
                            1:lambda:add_password(user_id),
                            2:lambda:show_passwords(user_id),
                            5:lambda:add_habits(user_id),
                            6:lambda:mark_complete(user_id),
                            7:lambda:show_habits(user_id),
                            8:lambda:get_weather(user_id),
                            9:lambda:Show_weather(user_id)
                                }
                        choice2 = int(input('your choice: '))
                        if choice2 in actions:
                            actions[choice2]()
                        elif choice2 == 3:
                            break
                        elif choice2 == 4:
                            choice == 3
                            break
                        else:
                            return 'unknown choice!'
            elif choice == 3:
                break
            else: return 'Unknown choice!'
        except ValueError:
            print('choise number')
            return

if __name__ == '__main__':
    Main()
#WEATHER IN RUSSIA


