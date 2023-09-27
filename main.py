from typing import Tuple, List, Optional, Any, Union
import sqlite3
import os
import bcrypt
from password_strength import PasswordPolicy

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


class inCollegeAppManager:
    def __init__(self, data_file="users.db", skills_file='data/example_skills.txt'):
        self.db_manager = DatabaseManager(data_file)
        self.setup_database()
        self._PasswordPolicy = PasswordPolicy.from_names(
            length=8, uppercase=1, numbers=1, special=1,
        )
        self._current_user = None
        

    def setup_database(self):
        self.db_manager.execute("PRAGMA foreign_keys=ON;")

        self.db_manager.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            user_id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            first_name TEXT NOT NULL,
            last_name TEXT NOT NULL
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
            print("\n\n Meet Sarah, a recent graduate who turned her dreams into reality with inCollege! \n Sarah joined inCollege during her final year, leveraging its vast network to connect with industry professionals.\n Through insightful discussions and mentorship, she honed her skills and gained invaluable advice. \n Thanks to inCollege, Sarah secured her dream job as a marketing strategist at a leading tech company immediately after graduation.\n Her journey from student to success story is proof that inCollege is the ultimate launchpad for your career! \n #CareerSuccess \n #inCollegeImpact \n ")
            print("\nIN COLLEGE")
            print("-----------")
            print("1. Log in")
            print("2. Create a new account")
            print("3. Find someone you know")
            print("4. Useful Links")
            print("5. Play Demo Video")
            print("6. InCollege Important Links")
            print("q. Quit\n")

        def useful_links(from_home_page):

            def general_options(from_home_page):

                def sign_up_options():
                    while True:
                        print("SIGN UP")
                        print("--------")
                        print("1. login")
                        print("2. Create an Account")
                        print("q. Quit")

                        choice = input("Select an option: ")
                        print()
                        if choice == "1":
                            _login_procedure()
                        elif choice == "2":
                            _create_account_procedure()
                        elif choice == "q":
                            break



                while True:
                    print("GENERAL HELP")
                    print("------------")
                    print("1. Help Center")
                    print("2. About")
                    print("3. Press")
                    print("4. Blog")
                    print("5. Careers")
                    print("6. Developers")
                    if from_home_page:
                        print("7. Sign Up")
                    print("q. quit")

                    choice = input("Select an option: ")
                    print()
                    if choice == "1":
                        print("We're here to help\n")
                    elif choice == "2":
                        print("In College: Welcome to In College, the world's largest college student network \nwith many users in many countries and territories worldwide\n")
                    elif choice == "3":
                        print("In College Pressroom: Stay on top of the latest news, updates, and reports\n")
                    elif choice == "4":
                        print("Under Construction\n")
                    elif choice == "5":
                        print("Under Construction\n")
                    elif choice == "6":
                        print("Under Construction\n")
                    elif choice == "7" and from_home_page:
                        sign_up_options()
                    elif choice == "q":
                        break

            while True:
                print("USEFUL LINKS")
                print("------------")
                print("1. General")
                print("2. Browse InCollege")
                print("3. Business Solutions")
                print("4. Directories")
                print("q. quit\n")

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    general_options(from_home_page)
                elif choice == "2":
                    print("Under Construction\n")
                elif choice == "3":
                    print("Under Construction\n")
                elif choice == "4":
                    print("Under Construction\n")
                elif choice == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")
                print()

        def additional_options(user):
            """
            Login options for a user
            """
            self._current_user = user
            def __LearnSkill():
                # Fetch all records from the 'skills' table
                self.db_manager.execute("SELECT * FROM skills")
                for i, row in enumerate(self.db_manager.fetchall("SELECT * FROM skills")):
                    skill_name, long_description = row[0], row[1]
                    print(f"\nSkill {i+1}: {skill_name}, Description: {long_description}")
                print('\nq: Quit')
                if input("\nPlease Select a Skill:").lower() != 'q': print("\nUnder Construction\n")

            def __ConnectWUser():
                find_user_from_account_page()

            def __SearchJob():
                print("\nUnder Construction\n")
            def __DeleteThisAccount():
                verify = input("Are you sure you want to delete your account? \nThis can not be undone. (y/n) ")
                if(verify == "y"):
                    verify = input("Are you REALLY sure? (y/n) ")
                    if(verify == "y"):
                        print("We are sorry to see you go")
                        self.db_manager.execute("DELETE FROM accounts WHERE user_id =?;",(self._current_user[0],))
                        # print(self._current_user)
                        self.db_manager.commit()
                        return True

                print("Account deletion canceled, returning to account menu")
                return False

            """
            TODO: Change this to work with main loop, implement "client/host connection" state transition logic.
            """
            options = {'1':__SearchJob, '2': __ConnectWUser, '3': __LearnSkill, '4': _postJob, '6':important_InCollege_links}
            while True:
                print("\nACCOUNT OPTIONS")
                print("---------------")
                print("1: Search for a job")
                print("2: Find someone you know")
                print("3: Learn a new skill")
                print("4: Post a job")
                print("5. Useful Links")
                print("6: InCollege Important links")
                print("7: Delete my account")
                print("q: Log out")

                option = input("\nPlease Select an Option: ")
                if option.lower() == 'q':
                    self._current_user = None
                    break
                if option == '7':
                    if __DeleteThisAccount() == True: 
                        self._current_user = None
                        break
                if option == "5":
                    useful_links(False)
                if option in options: options[option]()
                
        def _postJob():
            """
            Posts a job under the specified username
            """
            if self.db_manager.fetch('SELECT COUNT(*) FROM jobs;')[0] >= 5:
                print("All jobs have been created. Please come back later.")
                return
            try:
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
            username = input("Enter your username: ")
            password = input("Enter your password: ")
            _acc = self.__login(username=username, password=password)
            if _acc is not None:
                print("You have successfully logged in.")
                additional_options(_acc)
            else:
                print('Incorrect username / password, please try again')


        def find_user_from_home_page():
            """
            Finds a user from the home page
            """
            first_name = input("what is the first name of the person you are looking for:\n")
            last_name = input("what is the last name of the person you are looking for:\n")
            user = self._is_person_in_database(first_name, last_name)
            if user:
                print("looks like they have an account")
                return user
            else:
                print("sorry, they are not part of the InCollege system yet")
                return False
        def find_user_from_account_page():
            first_name = input("what is the first name of the person you are looking for:\n")
            last_name = input("what is the last name of the person you are looking for:\n")
            user = self._is_person_in_database(first_name, last_name)
            if user:
                print("looks like they have an account")
                return user
            else:
                print("sorry, they are not part of the InCollege system yet")
                return False
        
        def guest_controls():
            if self._current_user == None:
                print("Guest Controls\n")
                print(f"{'InCollege Email Notifications:':>31s} On")
                print(f"{'InCollege SMS Notifications:':>31s} On")
                print(f"{'InCollege Targeted Advertising:':>31s} On")
                print(f"{'Language:':>31s} English")
                print("\nNot signed in - cannot alter settings\n")
            else:
                while True:
                    cur = self.db_manager.fetchall("SELECT * FROM settings WHERE username=?", (self._current_user[1], ))
                    print(f"{'InCollege Email Notifications:':>31s} {'Off' if cur[0][1] == 0 else 'On'}")
                    print(f"{'InCollege SMS Notifications:':>31s} {'Off' if cur[0][2] == 0 else 'On'}")
                    print(f"{'InCollege Targeted Advertising:':>31s} {'Off' if cur[0][3] == 0 else 'On'}")
                    print(f"{'Language:':>31s} {cur[0][4]}")

                    change = input("\nWould you like to change one of these settings? (y/n) ")
                    if change == "y":
                        print("1. Email Notifications")
                        print("2. SMS Notifcations")
                        print("3. Targeted Advertising")
                        print("4. Language")
                        print("q. Quit")
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
                        elif option == "4":
                            print("\nChange Language")
                            print("1. English")
                            print("2. Spanish")
                            print("q. Quit")
                            choice = input("Select a language option: ")
                            if choice == "1" or choice == "2":
                                language = "Spanish" if choice == "2" else "English"
                                self.db_manager.execute("UPDATE settings SET language=? WHERE username=?", (language, self._current_user[1]))
                                print("Language successfully switched to", language, ".")
                            elif choice != "q":
                                print("Invalid choice. Please try again.")
                            print()
                        elif option != "q":
                            print("Invalid choice. Please try again.")
                        print()
                    else:
                        break

        def privacy_policy():
            while True:
                print("Privacy Policy")
                print("\n1. Read Privacy Policy")
                print("2. Guest Controls")
                print("q. Quit")

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print("Under Construction")
                elif choice == "2":
                    guest_controls()
                elif choice.lower() == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")
                print()

        def important_InCollege_links():
            while True:
                print("\nInCollege Important Links")
                print("1. A Copyright Notice")
                print("2. About")
                print("3. Accessibility")
                print("4. User Agreement")
                print("5. Privacy Policy")
                print("6. Cookie Policy")
                print("7. Copyright Policy")
                print("8. Brand Policy")
                print("9. Guest Controls")
                print("a. Languages")
                print("q. quit\n")

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print("Under Construction")
                elif choice == "2":
                    print("Under Construction")
                elif choice == "3":
                    print("Under Construction")
                elif choice == "4":
                    print("Under Construction")
                elif choice == "5":
                    privacy_policy()
                elif choice == "6":
                    print("Under Construction")
                elif choice == "7":
                    print("Under Construction")
                elif choice == "8":
                    print("Under Construction")
                elif choice == "9":
                    print("Under Construction")
                elif choice == "a":
                    print("Under Construction")
                elif choice.lower() == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")
                print()

                    
        def _create_account_procedure():
            try:
                username = input("Enter unique username: \n")
                password = input("Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n")
                name_first = input("Enter your first name: \n")
                name_last = input("Enter your last name: \n")
                _acc = self._create_account(username=username, password=password, first_name=name_first, last_name=name_last)
                if _acc is not None:
                    print('Successfully Created Account.')

                else:
                    print('Failed At Creating Account.')
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
        
    def _create_account(self, username, password, first_name, last_name) -> Any:
        """
            Attempts to Create Account with [username, password]. Returns True if successful, otherwise throws an Exception.
        """
        def valid_password(password):
            """ Validates a Password based on requirements. """
            return not self._PasswordPolicy.test(password) and len(password) < 13
        
        if not valid_password(password):
            raise Exception("Invalid password. Please ensure it meets the requirements.")

        if self.db_manager.fetch('SELECT COUNT(*) FROM accounts;')[0] >= 5:
            raise Exception("All permitted accounts have been created. Please come back later.")

        if self.db_manager.fetch('SELECT * FROM accounts WHERE username=?;', (username,)):
            raise Exception("Username already exists. Please choose another one.")

        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        self.db_manager.execute(
            'INSERT INTO accounts (username, password, first_name, last_name) VALUES (?, ?, ?, ?);',
            (username, hashed_password, first_name, last_name))
        
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
    inCollegeAppManager().Run()

if __name__ == '__main__':
    main()