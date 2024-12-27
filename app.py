import mysql.connector
import customtkinter as ctk
import openpyxl
import bcrypt
from datetime import datetime
from PIL import Image, ImageTk

# Database connection
def connect_db():
    return mysql.connector.connect(
        host="localhost",
        user="root",  # XAMPP default user
        password="",  # XAMPP default password (empty)
        database="hackerbot"
    )

# Load Q&A pairs from Excel file
def load_data(file_path):
    wb = openpyxl.load_workbook(file_path)
    sheet = wb.active
    qa_pairs = {}
    for row in sheet.iter_rows(min_row=2, values_only=True):
        question, answer = row
        if question:
            qa_pairs[question.lower()] = answer
    return qa_pairs

# Hash the password using bcrypt
def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

# Check if the password matches the stored hash
def check_password(hashed, password):
    return bcrypt.checkpw(password.encode('utf-8'), hashed)

class HackerbotApp(ctk.CTk):
    def __init__(self, username, qa_pairs):
        super().__init__()
        self.username = username
        self.qa_pairs = qa_pairs
        self.title(f"Hackerbot - {username}")
        self.geometry("1250x600+0+0")

        # Add logo to the parent window (it will be visible across screens)
        self.logo = Image.open("Hackerbot.png")
        self.logo = self.logo.resize((100, 100), Image.Resampling.LANCZOS)  # Resize using LANCZOS
        self.logo_img = ImageTk.PhotoImage(self.logo)

        # Create a frame for the logo at the top-center of the window
        self.logo_frame = ctk.CTkFrame(self, height=120)
        self.logo_frame.pack(fill="x", anchor="n")

        self.logo_label = ctk.CTkLabel(self.logo_frame, image=self.logo_img)
        self.logo_label.pack(pady=10)  # Add padding to prevent it from touching the top

        # Create a container frame for chat window elements
        self.chat_frame = ctk.CTkScrollableFrame(self, width=480, height=400)
        self.chat_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Adjust the position of the user input entry and send button
        self.user_input = ctk.CTkEntry(self, width=400)
        self.user_input.place(relx=0.5, rely=0.8, anchor="center")  # Shifted down to give space

        self.send_button = ctk.CTkButton(self, text="Send", command=self.send_message)
        self.send_button.place(relx=0.7, rely=0.8, anchor="center")  # Adjusted to match new position

    def send_message(self):
        user_text = self.user_input.get().strip()
        if user_text:
            self.display_message(self.username, user_text)  # Changed "You" to username
            self.store_message(self.username, user_text)
            response = self.qa_pairs.get(user_text.lower(), "Sorry, I don't understand that. I will improve my database as soon as possible InshaAllah.")
            self.display_message("Hackerbot", response)
            self.store_message("Hackerbot", response)
            self.user_input.delete(0, 'end')

    def display_message(self, sender, message):
        message_label = ctk.CTkLabel(self.chat_frame, text=f"{sender}: {message}", anchor='w', justify='left')
        message_label.pack(fill='x', pady=2)

    def store_message(self, sender, message):
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO chat_history (username, sender, message) VALUES (%s, %s, %s)", (self.username, sender, message))
        conn.commit()
        conn.close()

class AuthApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Hackerbot Login/Signup")
        self.geometry("1250x600+0+0")

        # Add logo to the parent window (it will be visible across screens)
        self.logo = Image.open("Hackerbot.png")
        self.logo = self.logo.resize((100, 100), Image.Resampling.LANCZOS)  # Resize using LANCZOS
        self.logo_img = ImageTk.PhotoImage(self.logo)

        # Create a frame for the logo at the top-center of the window
        self.logo_frame = ctk.CTkFrame(self, height=120)
        self.logo_frame.pack(fill="x", anchor="n")

        self.logo_label = ctk.CTkLabel(self.logo_frame, image=self.logo_img)
        self.logo_label.pack(pady=10)  # Add padding to prevent it from touching the top

        # Create a container frame for dynamic content (login/signup buttons)
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.place(relx=0.5, rely=0.5, anchor="center")

        # Main menu elements
        self.label = ctk.CTkLabel(self.main_frame, text="Choose an option:")
        self.label.grid(row=1, column=0, columnspan=3, pady=10)

        self.login_button = ctk.CTkButton(self.main_frame, text="Login", command=self.show_login)
        self.login_button.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.signup_button = ctk.CTkButton(self.main_frame, text="Signup", command=self.show_signup)
        self.signup_button.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

    def show_login(self):
        self.clear_screen()
        self.label = ctk.CTkLabel(self.main_frame, text="Login")
        self.label.grid(row=1, column=0, columnspan=3, pady=10)

        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username")
        self.username_entry.grid(row=2, column=0, columnspan=3, pady=5)

        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*")
        self.password_entry.grid(row=3, column=0, columnspan=3, pady=5)

        self.login_submit_button = ctk.CTkButton(self.main_frame, text="Login", command=self.login)
        self.login_submit_button.grid(row=4, column=0, columnspan=3, pady=5)

        self.back_button = ctk.CTkButton(self.main_frame, text="Back", command=self.show_main_menu)
        self.back_button.grid(row=5, column=0, columnspan=3, pady=5)

    def login(self):
        username = self.username_entry.get().strip()
        password = self.password_entry.get().strip()
        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("SELECT password FROM users WHERE username = %s", (username,))
        result = cursor.fetchone()
        conn.close()

        if result and check_password(result[0].encode('utf-8'), password):
            self.destroy()
            HackerbotApp(username, load_data("bot.xlsx")).mainloop()
        else:
            error_label = ctk.CTkLabel(self.main_frame, text="Incorrect username or password!", fg_color="red")
            error_label.grid(row=6, column=0, columnspan=3, pady=5)

    def show_signup(self):
        self.clear_screen()
        self.label = ctk.CTkLabel(self.main_frame, text="Signup")
        self.label.grid(row=1, column=0, columnspan=3, pady=10)

        self.username_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Username")
        self.username_entry.grid(row=2, column=0, columnspan=3, pady=5)

        self.fname_entry = ctk.CTkEntry(self.main_frame, placeholder_text="First Name")
        self.fname_entry.grid(row=3, column=0, columnspan=3, pady=5)

        self.lname_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Last Name")
        self.lname_entry.grid(row=4, column=0, columnspan=3, pady=5)

        self.email_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Email")
        self.email_entry.grid(row=5, column=0, columnspan=3, pady=5)

        self.password_entry = ctk.CTkEntry(self.main_frame, placeholder_text="Password", show="*")
        self.password_entry.grid(row=6, column=0, columnspan=3, pady=5)

        self.signup_submit_button = ctk.CTkButton(self.main_frame, text="Submit", command=self.signup)
        self.signup_submit_button.grid(row=7, column=0, columnspan=3, pady=5)

        self.back_button = ctk.CTkButton(self.main_frame, text="Back", command=self.show_main_menu)
        self.back_button.grid(row=8, column=0, columnspan=3, pady=5)

    def signup(self):
        username = self.username_entry.get().strip()
        fname = self.fname_entry.get().strip()
        lname = self.lname_entry.get().strip()
        email = self.email_entry.get().strip()
        password = self.password_entry.get().strip()

        hashed_password = hash_password(password)

        conn = connect_db()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO users (username, first_name, last_name, email, password) VALUES (%s, %s, %s, %s, %s)", 
                       (username, fname, lname, email, hashed_password))
        conn.commit()
        conn.close()

        self.show_main_menu()

    def show_main_menu(self):
        self.clear_screen()
        self.label = ctk.CTkLabel(self.main_frame, text="Choose an option:")
        self.label.grid(row=1, column=0, columnspan=3, pady=10)

        self.login_button = ctk.CTkButton(self.main_frame, text="Login", command=self.show_login)
        self.login_button.grid(row=2, column=0, padx=10, pady=5, sticky="nsew")

        self.signup_button = ctk.CTkButton(self.main_frame, text="Signup", command=self.show_signup)
        self.signup_button.grid(row=2, column=1, padx=10, pady=5, sticky="nsew")

    def clear_screen(self):
        for widget in self.main_frame.winfo_children():
            widget.destroy()

# Start the application
if __name__ == "__main__":
    app = AuthApp()
    app.mainloop()
