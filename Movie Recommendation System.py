from ast import literal_eval
from bs4 import BeautifulSoup
from collections import defaultdict
import csv
import hashlib
import math
import mysql.connector
import numpy as np
import os
import pandas as pd
import PIL.Image
import PIL.ImageTk
import random
from selenium import webdriver
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.metrics.pairwise import linear_kernel
import sqlite3
from stat import S_ISREG, ST_CTIME, ST_MODE
from surprise import Reader, Dataset, SVD, KNNBasic, NormalPredictor, accuracy
from surprise.model_selection import cross_validate, KFold
import time
from tkinter import *
from tkinter import messagebox
import tkinter.ttk as ttk
import urllib.parse
import urllib.request as request
import uuid
import webbrowser
import warnings
import sqlite3
warnings.simplefilter(action='ignore', category=FutureWarning)

class Images:
    def __init__(self, frame, width, height, row_no, column_no):
        """Takes dimension parameters so images can displayed on different fames in different places."""
        self.image_directory  ="Images"
        self.image_frame = frame
        self.width = width
        self.height = height
        self.row_no = row_no
        self.column_no = column_no
        
    def frame_image(self, photo):
        """Takes the photo as a parameter and displays it on the frame"""
        photo = photo.resize((self.width, self.height), PIL.Image.ANTIALIAS)
        photo = PIL.ImageTk.PhotoImage(photo)
        image_label = Label(self.image_frame, image = photo)
        image_label.image = photo
        image_label.grid(row = self.row_no, column = self.column_no)

    def scrape_image(self, URL, movie_name):
        """Scrapes the image from the given URL
              Called if the image for the required movie does not exist in the 'Images' folder."""
        movie_name = movie_name.lower()
        response = request.urlopen(URL)
        soup = BeautifulSoup(response, 'html.parser')
        if os.path.exists(self.image_directory+"\\"+movie_name+'.png') == False:        
            image_place = soup.find('div', {'class':'movie-thumbnail-wrap'})
            images = image_place.find('img')
            request.urlretrieve(images['data-src'], self.image_directory + "\\" + movie_name + '.png')

        image = PIL.Image.open(self.image_directory + "\\" + movie_name + ".png")
        self.frame_image(image)

    def get_image(self, movie_name):
        """Tries to find the image in the Images folder, if it doesn't exist, scrapes images from the internet"""
        movie_name = movie_name.lower()
        current_directory = self.image_directory + "\\" + movie_name + ".png"
        if os.path.isfile(current_directory) == True:
            image = PIL.Image.open(current_directory)
            self.frame_image(image)
        else:        
            movie_nameURL = re.sub(r"[^a-zA-Z0-9]+", ' ', movie_name)
            movie_nameURL = movie_nameURL.replace(" ", "_")
            URL = 'https://www.rottentomatoes.com/m/' + movie_nameURL
            try:
                self.scrape_image(URL, movie_name)
            except:
                try:
                    DRIVER_PATH = "C:\\Users\\viran\\Desktop\\Coursework\\Scraping\\chromedriver_win32\\chromedriver.exe"
                    driver = webdriver.Chrome(executable_path=DRIVER_PATH)
                    movie_nameURL = urllib.parse.quote(movie_name)
                    URL = 'https://www.rottentomatoes.com/search/?search=' + movie_nameURL
                    driver.minimize_window()
                    driver.get(URL)
                    time.sleep(2) 
                    content = driver.page_source.encode('utf-8').strip()
                    soup = BeautifulSoup(content, 'html.parser')
                    movie_name = soup.find_all('', {'class':'search__results-item-info-top'})[0]
                    movie_name = movie_name.find_all('a', href=True)[0]
                    movie_name = movie_name.string
                    if "'"  in movie_name:
                        movie_name = movie_name.replace("'", "")
                    movie_nameURL = re.sub(r"[^a-zA-Z0-9]+", ' ', movie_name)
                    movie_nameURL = movie_nameURL.replace(" ", "_")
                    URL = 'https://www.rottentomatoes.com/m/' + movie_nameURL
                    driver.close()
                    self.scrape_image(URL, movie_name)
                except:
                    image_label = Label(self.image_frame, text = "No Image", font = "Calibri 11")
                    image_label.grid(row = self.row_no, column = self.column_no, padx = 10)

    def random_image(self):
        """Finds a random image from the 'Images' folder"""
        image = random.choice(os.listdir(self.image_directory))
        image = self.image_directory + "\\" + image
        image = PIL.Image.open(image)
        self.frame_image(image)

    def update_directory(self):
        """Updates folder by deleting images if there are more than 100 in the folder"""
        number_images = len([image for image in os.listdir(self.image_directory) if os.path.isfile(os.path.join(self.image_directory, image))])
        if number_images > 100:
            all_images = (os.path.join(self.image_directory, image) for image in os.listdir(self.image_directory))
            all_images = ((os.stat(path), path) for path in all_images)
            all_images = ((stat[ST_CTIME], path) for stat, path in all_images if S_ISREG(stat[ST_MODE]))
            all_images = sorted(all_images)
            for image in range(10):
                os.remove(all_images[image][1])

        for image_name in os.listdir(self.image_directory):
            if image_name.endswith('.png') != True:
                os.remove(self.image_directory + '\\' + image_name)
                time.sleep(2)

    def __repr__(self):
        return "Class used to find images and display them to the window"

class Database:
    def __init__ (self):
        """Connects to the database with saved data"""
        try:
            self.connection = sqlite3.connect('RecommendationDatabase.db')
            self.cursor = self.connection.cursor()
        except:
            messagebox.showerror("Error!",  "Something went wrong")

    def run_select(self, sql_command):
        """Run's a given select statement"""
        try:
            self.cursor.execute(sql_command)
            results = self.cursor.fetchall()
            return results
        except:
            messagebox.showerror("Error!",  "Something went wrong")
        return results

    def run_update(self, sql_command):
        """Run's a given update statement"""
        try:
            self.cursor.execute(sql_command)
            self.connection.commit()
            return 'Successful'
        except:
            messagebox.showerror("Error!",  "Something went wrong")
            
        return 'Successful'

    def close(self):
        """Closes the connection with the database"""
        self.cursor.close()
        self.connection.close()

    def __repr__(self):
        return "Used to update or select data in the databse."

