import sqlite3
import hashlib

conn = sqlite3.connect('datete.db')
cursor = conn.cursor()

cursor.execute('''CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,login UNIQUE,pasword_hash TEXT)''')

cursor.execute('''CREATE TABLE IF NOT EXISTS passwords(
id INTEGER PRIMARY KEY,user_id INTEGER,site TEXT,login TEXT,password TEXT)''')

cursor.execute("SELECT users.id,passwords.user_id FROM passwords JOIN users ON users.id = passwords.user_id")

def registr(login,password):
    print("WELCOME")
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
    hash_obj = hashlib.sha256(password.encode())
    hash_hex = hash_obj.hexdigest()
    cursor.execute("SELECT if FROM users WHERE login = ? AND password_hash = ?",(login,hash_hex))
    user = cursor.fetchone()
    conn.close()
    if user:
        print('sucsesseful log in')
        return user[0]
    else:
        print('bad login or password')
        return None
def add_password(user_id):
    login = input('login: ')
    site = input('site: ')
    password = input('password: ')
    cursor.execute("INSERT INTO passwords (user_id,site,login,password) VALUES (?,?,?,?)",(user_id,site,login,password))
    conn.commit()
    conn.close()
    print('password save!')
def show_passwords(user_id):
    cursor.execute("SELECT site,login,password FROM passwords WHERE user_id = ?",(user_id))
    rows = cursor.fetchall()
    conn.close()
    if not rows:
        print('none password')
    else:
        for site,login,password in rows:
            print(f'site: {site},login: {login},password: {password}')
def Main():
    while True:
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
                    print('1- add password')
                    print('2- show passwords')
                    print('3- leave from account')
                    print('4- exit')
                    choice2 = int(input('your choice: '))
                    if choice2 == 1:
                        add_password(user_id)
                    elif choice2 == 2:
                        show_passwords(user_id)
                    elif choice2 == 3:
                        break
                    elif choice2 == 4:
                        choice = 3
                        break
                    else:
                        return 'unknown choice!'
        elif choice == 3:
            break
        else: return 'Unknown choice!'

if __name__ == '__Main__':
    Main()



