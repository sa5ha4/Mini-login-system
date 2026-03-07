import tkinter as tk
import json
import os
import hashlib
import secrets
import time

root = tk.Tk()
root.title("Programma")
root.geometry('800x800')
root.resizable(False, False)

canvas = tk.Canvas(root, bg="#AFE1E3", height=800, width=800)
canvas.pack(fill="both", expand=True)

failed_attempts = 0
blocked_until = 0
lockout_until = 0
timer = None
current_user = None
risk = 0

short_password = False
nonexistent_user = False

class User:
    def __init__(self, username, salt, password_hash):
        self.username = username
        self.salt = salt
        self.password_hash = password_hash

    def to_dict(self):
        return {
            "username": self.username,
            "salt": self.salt,
            "password_hash": self.password_hash
        }

    @staticmethod
    def from_dict(data):
        return User(data["username"], data["salt"], data["password_hash"])

class Storage:
    def __init__(self, filename="users.json"):
        self.filename = filename

    def load_users(self):
        if not os.path.exists(self.filename):
            return []

        if os.path.getsize(self.filename) == 0:
            return []

        try:
            with open(self.filename, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError:
            return []

        return [User.from_dict(user) for user in data]

    def save_users(self, users):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([u.to_dict() for u in users], f, indent=4)

storage = Storage()

def hash_password(password, salt):
    return hashlib.sha256((salt + password).encode()).hexdigest()

def tick():
    global blocked_until
    global lockout_until
    global risk

    canvas.delete("timer")
    now = time.time()

    if now < blocked_until:
        remaining = int(blocked_until - now)
        canvas.create_text(400, 550, text=f"{remaining} s", font=("Comic Neue", 20), tags="timer")
        root.after(1000, tick)

    elif now < lockout_until:
        remaining = int(lockout_until - now)
        canvas.create_text(400, 550, text=f"{remaining} s", font=("Comic Neue", 20), tags="timer")
        root.after(1000, tick)
    
    else:
        if lockout_until != 0:
            return_button = tk.Button(root, text="Return", command=start)
            canvas.create_window(400, 600, window=return_button)
            lockout_until = 0
            risk = 0

def sign_up():
    canvas.delete("all")

    canvas.create_text(400, 100, text="Reģistrēšana", font=("Comic Neue", 25), fill="#382B21")

    canvas.create_text(250, 200, text="Lietotājvārds", font=("Comic Neue", 18))
    canvas.create_text(250, 300, text="Parole", font=("Comic Neue", 18))
    canvas.create_text(250, 400, text="Paroles pārbaude", font=("Comic Neue", 18))

    username_entry = tk.Entry(root, font=("Comic Neue", 18))
    password_entry = tk.Entry(root, show="*", font=("Comic Neue", 18))
    confirm_entry = tk.Entry(root, show="*", font=("Comic Neue", 18))

    canvas.create_window(500, 200, window=username_entry)
    canvas.create_window(500, 300, window=password_entry)
    canvas.create_window(500, 400, window=confirm_entry)

    message = canvas.create_text(400, 500, text="", font=("Comic Neue", 16), fill="#511F3D")

    def register():
        username = username_entry.get()
        password = password_entry.get()
        confirm = confirm_entry.get()
        global current_user
        global short_password
        global risk

        if password != confirm:
            canvas.itemconfig(message, text="Paroles nesakrīt")
            return

        users = storage.load_users()
        for u in users:
            if u.username == username:
                canvas.itemconfig(message, text="Lietotājs jau eksistē")
                return
        
        if len(password) < 6:
            risk += 25
            short_password = True

        salt = secrets.token_hex(16)
        password_hash = hash_password(password, salt)
        users.append(User(username, salt, password_hash))
        storage.save_users(users)

        current_user = username

        canvas.delete("all")
        canvas.create_text(400, 300, text="Reģistrācija veiksmīga!", font=("Comic Neue", 25), fill="#1F5130")
        info_button = tk.Button(root, text="Profile info", command=info)
        canvas.create_window(400, 400, window=info_button)
        logout_button = tk.Button(root, text="Logout", command=start)
        canvas.create_window(400, 500, window=logout_button)

    register_button = tk.Button(root, text="Reģistrēties", command=register)
    canvas.create_window(400, 450, window=register_button)

def log_in():
    global failed_attempts
    global blocked_until

    canvas.delete("all")

    canvas.create_text(400, 100, text="Pieslēgšanās", font=("Comic Neue", 25))

    canvas.create_text(250, 250, text="Lietotājvārds", font=("Comic Neue", 18))
    canvas.create_text(250, 350, text="Parole", font=("Comic Neue", 18))

    username_entry = tk.Entry(root, font=("Comic Neue", 18))
    password_entry = tk.Entry(root, show="*", font=("Comic Neue", 18))

    canvas.create_window(500, 250, window=username_entry)
    canvas.create_window(500, 350, window=password_entry)

    message = canvas.create_text(400, 500, text="", font=("Comic Neue", 16), fill="#511F3D")

    def login_check():
        global failed_attempts
        global blocked_until
        global current_user
        global nonexistent_user
        global lockout_until
        global risk

        username = username_entry.get()
        password = password_entry.get()
        users = storage.load_users()

        if time.time() < blocked_until:
            canvas.itemconfig(message, text="Konts īslaicīgi bloķēts")
            return

        for u in users:
            if u.username == username:
                if hash_password(password, u.salt) == u.password_hash:
                    if risk < 40:
                        canvas.delete("all")
                        canvas.create_text(400, 300, text="Pieslēgšana veiksmīga!", font=("Comic Neue", 25), fill="#1F5130")
                    
                        if hash_password(password, u.salt) == u.password_hash:
                            current_user = u.username

                        info_button = tk.Button(root, text="Profile info", command=info)
                        canvas.create_window(400, 400, window=info_button)
                        logout_button = tk.Button(root, text="Logout", command=start)
                        canvas.create_window(400, 500, window=logout_button)

                        failed_attempts = 0
                        return
                    else:
                        if 40 <= risk <= 79:
                            lockout_until = time.time() + 30
                        elif risk >= 80:
                            lockout_until = time.time() + 120
                        canvas.delete("all")
                        canvas.create_text(400, 250, text="Lockout", font=("Comic Neue", 25), fill="#511F3D")

                        if short_password == True and nonexistent_user == True:
                            canvas.create_text(400, 300, text=f"Risk: {risk}({failed_attempts} fails, īsa parole, nezināms lietotājs)", font=("Comic Neue", 22), fill="#511F3D")
                        elif short_password == True and nonexistent_user == False:
                            canvas.create_text(400, 300, text=f"Risk: {risk}({failed_attempts} fails, īsa parole)", font=("Comic Neue", 22), fill="#511F3D")
                        elif short_password == False and nonexistent_user == True:
                            canvas.create_text(400, 300, text=f"Risk: {risk}({failed_attempts} fails, nezināms lietotājs)", font=("Comic Neue", 22), fill="#511F3D")
                        else:
                            canvas.create_text(400, 300, text=f"Risk: {risk}({failed_attempts} fails)", font=("Comic Neue", 22), fill="#511F3D")

                    if lockout_until == 0:
                        return_button = tk.Button(root, text="Return", command=start)
                        canvas.create_window(600, 600, window=return_button)
                else:
                    nonexistent_user = True

        failed_attempts += 1

        if failed_attempts == 1:
            blocked_until = time.time() + 30
            risk += 20
            tick()

        elif failed_attempts >= 2:
            blocked_until = time.time() + 30* failed_attempts
            risk += 20*failed_attempts
            tick()

    login_button = tk.Button(root, text="Log in", command=login_check)
    canvas.create_window(400, 420, window=login_button)

def info():
    global current_user
    canvas.delete("all")
    canvas.create_text(400, 200, text=f"{current_user}", font=("Comic Neue", 25))
    canvas.create_rectangle(100, 100, 300, 300, fill="#DACAFF", outline="#302B56")
    logout_button = tk.Button(root, text="Logout", command=start)
    canvas.create_window(600, 600, window=logout_button)

def start():
    canvas.delete("all")
    canvas.create_text(400, 100, text="Sākums", font=("Comic Neue", 25))
    signup_button = tk.Button(root, text="Sign up", command=sign_up)
    login_button = tk.Button(root, text="Log in", command=log_in)
    canvas.create_window(400, 300, window=signup_button)
    canvas.create_window(400, 350, window=login_button)

start()

root.mainloop()
