#import mysql.connector
import sqlite3

class Database():
    def __init__ (self):

        self.con = sqlite3.connect('RecommendationDatabase.db')
        self.cursor = self.con.cursor()

        self.cursor.execute('''CREATE TABLE Users (
	UserID int(3),
	FirstName varchar(10),
	Surname varchar(10),
	Username varchar(20),
	Age int(3),
	Email varchar(40),
	PasswordSalt varchar(32),
	HashedPassword varchar(128),
	Logged_in tinyint(1),
	PRIMARY KEY (UserID));
''')
        self.cursor.execute('''CREATE TABLE SecurityQuestions (
	SecurityID int(3),
	UserID int(3),
	Question tinyint(1),
	AnswerSalt varchar(32),
	HashedAnswer varchar(128),
	PRIMARY KEY (SecurityID),
	FOREIGN KEY (UserID) REFERENCES Users(UserID));
''')
        self.cursor.execute('''CREATE TABLE Ratings(
	UserID int(3),
	MovieID int(7),
	Rating tinyint(1),
	PRIMARY KEY (UserID, MovieID),
	FOREIGN KEY (UserID) REFERENCES Users(UserID));
''')

def test():
    db=Database()
    print("done")


       
if __name__ == "__main__":
    test()
