import json
from typing import Tuple, List, Optional, Any, Union
import sqlite3
import os
import bcrypt
from password_strength import PasswordPolicy
from tabulate import tabulate

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


class InCollegeAppManager:
    def __init__(self, data_file="users.db", skills_file='data/example_skills.txt'):
        self.db_manager = DatabaseManager(data_file)
        self.setup_database()
        self._PasswordPolicy = PasswordPolicy.from_names(
            length=8, uppercase=1, numbers=1, special=1,
        )
        self._current_user = None
        with open('./data/menus.json', 'r') as f:
            self.menus = json.load(f)['menus']
        
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
            major TEXT NOT NULL
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
            FOREIGN KEY (posted_by) REFERENCES accounts(user_id)
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

    def Run(self): # Can only Serve One Client at a time :(
        """Main loop for user interaction."""
        def intro():
            print(menu_seperate) #menu
            print(self.menus[0]["content"])

        def useful_links(from_home_page):

            def general_options(from_home_page):

                def sign_up_options():
                    while True:
                        print(menu_seperate) #menu
                        print(self.menus[1]["content"])
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
                    print(self.menus[2]['content'])
                    if from_home_page:
                        print("7. Sign Up")
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
                    elif choice == "7" and from_home_page:
                        sign_up_options()
                    elif choice == "q":
                        break
                    else:
                        print("Invalid choice. Please try again.")

            while True:
                print(menu_seperate) #menu
                print(self.menus[3]['content'])

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    general_options(from_home_page)
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

        def additional_options(user):
            """
            Login options for a user
            """
            self._current_user = user
            def learn_skill():
                print(menu_seperate) #menu
                print("Learn A Skill")
                print("-------------------------------")
                # Fetch all records from the 'skills' table
                self.db_manager.execute("SELECT * FROM skills")
                for i, row in enumerate(self.db_manager.fetchall("SELECT * FROM skills")):
                    skill_name, long_description = row[0], row[1]
                    print(f"\nSkill {i+1}: {skill_name}, Description: {long_description}")
                print('\nq: Quit')
                if input("\nPlease Select a Skill: ").lower() != 'q': print("\nUnder Construction")


            def connect_with_user():
                while True:
                    print(menu_seperate)
                    print(self.menus[18]['content'])
                    choice = input("Please select an option: ")
                    print()
                    
                    search_by = {"1":"last name", "2":"university", "3":"major"}

                    if choice == "q":
                        break
                    elif choice not in search_by:
                        print("Invalid choice. Please try again.")
                        continue
                    else:
                        print(f"Searching by {search_by[choice]}")
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
                            receiverNumber = input("Enter the User Num of the user to send a friend request: ")
                            try:
                                found = False
                                for user in users_matching:
                                    if user[0] == int(receiverNumber):
                                        send_friend_request(self._current_user[1], user[1])
                                        found = True
                                if not found:
                                    print("User not found, please try again.")
                            except:
                                print("User Num did not match. Please try again.")

            def search_job():
                print("\nUnder Construction")

            def delete_this_account():
                print(menu_seperate) #menu
                print("Delete Account")
                print("-------------------------------")
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

            """
            TODO: Change this to work with main loop, implement "client/host connection" state transition logic.
            """
            options = {'1':search_job, '2':connect_with_user, '3':learn_skill, '4':post_job, '6':important_InCollege_links}
            while True:
                print(menu_seperate) #menu
                print(self.menus[4]['content'])

                option = input("\nPlease Select an Option: ")
                if option in options: 
                    options[option]()
                elif option == '5':
                    useful_links(False)
                elif option == '7':
                    if delete_this_account() == True: 
                        self._current_user = None
                        break
                elif option.lower() == 'q':
                    print('Succesfully Logged Out.')
                    self._current_user = None
                    break
                else:
                    print("Invalid choice. Please try again.")

        def send_friend_request(sender, receiver):
            requestExists = (self.db_manager.fetchall("SELECT COUNT(*) FROM friend_requests WHERE (sender=? AND receiver=?)",
                                    (sender, receiver)))[0][0]
            
            pendingRequest = (self.db_manager.fetchall("SELECT COUNT(*) FROM friend_requests WHERE (sender=? AND receiver=?)",
                                    (receiver, sender)))[0][0]

            if not requestExists and not pendingRequest:
                self.db_manager.execute("INSERT INTO friend_requests(sender, receiver) VALUES (?, ?)", (sender, receiver))
                print("\nFriend Request Sent Successfully!")
            elif requestExists:
                print(f"You have already sent user {receiver} a friend request.\nYou will be notified when they accept your request.")
            elif pendingRequest:
                print(f"User {receiver} has already sent you a friend request.")
                acceptRequest = input("Would you like to accept their friend request? (y/n) ")
                # insert add friend function
        
        def post_job():
            """
            Posts a job under the specified username
            """
            if self.db_manager.fetch('SELECT COUNT(*) FROM jobs;')[0] >= 5:
                print("All jobs have been created. Please come back later.")
                return
            try:
                print(menu_seperate) #menu
                print("Create A Job")
                print("-------------------------------")
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
                
                print('Successfully Posted Job.')

            except Exception as e:
                print('Error While Posting Job:\n', e)
                
        def _login_procedure():
            """
            UI Screen for logging in
            """
            print(menu_seperate) #menu
            print("Log In")
            print("-------------------------------")
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            _acc = self.__login(username=username, password=password)
            if _acc is not None:
                print("\nYou have successfully logged in.")
                additional_options(_acc)
            else:
                print('\nIncorrect username / password, please try again')

        def find_user_from_home_page():
            """
            Finds a user from the home page
            """
            print(menu_seperate) #menu
            print("Find An InCollege User")
            print("-------------------------------")
            first_name = input("Please enter the first name of the person you are looking for:\n")
            last_name = input("Please enter the last name of the person you are looking for:\n")
            user = self._is_person_in_database(first_name, last_name)
            print("\nLooks like they have an account!") if user else print("\nSorry, they are not part of the InCollege system yet.")
            return user if user else False
            
        def find_user_from_account_page():
            print(menu_seperate) #menu
            print("Find An InCollege User")
            print("-------------------------------")
            first_name = input("Please enter the first name of the person you are looking for:\n")
            last_name = input("Please enter the last name of the person you are looking for:\n")
            user = self._is_person_in_database(first_name, last_name)
            if user:
                print("\nLooks like they have an account!")
                return user
            else:
                print("\nSorry, they are not part of the InCollege system yet.")
                return False
        
        def guest_controls():
            while True:
                print(menu_seperate) #menu
                print("Guest Controls")
                print("-------------------------------")
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
                        print(self.menus[5]["content"])
                        option = input("\nSelect which you would like to change: ")

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
                print(self.menus[6]['content'])

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print(menu_seperate) #menu
                    print(self.menus[7]['content'])
                elif choice == "2":
                    guest_controls()
                elif choice.lower() == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")

        def languages_menu():
            while True:
                print(menu_seperate) #menu
                print(self.menus[8]['content'])
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
                        print(self.menus[9]['content'])
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
                print(self.menus[10]['content'])

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print(menu_seperate) #menu
                    print(self.menus[11]['content'])
                elif choice == "2":
                    print(menu_seperate) #menu
                    print(self.menus[12]['content'])
                elif choice == "3":
                    print(menu_seperate) #menu
                    print(self.menus[13]['content'])
                elif choice == "4":
                    print(menu_seperate) #menu
                    print(self.menus[14]['content'])
                elif choice == "5":
                    privacy_policy()
                elif choice == "6":
                    print(menu_seperate) #menu
                    print(self.menus[15]['content'])
                elif choice == "7":
                    print(menu_seperate) #menu
                    print(self.menus[16]['content'])
                elif choice == "8":
                    print(menu_seperate) #menu
                    print(self.menus[17]['content'])
                elif choice == "9":
                    guest_controls()
                elif choice == "a":
                    languages_menu()
                elif choice.lower() == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")
      
        def _create_account_procedure():
            try:
                print(menu_seperate) #menu
                print("Create Account")
                print("-------------------------------")
                username = input("Enter unique username: \n")
                password = input("Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n")
                name_first = input("Enter your first name: \n")
                name_last = input("Enter your last name: \n")
                univ = input("Enter your university: \n")
                major = input("Enter your major: \n")
                _acc = self._create_account(username=username, password=password, first_name=name_first, last_name=name_last, university=univ, major=major)
                if _acc is not None:
                    print('\nSuccessfully Created Account.')
                else:
                    print('\nFailed At Creating Account.')
            except Exception as e:
                print('Error While Creating Account:\n', e)

        #home screen options
        while True:
            intro()
            choice = input("Select an option: ")
            if choice == "1":
                _login_procedure()
            elif choice == "2":
                _create_account_procedure()
            elif choice == "3":
                find_user_from_home_page()
            elif choice == "4":
                useful_links(True)
            elif choice == "5":
                print("Video is playing")
            elif choice == "6":
                important_InCollege_links()
            elif choice.lower() == "q":
                self._Terminate()
            else:
                print("Invalid choice. Please try again.")
    
    def _Terminate(self):
        """Closes the database connection and exits the program."""
        self.db_manager.close()
        print('Goodbye!')    
        exit(0)
        
    def _create_account(self, username, password, first_name, last_name, university, major) -> Any:
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
            'INSERT INTO accounts (username, password, first_name, last_name, university, major) VALUES (?, ?, ?, ?, ?, ?);',
            (username, hashed_password, first_name, last_name, university, major))
        
        self.db_manager.execute(
            'INSERT INTO settings (username, email_notifs, sms_notifs, target_ads, language) VALUES (?, ?, ?, ?, ?);',
            (username, 1, 1, 1, "English"))

        return self.__login(username=username, password=password)
 # Returns the account from Database

    def __login(self, username: str, password: str):
        user = self.db_manager.fetch('SELECT * FROM accounts WHERE username=?;',    (username,))
        if user:
            hashed_password = user[2].encode('utf-8')  # Encode back to bytes
            if bcrypt.checkpw(password.encode('utf-8'), hashed_password):
                return user
        return None

    # Updated to use db_manager
    def _is_person_in_database(self, first_name, last_name):
        user = self.db_manager.fetch("SELECT * FROM accounts WHERE first_name=? AND last_name =?;", (first_name, last_name))
        return bool(user)

def main():
    InCollegeAppManager().Run()

if __name__ == '__main__':
    main()