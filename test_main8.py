# Sprint 8 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Emin Mahmudzade
# Date created: 11/9/2023
# Last Update: 11/9/2023

import sqlite3
import json
import pytest
import main
from io import StringIO
import re
import uuid
import os
os.system('clean')

with open('./data/menus.json', 'r') as f:
    menus = json.load(f)['menus']

def clear_accounts():
    main.InCollegeAppManager("test.db", False)
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('''
    DELETE FROM accounts;
    ''')
    cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0;")
    conn.commit()
    conn.close()

# clear all tables in database
def __create_user_account_plus():
    try:
        main.InCollegeAppManager("test.db", False)._create_account('a', '!!!Goodpswd0', 'fname', 'lname', 'University', 'Major', True)
    except Exception as e:
        print(e)


def __create_user_account_standard():
    try:
        main.InCollegeAppManager("test.db", False)._create_account('b', '!!!Goodpswd0', 'fname2', 'lname2', 'University2', 'Major2', False)
    except Exception as e:
        print(e)

def __create_user_account_standard2():
    try:
        main.InCollegeAppManager("test.db", False)._create_account('c', '!!!Goodpswd0', 'fname3', 'lname3', 'University3', 'Major3', False)
    except Exception as e:
        print(e)

def __create_user_account_plus2():
    try:
        main.InCollegeAppManager("test.db", False)._create_account('d', '!!!Goodpswd0', 'fname4', 'lname4', 'University4', 'Major4', True)
    except Exception as e:
        print(e)


# function to run the inCollege program and return program output
def runInCollege(capsys):
    # Run the program, and collect the system exit code
    with pytest.raises(SystemExit) as e:
        main.InCollegeAppManager("test.db", False).Run()

    # verify the exit code is 0
    assert e.type == SystemExit
    assert e.value.code == 0

    # return the program's output
    return capsys.readouterr()
# Function to test the login feature
def test_dont_forget_to_create_profile(monkeypatch, capsys):
    # Clear any existing accounts
    clear_accounts()
    
    # Create a user account with plus membership
    __create_user_account_plus()
    userIn = ""

    # Simulate user input for login, account creation, and exit
    userIn += "1\na\n!!!Goodpswd0\nq\nq\nq\n"
    
    # Expected output after login
    expectedOut1 = "Don't forget to create a profile"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    # Run the function and capture output
    capture = runInCollege(capsys)
    print(capture.out)

    # Check if the expected output is present in the captured output
    assert expectedOut1 in capture.out


# Function to test notification for new user joining
def test_new_users_joined_notification(monkeypatch, capsys):
    clear_accounts()
    __create_user_account_plus()
    userIn = ""

    # Simulate user input for login, creating a new user, and exit
    userIn += "1\na\n!!!Goodpswd0\nq\n2\nbb\n!!!Goodpswd0\nfname2\nlname2\nusf\ncs\ny\n1\na\n!!!Goodpswd0\nq\nq\nq\n"

    # Expect to see a notification for the new user joining
    expectedOut1 = "New User! fname2 lname2 created an account!"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)
    
    # Run the function and capture output
    capture = runInCollege(capsys)
    print(capture.out)
    
    # Check if the expected output is present in the captured output
    assert expectedOut1 in capture.out


# Function to test notification for waiting messages
def test_notification_for_waiting_messages(monkeypatch, capsys):
    clear_accounts()
    __create_user_account_plus()
    __create_user_account_standard()

    userIn = ""

    # Simulate user input for sending and receiving messages
    userIn += "1\na\n!!!Goodpswd0\n8\n1\n2\n2\nTest Message Works\nq\nq\nq\n"
    userIn += "1\nb\n!!!Goodpswd0\n8\n3\n1\n2\n1\nHello\nq\nq\nq\n1\na\n!!!Goodpswd0\nq\nq\n"

    # Expect to see a notification for waiting messages
    expectedOut1 = "You have a message waiting for you in the message menu!"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin',userInput)

    # Run the function and capture output
    capture = runInCollege(capsys)
    print(capture.out)
    
    # Check if the expected output is present in the captured output
    assert expectedOut1 in capture.out


# Function to test the number of jobs applied
def test_number_of_jobs_applied(monkeypatch, capsys):
    clear_accounts()
    __create_user_account_plus()

    userIn = ""

    # Simulate user input for login and checking the number of applied jobs
    userIn += "1\na\n!!!Goodpswd0\n1\nq\nq\nq\nq\n"

    # Expect to see the number of applied jobs
    expectedOut1 = "You have currently applied for 0 jobs"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    # Run the function and capture output
    capture = runInCollege(capsys)
    print(capture.out)

    # Check if the expected output is present in the captured output
    assert expectedOut1 in capture.out
