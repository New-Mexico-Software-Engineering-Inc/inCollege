from typing import Tuple, List, Optional, Any, Union
import sqlite3
import os
import bcrypt
from password_strength import PasswordPolicy

menuSeperate = '\n' + '{:*^150}'.format(' InCollege ') + '\n'

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
            print(menuSeperate)
            print(" Meet Sarah, a recent graduate who turned her dreams into reality with InCollege! \n Sarah joined InCollege during her final year, leveraging its vast network to connect with industry professionals.\n Through insightful discussions and mentorship, she honed her skills and gained invaluable advice. \n Thanks to InCollege, Sarah secured her dream job as a marketing strategist at a leading tech company immediately after graduation.\n Her journey from student to success story is proof that InCollege is the ultimate launchpad for your career! \n #CareerSuccess \n #InCollegeImpact \n ")
            print("\nInCollege")
            print("-------------------------------")
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
                        print(menuSeperate)
                        print("Sign In/Sign Up")
                        print("-------------------------------")
                        print("1. Login")
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
                    print(menuSeperate)
                    print("General Help")
                    print("-------------------------------")
                    print("1. Help Center")
                    print("2. About")
                    print("3. Press")
                    print("4. Blog")
                    print("5. Careers")
                    print("6. Developers")
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
                print(menuSeperate)
                print("Useful Links")
                print("-------------------------------")
                print("1. General")
                print("2. Browse InCollege")
                print("3. Business Solutions")
                print("4. Directories")
                print("q. Quit\n")

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
            def __LearnSkill():
                print(menuSeperate)
                print("Learn A Skill")
                print("-------------------------------")
                # Fetch all records from the 'skills' table
                self.db_manager.execute("SELECT * FROM skills")
                for i, row in enumerate(self.db_manager.fetchall("SELECT * FROM skills")):
                    skill_name, long_description = row[0], row[1]
                    print(f"\nSkill {i+1}: {skill_name}, Description: {long_description}")
                print('\nq: Quit')
                if input("\nPlease Select a Skill: ").lower() != 'q': print("\nUnder Construction")

            def __ConnectWUser():
                find_user_from_account_page()

            def __SearchJob():
                print("\nUnder Construction")

            def __DeleteThisAccount():
                print(menuSeperate)
                print("Delete Account")
                print("-------------------------------")
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
                print(menuSeperate)
                print("Account Options")
                print("-------------------------------")
                print("1: Search for a job")
                print("2: Find someone you know")
                print("3: Learn a new skill")
                print("4: Post a job")
                print("5. Useful Links")
                print("6: InCollege Important links")
                print("7: Delete my account")
                print("q: Log out")

                option = input("\nPlease Select an Option: ")
                if option in options: 
                    options[option]()
                elif option == "5":
                    useful_links(False)
                elif option == '7':
                    if __DeleteThisAccount() == True: 
                        self._current_user = None
                        break
                elif option.lower() == 'q':
                    self._current_user = None
                    break
                else:
                    print("Invalid choice. Please try again.")
                
        def _postJob():
            """
            Posts a job under the specified username
            """
            if self.db_manager.fetch('SELECT COUNT(*) FROM jobs;')[0] >= 5:
                print("All jobs have been created. Please come back later.")
                return
            try:
                print(menuSeperate)
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
            print(menuSeperate)
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
            print(menuSeperate)
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
            
        def find_user_from_account_page():
            print(menuSeperate)
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
                print(menuSeperate)
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
                        print("1. Email Notifications")
                        print("2. SMS Notifcations")
                        print("3. Targeted Advertising")
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
                        elif option != "q":
                            print("Invalid choice. Please try again.")
                        print()
                    else:
                        break

        def privacy_policy():
            while True:
                print(menuSeperate)
                print("Privacy Policy")
                print("-------------------------------")
                print("1. Read Privacy Policy")
                print("2. Guest Controls")
                print("q. Quit")

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print(menuSeperate)
                    print("Privacy Policy for InCollege\n")
                    print("Last Updated: September 28, 2023\n")
                    print("1. Introduction: Welcome to InCollege! This Privacy Policy explains how we handle your information.\n")
                    print("2. Information We Collect: We collect personal and usage data for improving our services.\n")
                    print("3. How We Use Your Information: We use your data for providing and enhancing our services, communication, personalization, and analytics.\n")
                    print("4. Data Sharing and Disclosure: We share data with service providers, for legal compliance, and during business transfers.\n")
                    print("5. Your Choices: You can manage your settings, access, correct, or delete your data.\n")
                    print("6. Security: We implement security measures but cannot guarantee absolute security.\n")
                    print("7. Cookies and Tracking Technologies: We use cookies for analytics and functionality.\n")
                    print("8. Children's Privacy: Our services are not for children under 13.\n")
                    print("9. International Users: Your data may be transferred to and processed in the United States.\n")
                    print("10. Changes to this Privacy Policy: We may update this policy; please review it periodically.\n")
                    print("11. Contact Us: For questions or concerns, contact us at support@InCollege.com\n")
                    print("12. Governing Law: This policy follows the laws of Tampa, Florida.\n")
                    print("Thank you for choosing InCollege!")
                elif choice == "2":
                    guest_controls()
                elif choice.lower() == "q":
                    break
                else:
                    print("Invalid choice. Please try again.")

        def languages_menu():
            while True:
                print(menuSeperate)
                print("Languages")
                print("-------------------------------")
                print("1. English")
                print("2. Spanish")
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
                        print("\nChange Language")
                        print("1. English")
                        print("2. Spanish")
                        print("q. Quit")
                        choice = input("Select a language option: ")
                        if choice == "1" or choice == "2":
                            language = "Spanish" if choice == "2" else "English"
                            self.db_manager.execute("UPDATE settings SET language=? WHERE username=?", (language, self._current_user[1]))
                            print(f"Language successfully switched to {language}.")
                        elif choice != "q":
                            print("Invalid choice. Please try again.")

        def important_InCollege_links():
            while True:
                print(menuSeperate)
                print("InCollege Important Links")
                print("-------------------------------")
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
                print("q. Quit\n")

                choice = input("Select an option: ")
                print()
                if choice == "1":
                    print(menuSeperate)
                    print("InCollege Copyright Policy\n")
                    print("© 2023 InCollege, Inc. All rights reserved.\n")
                    print("Last Updated: September 28, 2023\n")
                    print("This content is protected by copyright laws. Unauthorized use, reproduction, or distribution is prohibited.")
                    print("For inquiries, contact copyright@InCollege.com\n")
                    print("Thank you for respecting our copyright.")
                elif choice == "2":
                    print(menuSeperate)
                    print("About In College")
                    print("Welcome to In College, the world's largest college student network with many users in many countries and territories worldwide!")
                elif choice == "3":
                    print(menuSeperate)
                    print("InCollege Accessibility\n")
                    print("Last Updated: September 28, 2023\n")
                    print("InCollege is dedicated to accessibility for all users. Our Accessibility Menu offers:\n")
                    print("1. High Contrast Mode: Enhances readability.\n")
                    print("2. Screen Reader Compatibility: Optimal for screen readers.\n")
                    print("3. Simplified UI: Streamlined interface.\n")
                    print("4. Help Center: Access resources and support.\n")
                    print("5. Feedback: Report issues and suggest improvements.\n")
                    print("We're committed to an inclusive InCollege experience. Contact us at support@InCollege.com or (813) 555-5555 for assistance or feedback.")
                elif choice == "4":
                    print(menuSeperate)
                    print("User Agreement for InCollege\n")
                    print("Last Updated: September 28, 2023\n")
                    print("Welcome to InCollege! By using our services, you agree to the following terms:\n")
                    print("1. Acceptance: You agree to abide by this agreement.\n")
                    print("2. Eligibility: Users must be at least 13 years old and have parental consent if under 18.\n")
                    print("3. Privacy: Your data usage is governed by our Privacy Policy.\n")
                    print("4. Conduct: Use InCollege lawfully and respectfully. No impersonation, harassment, or infringement of others' rights.\n")
                    print("5. Content: Respect intellectual property rights. Do not use, reproduce, or distribute InCollege's content without permission.\n")
                    print("6. Termination: We can suspend or terminate your InCollege access for violations.\n")
                    print("7. Disclaimers: We provide InCollege 'as is' and are not liable for user-generated content or certain damages.\n")
                    print("8. Changes: We may update this agreement; your use implies acceptance of changes.\n")
                    print("9. Contact: Reach us at support@InCollege.com for questions or concerns.\n")
                    print("10. Governing Law: This agreement follows the laws of Tampa, Florida.\n")
                    print("Thank you for using InCollege. We hope you have a great experience!")
                elif choice == "5":
                    privacy_policy()
                elif choice == "6":
                    print(menuSeperate)
                    print("Cookie Policy for InCollege\n")
                    print("Last Updated: September 28, 2023\n")
                    print("1. What Are Cookies?")
                    print("Cookies are small text files that help us recognize your device and remember preferences.\n")
                    print("2. Why Do We Use Cookies?")
                    print("   - Essential Cookies: Required for basic functionality.")
                    print("   - Analytics Cookies: Improve our services.")
                    print("   - Advertising Cookies: Deliver targeted ads.\n")
                    print("3. Types of Cookies")
                    print("   - Session Cookies: Temporary cookies.")
                    print("   - Persistent Cookies: Remain for a set period.")
                    print("   - First-Party Cookies: Set by InCollege.")
                    print("   - Third-Party Cookies: Set by third parties.\n")
                    print("4. Your Choices")
                    print("Manage cookies via browser settings. Choices may affect site functionality.\n")
                    print("5. Third-Party Cookies")
                    print("Third parties may use cookies; review their policies.\n")
                    print("6. Updates to this Policy")
                    print("We may update this policy; check periodically.\n")
                    print("7. Contact Us")
                    print("Questions or concerns? Contact us at support@InCollege.com\n")
                    print("Thanks for using InCollege!")
                elif choice == "7":
                    print(menuSeperate)
                    print("A Copyright Notice for InCollege\n")
                    print("© 2023 InCollege, Inc. All Rights Reserved.\n")
                    print("Last Updated: September 28, 2023\n")
                    print("The InCollege application and its content are protected by copyright laws. InCollege owns or has licensed all content.")
                    print("By using InCollege, you agree to:\n")
                    print("1. Ownership: All content belongs to InCollege or its providers.\n")
                    print("2. Permissible Use: You can use InCollege for personal, non-commercial use only.\n")
                    print("3. Prohibited: You cannot copy, distribute, modify, or remove copyrights, use for commercial purposes, or reverse engineer the app.\n")
                    print("4. Trademarks: All trademarks are the property of InCollege or respective owners.\n")
                    print("5. Reporting Infringements: Report copyright infringements to copyright@InCollege.com\n")
                    print("6. Contact: For questions, contact us at:")
                    print("            support@InCollege.com")                    
                    print("            (813) 555-555\n")
                    print("InCollege may update this notice; your continued use implies acceptance.\n")
                elif choice == "8":
                    print(menuSeperate)
                    print("InCollege Brand Policy\n")
                    print("Last Updated: September 28, 2023\n")
                    print("Welcome to the InCollege Brand Policy. This document outlines the guidelines for the use of InCollege's branding elements,\
                           \nincluding our logo, name, and other brand assets. By using our branding, you agree to follow these guidelines:\n")
                    print("1. Logo Usage:")
                    print("   - Use the official InCollege logo as provided by us.")
                    print("   - Do not modify, distort, or alter the logo in any way.")
                    print("   - Ensure proper spacing and clear visibility when placing the logo.\n")
                    print("2. Name Usage:")
                    print('   - Refer to our service as "InCollege" (with a capital "I" and "C").')
                    print("   - Do not use our name in a way that suggests affiliation or endorsement without permission.\n")
                    print("3. Color Palette:")
                    print("   - Our primary brand colors are blue and white. Use them consistently.\n")
                    print("4. Typography:")
                    print("   - Use the designated fonts for InCollege materials.\n")
                    print("5. Brand Assets:")
                    print("   - Obtain permission to use any official InCollege brand assets.")
                    print("   - Do not use our branding for misleading or harmful purposes.\n")
                    print("6. Compliance:")
                    print("   - Adhere to applicable laws and regulations when using our branding.\n")
                    print("7. Reporting Misuse:")
                    print("   - If you encounter unauthorized use of InCollege branding, please report it to us at copyright@InCollege.com\n")
                    print("8. Changes to this Policy:")
                    print("   - We may update this Brand Policy; please stay informed about any changes.\n")
                    print("Thank you for respecting InCollege's brand identity. Proper usage of our branding helps maintain consistency and trust in our services.")
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
                print(menuSeperate)
                print("Create Account")
                print("-------------------------------")
                username = input("Enter unique username: \n")
                password = input("Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n")
                name_first = input("Enter your first name: \n")
                name_last = input("Enter your last name: \n")
                _acc = self._create_account(username=username, password=password, first_name=name_first, last_name=name_last)
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
    InCollegeAppManager().Run()

if __name__ == '__main__':
    main()