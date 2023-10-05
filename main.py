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
    def __init__(self, data_file="users.db"):
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

                for i in range(len(friends_list)):
                    friends_list[i] = list(friends_list[i])
                    friends_list[i].insert(0, i+1)

                return friends_list

            def print_friends():
                friends = create_friends_list(self._current_user[1])

                if friends:
                    print("\nFriends List")
                    print("-------------------------------")
                    head = ["Friend Num", "Username", "First Name", "Last Name", "University", "Major"]
                    print(tabulate(friends, headers=head, tablefmt="grid"), "\n")

                return friends

            # function to show the user's list of friends, and then provide the option to remove any of them or to quit
            def show_my_network():
                while True:
                    print(menu_seperate)
                    print(self.menus["show_my_network"])
                    choice = input("Please select an option: ")

                    if choice == "1":
                        friends = print_friends()
                        if not friends:
                            print("\nNo friends at this time.")
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

            def search_job():
                print("\nUnder Construction")

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

            def post_job():
                """
                Posts a job under the specified username
                """
                if self.db_manager.fetch('SELECT COUNT(*) FROM jobs;')[0] >= 5:
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
                    
                    print('Successfully Posted Job.')

                except Exception as e:
                    print('Error While Posting Job:\n', e)
            
            options = {'1':search_job, '2':connect_with_user, '3':learn_skill, '4':post_job, '5':useful_links, '6':important_InCollege_links, '7':show_my_network}
            while True:
                print(menu_seperate) #menu
                numberOfRequests = (self.db_manager.fetchall("SELECT COUNT(*) FROM friend_requests WHERE receiver=?", (self._current_user[1], )))[0][0]
                if numberOfRequests:
                    print(f"You have [{numberOfRequests}] new friend request{'s' if numberOfRequests > 1 else ''}!\n")
                print(self.menus["signed_in"])

                option = input("Select an option: ")
                if option in options: 
                    options[option]()
                elif option == '8':
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
            print(menu_seperate) #menu
            print("Find An InCollege User\n-------------------------------")
            first_name = input("Please enter the first name of the person you are looking for:\n")
            last_name = input("Please enter the last name of the person you are looking for:\n")
            user = self._is_person_in_database(first_name, last_name)
            print("\nLooks like they have an account!") if user else print("\nThey are not part of the InCollege system yet.")
            return user if user else False
         
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
                _acc = self._create_account(username=username, password=password, first_name=name_first, last_name=name_last, university=univ, major=major)
                if _acc is not None:
                    print('\nYou have successfully created an account!\nLog in to start using InCollege.')
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