import json
from typing import Tuple, List, Optional, Any, Union
import sqlite3
import os
import bcrypt
from password_strength import PasswordPolicy
from tabulate import tabulate
from datetime import datetime

__DEBUG__ = 0
menu_seperate = '\n' + '{:*^150}'.format(' InCollege ') + '\n'

class DatabaseManager:
    def __init__(self, data_file):
        self.conn = sqlite3.connect(data_file)
        self.cursor = self.conn.cursor()

    def execute(self, query, params=()):
        try:
            self.cursor.execute(query, params)
            self.commit()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            
    def commit(self):
        self.conn.commit()
        
    def fetch(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchone()

    def fetchall(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall() 

    def find_jobs_by_title(self, job_title):
        return self.fetchall("SELECT * FROM jobs where job_title LIKE ?;", ("%"+job_title+"%",))
    
    def find_jobs_by_id(self, job_id):
        return self.fetchall("SELECT * FROM jobs where job_id=?;", (job_id,))
    
    def close(self):
        self.conn.close()
    
    def post_job(self, skill_name, long_description, job_title, job_description, employer, location, salary, user_id):
        user = self.fetch('SELECT * FROM accounts WHERE user_id=?;', (user_id,))
        assert user is not None, "Could not find user"

        self.execute('''
            INSERT INTO jobs (skill_name, long_description, job_title, job_description, employer, location, salary, posted_by, user_first_name, user_last_name)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);''',
            (skill_name, long_description, job_title, job_description, employer, location, salary, user[0], user[3], user[4]))
        return True
    
    def user_apply_job(self, user_id, job_id, gr_date, s_date, quals):
        user = self.fetch('SELECT * FROM accounts WHERE user_id=?;', (user_id,))
        assert user is not None, "Could not find user"
        job = self.fetch('SELECT * FROM jobs WHERE job_id=?;', (job_id,))
        assert job is not None, "Could not find job"

        self.execute('''
            INSERT INTO job_applications (applicant, job_id, gr_date, s_date, quals)
            VALUES (?, ?, ?, ?, ?);
            ''',
            (user_id, job_id, gr_date, s_date, quals))
        return True
    
    def user_is_applicant(self, user_id, job_id):
        return self.fetchall("SELECT COUNT(*) FROM   job_applications WHERE (applicant=? AND job_id=?)",(user_id, job_id))[0][0] > 0
    
    def check_friendship_status(self, user1_id, user2_id):
                query = """
                SELECT COUNT(1) FROM friendship 
                WHERE (user_one = (SELECT username FROM accounts WHERE user_id = ?) 
                AND user_two = (SELECT username FROM accounts WHERE user_id = ?)) 
                OR (user_one = (SELECT username FROM accounts WHERE user_id = ?) 
                AND user_two = (SELECT username FROM accounts WHERE user_id = ?))
                """
                try:
                    # Execute the SQL query
                    result = self.fetch(query, (user1_id, user2_id, user2_id, user1_id))
                    # Check if the friendship exists
                    return result[0] > 0  # True if count is more than 0, otherwise False
                except Exception as e:
                    # Handle any exceptions, such as database connection errors or query errors
                    print(f"An error occurred: {e}")
                    return False

class InCollegeAppManager:
    def __init__(self, data_file="users.db", DEBUG=False):
        self.db_manager = DatabaseManager(data_file)
        self.setup_database()
        self._PasswordPolicy = PasswordPolicy.from_names(
            length=8, uppercase=1, numbers=1, special=1,
        )
        self._current_user = None
        with open('./data/menus.json', 'r') as f:
            self.menus = json.load(f)['menus']

        if DEBUG:
            self.InitDebugData()

    def InitDebugData(self):
        # For the accounts table
        pw = bcrypt.hashpw("p1".encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        self.db_manager.execute('''
            INSERT OR IGNORE INTO accounts (username, password, first_name, last_name, university, major, plus)
            VALUES ("test_user1", ?, "John", "Doe", "University1", "Major1", ?);
        ''', (pw, True))

        self.db_manager.execute('''
            INSERT OR IGNORE INTO accounts (username, password, first_name, last_name, university, major, plus)
            VALUES ("test_user2", ?, "Jason", "Morris", "University2", "Major2", ?);
        ''', (pw, False))
        
        
        # For the settings table
        self.db_manager.execute('''
            INSERT OR IGNORE INTO settings (username, email_notifs, sms_notifs, target_ads, language)
            VALUES ("test_user1", 1, 0, 1, "English");
        ''')
        
        # For the profiles table
        self.db_manager.execute('''
            INSERT OR IGNORE INTO profiles (username, first_name, last_name, title, major, university, about, pastJob1, pastJob2, pastJob3, education, posted)
            VALUES ("test_user1", "John", "Doe", "Software Developer", "Major1", "University1", "About me...", "Past Job 1", "Past Job 2", "Past Job 3", "My Education", "Last Posted");
        ''')
        
        # For the skills table
        self.db_manager.execute('''
            INSERT OR IGNORE INTO skills (skill_name, long_description)
            VALUES ("Python", "A high-level programming language.");
        ''')

        # For the jobs table
        self.db_manager.execute('''
            INSERT OR IGNORE INTO jobs (skill_name, long_description, job_title, job_description, employer, location, salary, posted_by, user_first_name, user_last_name)
            VALUES ("Python", "A high-level programming language.", "Python Developer", "Develop in Python", "Company1", "Location1", 60000, 1, "John", "Doe");
        ''')

        # For the friend_requests table
        self.db_manager.execute('''
            INSERT OR IGNORE INTO friend_requests (sender, receiver)
            VALUES ("test_user1", "test_user2");
        ''')
        
        # For the friendship table
        self.db_manager.execute('''
            INSERT OR IGNORE INTO friendship (user_one, user_two)
            VALUES ("test_user1", "test_user2");
        ''')
        
        # For the job_applications table
        self.db_manager.execute('''
            INSERT OR IGNORE INTO job_applications (applicant, job_id, gr_date, s_date, quals)
            VALUES (1, 1, "00/00/0000", "00/00/0000", "Very Qualified Candidate");
        ''')

        # Commit changes
        self.db_manager.commit()
        
    def setup_database(self):
        self.db_manager.execute("PRAGMA foreign_keys=ON;")

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            university TEXT NOT NULL,
            major TEXT NOT NULL,
            plus BOOL NOT NULL,
            last_job_application_timestamp TIMESTAMP NOT NULL
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS notifications (
            user_id INTEGER NOT NULL,
            notification TEXT NOT NULL
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS messages (
            recipient INTEGER NOT NULL,
            message TEXT NOT NULL,
            sender INTEGER NOT NULL,
            FOREIGN KEY (recipient) REFERENCES accounts(user_id) ON DELETE CASCADE,
            FOREIGN KEY (sender) REFERENCES accounts(user_id) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS settings (
            username TEXT PRIMARY KEY,
            email_notifs BOOL NOT NULL,
            sms_notifs BOOL NOT NULL,
            target_ads BOOL NOT NULL,
            language TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS profiles (
            username TEXT PRIMARY KEY,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL,
            title TEXT NOT NULL,
            major TEXT NOT NULL,
            university TEXT NOT NULL,
            about TEXT NOT NULL,
            pastJob1 TEXT NOT NULL,
            pastJob2 TEXT NOT NULL,
            pastJob3 TEXT NOT NULL,
            education TEXT NOT NULL,
            posted TEXT NOT NULL,
            FOREIGN KEY (username) REFERENCES accounts(username) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS friend_requests (
            request_id INTEGER PRIMARY KEY AUTOINCREMENT,
            sender TEXT NOT NULL,
            receiver TEXT NOT NULL,
            FOREIGN KEY (sender) REFERENCES accounts(username) ON DELETE CASCADE,
            FOREIGN KEY (receiver) REFERENCES accounts(username) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS friendship (
            friendship_id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_one TEXT NOT NULL,
            user_two TEXT NOT NULL,
            FOREIGN KEY (user_one) REFERENCES accounts(username) ON DELETE CASCADE,
            FOREIGN KEY (user_two) REFERENCES accounts(username) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            skill_name TEXT PRIMARY KEY,
            long_description TEXT UNIQUE NOT NULL
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS jobs (
            job_id INTEGER PRIMARY KEY AUTOINCREMENT,
            skill_name TEXT NOT NULL,
            long_description TEXT UNIQUE NOT NULL,
            job_title TEXT NOT NULL,
            job_description TEXT NOT NULL,
            employer TEXT NOT NULL,
            location TEXT NOT NULL,
            salary REAL NOT NULL,
            posted_by INTEGER,
            user_first_name TEXT NOT NULL,
            user_last_name TEXT NOT NULL,
            FOREIGN KEY (posted_by) REFERENCES accounts(user_id) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS job_applications (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            gr_date TEXT NOT NULL,
            s_date TEXT NOT NULL,
            quals TEXT NOT NULL,
            FOREIGN KEY (applicant) REFERENCES accounts(user_id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS deleted_job_notifs (
            applicantID INTEGER,
            jobID INTEGER,
            jobTitle TEXT NOT NULL,
            FOREIGN KEY (applicantID) REFERENCES accounts(user_id) ON DELETE CASCADE
        );
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS new_job_notifs (
            notifID INTEGER PRIMARY KEY AUTOINCREMENT,
            recipientID INTEGER,
            message TEXT NOT NULL,
            FOREIGN KEY (recipientID) REFERENCES accounts(user_id) ON DELETE CASCADE
        )
        ''')

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS job_save (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            applicant INTEGER NOT NULL,
            job_id INTEGER NOT NULL,
            saved BOOL NOT NULL,
            FOREIGN KEY (applicant) REFERENCES accounts(user_id) ON DELETE CASCADE,
            FOREIGN KEY (job_id) REFERENCES jobs(job_id) ON DELETE CASCADE
        );
        ''')

        self.db_manager.commit()

        if self.db_manager.fetch("SELECT COUNT(*) FROM skills")[0] == 0:
            self.populate_skills_from_file()

    def populate_skills_from_file(self, skills_file='data/example_skills.txt'):
        try:
            with open(os.path.join(os.getcwd(), skills_file), 'r') as f:
                for line in f:
                    skill_name, long_description = line.strip().split('$$$')
                    self.db_manager.execute("INSERT INTO skills (skill_name, long_description) VALUES (?, ?)", (skill_name, long_description))
        except Exception as e:
            print('Error while parsing skills file. Did you configure the file properly?')
            print(e)

    def _Terminate(self):
        self.db_manager.close()
        print('Goodbye!')
        exit(0)
        
    def _create_account(self, username, password, first_name, last_name, university, major, plus) -> Any:
        """
            Attempts to Create Account with [username, password]. Returns True if successful, otherwise throws an Exception.
        """
        def valid_password(password):
            """ Validates a Password based on requirements. """
            return not self._PasswordPolicy.test(password) and len(password) < 13
        
        if not valid_password(password):
            raise Exception("Invalid password. Please ensure it meets the requirements.")

        if self.db_manager.fetch('SELECT COUNT(*) FROM accounts;')[0] >= 10:
            raise Exception("All permitted accounts have been created. Please come back later.")

        if self.db_manager.fetch('SELECT * FROM accounts WHERE username=?;', (username,)):
            raise Exception("Username already exists. Please choose another one.")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.db_manager.execute(
            'INSERT INTO accounts (username, password, first_name, last_name, university, major, plus, last_job_application_timestamp) VALUES (?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP);',
            (username, hashed_password, first_name, last_name, university, major, plus))

        self.db_manager.execute(
            'INSERT INTO settings (username, email_notifs, sms_notifs, target_ads, language) VALUES (?, ?, ?, ?, ?);',
            (username, 1, 1, 1, "English"))

        self.db_manager.execute('INSERT INTO profiles (username, first_name, last_name, title, major, university, about, pastJob1,\
                                pastJob2, pastJob3, education, posted) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?);',
                                (username, first_name, last_name, "n/a", major, university, "n/a", "n/a", "n/a", "n/a", "n/a", "no"))

        # Returns the account from Database
        return self.__login(username=username, password=password)

    def __login(self, username: str, password: str):
        user = self.db_manager.fetch('SELECT * FROM accounts WHERE username=?;',    (username,))
        if user:
            hashed_password = user[2].encode('utf-8')  # Encode back to bytes
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return user
        return None

    def _is_person_in_database(self, first_name, last_name):
        user = self.db_manager.fetch("SELECT * FROM accounts WHERE first_name=? AND last_name =?;", (first_name, last_name))
        return bool(user)

    def Run(self): # Can only Serve One Client at a time :(
        # function that holds useful incollege links and their functionalities
        def useful_links():

            def general_options():

                def sign_up_options():
                    while True:
                        print(menu_seperate) #menu
                        print(self.menus["sign_in_up"])
                        choice = input("Select an option: ")
                        print()
                        if choice == "1":
                            _login_procedure()
                        elif choice == "2":
                            _create_account_procedure()
                        elif choice == "q":
                            break

                while True:
                    print(menu_seperate) #menu
                    print(self.menus["general_help"])
                    if self._current_user == None:
                        print("7. Sign in/Sign Up")
                    print("q. Quit")
                    choice = input("Select an option: ")
                    print()
                    if choice == "1":
                        print("We're here to help!")
                    elif choice == "2":
                        print("In College: Welcome to In College, the world's largest college student network with many users in many countries and territories worldwide!")
                    elif choice == "3":
                        print("In College Pressroom: Stay on top of the latest news, updates, and reports")
                    elif choice == "4":
                        print("Under Construction")
                    elif choice == "5":
                        print("Under Construction")
                    elif choice == "6":
                        print("Under Construction")
                    elif choice == "7" and self._current_user == None:
                        sign_up_options()
                    elif choice == "q":
                        break
                    else:
                        print("Invalid choice. Please try again.")

            while True:
                print(menu_seperate) #menu
                print(self.menus["useful_links"])

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    general_options()
                elif choice == "2":
                    print("Under Construction")
                elif choice == "3":
                    print("Under Construction")
                elif choice == "4":
                    print("Under Construction")
                elif choice == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")

        def guest_controls():
            while True:
                print(menu_seperate) #menu
                print("Guest Controls\n-------------------------------")
                cur = 0
                if self._current_user != None:
                    cur = self.db_manager.fetchall("SELECT * FROM settings WHERE username=?", (self._current_user[1], ))
                print(f"{'InCollege Email Notifications:':>31s} {'Off' if cur and cur[0][1] == 0 else 'On'}")
                print(f"{'InCollege SMS Notifications:':>31s} {'Off' if cur and cur[0][2] == 0 else 'On'}")
                print(f"{'InCollege Targeted Advertising:':>31s} {'Off' if cur and cur[0][3] == 0 else 'On'}")
                if self._current_user == None:
                    print("\nNot signed in - cannot alter settings")
                    break
                else:
                    change = input("\nWould you like to change one of these settings? (y/n) ")
                    if change == "y":
                        print(self.menus["controls"])
                        option = input("Select which you would like to change: ")

                        if option == "1":
                            bool = 1 if cur[0][1] == 0 else 0
                            self.db_manager.execute("UPDATE settings SET email_notifs=? WHERE username=?", (bool, self._current_user[1]))
                            print("Email notifications successfully turned", "on." if bool else "off.")
                        elif option == "2":
                            bool = 1 if cur[0][2] == 0 else 0
                            self.db_manager.execute("UPDATE settings SET sms_notifs=? WHERE username=?", (bool, self._current_user[1]))
                            print("SMS notifications successfully turned", "on." if bool else "off.")
                        elif option == "3":
                            bool = 1 if cur[0][3] == 0 else 0
                            self.db_manager.execute("UPDATE settings SET target_ads=? WHERE username=?", (bool, self._current_user[1]))
                            print("Targeted Advertising successfully turned", "on." if bool else "off.")
                        elif option != "q":
                            print("Invalid choice. Please try again.")
                        print()
                    else:
                        break

        def privacy_policy():
            while True:
                print(menu_seperate) #menu
                print(self.menus["privacy_menu"])

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print(menu_seperate) #menu
                    print(self.menus["privacy_policy"])
                elif choice == "2":
                    guest_controls()
                elif choice == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")

        def languages_menu():
            while True:
                print(menu_seperate) #menu
                print(self.menus["languages"])
                print("Current language: ", end="")
                if self._current_user == None:
                    print("English\n\nNot signed in - cannot alter language settings")
                    break
                else:
                    cur = self.db_manager.fetchall("SELECT language FROM settings WHERE username=?", (self._current_user[1], ))
                    print(cur[0][0])
                    changeLanguage = input("Would you like to change languages? (y/n) ")
                    if changeLanguage != "y":
                        break
                    else:
                        print(f'\n{self.menus["change_language"]}')
                        choice = input("Select a language option: ")
                        if choice == "1" or choice == "2":
                            language = "Spanish" if choice == "2" else "English"
                            self.db_manager.execute("UPDATE settings SET language=? WHERE username=?", (language, self._current_user[1]))
                            print(f"Language successfully switched to {language}.")
                        elif choice != "q":
                            print("Invalid choice. Please try again.")

        def important_InCollege_links():
            while True:
                print(menu_seperate) #menu
                print(self.menus["important_links"])

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print(menu_seperate) #menu
                    print(self.menus["copyright_policy"])
                elif choice == "2":
                    print(menu_seperate) #menu
                    print(self.menus["about"])
                elif choice == "3":
                    print(menu_seperate) #menu
                    print(self.menus["accessibility"])
                elif choice == "4":
                    print(menu_seperate) #menu
                    print(self.menus["agreement"])
                elif choice == "5":
                    privacy_policy()
                elif choice == "6":
                    print(menu_seperate) #menu
                    print(self.menus["cookies"])
                elif choice == "7":
                    print(menu_seperate) #menu
                    print(self.menus["copyright_notice"])
                elif choice == "8":
                    print(menu_seperate) #menu
                    print(self.menus["brand_policy"])
                elif choice == "9":
                    guest_controls()
                elif choice == "a":
                    languages_menu()
                elif choice == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")

        # function that holds the main menu for a signed in user and its functionality
        def signed_in_menu(user):
            self._current_user = user

            def learn_skill():
                print(menu_seperate) #menu
                print("Learn A Skill\n-------------------------------")
                # Fetch all records from the 'skills' table
                self.db_manager.execute("SELECT * FROM skills")
                for i, row in enumerate(self.db_manager.fetchall("SELECT * FROM skills")):
                    skill_name, long_description = row[0], row[1]
                    print(f"\nSkill {i+1}: {skill_name}, Description: {long_description}")
                print('\nq: Quit')
                if input("\nPlease Select a Skill: ").lower() != 'q': print("\nUnder Construction")

            def friend_requests():
                while True:
                    print(menu_seperate)
                    print(self.menus["friend_requests"])
                    choice = input("Select an option: ")
                    print()

                    if choice == "1":
                        incoming_requests = self.db_manager.fetchall("SELECT sender, first_name, last_name, university, major FROM friend_requests INNER JOIN accounts ON sender = username WHERE receiver=?", (self._current_user[1], ))
                        if not incoming_requests:
                            print('You have no new friend requests.')
                            continue

                        print(menu_seperate)
                        print("Incoming Friend Requests\n-------------------------------")

                        for i in range(len(incoming_requests)):
                            incoming_requests[i] = list(incoming_requests[i])
                            incoming_requests[i].insert(0, i+1)

                        print(f"You have {len(incoming_requests)} new friend requests!")

                        print("\nFriend Requests:")
                        head = ["Request Num", "Username", "First Name", "Last Name", "University", "Major"]
                        print(tabulate(incoming_requests, headers=head, tablefmt="grid"))

                        manageRequest = input("\nWould you like to manage your requests? (y/n) ")

                        if manageRequest != "y":
                            continue
                        
                        requestNum = input("Enter the request number of the request you wish to respond to: ")
                        try:
                            requestNum = int(requestNum) - 1
                        except:
                            print("Request number did not match. Please try again.")
                            continue

                        if 0 <= requestNum < len(incoming_requests):
                            print(f"\nFriend Request from {incoming_requests[requestNum][1]}:")
                            print("1. Accept\n2. Reject\nq. Quit")
                            response = input("\nSelect a response: ")

                            if response == "1":
                                add_friend(self._current_user[1], incoming_requests[requestNum][1])
                            elif response == "2":
                                self.db_manager.execute("DELETE FROM friend_requests WHERE sender=? AND receiver=?", (incoming_requests[requestNum][1], self._current_user[1]))
                                print("\nFriend request successfully denied.\nThe sender will not be notified you denied their request.")
                            elif response != "q":
                                print("Invalid choice. Please try again.")
                        else:
                            print("Request number did not match. Please try again.")
                    elif choice == "2":
                        pending_requests = self.db_manager.fetchall("SELECT receiver, first_name, last_name, university, major FROM friend_requests INNER JOIN accounts ON receiver = username WHERE sender=?", (self._current_user[1], ))
                        if not pending_requests:
                            print('You have no new outgoingfriend requests.')
                            continue

                        print(menu_seperate)
                        print("Outgoing Friend Requests\n-------------------------------")
                        head = ["Username", "First Name", "Last Name", "University", "Major"]
                        print(tabulate(pending_requests, headers=head, tablefmt="grid"))
                    elif choice == "q":
                        break
                    else:
                        print("Invalid choice. Please try again.")

            def connect_with_user():
                while True:
                    print(menu_seperate)
                    print(self.menus["find_someone"])
                    choice = input("Select an option: ")
                    print()
                    
                    search_by = {"1":"last name", "2":"university", "3":"major"}

                    if choice == "q":
                        break
                    elif choice not in search_by:
                        print("Invalid choice. Please try again.")
                        continue
                    else:
                        print(f"Searching by {search_by[choice]}.")
                        search_for = input(f"Enter the user you wish to find's {search_by[choice]}: ")
                        users_matching = self.db_manager.fetchall(f"SELECT username, first_name, last_name, university, major FROM accounts \
                                                                  WHERE {search_by[choice].replace(' ', '_')}=? AND NOT username=?", (search_for, self._current_user[1]))
                                                
                        if len(users_matching) == 0:
                            print(f'\nNo users found with {search_by[choice]} equal to "{search_for}".')
                            continue
                        
                        for i in range(len(users_matching)):
                            users_matching[i] = list(users_matching[i])
                            users_matching[i].insert(0, i+1)

                        print(f'\nUsers found with {search_by[choice]} equal to "{search_for}":')
                        head = ["User Num", "Username", "First Name", "Last Name", "University", "Major"]
                        print(tabulate(users_matching, headers=head, tablefmt="grid"))

                        sendRequest = input("\nWould you like to send one of these users a friend request? (y/n) ")
                        if sendRequest == "y":
                            receiverNumber = input("Enter the user num of the user to send a friend request: ")
                            try:
                                found = False
                                receiverNumber = int(receiverNumber) - 1
                                if 0 <= receiverNumber < len(users_matching):
                                    send_friend_request(self._current_user[1], users_matching[receiverNumber][1])
                                    found = True

                                if not found:
                                    print("User not found, please try again.")
                            except:
                                print("User Num did not match. Please try again.")

            # function that sends a friend request to the "receiver" user from the "sender" user
            def send_friend_request(sender, receiver):
                request_exists = (self.db_manager.fetchall("SELECT COUNT(*) FROM friend_requests WHERE (sender=? AND receiver=?)",
                                        (sender, receiver)))[0][0]
                
                pending_request = (self.db_manager.fetchall("SELECT COUNT(*) FROM friend_requests WHERE (sender=? AND receiver=?)",
                                        (receiver, sender)))[0][0]
                
                already_friends = (self.db_manager.fetchall("SELECT COUNT(*) FROM friendship WHERE (user_one=? AND user_two=?) OR (user_one=? AND user_two=?)",
                                        (sender, receiver, receiver, sender)))[0][0]

                if request_exists:
                    print(f"\nYou have already sent user {receiver} a friend request.\nYou will be notified when they accept your request.")
                elif pending_request:
                    print(f"\nUser {receiver} has already sent you a friend request.")
                    acceptRequest = input("Would you like to accept their friend request? (y/n) ")
                    if acceptRequest == "y":
                        add_friend(sender, receiver)
                elif already_friends:
                    print(f"\nYou are already friends with {receiver}.")
                else:
                    self.db_manager.execute("INSERT INTO friend_requests(sender, receiver) VALUES (?, ?)", (sender, receiver))
                    print(f"\nFriend request sent to {receiver} successfully!")
            
            # function to add a friendship between the usernames passed as arguments so long as one does not already exist
            def add_friend(friendA, friendB):
                # check if there exists a friendship between the two users already
                friendsOfA = create_friends_list(friendA)
                friendsOfB = create_friends_list(friendB)

                if friendB in friendsOfA and friendA in friendsOfB:
                    print(f"You are already friends with {friendB}\n")
                else:
                    self.db_manager.execute("INSERT INTO friendship(user_one, user_two) VALUES (?, ?)", (friendA, friendB))
                    self.db_manager.execute("DELETE FROM friend_requests WHERE sender=? AND receiver=?", (friendA, friendB))
                    self.db_manager.execute("DELETE FROM friend_requests WHERE sender=? AND receiver=?", (friendB, friendA))
                    print(f"You have successfully added {friendB} to your network!")

            # function to remove a friendship if it exists between current user and passed argument username
            def remove_friend(friend_to_remove):
                current_user_name = self._current_user[1]
                self.db_manager.execute("DELETE FROM friendship WHERE (user_one=? AND user_two=?)", (current_user_name, friend_to_remove))
                self.db_manager.execute("DELETE FROM friendship WHERE (user_one=? AND user_two=?)", (friend_to_remove, current_user_name))
                print(f"\nYou have removed {friend_to_remove} from your network.")

            # function to create and return a list that holds all of the friends of the passed username
            def create_friends_list(current_user_name):
                friends_list = []
                friendships_with_user1 = self.db_manager.fetchall("SELECT user_two, first_name, last_name, university, major \
                        FROM friendship INNER JOIN accounts ON user_two = username WHERE (user_one=?)", (current_user_name, ))
                friendships_with_user2 = self.db_manager.fetchall("SELECT user_one, first_name, last_name, university, major \
                        FROM friendship INNER JOIN accounts ON user_one = username WHERE (user_two=?)", (current_user_name, ))

                friends_list = friendships_with_user1 + friendships_with_user2

                # inserts number to front of the list
                for i in range(len(friends_list)):
                    friends_list[i] = list(friends_list[i])
                    friends_list[i].insert(0, i+1)
                    profile_status = self.db_manager.fetch('SELECT posted FROM profiles WHERE (username=?)', (friends_list[i][1],))
                    if profile_status and profile_status[0] == "yes":
                        friends_list[i].append("View Profile")
                    else:
                        friends_list[i].append("No Profile Posted")

                return friends_list

            def print_friends():
                friends = create_friends_list(self._current_user[1])

                if friends:
                    print("\nFriends List")
                    print("-------------------------------")
                    head = ["Friend Num", "Username", "First Name", "Last Name", "University", "Major", "Profile"]
                    print(tabulate(friends, headers=head, tablefmt="grid"), "\n")

                return friends

            # function to show the user's list of friends, and then provide the option to remove any of them or to quit
            def show_my_network():
                while True:
                    print(menu_seperate)
                    print(self.menus["show_my_network"])
                    user_messages = self.db_manager.fetchall("""SELECT COUNT(*) from messages WHERE recipient=?""", (self._current_user[0],))
                    if user_messages and user_messages[0][0] > 0:
                        print("You have a message waiting for you in the Message Center.")
                    choice = input("Please select an option: ")

                    if choice == "1":
                        friends = print_friends()
                        if not friends:
                            print("\nNo friends at this time.")
                            continue
                        print("\nFriends List Options")
                        print("-------------------------------")
                        print("1. View a Friend's Profile\nq. Quit\n")
                        userChoice = input("Please select an option: ")
                        if (userChoice == 'q'):
                            continue
                        elif (userChoice == '1'):
                            friendNum = input("Enter the number of the friend whose profile you wish to view: ")
                            try:
                                friendNum = int(friendNum)
                            except ValueError:
                                print("\nPlease enter the number associated with the friend in your network.\n")
                                continue

                            # get actual index in friends
                            friendNum -= 1

                            if friendNum >= len(friends):
                                print("\nPlease enter the number associated with the friend in your network.\n")
                                continue

                            if (friends[friendNum][6] == "View Profile"):
                                print("")
                                printProfile(friends[friendNum][1])
                            else:
                                print(f"\n{friends[friendNum][1]} does not currently have a posted profile\n")
                        else:
                            print("Invalid choice. Returning to Show my network screen.")


                    elif choice == "2":
                        friends = print_friends()
                        if not friends:
                            print("\nNo friends to remove.")
                            continue

                        numToDelete = input("Enter the number of the friend you wish to remove (enter q to cancel) : ")
                        if numToDelete == "q":
                            continue

                        try:
                            numToDelete = int(numToDelete)
                        except ValueError:
                            print("Please enter the number associated with the friend in your network.\n")
                            continue

                        # get actual index in friends
                        numToDelete -= 1

                        if numToDelete >= len(friends):
                            print("Please enter the number associated with the friend in your network.\n")
                            continue
                        
                        print(f"You are about to remove {friends[numToDelete][1]} from your network.")
                        user_confirm = input("Do you wish to proceed? (y/n) ")
                        if user_confirm == "y":
                            remove_friend(friends[numToDelete][1])
                        else:
                            print("Removal cancelled.")
                    elif choice == "3":
                        friend_requests()
                    elif choice == "q":
                        break
                    else:
                        print("Invalid choice. Please try again.")

            # function to print a user's profile 
            def printProfile(username):
                print(menu_seperate)
                profileContent = self.db_manager.fetch('SELECT first_name, last_name, title, major, university, about, pastJob1, pastJob2, \
                                                       pastJob3, education, posted FROM profiles WHERE (username=?)', (username,))
                if profileContent[10] != "yes":
                    return
                    # this profile is not posted
                
               # print(menu_separate)
                print(f"\n{profileContent[0]} {profileContent[1]}'s Profile")
                print("-------------------------------")
                print(f"Username:\n----\n{username}\n")
                print(f"Title:\n----\n{profileContent[2]}\n")
                print(f"Major:\n----\n{profileContent[3]}\n")
                print(f"University:\n----\n{profileContent[4]}\n")
                print(f"About {profileContent[0]} {profileContent[1]}:\n----\n{profileContent[5]}\n")

                if profileContent[6] != "n/a" and profileContent[6] != "\n":
                    print(f"Job 1:\n----\n{profileContent[6]}\n")

                if profileContent[7] != "n/a" and profileContent[7] != "\n":
                    print(f"Job 2:\n----\n{profileContent[7]}\n")
                    
                if profileContent[8] != "n/a" and profileContent[8] != "\n":
                    print(f"Job 3:\n----\n{profileContent[8]}\n")

                print(f"Education:\n----\n{profileContent[9]}")
                                
            # function to modify profile's options
            def myProfileOptions():
                username = self._current_user[1]
                profileContent = self.db_manager.fetch('SELECT first_name, last_name, title, major, university, about, pastJob1, pastJob2, \
                                                            pastJob3, education, posted FROM profiles WHERE (username=?)', (username,))
                # profile is not posted, so they have the option to create a profile and are asked if they want to post it there
                if profileContent[10] != "yes":
                    while True and profileContent[10] != "yes":
                        print(menu_seperate)
                        print("My Profile Options\n-------------------------------")
                        print("1. Create a Profile\n2. Post my Profile\nq. Quit\n")
                        userChoice = input("\nPlease enter a provided option: ")

                        if userChoice == "q":
                            break
                        elif userChoice == "1":
                            createProfile(self, username)
                            profileContent = self.db_manager.fetch('SELECT first_name, last_name, title, major, university, about, pastJob1, pastJob2, \
                                                                       pastJob3, education, posted FROM profiles WHERE (username=?)', (username,))

                        elif userChoice == "2":
                            self.db_manager.execute("UPDATE profiles SET posted='yes' WHERE username=?", (username,))
                            print("Your profile has been posted!\n")
                            break
                        else:
                            print("Invalid choice. Please try again.")


                # profile is displayed, so they have the option to update it or view their profile
                if profileContent[10] == "yes":
                    while True:
                        print(menu_seperate)
                        print("My Profile Options\n-------------------------------")
                        print("1. View my Profile\n2. Update my Profile\nq. Quit\n")
                        userChoice = input("\nPlease enter a provided option: ")

                        if userChoice == "q":
                            break
                        elif userChoice == "1":
                            printProfile(username)
                        elif userChoice == "2":
                            updateProfile(self,username)
                        else:
                            print("Invalid choice. Please try again.")
     
            def createProfile(self, username):
                """
                Allows the user to create their profile and save it in the database.
                """
                title = input("Enter your title (e.g. '3rd year Computer Science student'): ")
                title = title.title()
                major = input("Enter your major: ")
                major = major.title()
                university = input("Enter your university name: ")
                university = university.title()
                about = input("Enter a paragraph about yourself: ")
    
                # Experience Section
                # Collect information for up to three past jobs
                past_jobs = ["n/a", "n/a", "n/a"]
                for i in range(3):
                    job_title = input(f"Enter job title for past job {i + 1} (or press Enter to skip): ")
                    if not job_title:
                        break
                    job_title = job_title.title()
                    employer = input("Enter employer: ")
                    employer = employer.title()
                    date_started = input("Enter date started (e.g., MM/YYYY): ")
                    date_ended = input("Enter date ended (e.g., MM/YYYY): ")
                    location = input("Enter location: ")
                    location = location.title()
                    job_description = input("Enter job description: ")
                    past_jobs[i] = f"Title:\n{job_title}\n"
                    past_jobs[i] += f"Employer:\n{employer}\n"
                    past_jobs[i] += f"Date Started:\n{date_started}\n"
                    past_jobs[i] += f"Date Ended:\n{date_ended}\n"
                    past_jobs[i] += f"Location:\n{location}\n"
                    past_jobs[i] += f"Job Description:\n{job_description}\n"

                # Collect education information
                print("Enter Education Information Below:")
                school_name = input("Enter school name: ")
                school_name = school_name.title()
                degree = input("Enter degree: ")
                degree = degree.title()
                years_attended = input("Enter years attended (e.g., YYYY-YYYY): ")

                education = ""
                education += f"School Name:\n{school_name}\n"
                education += f"Degree:\n{degree}\n"
                education += f"Years Attended:\n{years_attended}\n"
            
                self.db_manager.execute("UPDATE profiles SET about=?, title=?, major=?, university=?, pastJob1=?, pastJob2=?, pastJob3=?, education=? \
                                        WHERE username=?", (about, title, major, university, past_jobs[0], past_jobs[1], past_jobs[2], education, username))
                print("Profile saved successfully!")

                # Ask user if they want to post their profile
                post_profile = input("Do you want to post your profile? (yes/no): ").lower()
                if post_profile == "yes":
                    self.db_manager.execute("UPDATE profiles SET posted='yes' WHERE username=?", (username,))
                    print("Profile posted successfully!")
                else:
                    print("Profile not posted.")

            def updateProfile(self, username):
                print(menu_seperate)
                """
                Allows the user to update their profile after it has been posted.
                """
                print("Select the number for the part of your profile you want to update:")
                print("1. Title")
                print("2. Major")
                print("3. University")
                print("4. About")
                print("5. Past Jobs")
                print("6. Education")
                print("q. Exit\n")

                choice = input("Enter your choice: ")

                if choice == "1":
                    new_title = input("Enter your new title: ")
                    new_title = new_title.title()
                    self.db_manager.execute("UPDATE profiles SET title=? WHERE username=?", (new_title, username))
                elif choice == "2":
                    new_major = input("Enter your new major: ")
                    new_major = new_major.title()
                    self.db_manager.execute("UPDATE profiles SET major=? WHERE username=?", (new_major, username))
                elif choice == "3":
                    new_university = input("Enter your new university name: ")
                    new_university = new_university.title()
                    self.db_manager.execute("UPDATE profiles SET university=? WHERE username=?", (new_university, username))
                elif choice == "4":
                    new_about = input("Enter your new About section: ")
                    self.db_manager.execute("UPDATE profiles SET about=? WHERE username=?", (new_about, username))
                elif choice == "5":
                    job_number = input("Enter the job number to update (1, 2, or 3): ")
                    column_name = f"pastJob{job_number}"
                    new_past_job = ""
                    job_title = input(f"Enter job title for past job {job_number}: ")
                    job_title = job_title.title()
                    employer = input("Enter employer: ")
                    employer = employer.title()
                    date_started = input("Enter date started (e.g., MM/YYYY): ")
                    date_ended = input("Enter date ended (e.g., MM/YYYY): ")
                    location = input("Enter location: ")
                    location = location.title()
                    job_description = input("Enter job description: ")
                    new_past_job = f"Title:\n{job_title}\n"
                    new_past_job += f"Employer:\n{employer}\n"
                    new_past_job += f"Date Started:\n{date_started}\n"
                    new_past_job += f"Date Ended:\n{date_ended}\n"
                    new_past_job += f"Location:\n{location}\n"
                    new_past_job += f"Job Description:\n{job_description}\n"
                    self.db_manager.execute(f"UPDATE profiles SET {column_name}=? WHERE username=?", (new_past_job, username))
                elif choice == "6":
                    new_education = ""
                    print("Enter New Education Information Below:")
                    school_name = input("Enter school name: ")
                    school_name = school_name.title()
                    degree = input("Enter degree: ")
                    degree = degree.title()
                    years_attended = input("Enter years attended (e.g., YYYY-YYYY): ")
                    new_education += f"School Name:\n{school_name}\n"
                    new_education += f"Degree:\n{degree}\n"
                    new_education += f"Years Attended:\n{years_attended}\n"
                    self.db_manager.execute("UPDATE profiles SET education=? WHERE username=?", (new_education, username))
                elif choice == "q":
                    print("Exiting profile update.")
                else:
                    print("Invalid choice. Please try again.")

                print("Profile updated successfully!")

            def delete_this_account():
                print(menu_seperate) #menu
                print("Delete Account\n-------------------------------")
                verify = input("Are you sure you want to delete your account? \nThis can not be undone. (y/n) ")
                if(verify == "y"):
                    verify = input("Are you REALLY sure? (y/n) ")
                    if(verify == "y"):
                        print("\nWe are sorry to see you go!")
                        self.db_manager.execute("DELETE FROM accounts WHERE user_id =?;",(self._current_user[0],))
                        # print(self._current_user)
                        self.db_manager.commit()
                        return True

                print("Account deletion canceled, returning to account menu")
                return False

            def jobs():
                def post_job():
                    """
                    Posts a job under the specified username
                    """
                    if self.db_manager.fetch('SELECT COUNT(*) FROM jobs;')[0] >= 10:
                        print("All jobs have been created. Please come back later.")
                        return
                    try:
                        print(menu_seperate) #menu
                        print("Create A Job\n-------------------------------")
                        # Capture job details
                        job_title = input("Enter the job title: \n")
                        job_description = input("Enter the job description: \n")
                        skill_name = input("Enter the required skill name: \n")
                        long_description = input("Enter a long description for the skill: \n")
                        employer = input("Enter the employer: \n")
                        location = input("Enter the location: \n")
                        salary = input("Enter the salary: \n")

                        # ensure that the value entered for salary is numerical, otherwise we print message and leave function
                        try:
                            float(salary)
                        except ValueError:
                            print("Please enter a number for salary")
                            return

                        salary = float(salary)

                        assert job_title and job_description and skill_name and long_description and employer and location and salary, "Error: Cannot leave field Blank."

                        # Insert job details into jobs table
                        if not self.db_manager.post_job(skill_name, long_description, job_title, job_description, employer, location, salary, self._current_user[0]):
                            raise Exception("Could not create job.")
                        
                        all_incollege_users = self.db_manager.fetchall("SELECT * FROM accounts WHERE NOT user_id=?", (self._current_user[0],))
                        message = f'A new job "{job_title}" has been posted.'
                        for user in all_incollege_users:
                            cur_user_id = user[0]
                            self.db_manager.execute("INSERT INTO new_job_notifs(recipientID, message) VALUES(?, ?)", (cur_user_id, message))
                        
                        print('\nSuccessfully posted the job!')

                    except Exception as e:
                        print('Error While Posting Job:\n', e)

                def delete_job():
                    print(menu_seperate)
                    print("Jobs you have posted\n-------------------------------")
                    try:
                        user_id = self._current_user[0]
                        jobs_from_user = self.db_manager.fetchall("SELECT * FROM jobs WHERE posted_by=?", (user_id,))
                        if not jobs_from_user:
                            print("You have no jobs posted.")
                            return
                        
                        display_job = lambda x: f"Title: {x[3]}\nDescription: {x[4]}\nID: {x[0]}\n"
                        jobs = [self.db_manager.find_jobs_by_id(job[0])[0] for job in jobs_from_user]
                        print("\n".join([display_job(j) for j in jobs])) if jobs else print("Could not find any jobs.")

                        print("Delete a job\n-------------------------------")
                        job_id = input("Enter the ID of the job you wish to delete (or enter q to cancel): ")
                        if job_id == "q":
                            return
                        job_id = int(job_id)
                        job_details = self.db_manager.fetchall("SELECT * FROM jobs WHERE job_id=? AND posted_by=?", (job_id, user_id))
                        assert job_details, 'Job not found or you do not have permission to delete this job.'
                        job_title = job_details[0][3]

                        # add all users that have applied to this job to the deleted_job_notifs table
                        applicantIDs = self.db_manager.fetchall("SELECT applicant FROM job_applications WHERE job_id=?", (job_id,))
                        for i in applicantIDs:
                            self.db_manager.execute("INSERT INTO deleted_job_notifs (applicantID, jobID, jobTitle) VALUES (?, ?, ?)", (i[0], job_id, job_title))

                        # Delete the job from jobs table
                        self.db_manager.execute("DELETE FROM jobs WHERE job_id=?", (job_id,))
                        print(f"Job with ID {job_id} has been successfully deleted.\nAll applications to this job have also been deleted.")

                    except Exception as e:
                        print("Error: ", e)

                def search_job():
                    print(menu_seperate)
                    job_titles = self.db_manager.fetchall("SELECT job_title, job_id FROM jobs")
                    print("Titles of Jobs Currently Posted\n-------------------------------")
                    if job_titles:
                        for job_title in job_titles:
                            print(f"Title: {job_title[0]} ID: {job_title[1]}")
                    else:
                        print("No job titles found.")
                    
                    print("\nSearching for Jobs\n-------------------------------")
                    job = input("Enter a job title to search for: ")
                    user_id = self._current_user[0]
                    display_job = lambda x, y: f"Title: {x[3]}\nDescription: {x[4]}\nEmployer: {x[5]}\nSalary: {str(x[7])}\nPosted By: {x[9] + ' '  + x[10]}\nApplied For: {y}\nJob ID: {x[0]}\n"
                    jobs = self.db_manager.find_jobs_by_title(job)
                    
                    def all():  
                        print("\n".join([display_job(j, self.db_manager.user_is_applicant(user_id, j[0])) for j in jobs])) if jobs else print("Could not find any jobs by that name.")
                    
                    def applied_for():
                        print("\n".join([display_job(j, True) for j in jobs if self.db_manager.user_is_applicant(user_id, j[0])])) if jobs else print("Could not find any jobs by that name.")
                    
                    def n_applied_for():
                        print("\n".join([display_job(j, False) for j in jobs if not self.db_manager.user_is_applicant(user_id, j[0])])) if jobs else print("Could not find any jobs by that name.")
                    
                    queries = {'a': all, '1': applied_for, '2': n_applied_for}
                    print("\nEnter Job Query:")
                    query = input('a. Search All Jobs\n1. Search Jobs You\'ve Applied For\n2. Search Jobs You Haven\'t Applied For\nq. Quit\nSelect an option: ')
                    if query == "q": 
                        return
                    print("\nJobs Found\n-------------------------------")
                    queries.get(query, all)()

                def print_jobs_applied_for():
                    print(menu_seperate)
                    print("Jobs You Have Applied For\n-------------------------------")
                    applied_for_jobs = self.db_manager.fetchall("SELECT * from job_applications WHERE applicant=?", (self._current_user[0],))
                    if applied_for_jobs:
                        display_job = lambda x: f"Title: {x[3]}\nDescription: {x[4]}\nEmployer: {x[5]}\nSalary: {str(x[7])}\nPosted By: {x[9] + ' '  + x[10]}\nJob ID: {x[0]}\n"
                        jobs = [self.db_manager.find_jobs_by_id(job[2])[0] for job in applied_for_jobs]
                        print("\n".join([display_job(j) for j in jobs])) if jobs else print("Could not find any jobs by that name.")
                    else:
                        print("You have no currently active job applications.")

                def print_jobs_not_applied_for():
                    print(menu_seperate)
                    print("Jobs You Have Not Applied For\n-------------------------------")
                    applied_for_jobs = self.db_manager.fetchall("SELECT * from job_applications WHERE applicant=?", (self._current_user[0],))

                    applied_job_ids = []
                    for i in applied_for_jobs:
                        applied_job_ids.append(i[2])

                    not_applied_ids = []

                    all_ids = self.db_manager.fetchall("SELECT job_id from jobs")

                    for i in all_ids:
                        if i[0] not in applied_job_ids:
                            not_applied_ids.append(i[0])

                    if not_applied_ids:
                        display_job = lambda x: f"Title: {x[3]}\nDescription: {x[4]}\nEmployer: {x[5]}\nSalary: {str(x[7])}\nPosted By: {x[9] + ' '  + x[10]}\nJob ID: {x[0]}\n"
                        jobs = [self.db_manager.find_jobs_by_id(job)[0] for job in not_applied_ids]
                        print("\n".join([display_job(j) for j in jobs])) if jobs else print("Could not find any jobs by that name.")
                    else:
                        print("There are currently no jobs that you have not already applied to.")
                
                def print_saved_jobs():
                    print(menu_seperate)
                    print("Jobs You Have Saved\n-------------------------------")
                    saved_jobs = self.db_manager.fetchall("SELECT * from job_save WHERE (saved=1 AND applicant=?)", (self._current_user[0],))
                    if saved_jobs:
                        display_job = lambda x: f"Title: {x[3]}\nDescription: {x[4]}\nID: {x[0]}\n"
                        jobs = [self.db_manager.find_jobs_by_id(job[2])[0] for job in saved_jobs]
                        print("\n".join([display_job(j) for j in jobs])) if jobs else print("Could not find any jobs by that name.")
                        # Ask user if they want to unmark a job as saved
                        unsave_job = input("Do you wish to unsave a job? (y/n) ")
                        if unsave_job != "y":
                            return
                        
                        job_id_to_unmark = input("Enter the ID of the job you want to unsave (or enter q to cancel): ")
                        if job_id_to_unmark == "q":
                            return
                        
                        try:
                            job_id_to_unmark = int(job_id_to_unmark)
                            job_exists = self.db_manager.fetchall("SELECT * FROM jobs WHERE job_id=?;", (job_id_to_unmark,))
                            if job_exists:
                                self.db_manager.execute("DELETE FROM job_save WHERE (job_id=? AND applicant=?)", (job_id_to_unmark, self._current_user[0]))
                                print(f"Job with ID {job_id_to_unmark} has been unmarked as saved.")
                            else:
                                print(f"Job with ID {job_id_to_unmark} not found.")
                        except Exception as e:
                            print("Invalid input. Please enter a valid job ID.")
                    else:
                        print("You have no saved jobs.")

                  # Function for allowing users to apply for jobs
                
                def apply_for_job():
                    print(menu_seperate)
                    job_titles = self.db_manager.fetchall("SELECT job_title, job_id FROM jobs")
                    print("Titles of Jobs Currently Posted\n-------------------------------")
                    if job_titles:
                        for job_title in job_titles:
                            print(f"Title: {job_title[0]} - ID: {job_title[1]}")
                    else:
                        print("No job titles found.")
                    print("\n")
                    print("Apply for a Job\n-------------------------------")
                    try:
                        correct_date = lambda x: len(x) == 3 and len(x[0]) == 2 and len(x[1]) == 2 and len(x[2]) == 4
                        user = self._current_user[0]

                        job = input("Enter the job ID (or enter 'q' to quit): ")

                        if job.lower() == 'q':
                            return

                        job = int(job)

                        jobTest = self.db_manager.fetchall("SELECT * FROM jobs WHERE job_id=?;", (job,))

                        assert (self.db_manager.fetchall("SELECT * FROM jobs WHERE job_id=?;",  (job,))[0][0]), 'Job does not exist.'

                        currUserId = self._current_user[0]

                        # check if current user posted the job
                        if jobTest[0]:
                            assert not (jobTest[0][8] == currUserId), "Cannot apply to your own posting."

                        #appl_exists
                        assert not self.db_manager.fetchall("SELECT COUNT(*) FROM job_applications WHERE (applicant=? AND job_id=?)",
                                                (user, job))[0][0], "Cannot apply more than once for a job."
                        gr_date = input("Please Enter your Graduation Date (dd/mm/yyyy): ")
                        assert gr_date and correct_date(gr_date.split('/')), 'Cannot enter empty or incorectly formatted date.'
                        w_date = input("Please Enter your Available Start Date (dd/mm/yyyy): ")
                        assert w_date and correct_date(w_date.split('/')), 'Cannot enter empty or incorectly formatted date.'
                        quals = input("Tell us about yourself and why you want the job: \n")
                        assert quals, 'Cannot Leave field Empty.'
                        self.db_manager.user_apply_job(user, job, gr_date, w_date, quals)
                        
                        # update last job application timestamp value for user to keep track of last job application
                        self.db_manager.execute("UPDATE accounts SET last_job_application_timestamp = CURRENT_TIMESTAMP WHERE user_id=?", (currUserId,))
                        
                        print("\nSuccessfully Applied for the job.")
                    except Exception as e:
                        print("Error Applying for Job:", e)

                def save_a_job():
                    print(menu_seperate)
                    job_titles = self.db_manager.fetchall("SELECT job_title, job_id FROM jobs")
                    print("Titles of Jobs Currently Posted\n-------------------------------")
                    if job_titles:
                        for job_title in job_titles:
                            print(f"Title: {job_title[0]} - ID: {job_title[1]}")
                    else:
                        print("No job titles found.")
                    print("\n")
                    print("Save A Job\n-------------------------------")
                    try:
                        user_id = self._current_user[0]
                        job_id = int(input("Enter the job ID: "))
                        job_exists = self.db_manager.fetchall("SELECT * FROM jobs WHERE job_id=?;", (job_id,))
                        assert job_exists, 'Job does not exist.'

                        job_details = job_exists[0]

                        # Check if the current user is trying to save their own job posting
                        assert not (user_id == job_details[8]), "Cannot save your own posting."

                        # Check if the user has already saved this job
                        saved_job_applied = self.db_manager.fetchall("SELECT COUNT(*) FROM job_applications WHERE (applicant=? AND job_id=? )", (user_id, job_id))[0][0]
                        saved_job = self.db_manager.fetchall("SELECT COUNT(*) FROM job_save WHERE (job_id=? AND applicant=?)", (job_id, user_id))[0][0]

                        print("\nJob Details\n-------------------------------")
                        print(f"Title: {job_details[3]}\nDescription: {job_details[4]}\nEmployer: {job_details[5]}\nSalary: {str(job_details[7])}\nPosted By: {job_details[9] + ' '  + job_details[10]}\nApplied For: {'True' if saved_job_applied else 'False'}\nJob ID: {job_details[0]}\n")

                        if saved_job_applied:
                            print("You have already applied to this job.")
                        elif saved_job:
                            print("You have already saved this job.")
                        else:
                            # Update the saved column to True in the jobs table
                            self.db_manager.execute("INSERT INTO job_save (job_id, applicant, saved) VALUES (?, ?, True)", (job_id, user_id))
                            self.db_manager.commit()
                            print("Job saved successfully!")

                    except Exception as e:
                        print("Error: ", e)
                
                def job_notifications():
                    userID = self._current_user[0]
                    num_jobs_applied_for = (self.db_manager.fetchall("SELECT COUNT(*) from job_applications WHERE applicant=?", (userID,)))[0][0]
    
                    print("Job Notifications:\n-------------------------------")
                    print(f"* You have currently applied for {num_jobs_applied_for} job{'s' if num_jobs_applied_for != 1 else ''}.")

                    # if there are any deleted_job_notif entries with this user's user_id, we will display the notifs and then remove the entries
                    deleted_jobs = self.db_manager.fetchall("SELECT * FROM deleted_job_notifs WHERE applicantID=?", (userID,))
                    if deleted_jobs:
                        for job in deleted_jobs:
                            print(f'* The job "{job[2]}" that you applied for was deleted.')
                        self.db_manager.execute("DELETE FROM deleted_job_notifs where applicantID=?", (userID,))

                    # if there are any new_job_notifs entries with this user's user_id, we will display the notifs and then remove the entries
                    new_job_notifs = self.db_manager.fetchall("SELECT * FROM new_job_notifs WHERE recipientID=?", (userID,))
                    if new_job_notifs:
                        for notification in new_job_notifs:
                            print(f'* {notification[2]}')
                        self.db_manager.execute("DELETE FROM new_job_notifs where recipientID=?", (userID,))


                functions = {'1':search_job, '2':post_job, '3':apply_for_job, '4':print_jobs_applied_for, '5':save_a_job, '6':print_saved_jobs, '7': print_jobs_not_applied_for, '8': delete_job}
                while True:
                    print(menu_seperate)
                    job_notifications()

                    print("\n" + self.menus["jobs"])
                    option = input("\nSelect an option: ")
                    if option in functions:
                        functions[option]()
                    elif option.lower() == "q":
                        break
                    else:
                        print("Invalid choice. Please try again.")

            def messsaging_menu():
                def send_message():
                    while True:
                        #generate list of friends
                        print(menu_seperate)

                        print(self.menus["send_message"])
                        choice = input("Select an option: ")

                        if choice == '1':
                            friend_list = print_friends()
                            if not friend_list:
                                print("\nYou currently have no InCollege friends.")
                                break
                            receiverNumber = input("Enter the friend num of the user to send a message to: ")
                            try:
                                found = False
                                receiverNumber = int(receiverNumber) - 1
                                if 0 <= receiverNumber < len(friend_list):
                                    r_user = friend_list[receiverNumber][1]
                                    sender = self._current_user[0]
                                    recipient = self.db_manager.fetchall("SELECT * FROM accounts WHERE (username =?)", (r_user,))[0][0]
                                    assert recipient, "Error: User could not be found."
                                    is_friend = self.db_manager.check_friendship_status(self._current_user[0], recipient)
                                    # Assert user is friend or user is plus
                                    assert self._current_user[7] or is_friend, "Error: You must be a plus user to send messages to users who you are not friends with."
                                    message = input("What message would you like to send?\nHit \"ENTER\" after you are done typing your message.\n")

                                    self.db_manager.execute(
                                        "INSERT INTO messages(recipient, message, sender) VALUES (?, ?, ?)",
                                        (recipient, message, sender))
                                    print(f"\nMessage sent to '{r_user}' successfully!")

                                    found = True
                                if not found:
                                    print("User not found, please try again.")
                            except Exception as e:
                                print("Error while sending a message:", e)
                        elif choice == '2':
                            if self._current_user[7]:
                                try:
                                    users = self.db_manager.fetchall("SELECT username, first_name, last_name, university, major FROM accounts")
                                    if not users:
                                        print("No users to send messages to.")
                                        break
                                    
                                    for i in range(len(users)):
                                        users[i] = list(users[i])
                                        users[i].insert(0, i+1)

                                    print("\nAll Users List")
                                    print("-------------------------------")
                                    head = ["User Num", "Username", "First Name", "Last Name", "University", "Major"]
                                    print(tabulate(users, headers=head, tablefmt="grid"), "\n")

                                    id = input("Enter the User Num of the user to send a message to (or enter 'q' to quit): ").strip()
                                    if id.lower() == "q": break
                                    id = int(id) - 1

                                    if 0 <= id < len(users):
                                        r_user = users[id][1]
                                        sender = self._current_user[0]
                                        recipient = self.db_manager.fetchall("SELECT * FROM accounts WHERE (username =?)", (r_user,))[0]
                                        assert recipient, "Error: User could not be found."
                                        message = input("What message would you like to send?\nHit \"ENTER\" after you are done typing your message.\n")

                                        self.db_manager.execute(
                                            "INSERT INTO messages(recipient, message, sender) VALUES (?, ?, ?)",
                                            (recipient[0], message, sender))
                                        
                                        print(f"\nMessage sent to '{recipient[3]}' successfully!")
                                    else:
                                        print("User not found, please try again.")
                                except Exception as e:
                                    print("Error while sending a message:", e )
                            else:
                                print("Only plus members may view the list of all users.")
                        elif choice == 'q':
                            break
                        else:
                            print("Invalid choice. Please try again.")

                    return 0
                
                def view_full_message(text, user):
                    print(menu_seperate)
                    print("Full Message\n-------------------------------")
                    print(text)
                    print("\n- " + user)
                
                def delete_message(message_to_delete):
                    recipient = message_to_delete[0]
                    message = message_to_delete[1]
                    sender = message_to_delete[2]

                    self.db_manager.execute("DELETE FROM messages WHERE sender=? AND message=? AND recipient=?",((sender, message, recipient)))
                    print('\nMessage successfully deleted!')
                    return 0
                
                def reply_message(message_to_reply):
                    recipient = message_to_reply[0]
                    message = message_to_reply[1]
                    sender = message_to_reply[2]

                    s_user = self.db_manager.fetchall("SELECT * FROM accounts WHERE (user_id =?)", (sender,))[0][1]

                    reply = input("How would you like to reply to this message?\nHit \"ENTER\" after you are done typing your reply.\n")

                    new_message = reply + "\n\n- " + self._current_user[1] + "\n-------------------\n" + message

                    self.db_manager.execute("INSERT INTO messages(recipient, message, sender) VALUES (?, ?, ?)",(sender, new_message, recipient))
                    print(f"\nReply sent to '{s_user}' successfully!")

                while True:
                    #print a preview of all messages to this user
                    messages = self.db_manager.fetchall("SELECT * FROM messages WHERE (recipient =?)", (self._current_user[0],))
                    modified_messages = []

                    print(menu_seperate)
                    print("Your Messages\n-------------------------------")
                    if not messages:
                        print("You have no new messages.\n")
                    else:
                        for i in range(len(messages)):
                            modified_string = messages[i][1] [:100] + '...' if len(messages[i][1]) > 100 else messages[i][1]
                            username = self.db_manager.fetchall("SELECT * FROM accounts WHERE (user_id =?)", (messages[i][2],))[0][1]
                            modified_messages.append([i+1, username, modified_string])

                        head = ["message ID", "sender", "message"]
                        print(tabulate(modified_messages, headers=head, tablefmt="grid"), "\n")


                    #print the menu
                    print(self.menus["messages"])
                    choice = input("Select an option: ")

                    #send a new message
                    if choice == '1':
                        send_message()
                    #reply to a message
                    elif choice == '2':
                        choice = input("\nEnter the message ID of the message would you like to reply to: ")
                        try:
                            choice = int(choice) - 1
                            reply_message(messages[choice])
                        except:
                            print("\nMessage not found. Please try again.")
                    #view full message
                    elif choice == '3':
                        choice = input("\nEnter the message ID of the message you would like to view in full: ")
                        try:
                            choice = int(choice)-1
                            view_full_message(messages[choice][1],modified_messages[choice][1])
                        except:
                            print("\nMessage not found. Please try again.")
                    #delete a message
                    elif choice == '4':
                        choice = input("\nEnter the message ID of the message you would like to delete: ")
                        try:
                            choice = int(choice) - 1
                            delete_message(messages[choice])
                        except:
                            print("\nMessage not found. Please try again.")
                    #quit
                    elif choice == 'q':
                        break
                    #else invalid
                    else:
                        print("Invalid choice. Please try again.")

            def apply_for_jobs_reminder():
                current_utc_time = datetime.utcnow()
                last_application_time = datetime.strptime((self.db_manager.fetchall("SELECT last_job_application_timestamp FROM accounts WHERE user_id=?", (self._current_user[0],)))[0][0], "%Y-%m-%d %H:%M:%S")
                difference_in_seconds = abs(int((current_utc_time-last_application_time).total_seconds()))
                difference_in_days = difference_in_seconds // (24 * 60 * 60)
                if difference_in_days >= 7:
                    print("It seems like you haven't applied to a job in the last seven days.")
                    print("Remember: you're going to want to have a job when you graduate. Make sure that you start to apply for jobs today!\n")

            options = {'1':jobs, '2':connect_with_user, '3':learn_skill, '4':useful_links, '5':important_InCollege_links, '6':show_my_network,
            '7': myProfileOptions, '8':messsaging_menu}
            
            reminderDisplayed = False
            while True:
                print(menu_seperate) #menu

                print(f"Welcome back to InCollege, {self._current_user[3]}!\n")
                if not reminderDisplayed:
                    apply_for_jobs_reminder()
                    reminderDisplayed = True
                
                numberOfRequests = (self.db_manager.fetchall("SELECT COUNT(*) FROM friend_requests WHERE receiver=?", (self._current_user[1], )))[0][0]
                if numberOfRequests:
                    print(f"You have [{numberOfRequests}] new friend request{'s' if numberOfRequests > 1 else ''}!\n")
                
                user_messages = self.db_manager.fetchall("SELECT COUNT(*) from messages WHERE recipient=?", (self._current_user[0],))
                if user_messages and user_messages[0][0] > 0:
                    print("You have a message waiting for you in the message menu!\n")

                # notify user of no profile
                has_profile = self.db_manager.fetchall("SELECT * FROM profiles WHERE username =? AND posted =?", (self._current_user[1],'yes'))
                if not has_profile:
                    print("Don't forget to create a profile!\n")

                # notify user of one time notifications
                notifications = self.db_manager.fetchall("SELECT * FROM notifications WHERE (user_id =?)",(self._current_user[0],))
                for notification in notifications:
                    print(notification[1])
                #remove one time notifications from table
                self.db_manager.execute("DELETE FROM notifications WHERE (user_id =?)",(self._current_user[0],))

                print(self.menus["signed_in"])

                option = input("Select an option: ")
                if option in options: 
                    options[option]()
                elif option == '9':
                    if delete_this_account() == True: 
                        self._current_user = None
                        break
                elif option.lower() == 'q':
                    print('Succesfully Logged Out.')
                    self._current_user = None
                    break
                else:
                    print("Invalid choice. Please try again.")

        def _login_procedure():
            """
            UI Screen for logging in
            """
            print(menu_seperate) #menu
            print("Log In\n-------------------------------")
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            _acc = self.__login(username=username, password=password)
            if _acc is not None:
                print("\nYou have successfully logged in.")
                signed_in_menu(_acc)
            else:
                print('\nIncorrect username / password, please try again')

        def find_user_from_home_page():
            """
            Finds a user from the home page
            """
            while True:
                print(menu_seperate)
                print(self.menus["find_someone"])
                choice = input("Select an option: ")
                print()

                search_by = {"1": "last name", "2": "university", "3": "major"}

                if choice == "q":
                    break
                elif choice not in search_by:
                    print("Invalid choice. Please try again.")
                    continue
                else:
                    print(f"Searching by {search_by[choice]}.")
                    search_for = input(f"Enter the user you wish to find's {search_by[choice]}: ")
                    users_matching = self.db_manager.fetchall(f"SELECT username, first_name, last_name, university, major FROM accounts \
                                                              WHERE {search_by[choice].replace(' ', '_')}=?", (search_for,))

                    if len(users_matching) == 0:
                        print(f'\nNo users found with {search_by[choice]} equal to "{search_for}".')
                        continue

                    for i in range(len(users_matching)):
                        users_matching[i] = list(users_matching[i])
                        users_matching[i].insert(0, i + 1)

                    print(f'\nUsers found with {search_by[choice]} equal to "{search_for}":')
                    head = ["User Num", "Username", "First Name", "Last Name", "University", "Major"]
                    print(tabulate(users_matching, headers=head, tablefmt="grid"))

         
        def _create_account_procedure():
            try:
                print(menu_seperate) #menu
                print("Create Account\n-------------------------------")
                username = input("Enter unique username: \n")
                password = input("Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n")
                name_first = input("Enter your first name: \n")
                name_last = input("Enter your last name: \n")
                univ = input("Enter your university: \n")
                major = input("Enter your major: \n")

                plus = input("Would you like to create a plus account?(y/n)\nYou will be charged 10$ a month\n")
                plus = (plus == 'y')

                _acc = self._create_account(username=username, password=password, first_name=name_first, last_name=name_last, university=univ, major=major, plus=plus)
                if _acc is not None:
                    print('\nYou have successfully created an account!\nLog in to start using InCollege.')
                    #insert notifications of new account
                    accounts = (self.db_manager.fetchall("SELECT * FROM accounts",))
                    for user in accounts:
                        if user[0] == _acc[0]:
                            continue
                        self.db_manager.execute(
                            "INSERT INTO notifications (user_id, notification) VALUES (?, ?)",
                            ((user[0]), f"New User! {_acc[3]} {_acc[4]} created an account!\n"))

                else:
                    print('\nThere has been an unexpected error while creating your account.')
            except Exception as e:
                print('Error While Creating Account:\n', e)

        # home screen
        while True:
            print(menu_seperate) #menu
            print(self.menus["success_story"])
            choice = input("Select an option: ")
            if choice == "1":
                _login_procedure()
            elif choice == "2":
                _create_account_procedure()
            elif choice == "3":
                find_user_from_home_page()
            elif choice == "4":
                useful_links()
            elif choice == "5":
                print("Video is playing")
            elif choice == "6":
                important_InCollege_links()
            elif choice == "q":
                self._Terminate()
            else:
                print("Invalid choice. Please try again.")

def main():
    InCollegeAppManager().Run()

if __name__ == '__main__':
    main()