class Template:
    def __init__(self, master, header, num_rows, num_columns, logged_in, picture):
        """Contains common attributes which will be shared by every frame"""
        self.master = master
        self.master.option_add('*Font', 'Calibri 14')
        self.master.option_add('*Background', '#90E3F7')
        self.master.option_add('*Foreground', 'black')
        self.master.option_add('*Label.Font', 'Calibri 14')
        self.master.option_add('*Label.Borderwidth', '1')
        self.master.option_add('*Label.Relief', 'solid')
        self.master.config(borderwidth = 20, background = "#D4F2F9")
        
        self.canvas = Canvas(self.master)
        self.scrollbar = ttk.Scrollbar(self.master, orient = "vertical", command = self.canvas.yview)
        self.main_frame = Frame(self.master)
        self.main_frame.config(padx = 10, pady = 10)
        self.main_frame.bind("<Configure>", lambda event: self.canvas.configure(scrollregion = self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window = self.main_frame, anchor = "w")
        self.canvas.configure(yscrollcommand = self.scrollbar.set)
        self.canvas.pack(side = "left", fill = "both", expand = True)

        self.v_title = StringVar()
        self.v_title.set(header)
        self.l_title = Label(self.main_frame)
        self.l_title.config(textvariable = self.v_title, font = "Calibri 18 bold", background = "#2D64A5", foreground = "white")
        self.l_title.grid(row = 0, column = 0, columnspan = num_columns+2, sticky = "ew")
                                            
        if picture == True:
            self.image_frame = Frame(self.main_frame)
            self.image_frame.config(padx = 10, pady = 10)
            self.image_frame.grid(row = 1, column = num_columns+1, rowspan = num_rows)

            image_class = Images(self.image_frame, 200, 300, 0, 0)
            image_class.random_image()
            
        for i in range(num_rows):
            self.main_frame.grid_rowconfigure(i, pad = 15)
        for i in range(num_columns+1):
            self.main_frame.grid_columnconfigure(i, pad = 15)

        if logged_in == True:
            self.menubar = Menu(self.main_frame, background = "white", foreground = "black", activebackground = "black", activeforeground = "white")
            self.master.config(menu = self.menubar)
            self.fileMenu = Menu(self.menubar, background = "white", foreground = "black", activebackground = "black", activeforeground = "white")
            frames = [MainMenu, RecommendedFilm, RecommendedYou, MovieDetails, MyMovies]
            frames_list = ["Main Menu", "Recommended by Film", "Recommended For You", "Movie Details", "My Movies"]
            for option in range(len(frames_list)):
               self.fileMenu.add_command(label = frames_list[option], command = lambda frame = frames[option]: self.switch_frame(frame))
            self.fileMenu.add_separator()
            self.fileMenu.add_command(label = "Exit", command = self.log_out)
            self.menubar.add_cascade(label = "Menu", menu = self.fileMenu)
        
    def switch_frame(self, frame):
        '''Used to switch between the different frames of the program.'''
        self.canvas.forget()
        self.scrollbar.forget()
        frame(self.master)

    def open_dataset(self):
        """Opens the movie dataset and calculates a score column"""
        self.credit_dataset = pd.read_csv("Movie Metadata\CreditData.csv")
        self.movie_dataset = pd.read_csv("Movie Metadata\MovieData.csv")
        self.credit_dataset.columns = ["id", "tittle", "cast", "crew"]
        self.movie_dataset = self.movie_dataset.merge(self.credit_dataset, on = "id")

        features = ['cast', 'crew', 'keywords', 'genres', 'production_companies']
        for feature in features:
            self.movie_dataset[feature] = self.movie_dataset[feature].apply(literal_eval)

        mean_vote = self.movie_dataset['vote_average'].mean()
        minimum_votes = self.movie_dataset['vote_count'].quantile(0.95)
        minimum_votes = 1
        qualified_movies = self.movie_dataset.copy().loc[self.movie_dataset['vote_count'] >= minimum_votes]
        number_votes = qualified_movies['vote_count']
        average_rating = qualified_movies['vote_average']
        imdb_rating = (number_votes / (number_votes + minimum_votes) * average_rating) + (minimum_votes / (number_votes + minimum_votes) * mean_vote)
        self.movie_dataset['score'] = imdb_rating

    def blank_line(self, frame, row_no, column_no, rows_covered, columns_covered, sticky_val, pady_val):
        """Creates a black line on the given frame, used to create tables to neatly present data"""
        l_blank = Label(frame, text = " ", font = "Calibri 5")
        l_blank.configure(background = "black", foreground = "black")
        l_blank.grid(row = row_no, column = column_no, rowspan = rows_covered, columnspan = columns_covered, sticky = sticky_val, pady = pady_val)

    def log_out(self):
        """Logs out the logged in user and closes the program"""
        database = Database()
        sql_command = "UPDATE Users SET logged_in = 0"
        results = database.run_update(sql_command)
        database.close()
        self.master.destroy()

class LogIn(Template):
    def __init__(self, master):
        """Allows the user to log in, create an account or reset their password"""
        super().__init__(master, 'Log In', 4, 1, False, True)
        self.master = master
        self.master.title('Log In')
        self.master.geometry('650x420+25+25')

        l_Username = Label(self.main_frame, text = "Username", width = 13)
        l_Username.grid(row = 1, column = 0)
        e_Username = Entry(self.main_frame, background = "white", width = 15)
        e_Username.grid(row = 1, column = 1)
        
        l_Password = Label(self.main_frame, text = "Password", width = 13)
        l_Password.grid(row = 2, column = 0)
        e_Password = Entry(self.main_frame, background = "white", show = "*", width = 15)
        e_Password.grid(row = 2, column = 1)

        b_LogIn = Button(self.main_frame, text = "Log In", background = "white", width = 15)
        b_LogIn["command"] = lambda username = e_Username, password = e_Password: self.log_in(username, password)
        b_LogIn.grid(row = 3, column = 0, columnspan = 2)

        b_Register = Button(self.main_frame, text = "Register", background = "white", width = 15)
        b_Register["command"] = lambda frame = RegisterPage1: self.switch_frame(frame)
        b_Register.grid(row = 4, column = 0)

        b_ResetPassword = Button(self.main_frame, text = "Reset Password", background = "white", width = 15)
        b_ResetPassword["command"] = lambda frame = ResetPassword, username = e_Username: self.reset_password(frame, username)
        b_ResetPassword.grid(row = 4, column = 1)

    def log_in(self, username, password):
        """Checks whether the users username and password is accurate"""
        log_in = True
        username = username.get()
        password = password.get()
        if username == "" or password == "":
            messagebox.showerror("Error!", "Please enter your username and password!")
            log_in = False
        else:
            database = Database()
            sql_command = "SELECT PasswordSalt, HashedPassword FROM Users WHERE Username = '{}'".format(username)            
            results = database.run_select(sql_command)

        if len(results) == 0 and log_in == True:
            messagebox.showerror("Error!", "Username doesn't exist!")
            log_in = False
        else:
            hash_function = hashlib.sha512()
            hash_function.update(('%s%s' % (results[0][0], password)).encode('utf-8'))
            hashed_entry = hash_function.hexdigest()
            if results[0][1] == hashed_entry:
                log_in = True
            else:
                messagebox.showerror("Error!", "Username or Password is incorrect!")
                log_in = False

        if log_in == True:
            sql_command = "UPDATE Users SET logged_in = 1 WHERE Username = '{}'".format(username)
            results = database.run_update(sql_command)
            database.close()
            self.switch_frame(MainMenu)
        elif log_in == False:
            database.close()
            self.switch_frame(LogIn)

    def reset_password(self, frame, username):
        """Checks whether the entered username exists  in the database"""
        username = username.get()
        valid_reset = True
        if username == "":
            valid_reset = False
            messagebox.showerror("Error!", "Please enter your username")
        else:
            database = Database()
            sql_command = "SELECT Username FROM Users WHERE Username = '{}'".format(username)
            results = database.run_select(sql_command)
            database.close()

        if results == [] and valid_reset == True:
            messagebox.showerror("Error!", "Username doesn't exist!")
            valid_reset = False
        
        if valid_reset == True:
            self.canvas.forget()
            self.scrollbar.forget()
            frame(self.master, username)

class RegisterPage1(Template):
    """Allows the user to enter their detalis to create an account"""
    def __init__(self, master):
        super().__init__(master, 'Register', 8, 1, False, True)
        self.master = master
        self.master.title('Register')
        self.master.geometry('900x460+25+25')

        labels = {}
        entry = {}
        current_column = 0
        current_row = 1
        widget_names = ["First Name", "Surname", "Username", "Age", "Email Address", "Password", "Re-enter Password"]
        for i in range(len(widget_names)):
            labels[widget_names[i]] = Label(self.main_frame, text = widget_names[i], width = 20)
            labels[widget_names[i]].grid(row = current_row, column = current_column)
            current_column += 1

            entry[widget_names[i]] = Entry(self.main_frame, background = "white", width = 35)
            entry[widget_names[i]].grid(row = current_row, column = current_column)
            if widget_names[i] == "Password" or widget_names[i] == "Re-enter Password":
                entry[widget_names[i]].configure(show = "*")
            current_column = 0
            current_row += 1

        entry["Age"].configure(width = 6)
        b_Continue = Button(self.main_frame, text = "Continue", background = "white", width = 20)
        b_Continue["command"] = lambda entry = entry, widget_names = widget_names, frame = RegisterPage2: self.ContinueRegister(entry, widget_names, frame)
        b_Continue.grid(row = 8, column = 1)

    def ContinueRegister(self, entry, widget_names, frame):
        """Checks whether user's input is correctly formatted and whether the username is entered accurately"""
        accurate_entry = True
        new_entry = []
        for widget in range(len(entry)):
            current_entry = entry[widget_names[widget]].get()
            if current_entry == "":
                accurate_entry = False
            new_entry.append(entry[widget_names[widget]].get())
            
        if new_entry[5] != new_entry[6]:
            accurate_entry = False
    
        input_lengths = [10, 15, 20, 3, 40]
        for attribute in range(5):
            if len(str(new_entry[attribute])) > input_lengths[attribute]:
                accurate_entry = False

        database = Database()
        sql_command = "SELECT Username FROM Users WHERE Username = '{}'".format(new_entry[2])
        results = database.run_select(sql_command)
        database.close()

        if results != []:
            messagebox.showerror("Error!", "Username is already taken!")
            accurate_entry = False

        if accurate_entry == False:
            messagebox.showerror("Error!", "Invalid Data!")
            self.switch_frame(RegisterPage1)
        elif accurate_entry == True:            
            self.canvas.forget()
            self.scrollbar.forget()
            frame(self.master, entry, widget_names)

class RegisterPage2(Template):
    def __init__(self, master, entry, widget_names):
        """Allows user to answer security questions""" 
        super().__init__(master, 'Register', 9, 2, False, True)
        self.master = master
        self.master.title('Register')
        self.master.geometry('900x460+25+25')
        
        self.drop_options = ["Select a Question:",
                        "Where were you born?",
                        "What was the name of your first school?",
                        "What is the name of your favourite author?",
                        "What is the name of your favourite film?",
                        "What is the name of your favourite book?",
                        "What is the name of your favourite childhood friend?"]
        self.drop_entry = [StringVar(self.main_frame), StringVar(self.main_frame), StringVar(self.main_frame)]
        
        drop_menus = {}
        labels = {}
        label_text = [StringVar(self.main_frame), StringVar(self.main_frame), StringVar(self.main_frame)]  
        current_row = 1
        current_column = 0
        for i in range(3):
            label_text[i].set("Security Question " + str(i+1))
            self.drop_entry[i].set(self.drop_options[0])
            labels["Security Question #", i+1] = Label(self.main_frame, textvariable = label_text[i], width = 20)
            labels["Security Question #", i+1].grid(row = current_row, column = current_column)
            widget_names.append(("Security Question #", i+1))
            current_column += 1
            drop_menus["Security Question #", i+1] = OptionMenu(self.main_frame, self.drop_entry[i], *self.drop_options)
            drop_menus["Security Question #", i+1].configure(background = "white")
            self.drop_entry[i].trace('w', self.on_dropdown)
            drop_menus["Security Question #", i+1].grid(row = current_row, column = current_column)
            current_column = 0
            current_row += 1
            answer_label = Label(self.main_frame, text = "Answer:", width = 20)
            answer_label.grid(row = current_row, column = current_column)
            current_column += 1
            entry["Security Question #", i+1] = Entry(self.main_frame, background = "white", width = 35)
            entry["Security Question #", i+1].grid(row = current_row, column = current_column, padx = 10)
            current_column = 0
            current_row += 2
            
        b_Finish = Button(self.main_frame, text = "Register", background = "white", width = 20)
        b_Finish["command"] = lambda entry = entry, widget_names = widget_names, security_questions = self.drop_entry: self.CompleteRegister(entry, widget_names, security_questions)
        b_Finish.grid(row = current_row, column = 1)

    def on_dropdown(self, *args):
        """Shows the option the user has selected and checks whether the user has selected the same security questions multiple times"""
        temp_list = []
        same_item = False
        selected_items = True
        for item in self.drop_entry:
            temp_list.append(item.get())
            if temp_list.count(item.get()) > 1:
                same_item = True
            if item.get() == self.drop_options[0]:
                selected_items = False

        if selected_items == True and same_item == True:
            messagebox.showerror("Error!", "Please do not select the same security question!")
            for item in self.drop_entry:
                item.set(self.drop_options[0]) 

    def CompleteRegister(self, entry, widget_names, security_questions):
        """Checks whether the user's input is accurate and adds their information to the database."""
        accurate_entry = True
        new_entry = []

        salt = uuid.uuid4().hex
        password = entry["Password"].get()
        hash_function = hashlib.sha512()
        hash_function.update(('%s%s' % (salt, password)).encode('utf-8'))
        hashed_password = hash_function.hexdigest()
        
        for widget in range(len(entry)):
            current_entry = entry[widget_names[widget]].get()
            if current_entry == "":
                accurate_entry = False
                messagebox.showerror("Error!", "Please enter something!")
            new_entry.append(entry[widget_names[widget]].get())
        entry = new_entry
        
        new_questions = []
        for question in range(len(security_questions)):
            new_questions.append(security_questions[question].get())
        security_questions = new_questions

        indexes = []
        for user_question in security_questions:
            for premade_question in range(len(self.drop_options)):
                if user_question == self.drop_options[premade_question]:
                    indexes.append(premade_question)
        security_questions = indexes
        
        user_information = entry[0:5]
        user_information.append(salt)
        user_information.append(hashed_password)
        user_information.append(1)
        security_answers = entry[7:10]

        salts = []
        for i in range(len(security_answers)):
            salts.append(uuid.uuid4().hex)
            hash_function = hashlib.sha512()
            hash_function.update(('%s%s' % (salts[i], security_answers[i])).encode('utf-8'))
            security_answers[i] = hash_function.hexdigest()

        if accurate_entry == True:
            database = Database()
            user_id = database.run_select('SELECT COUNT(*) FROM Users')
            user_id = user_id[0][0]
            sql_command = """INSERT INTO Users VALUES ({}, "{}", "{}", "{}", {}, "{}", "{}", "{}", "{}");""".format(user_id, *user_information)
            status = database.run_update(sql_command)
            
            security_id = database.run_select('SELECT COUNT(*) FROM SecurityQuestions')
            security_id = security_id[0][0]            
            security_id += 1
            for question in range(3):
                sql_command = """INSERT INTO SecurityQuestions VALUES ({}, {}, {}, "{}", "{}");""".format(security_id, user_id, int(security_questions[question]), salts[question], security_answers[question])
                status = database.run_update(sql_command)
                security_id += 1
            database.close()
            self.switch_frame(MainMenu)
        elif accurate_entry == False:
            messagebox.showerror("Error!", "Invalid Data!")
            self.switch_frame(LogIn)
        
class ResetPassword(Template):
    def __init__(self, master, username):
        """Allows the user to answer their security questions and reset their password"""
        super().__init__(master, 'Reset Password', 14, 2, False, True)
        self.master = master
        self.master.title('Main Menu')
        self.master.geometry('600x650+25+25')

        l_information = Label(self.main_frame, text = "Please answer your premade security questions:", font = "Calibri 10")
        l_information.grid(row = 1, column = 0)

        entry = {}
        labels = {}
        label_text = [StringVar(), StringVar(), StringVar()]
        database = Database()
        sql_command = "SELECT UserID FROM Users WHERE Username = '{}'".format(username)
        user_id = database.run_select(sql_command)
        user_id = user_id[0][0]
        sql_command = "SELECT Question FROM SecurityQuestions WHERE UserID = '{}'".format(user_id)
        security_questions = database.run_select(sql_command)
        database.close()
        question_options = ["Select a Question:",
                        "Where were you born?",
                        "What was the name of your first school?",
                        "What is the name of your favourite author?",
                        "What is the name of your favourite film?",
                        "What is the name of your favourite book?",
                        "What is the name of your favourite childhood friend?"]
        security_questions = [question_options[security_questions[i][0]] for i in range(len(security_questions))]

        current_row = 2
        for i in range(3):
            label_text[i].set(security_questions[i])
            labels["Security Question #", i+1] = Label(self.main_frame, textvariable = label_text[i], font = "Calibri 12")
            labels["Security Question #", i+1].grid(row = current_row, column = 0)
            current_row += 1
            entry["Security Question #", i+1] = Entry(self.main_frame, background = "white", width = 20)
            entry["Security Question #", i+1].grid(row = current_row, column = 0)
            current_row += 1

        l_newpassword = Label(self.main_frame, text = "New Password:", width = 20, font = "Calibri 12")
        l_newpassword.grid(row = 9, column = 0)
        entry["New Password"] = Entry(self.main_frame, background = "white", width = 20, show = "*")
        entry["New Password"].grid(row = 10, column = 0)

        l_confirmpassword = Label(self.main_frame, text = "Confirm Password:", width = 20, font = "Calibri 12")
        l_confirmpassword.grid(row = 11, column = 0)
        entry["Confirm Password"] = Entry(self.main_frame, background = "white", width = 20, show = "*")
        entry["Confirm Password"].grid(row = 12, column = 0)

        b_Finish = Button(self.main_frame, text = "Finish", background = "white", width = 20)
        b_Finish["command"] = lambda user_input = entry: self.FinishReset(user_input, user_id)
        b_Finish.grid(row = 13, column = 0)

    def FinishReset(self, user_input, user_id):
        """Checks whether the user has answered their security questions correctly before resetting their password"""
        valid_reset = True

        for entry in user_input:
            if len(entry) == 0:
                valid_reset = False

        if user_input["New Password"].get() != user_input["Confirm Password"].get() and valid_reset == True:
            valid_reset = False
        else:
            database = Database()
            sql_command = "SELECT AnswerSalt, HashedAnswer FROM SecurityQuestions WHERE UserID = {}".format(user_id) #change this
            results = database.run_select(sql_command)
            database.close()
            for i in range(len(results)):
                hash_function = hashlib.sha512()
                hash_function.update(('%s%s' % (results[i][0], user_input["Security Question #",i+1].get())).encode('utf-8'))
                hashed_entry = hash_function.hexdigest()
                if hashed_entry != results[i][1]:
                    valid_reset = False     

        if valid_reset == True:
            database = Database()
            salt = uuid.uuid4().hex
            password = user_input["New Password"].get()
            hash_function = hashlib.sha512()
            hash_function.update(('%s%s' % (salt, password)).encode('utf-8'))
            hashed_password = hash_function.hexdigest()
            
            sql_command =  "Update Users SET PasswordSalt = '{}', HashedPassword = '{}', logged_in = 1 WHERE UserID = {}".format(salt, hashed_password, user_id)
            result = database.run_update(sql_command)
            database.close()
            messagebox.showinfo("Success!", "Password has been updated!") 
            self.switch_frame(MainMenu)
        elif valid_reset == False:
            messagebox.showerror("Error!", "Reset unsuccessful!")
            self.switch_frame(LogIn)

class MainMenu(Template):
    def __init__(self, master):
        """Allows the user to navigate the program easily"""
        super().__init__(master, 'Main Menu', 6, 1, True, True)
        self.master = master
        self.master.title('Main Menu')
        self.master.geometry('500x430+25+25')

        page_names = ["Recommended by Film", "Recommended For You", "Movie Details", "My Movies"]
        pages = [RecommendedFilm, RecommendedYou, MovieDetails, MyMovies]
        buttons = {}
        for i in range(len(page_names)):
            buttons[page_names[i]] = Button(self.main_frame, text = page_names[i], background = "white", width = 20)
            buttons[page_names[i]]["command"] = lambda frame = pages[i]: self.switch_frame(frame)
            buttons[page_names[i]].grid(row = i+1, column = 0)
        buttons["Exit"] = Button(self.main_frame, text = "Exit", background = "white", width = 20)
        buttons["Exit"]["command"] = self.log_out
        buttons["Exit"].grid(row = i+2, column = 0)

class SeveralMovies(Template):
    def __init__(self, master, old_frame, movie_title, dataset):
        """Creates a table which will display multiple films based on the contents of the parameter 'dataset'"""
        super().__init__(master, movie_title, 15, 7, True, False)
        self.master = master
        self.master.title('Main Menu')
        self.master.geometry('1050x800+25+25')
        self.v_title.set(movie_title)
        self.scrollbar.pack(side = "right", fill = "y")

        column_text = ["Title", "Genre", "Rating", "Description", "Release Date", "Image"]
        column_counter = 0
        for title in range(len(column_text)):
            self.blank_line(self.main_frame, 4, column_counter, 11, 1, "nsw", 10)
            l_header = Label(self.main_frame, text = column_text[title], font = "Calibri 14")
            l_header.configure(background = "black", foreground = "white")
            if column_text[title] == "Genre":
                l_header.grid(row = 4, column = column_counter, columnspan = 3, sticky = "we")
                column_counter += 3
            else:
                l_header.grid(row = 4, column = column_counter, sticky = "we")
                column_counter += 1
        self.blank_line(self.main_frame, 4, column_counter+1, 11, 1, "nsw", 8)

        self.SetTable()
        self.index = 0
        self.page_no = StringVar()
        self.title_text = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        self.genre_text = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        self.rating_text = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        self.date_text = [StringVar(), StringVar(), StringVar(), StringVar(), StringVar()]
        self.genre_index = []

        self.UpdateTable(dataset)

        b_Next = Button(self.main_frame, text = "Next", background = "white")
        b_Next["command"] = lambda increase_by = +1, data_to_view = self.dataview: self.ChangeFilms(increase_by, data_to_view)
        b_Next.grid(row = 15, column = 7)

        b_PreviousFrame = Button(self.main_frame, text = "Previous Page", background = "white")
        b_PreviousFrame["command"] = lambda frame = old_frame: self.switch_frame(old_frame)
        b_PreviousFrame.grid(row = 15, column = 3, columnspan = 2)

        b_Back = Button(self.main_frame, text = "Back", background = "white")
        b_Back["command"] = lambda increase_by = -1, data_to_view = self.dataview: self.ChangeFilms(increase_by, data_to_view)
        b_Back.grid(row = 15, column = 0, sticky = "w")

    def SetTable(self):
        """Removes the contents of the table"""
        self.descriptions = {}
        self.description_buttons = {}
        self.previous_buttons = {}
        self.next_buttons = {}
        self.movie_genres = [[], [], [], [], []]
        self.genre_index = []

    def UpdateTable(self, data_to_view):
        """Updates the contents of the table"""
        data_to_view = data_to_view[['id', 'title', 'genres', 'score', 'overview', 'release_date']]
        self.dataview = data_to_view.copy()
        no_chunks = math.ceil(len(data_to_view)/5)
        data_to_view = np.array_split(data_to_view, no_chunks)
        data_to_view = data_to_view[self.index]
        self.current_film = 0
        row_no = 5
        while True:
            title = data_to_view.iat[self.current_film, 1]
            self.title_text[self.current_film].set(title)
            genres = data_to_view.iat[self.current_film, 2]
            for current_genre in range(len(genres)):
                try:
                    new_genre = genres[current_genre]["name"]
                    self.movie_genres[self.current_film].append(new_genre)
                except:
                    self.movie_genres[self.current_film].append(genres[current_genre])
            self.movie_genres[self.current_film].sort()
            no_genres = len(self.movie_genres[self.current_film])
            rating = data_to_view.iat[self.current_film, 3]
            rating = round(rating, 2)
            self.rating_text[self.current_film].set(rating)
            release_date = data_to_view.iat[self.current_film, 5]
            self.date_text[self.current_film].set(release_date)

            l_title = Label(self.main_frame, textvariable = self.title_text[self.current_film], font = "Calibri 14")
            l_title.grid(row = row_no, column = 0)
            self.genre_index.append(0)            
            self.genre_text[self.current_film].set(self.movie_genres[self.current_film][self.genre_index[self.current_film]].capitalize())
            if len(self.movie_genres[self.current_film]) > 1:
                self.previous_buttons[title] = Button(self.main_frame, text = "<", background = "white", font = "Calibri 10")
                self.previous_buttons[title]["command"] = lambda film_index = self.current_film, increase_by = -1: self.UpdateGenres(film_index, increase_by)
                self.previous_buttons[title].grid(row = row_no, column = 1, padx = 10)
                self.next_buttons[title] = Button(self.main_frame, text = ">", background = "white", font = "Calibri 10")
                self.next_buttons[title]["command"] = lambda film_index = self.current_film, increase_by = +1: self.UpdateGenres(film_index, increase_by)
                self.next_buttons[title].grid(row = row_no, column = 3, padx = 10)
            l_genre = Label(self.main_frame, textvariable = self.genre_text[self.current_film], font = "Calibri 14")
            l_genre.grid(row = row_no, column = 2)
            l_rating = Label(self.main_frame, textvariable = self.rating_text[self.current_film], font = "Calibri 14")
            l_rating.grid(row = row_no, column = 4)
            self.descriptions[title] = data_to_view.iat[self.current_film, 4]
            self.description_buttons[title] = Button(self.main_frame, text = "Expand", background = "white", width = 20, font = "Calibri 14")
            self.description_buttons[title]["command"] = lambda description_text = self.descriptions[title], movie_name = title: self.Expand(description_text, movie_name)
            self.description_buttons[title].grid(row = row_no, column = 5, padx = 10)
            l_date = Label(self.main_frame, textvariable = self.date_text[self.current_film], font = "Calibri 14")
            l_date.grid(row = row_no, column = 6)

            image_class = Images(self.main_frame, 75, 115, row_no, 7)
            image_class.get_image(title)
            image_class.update_directory()
            
            row_no += 1
            self.blank_line(self.main_frame, row_no, 0, 1, 8, "we", 0)
            row_no += 1

            self.current_film += 1
            if self.current_film >= 5:
                break
        
    def UpdateGenres(self, film_index, increase_by):
        """Changes the viewed genrre for the selected movie"""
        new_index = self.genre_index[film_index] + increase_by
        if new_index > len(self.movie_genres[film_index])-1:
            new_index = 0
        elif new_index < 0:
            new_index = len(self.movie_genres[film_index])-1
        self.genre_index[film_index] = new_index
        self.genre_text[film_index].set(self.movie_genres[film_index][self.genre_index[film_index]].capitalize())
    
    def Expand(self, description_text, movie_name):
        """Creates a frame which shows the description of the selected movie"""
        new_window = Toplevel()
        new_window.configure(
            background = '#90E3F7',
            highlightthickness = 20,
            relief = 'solid',
            highlightbackground = '#D4F2F9',
            height = 300,
            width = 800)
        new_window.title(movie_name)
        
        header_frame = Frame(new_window)
        header_frame.pack(side = TOP, fill = "x")

        v_title = StringVar()
        v_title.set(movie_name)
        l_title = Label(header_frame, textvariable = v_title, font = "Calibri 18 bold", background = "#2D64A5", foreground = "white")
        l_title.pack(fill = "x", expand = True)

        v_description = StringVar()
        v_description.set(description_text)
        l_description = Message(new_window, textvariable = v_description, font = "Calibri 12")
        l_description.pack(padx = 10, pady = 10, anchor = "center")

        b_close = Button(new_window, text = "Close", background = "white", font = "Calibri 12")
        b_close["command"] = new_window.destroy
        b_close.pack(padx = 10, pady = 10)
        
    def ChangeFilms(self, increase_by, data_to_view):
        """Updates the content of the table based on whether the user has pressed the 'Next' or  'Back' button"""
        self.index += increase_by
        if self.index >= math.ceil(len(data_to_view)/5):
            self.index = 0
        elif self.index < 0:
            self.index = math.ceil(len(data_to_view)/5)-1
        self.SetTable()
        self.UpdateTable(self.dataview)

class RecommendedFilm(Template):
    def __init__(self, master):
        """Allows the user to enter the name of a film and view similar films"""
        super().__init__(master, 'Recommended By Film', 15, 6, True, False) 
        self.master = master
        self.master.title('Recommended By Film')
        self.master.geometry('550x200+25+25') 
        self.master.option_add('*Label.Relief', 'flat')

        self.e_Search = Entry(self.main_frame, background = "white")
        self.e_Search.grid(row = 1, column = 0)
        self.e_Search.insert(0, "Search for Similar Movies")
        
        b_Search = Button(self.main_frame, text = "Search!", background = "white", width = 20)
        b_Search["command"] = self.FindRecommended
        b_Search.grid(row = 1, column = 1)

        b_Genres = Button(self.main_frame, text = "Search by Genre", background = "white", width = 20)
        b_Genres["command"] = self.GenresFrame
        b_Genres.grid(row = 2, column = 0, columnspan = 2)

    def get_list(self, dataset):
        if isinstance(dataset, list):
            names = [i['name'] for i in dataset]
            return names
        return []
        
    def FindRecommended(self):
        """Calculates similar films based on the user's input"""
        def get_recommendations(title, cosine_sim, indices_list):
            """Uses information in the dataset to find similar movies"""
            movie_index = indices_list[title]
            similar_scores = list(enumerate(cosine_sim[movie_index]))
            similar_scores = sorted(similar_scores, key = lambda x: x[1], reverse = True)
            movie_indices = [i[0] for i in similar_scores]
            return rating_dataset['title'].iloc[movie_indices], similar_scores

        def get_director(dataset):
            """Gets the movie director from the cast column of the dataset"""
            for i in dataset:
                if i['job'] == 'Director':
                    return i['name']
            return np.nan

        def cleanse_data(dataset):
            """Changes the data into a better format so they can be neatly displayed on the frame"""
            if isinstance(dataset, list):
                return [str.lower(i.replace(" ", "")) for i in dataset]
            else:
                if isinstance(dataset, str):
                    return str.lower(dataset.replace(" ", ""))
                else:
                    return ' '

        def generate_metadata(dataset):
            """joins some columns of the dataset so they can be easily compared"""
            return ' '.join(dataset['keywords']) + ' ' + ' '.join(dataset['cast']) + ' ' + dataset['director'] + ' ' + ' '.join(dataset['genres'])

        self.open_dataset()
        rating_dataset = self.movie_dataset.copy()
        tfidf = TfidfVectorizer(stop_words = 'english')
        rating_dataset['overview'] = rating_dataset['overview'].fillna('')
        tfidf_matrix = tfidf.fit_transform(rating_dataset['overview'])
        tfidf_matrix.shape

        movie_title = self.e_Search.get()
        movie_title = movie_title.title()
        self.open_dataset()
        self.searched_movie = self.movie_dataset.copy().loc[self.movie_dataset['original_title'] == movie_title]
        if len(self.searched_movie) == 0:
            messagebox.showerror("Error!", "Entered movie does not exist!")
        else:
            cosine_sim = linear_kernel(tfidf_matrix, tfidf_matrix)
            indices_list = pd.Series(rating_dataset.index, index = rating_dataset['title']).drop_duplicates()
            
            content_recommendations, content_scores = get_recommendations(movie_title, cosine_sim, indices_list)
            
            rating_dataset['director'] = rating_dataset['crew'].apply(get_director)

            features = ['cast', 'keywords', 'genres']
            for feature in features:
                rating_dataset[feature] = rating_dataset[feature].apply(self.get_list)
            rating_dataset[['title', 'cast', 'director', 'keywords', 'genres']].head(3)

            features.append('director')
            for feature in features:
                rating_dataset[feature] = rating_dataset[feature].apply(cleanse_data)
            rating_dataset['metadata'] = rating_dataset.apply(generate_metadata, axis = 1)

            count = CountVectorizer(stop_words = 'english')
            count_matrix = count.fit_transform(rating_dataset['metadata'])
            cosine_sim2 = cosine_similarity(count_matrix, count_matrix)
            
            rating_dataset = rating_dataset.reset_index()
            indices_list = pd.Series(rating_dataset.index, index = rating_dataset['title'])

            category_recommendations, category_scores = get_recommendations(movie_title, cosine_sim2, indices_list)

            new_list =  defaultdict(list)
            for a, b in content_scores + category_scores:
                new_list[a].append(b)
            overall_scores = sorted([(a, max(b)) for a, b in new_list.items()], key = lambda x:x[0])
            overall_scores = sorted(overall_scores, key = lambda tup: tup[1], reverse = True)
            movie_indices = [i[0] for i in overall_scores]

            rating_dataset['new_score'] = [rating_dataset['score'][overall_scores[movie][0]] * overall_scores[movie][1]  for movie in movie_indices]
            del movie_indices[0]
            final_recommendations = rating_dataset.iloc[movie_indices]
            final_recommendations.sort_values('new_score', ascending = False)

            self.canvas.forget()
            self.scrollbar.forget()
            SeveralMovies(self.master, RecommendedFilm, movie_title, final_recommendations)
        
    def GenresFrame(self):
        """Will allow the user to find the highest rated films from a given genre"""
        self.canvas.forget()
        self.master.geometry('1050x800+25+25')
        
        self.genre_frame = Frame(self.master)
        self.genre_frame.config(padx = 10, pady = 10)
        self.genre_frame.pack(expand = True, fill = "both")

        for i in range(10):
            self.genre_frame.grid_rowconfigure(i, pad = 15)
        for i in range(10):
            self.genre_frame.grid_columnconfigure(i, pad = 15)

        self.blank_line(self.genre_frame, 0, 0, 1, 10, "ew", 0)
        for column_no in range(11):
            self.blank_line(self.genre_frame, 0, column_no, 10, 1, "nsw", 8)

        genre_names = ["Action", "Adventure", "Animation", "Comedy", "Crime", "Documentary", "Drama", "Family", "Fantasy", "History", "Horror", "Music", "Mystery", "Romance", "Science Fiction", "Thriller", "War", "Western"]
        genre_buttons = {}
        row_no = 1
        column_no = 0
        top_movie_names = []
        self.open_dataset()
        genre_datasets = {}
        for genre in range(len(genre_names)):
            genre_buttons[genre_names[genre]] = Button(self.genre_frame, text = genre_names[genre], background = "white")
            genre_buttons[genre_names[genre]].grid(row = row_no, column = column_no)

            genre_datasets[genre_names[genre]] = self.movie_dataset.copy()
            genre_datasets[genre_names[genre]] = genre_datasets[genre_names[genre]].sort_values('score', ascending=False)
            genre_datasets[genre_names[genre]] = genre_datasets[genre_names[genre]][['id', 'title', 'genres', 'score', 'overview', 'release_date']]
            genre_datasets[genre_names[genre]]["genres"] = genre_datasets[genre_names[genre]]["genres"].apply(self.get_list)
            mask = genre_datasets[genre_names[genre]]["genres"].apply(lambda x: genre_names[genre] in x)
            genre_datasets[genre_names[genre]] = genre_datasets[genre_names[genre]][mask]

            top_movie_index = 0            
            while genre_datasets[genre_names[genre]]['title'].iat[top_movie_index] in top_movie_names:
                top_movie_index += 1                    
            movie_name = genre_datasets[genre_names[genre]]['title'].iat[top_movie_index]
            top_movie_names.append(movie_name)

            image_class = Images(self.genre_frame, 75, 115, row_no, column_no+1)
            image_class.get_image(movie_name)
            
            row_no += 1
            self.blank_line(self.genre_frame, row_no, column_no, 1, 10, "ew", 0)
            row_no += 1

            genre_buttons[genre_names[genre]]["command"] = lambda genre_name = genre_names[genre], dataset = genre_datasets[genre_names[genre]]: self.RecommendedGenres(genre_name, dataset)
            if genre == 3 or genre == 7 or genre == 11 or genre == 15:
                column_no += 2
                row_no = 1

    def RecommendedGenres(self, genre_name, dataset):
        '''Switches fame to show the results in a table'''
        self.genre_frame.pack_forget()
        SeveralMovies(self.master, RecommendedFilm, genre_name, dataset)
        
class RecommendedYou(Template):
    def __init__(self, master):
        """Wil calculate recommended films for  a user based on other peoples ratings"""
        super().__init__(master, 'Recommended For You', 19, 4, True, False) 
        self.master = master
        self.master.title('Recommended For You')
        self.scrollbar.pack(side = "right", fill = "y")
        
        def GetTop(predictions, user_id):
            top_films = []
            for uid, iid, true_r, est, _ in predictions:
                if int(uid) == int(user_id):
                    top_films.append((iid, est))

            top_films.sort(key = lambda x: x[1], reverse = True)
            return top_films

        database = Database()
        user_id = database.run_select('SELECT UserID FROM Users WHERE logged_in = 1')
        user_id = user_id[0][0]
        results = database.run_select("SELECT * FROM Ratings")
        ratings = pd.DataFrame(results, columns = ['UserID', 'MovieID', 'Rating'])
        reader = Reader(rating_scale=(1, 10))
        ratings = Dataset.load_from_df(ratings[['UserID', 'MovieID', 'Rating']], reader)

        trainset = ratings.build_full_trainset()
        algorithm = SVD()
        algorithm.fit(trainset)

        self.open_dataset()
        iids = self.movie_dataset.copy()
        iids = iids['id']
        user_ratings = database.run_select("SELECT * FROM Ratings WHERE UserId = {}".format(user_id))
        database.close()
        user_ratings = [rating[1] for rating in user_ratings]
        iids_to_predict = np.setdiff1d(iids, user_ratings)
        iids_to_predict = [int(id) for id in iids_to_predict]
        testset = [[int(user_id), iid, 4.] for iid in iids_to_predict]

        predictions = algorithm.test(testset) 
        top_films = GetTop(predictions, user_id)
        estimates = []
        for movie in top_films:
            if movie[1] in estimates:
                top_films.remove(movie)
            else:
                estimates.append(movie[1])
        top_films = [movie[0] for movie in top_films]

        if len(top_films) <= 10:
            self.open_dataset()
            database = Database()
            my_dataset = self.movie_dataset[["id", "title", "genres", "keywords", "overview"]].copy()
            my_ratings = database.run_select("SELECT * FROM Ratings WHERE UserID = {}".format(user_id))
            my_movies  = [movie[1] for movie in my_ratings]
            my_ratings = pd.DataFrame(my_ratings, columns = ["UserID", "MovieID", "Rating"])
            my_dataset = my_dataset[my_dataset['id'].isin(my_movies)]
            my_ratings = my_ratings.merge(my_dataset.rename(columns={'id':'MovieID'}))
            my_bad = my_ratings[my_ratings['Rating'] <= 5].values.tolist()        
            bad_genres = []
            bad_words = []
            for current_movie in my_bad:
                for genre in current_movie[4]:
                    bad_genres.append(genre["name"])
                for word in current_movie[5]:
                    bad_words.append(word["name"])
            bad_genres = list(dict.fromkeys(bad_genres))
            bad_words = list(dict.fromkeys(bad_words))

            other_dataset = self.movie_dataset[["id", "title", "genres", "keywords", "overview"]].copy()
            other_ratings = database.run_select("SELECT * FROM Ratings WHERE UserID <> {}".format(user_id))
            other_movies = [movie[1] for movie in other_ratings]
            other_ratings = pd.DataFrame(other_ratings, columns = ["UserID", "MovieID", "Rating"])
            other_dataset = other_dataset[other_dataset['id'].isin(other_movies)]
            other_ratings = other_ratings.merge(other_dataset.rename(columns={'id':'MovieID'}))
            other_ratings = other_ratings[other_ratings['Rating'] >= 6].values.tolist()
            other_ratings = [movie["id"] for movie in other_ratings]
            database.close()
            
            for current_movie in other_ratings:
                delete = False
                if current_movie[1] in my_movies:
                    delete = True
                    
                for genre in current_movie[4]:
                    if genre in bad_genres:
                        delete = True

                for word in current_movie[5]:
                    if word in bad_words:
                        delete = True

                if delete == True:
                    other_ratings.remove(current_movie)

            top_films.append(other_ratings)
        final_dataset = self.movie_dataset.copy()
        final_dataset = final_dataset[final_dataset['id'].isin(top_films)]
        top_films = final_dataset
        
        self.canvas.forget()
        self.scrollbar.forget()
        SeveralMovies(self.master, MainMenu, "Recommended For You!", top_films)

class IndividualMovies(Template):
    def __init__(self, master, movie_title, old_frame):
        """Creates a table to show information for a single searched movie"""
        super().__init__(master, 'Movie Details', 5, 8  , True, True)
        self.master = master
        self.master.title(movie_title)
        self.master.geometry('1000x550+25+25')
        self.v_title.set(movie_title)

        self.open_dataset()
        self.searched_movie = self.movie_dataset.copy().loc[self.movie_dataset['original_title'] == movie_title]
        self.searched_movie = self.searched_movie[['id', 'title', 'tagline', 'overview', 'genres', 'homepage', 'release_date', 'runtime', 'score', 'cast', 'crew', 'revenue', 'budget']]
        self.movie_line = self.searched_movie.index[0]

        if len(self.searched_movie) == 0:
            messagebox.showerror("Error!", "Entered movie does not exist!")
            self.switch_frame(MainMenu)
            
        for image_label in self.image_frame.winfo_children():
            image_label.destroy()

        image_class = Images(self.image_frame, 200, 300, 0, 0)
        image_class.get_image(self.v_title.get())
        image_class.update_directory()
            
        label_titles = ["Genres", "Homepage", "Date", "Duration", "Rating", "Cast", "Director", "Profit"]
        self.labels = {}
        column_counter = 0
        row_counter = 3
        for title in label_titles:
            self.labels[title] = Label(self.main_frame, text = title)
            self.labels[title].grid(row = row_counter, column = column_counter, sticky = "nsew")
            row_counter += 1

            if row_counter == 7:
                column_counter += 4
                row_counter = 3

        self.label_variables = {}
        self.label_titles = ["tagline", "overview", "homepage", "duration", "release_date", "score", "profit", "director", "genres"]
        for title in self.label_titles:
            self.label_variables[title] = StringVar()
            
        l_tagline = Label(self.main_frame, textvariable = self.label_variables["tagline"])
        l_tagline.grid(row = 1, column = 0, columnspan = 9, sticky = "nsew")
        l_overview = Message(self.main_frame, textvariable = self.label_variables["overview"], relief = "solid", aspect = 375, justify = "center")
        l_overview.grid(row = 2, column = 0, columnspan = 9, sticky = "nsew")
        
        self.movie_genres = []
        genres = self.searched_movie['genres'][self.movie_line]
        for current_genre in range(len(genres)):
            new_genre = genres[current_genre]["name"]
            self.movie_genres.append(new_genre)
        self.movie_genres.sort()
        self.label_variables['genres'].set(self.movie_genres[0])

        self.genre_index = 0
        b_previous = Button(self.main_frame, text = "<", background = "white", font = "Calibri 10", relief = "solid")
        b_previous["command"] = lambda increase_by = -1: self.UpdateCategory(increase_by)
        b_previous.grid(row = 3, column = 1, padx = 10)
        self.labels["genre1"] = Label(self.main_frame, textvariable = self.label_variables["genres"], font = "Calibri 14", relief = "flat")
        self.labels["genre1"].grid(row = 3, column = 2)
        b_next = Button(self.main_frame, text = ">", background = "white", font = "Calibri 10", relief = "solid")
        b_next["command"] = lambda increase_by = +1: self.UpdateCategory(increase_by)
        b_next.grid(row = 3, column = 3, padx = 10)

        cast_members = []
        cast = self.searched_movie['cast'][self.movie_line]
        for current_member in range(len(cast)):
            temp_dictionary = {}
            temp_dictionary["name"] = cast[current_member]["name"]
            temp_dictionary["character"] = cast[current_member]["character"]
            cast_members.append(temp_dictionary)

        self.b_cast = Button(self.main_frame, text = "View Cast", foreground = "black", background = "white")
        self.b_cast["command"] = lambda cast_members = cast_members: self.ViewCast(cast_members)
        self.b_cast.grid(row = 4, column = 6, columnspan = 2, sticky = "nsew")
            
        duration = self.searched_movie['runtime'][self.movie_line]
        minutes = int(duration % 60)
        if minutes < 10:
            minutes = "0" + str(minutes)
        hours = int(duration / 60)
        duration = "0" + str(hours) + ":" + str(minutes) 
        self.label_variables["duration"].set(duration)

        director = self.searched_movie["crew"][self.movie_line]
        director = next(item for item in director if item["job"] == "Director")
        director = director["name"]
        self.label_variables["director"].set(director)

        profit = self.searched_movie["revenue"][self.movie_line] - self.searched_movie["budget"][self.movie_line]
        profit = "£" + '{:,}'.format(profit)
        self.label_variables["profit"].set(profit)

        self.label_titles = ["tagline", "overview", "homepage", "release_date", "score"]
        for title in self.label_titles:
            if self.searched_movie[title][self.movie_line] == float('nan'):
                self.label_variables[title].set("No " + title)
            elif type(self.searched_movie[title][self.movie_line]) == np.float64:
                self.label_variables[title].set(int(self.searched_movie[title][self.movie_line]))
            else:
                self.label_variables[title].set(str(self.searched_movie[title][self.movie_line]))  

        b_homepage = Button(self.main_frame, text = "View Homepage", foreground = "black", background = "white")
        b_homepage["command"] = lambda: webbrowser.open(self.label_variables["homepage"].get(), new = 2)
        b_homepage.grid(row = 4, column = 1, columnspan = 3, sticky = "nsew")
        
        footer_text = ["release_date", "duration", "score", "director", "profit"]
        row_no = 5
        column_counter = 1
        for category in footer_text:
            self.labels[category + "1"] = Label(self.main_frame, textvariable = self.label_variables[category])
            if category != "score":
                self.labels[category + "1"].grid(row = row_no, column = column_counter, columnspan = 3, sticky = "nsew")
            if category == "duration":
                column_counter = 6
                row_no = 3
            elif category == "score":
                self.labels[category + "1"].grid(row = row_no, column = column_counter, columnspan = 1, sticky = "nsew")
                row_no += 2
            else:
                row_no += 1
        self.labels["release_date1"].grid(row = 5, column = 1, columnspan = 3, sticky = "nsew")
        self.labels["duration1"].grid(row = 6, column = 1, columnspan = 3, sticky = "nsew")
        self.labels["score1"].grid(row = 3, column = 6, sticky = "nsew")
        self.labels["director1"].grid(row = 5, column = 6, columnspan = 2, sticky = "nsew")
        self.labels["profit1"].grid(row = 6, column = 6, columnspan = 2, sticky = "nsew")

        self.b_RateMovie = Button(self.main_frame, text = "Rate Movie", background = "white")
        self.b_RateMovie["command"] = self.RateMovie
        self.b_RateMovie.grid(row = 3, column = 7, sticky = "nsew")

        b_back = Button(self.image_frame, text = "Go Back", background = "white")
        b_back["command"] = lambda frame = old_frame: self.switch_frame(frame)
        b_back.grid(row = 1, column = 0, sticky = "nsew")
        
    def UpdateCategory(self, increase_by):
        """Changes data that is showing on the table, valled by pressing a button"""
        self.genre_index += increase_by
        if self.genre_index < 0:
            self.genre_index = len(self.movie_genres) - 1
        elif self.genre_index >= len(self.movie_genres):
            self.genre_index = 0        

        self.label_variables["genres"].set(self.movie_genres[self.genre_index])

    def ViewCast(self, cast_members):
        """Shows the cast in a top-level window, called when the user presses a button"""
        new_window = Toplevel()
        new_window.configure(
            background = '#90E3F7',
            highlightthickness = 20,
            relief = 'solid',
            highlightbackground = '#D4F2F9',
            height = 300,
            width = 800)
        new_window.title(self.v_title.get())
        
        header_frame = Frame(new_window)
        header_frame.pack(side = TOP, fill = "x")

        l_title = Label(header_frame, textvariable = self.v_title.get(), font = "Calibri 18 bold", background = "#2D64A5", foreground = "white")
        l_title.pack(fill = "x", expand = True)

        style = ttk.Style()
        style.configure("mystyle.Treeview", font = ("Calibri", 13))
        style.configure("mystyle.Treeview.Heading", font = ("Calibri", 14, "bold"))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        self.cast_tree = ttk.Treeview(new_window, style = "mystyle.Treeview")
        self.cast_tree["columns"] = ("one")
        self.cast_tree.column("#0", width = 300, stretch = YES)
        self.cast_tree.heading("#0", text = "Character", anchor = CENTER)
        self.cast_tree.column("one", width =  300, stretch = YES)
        self.cast_tree.heading("one", text = "Name", anchor = CENTER)
        self.cast_tree.pack(padx = 10, pady = 10)

        for member in reversed(cast_members):
            self.cast_tree.insert("", "0", text = member["name"], values = (member["character"]))
            
        b_close = Button(new_window, text = "Close", background = "white", font = "Calibri 12")
        b_close["command"] = new_window.destroy
        b_close.pack(padx = 10, pady = 10)
            
    def RateMovie(self):
        """Allows the user to rate a movie"""
        def AddRating():
            """Adds the user's rating to the database"""
            ratemovie = False
            rating = self.e_RateMovie.get()
            if len(str(rating)) == 1 or len(str(rating)) == 2 and int(rating) > 0 and int(rating) < 11:
                database = Database()
                user_id = database.run_select('SELECT UserID FROM Users WHERE logged_in = 1')
                user_id = user_id[0][0]
                movie_id = self.searched_movie['id'][self.movie_line]
                sql_command = "SELECT 1 FROM Ratings WHERE UserID = {} AND MovieID = {}".format(user_id, movie_id)
                rating_exists = database.run_select(sql_command)
                
                message_result = None
                if len(rating_exists) == 1:
                    message_result = messagebox.askyesnocancel("Error!", "You have already rated this movie, would you like to update your rating?")
                if message_result == "Yes" or len(rating_exists) == 0:
                    sql_command = "INSERT INTO Ratings VALUES ({}, {}, {});".format(user_id, movie_id, rating)
                    status = database.run_update(sql_command)
                database.close()

                self.e_RateMovie.grid_forget()
                self.b_Rate.grid_forget()
                
                self.labels["score1"].grid(row = 3, column = 6, sticky = "nsew")
                self.b_RateMovie.grid(row = 3, column = 7, sticky = "nsew")
                self.b_cast.grid(row = 4, column = 6, columnspan = 2, sticky = "nsew")

            else:
                messagebox.showerror("Error!", "Please enter your rating as an integer between 1 and 10!")

        self.labels["score1"].grid_forget()
        self.b_RateMovie.grid_forget()
        
        self.e_RateMovie = Entry(self.main_frame, background = "white", width = 5)
        self.e_RateMovie.grid(row = 3, column = 6, padx = (0,15))

        self.b_Rate = Button(self.main_frame, background = "white", text = "Rate!")
        self.b_Rate["command"] = AddRating
        self.b_Rate.grid(row = 3, column = 7, padx = (15, 0))

class MovieDetails(Template):
    def __init__(self, master):
        """Allows the user to search for a movie and view it's details"""
        super().__init__(master, 'Rate A Movie', 1, 4, True, False)  
        self.master = master
        self.master.title('Movie Details')
        self.master.geometry('600x200+25+25')

        e_Search = Entry(self.main_frame, background = "white", width = 30)
        e_Search.grid(row = 1, column = 0, columnspan = 4, padx = 10, pady = 15)
        e_Search.insert(0, "Search for a movie:")
        b_Search = Button(self.main_frame, text = "Search", background = "white", width = 15)
        b_Search["command"] = lambda user_input = e_Search: self.SearchMovies(user_input)
        b_Search.grid(row = 1, column = 4, padx = 10)

    def SearchMovies(self, user_input):
        '''Gets the details of the searched movie'''
        movie_title = user_input.get()
        movie_title = movie_title.title()
        self.open_dataset()
        self.searched_movie = self.movie_dataset.copy().loc[self.movie_dataset['original_title'] == movie_title]
        if len(self.searched_movie) == 0:
            messagebox.showerror("Error!", "Entered movie does not exist!")
        else:
            self.canvas.forget()
            self.scrollbar.forget()
            IndividualMovies(self.master, movie_title, MovieDetails)

class MyMovies(Template):
    def __init__(self, master):
        """Allows the user to view the movies they have rated in the past"""
        super().__init__(master, 'My Movies', 1, 4, True, False)  
        self.master = master
        self.master.title('My Movies')
        self.master.geometry('600x500+25+25')
        
        database = Database()
        user_id = database.run_select("SELECT UserID FROM Users WHERE logged_in = 1;")
        user_id = user_id[0][0]
        sql_command = "SELECT MovieID FROM Ratings WHERE UserID = {}".format(user_id)
        self.rated_movies = database.run_select(sql_command)
        database.close()

        if len(self.rated_movies) == 0:
            messagebox.showerror("Error!", "You have not rated any movies!")
            self.switch_frame(MainMenu)        
        self.rated_movies = [rating[0] for rating in self.rated_movies]

        l_information = Label(self.main_frame, text = "Please double click a movie to view it's details", font = "Calibri 10")
        l_information.grid(row = 1, column = 0, pady = 10)
        
        style = ttk.Style()
        style.configure("mystyle.Treeview", font = ("Calibri", 13))
        style.configure("mystyle.Treeview.Heading", font = ("Calibri", 14, "bold"))
        style.layout("mystyle.Treeview", [('mystyle.Treeview.treearea', {'sticky': 'nswe'})])
        self.movies_tree = ttk.Treeview(self.main_frame, style = "mystyle.Treeview")
        self.movies_tree.column("#0", width = 400, stretch = YES)
        self.movies_tree.heading("#0", text = "Movie Name", anchor = CENTER)
        self.movies_tree.grid(row = 2, column = 0)

        self.open_dataset()
        for movie in self.rated_movies:
            current_details  = self.movie_dataset.copy().loc[self.movie_dataset['id'] == movie][['title']]
            movie_line = current_details.index[0]
            movie_title = current_details['title'][movie_line]
            self.movies_tree.insert("", "0", text = movie_title)
            self.movies_tree.bind("<Double-1>", self.SelectMovie)

    def SelectMovie(self, event):
        """Switches frame based on the movie the user has clicked on"""
        movie_title = self.movies_tree.selection()[0]
        self.canvas.forget()
        self.scrollbar.forget()
        IndividualMovies(self.master, self.movies_tree.item(movie_title, "text"), MyMovies)
        
def main():
    root = Tk()
    app = LogIn(root)
    root.mainloop()

if __name__ == "__main__":
    main()

