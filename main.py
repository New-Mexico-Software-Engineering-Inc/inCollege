from typing import Tuple, List, Optional, Any, Union
import sqlite3
import os
import bcrypt
from password_strength import PasswordPolicy

class inCollegeAppManager:
    """
        Manages the inCollege App's database, login, and account creation.
    """
    
    def __init__(self, data_file="users.db", skills_file='data\example_skills.txt'):
        """Initializes database connection and sets up password policy."""
        # Establish database connection and create table if not exists
        conn = sqlite3.connect(data_file)
        cursor = conn.cursor()
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS accounts (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        );
        ''')
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS skills (
            skill_name TEXT PRIMARY KEY,
            long_description TEXT UNIQUE NOT NULL
        );
        ''')
        conn.commit()
        

        cursor.execute("SELECT COUNT(*) FROM skills")
        # if table is empty, populate table from file
        if cursor.fetchone()[0] == 0:
            try:
                with open(os.path.join(os.getcwd(), skills_file), 'r') as f:
                    for line in f:
                        skill_name, long_description = line.strip().split('$$$')
                        cursor.execute("INSERT INTO skills (skill_name, long_description) VALUES (?, ?)", (skill_name, long_description))
            except Exception as e:
                print('Error while parsing skills file. Did you configre the file properly?')
                print(e)
            # Commit the changes
            conn.commit()
        self._db = conn
        self._cursor = self._db.cursor()
        self._PasswordPolicy = PasswordPolicy.from_names(
            length = 8, uppercase = 1, numbers = 1, special = 1,
        )
        

    def Run(self, ): # Can only Serve One Client at a time :(
        """Main loop for user interaction."""
        def intro():
            print("\n1. Log in")
            print("2. Create a new account")
            print("3. Exit")
        
        def additional_options(user):
            def __LearnSkill():
                # Fetch all records from the 'skills' table
                self._cursor.execute("SELECT * FROM skills")
                for i, row in enumerate(self._cursor.fetchall()):
                    skill_name, long_description = row
                    print(f"\nSkill {i+1}: {skill_name}, Description: {long_description}")
                input("\nPlease Select an Skill:")
                print('Under Construction')
            def __SearchJob():
                print("Under Construction")
            def __ConnectWUser():
                print('Under Construction')

            """
            TODO: Change this to work with main loop, implement "client/host connection" state transition logic.
            """
            options = {2: __SearchJob, 3:__LearnSkill, 1:__ConnectWUser}
            while True:
                print("\n1. Search for Job")
                print("2. Find Someone you Know")
                print("3. Learn a new skill")
                print("4. Log out")
                option = int(input("\nPlease Select an Option."))
                if option == 4: break
                run_option = options.get(option, None)
                if run_option: run_option()
                
            
            
        def _login_procedure(): 
            
                username = input("Enter your username: ")
                password = input("Enter your password: ")
                _acc = self.__login(username=username, password=password)
                if _acc is not None:
                    print("You have successfully logged in.")
                    additional_options(_acc)
                else:
                    print('Account does not Exist')
                    
        def _create_account_procedure():
            try:
                username = input("Enter unique username: \n")
                password = input("Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n")
                _acc = self._create_account(username=username, password=password)
                if _acc is not None:
                    print('Successfully Created Account.')
                else:
                    print('Failed At Creating Account.')
            except Exception as e:
                print('Error While Creating Account:\n', e)
        
        while True:
            intro()
            choice = input("Select an option: ")
            if choice == "1":
                _login_procedure()
            elif choice == "2":
                _create_account_procedure()
            elif choice == "3":
                self._Terminate()
            else:
                print("Invalid choice. Please try again.")
    
    def _Terminate(self):
        """Closes the database connection and exits the program."""
        self._db.close()
        print('Goodbye!')    
        exit(0)
        
    def _create_account(self, username, password) -> Any:
        """
            Attempts to Create Account with [username, password]. Returns True if successful, otherwise throws an Exception.
        """
        def valid_password(password):
            """ Validates a Password based on requirements. """
            return not self._PasswordPolicy.test(password) and len(password) < 13
        
        if self._cursor.execute('SELECT COUNT(*) FROM accounts;').fetchone()[0] >= 5: raise Exception("All permitted accounts have been created. Please come back later.")
        if self._cursor.execute('SELECT * FROM accounts WHERE username=?;', (username,)).fetchone(): raise Exception("Username already exists. Please choose another one.")
        if not valid_password(password):
                raise Exception("Invalid password. Please ensure it meets the requirements.")
        hashed_password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        self._cursor.execute('INSERT INTO accounts (username, password) VALUES (?, ?);', (username,   hashed_password))
        self._db.commit()
        return self.__login(username=username, password=password)


    def __login(self, username, password):
        user = self._cursor.execute('SELECT * FROM accounts WHERE username=?;', (username,)).fetchone()
        return user if user and bcrypt.checkpw(password.encode('utf-8'), user[1]) else None





# Introduction
def main():
    inCollegeAppManager().Run()

if __name__ == '__main__':
    main()