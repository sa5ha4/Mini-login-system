import tkinter as tk
import json
import os

root = tk.Tk()
root.title("Programme")
root.geometry('800x800')
root.resizable(False, False)

canvas = tk.Canvas(root, bg="#AAD6BE", height=800, width=800)
canvas.pack(fill="both", expand=True)


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

class Storage:
    def __init__(self, filename="users.json"):
        self.filename = filename

    def load_users(self):
        if not os.path.exists(self.filename):
            return []

        with open(self.filename, "r", encoding="utf-8") as f:
            data = json.load(f)

        return [User.from_dict(user) for user in data]

    def save_users(self, users):
        with open(self.filename, "w", encoding="utf-8") as f:
            json.dump([user.to_dict() for user in users], f, indent=4)

def sign_up():
    canvas.delete("all")
    canvas.create_text(400, 100, text="Reģistrēšana", font=("Comic Neue", 22), fill="#382B21")
    canvas.create_text(200, 200, text="Ievādi lietotājvārdu", font=("Comic Neue", 18), fill="#382B21")
    canvas.create_text(200, 350, text="Ievādi paroli", font=("Comic Neue", 18), fill="#382B21")
    global username
    global password
    username = tk.Entry(root, font=("Comic Neue", 18))
    password = tk.Entry(root, font=("Comic Neue", 18))

    canvas.create_window(200, 250, window=username)
    canvas.create_window(200, 400, window=password)
    enter_button = tk.Button(root, text="Reģistrēties", command=Storage(save_users))
    canvas.create_window(200, 200, window = enter_button)


def start():
    canvas.delete("all")
    canvas.create_text(400, 100, text="Pieslēgšana", font=("Comic Neue", 22), fill="#382B21")
    signup_button = tk.Button(root, text="Sign up", command=sign_up)
    #login_button = tk.Button(root, text="Log in", command=log_in)
    canvas.create_window(200, 200, window = signup_button)
    #canvas.create_window(300, 200, window = login_button)


start()

root.mainloop()
