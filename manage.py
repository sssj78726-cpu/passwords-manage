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

class User:
    def __init__(self,login,password):
        self.login = login
        self.password = password
        
    def registr(self,login,password):
        print("WELCOME")
        conn = sqlite3.connect('datete.db')
        cursor = conn.cursor()
        self.hash_obj = hashlib.sha256(password.encode())
        self.hash_hex = self.hash_obj.hexdigest()
        try:
            cursor.execute("INSERT INTO users (login,password_hash) VALUES (?,?)",(login,self.hash_hex))
            conn.commit()
            print('secssuseful')
            return True
        except sqlite3.IntegrityError:
            print('login in base')
            return False
        finally:
            conn.close()

    def Login(self,password,login):
        conn = sqlite3.connect('datete.db')
        cursor = conn.cursor()
        self.hash_obj = hashlib.sha256(password.encode())
        self.hash_hex = self.hash_obj.hexdigest()
        cursor.execute("SELECT id FROM users WHERE login = ? AND password_hash = ?",(login,self.hash_hex))
        self.user = cursor.fetchone()
        conn.close()
        if self.user:
            print('sucsesseful log in')
            return self.user[0]
        else:
            print('bad login or password')
            return None

class Passwords:
    def __init__(self):
        self.site = ''
        self.login = ''
        self.password = None
    def add_password(self,user_id):
        conn = sqlite3.connect('datete.db')
        cursor = conn.cursor()
        self.login = input('login: ')
        self.site = input('site: ')
        self.password = input('password: ')
        cursor.execute("INSERT INTO passwords (user_id,site,login,password) VALUES (?,?,?,?)",(user_id,self.site,self.login,self.password))
        conn.commit()
        conn.close()
        print('password save!')
    def show_passwords(self,user_id):
        conn = sqlite3.connect('datete.db')
        cursor = conn.cursor()
        cursor.execute("SELECT site,login,password FROM passwords WHERE user_id = ?",(user_id,))
        self.rows = cursor.fetchall()
        conn.close()
        if not self.rows:
            print('none password')
        else:
            for self.site,self.login,self.password in self.rows:
                print(f'site: {self.site},login: {self.login},password: {self.password}')

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

def delet_habit(user_id):
    conn = sqlite3.connect('datete.db')
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id,name FROM habits WHERE user_id = ?",(user_id,))
        habits = cursor.fetchall()
        if not habits:
            print('you dont have habits!')
            conn.close()
            return
        else:
            for habit_id,name in habits:
                print(habit_id,name)
        try:
            habit_id = int(input('ID: '))
        except ValueError:
            print('error,print number!')
            conn.close()
            return
        if habit_id:
            cursor.execute("SELECT id FROM habits WHERE id = ? AND user_id = ?",(habit_id,user_id,))            
            if cursor.fetchone() is None:
                print('its not you or you dont have this habits')
                conn.close()
                return
            cursor.execute("DELETE FROM habits WHERE id = ?",(habit_id,))
            conn.commit()
            print('habit deleted')
        else :
            print('this habit not in base')
            conn.close()
            return
    except:
        return('error')
    finally:
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
        conn.close()
        return

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
                user = User(login,password)
                user.registr(login,password)
            elif choice == 2: 
                login = input('login: ')
                password = input('password: ')
                user = User(login,password)
                user_id = user.Login(password,login)
                if user_id:
                    while True:
                        print('1 -> passwords for site')
                        print('2 -> habits')
                        print('3 -> weather')
                        print('4 -> exit')
                        choice3 = int(input('choice: '))
                        if choice3 == 1:
                                while True:
                                    passwo = Passwords()
                                    passw = {
                                        1:lambda:passwo.add_password(user_id),
                                        2:lambda:passwo.show_passwords(user_id)
                                        }
                                    print('1 -> add password')
                                    print('2 -> show passwords')
                                    print('3 -> exit')
                                    choice2 = int(input('choice: '))
                                    if choice2 in passw:
                                        passw[choice2]()
                                    elif choice2 == 3:
                                        break
                                    else:
                                        return'unknown choice'
                        elif choice3 == 2:
                            while True:
                                habbit = {
                                    1:lambda:add_habits(user_id),
                                    2:lambda:mark_complete(user_id),
                                    3:lambda:show_habits(user_id),
                                    4:lambda:delet_habit(user_id)
                                    }
                                print('1 -> add habits')
                                print('2 -> mark a habits')
                                print('3 -> show habits')
                                print('4 -> delete habit')
                                print('5 -> exit')
                                choice2 = int(input('choice: '))
                                if choice2 in habbit:
                                    habbit[choice2]()
                                elif choice2 == 5:
                                    break
                                else:
                                    return 'unknown choice'
                        elif choice3 == 3:
                            while True:
                                weath ={
                                    1:lambda:get_weather(user_id),
                                    2:lambda:Show_weather(user_id)
                                    }

                                print('1 -> get weather')
                                print('2 -> show weather history')
                                print('3 -> exit')
                                choice2 = int(input('your choice: '))
                                if choice2 in weath:
                                    weath[choice2]()
                                elif choice2 == 3:
                                    break
                            else:
                                return 'unknown choice!'
                        elif choice3 == 4:
                            break
                        else:
                            return'unknown choice'
            elif choice == 3:
                break
            else: return 'Unknown choice!'
        except ValueError:
            print('choise number')
            return

if __name__ == '__main__':
    Main()
#RUSSIAN WEATHER!!!
