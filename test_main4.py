# Sprint 4 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Herbert J Keels,
# Date created: 10/06/2023
# Last Update: 10/08/2023

import sqlite3
import json
import pytest
import main
from io import StringIO
import re
from io import StringIO
import uuid
import os
os.system('clean')

with open('./data/menus.json', 'r') as f:
    menus = json.load(f)['menus']

def clear_accounts():
    main.InCollegeAppManager("test.db")
    conn = sqlite3.connect("test.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA foreign_keys=ON;")
    cursor.execute('''
    DELETE FROM accounts;
    ''')
    conn.commit()
    conn.close()

# clear all tables in database
def __create_user_account():
    try:
        main.InCollegeAppManager("test.db")._create_account('a', '!!!Goodpswd0', 'fname', 'lname', 'University', 'Major')
    except Exception as e:
        print(e)

# function to run the inCollege program and return program output
def runInCollege(capsys):
    # Run the program, and collect the system exit code
    with pytest.raises(SystemExit) as e:
        main.InCollegeAppManager("test.db").Run()

    # verify the exit code is 0
    assert e.type == SystemExit
    assert e.value.code == 0

    # return the program's output
    return capsys.readouterr()

def test_request_university_and_major_upon_signup(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Below is the expected output from ///
    expectedOut1 = "Enter unique username: \n"
    expectedOut2 = "Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n"
    expectedOut3 = "Enter your first name: \n"
    expectedOut4 = "Enter your last name: \n"
    expectedOut5 = "Enter your university: \n"
    expectedOut6 = "Enter your major: \n"

    # create a StringIO object and set it as the test input
    choiceInput = StringIO('2\nuser1\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nCSE\nq\n')

    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)

    # Run the program and capture program input
    captured = runInCollege(capsys)

    # compare expected output to actual output
    assert expectedOut1 in captured.out
    assert expectedOut2 in captured.out
    assert expectedOut3 in captured.out
    assert expectedOut4 in captured.out
    assert expectedOut5 in captured.out
    assert expectedOut6 in captured.out

#this test creates 10 users for further testing
def test_create_10_accounts(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Clear tables to make room for 10 new accounts
    userList = [str(uuid.uuid4()) for _ in range(10)]
    pw = "!!!Goodpswd0"
    fname = "fname"
    lname = "lname"
    uni = "University"
    major = "CSE"

    expectedCreation = "\nYou have successfully created an account!\nLog in to start using InCollege."
    expectedLoginSuccess = "\nYou have successfully logged in."

    # create input string to create 10 and login 10 times

    userIn = ""
    for i in range(10):
        userIn += f"2\n{userList[i]}\n{pw}\n{fname}\n{lname}\n{uni}\n{major}\n"

    # loop to verify login works correctly for all 10 following same process as above

    for i in range(10):
        userIn += f"1\n{userList[i]}\n{pw}\nq\n"

    # ends program
    userIn += "q\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    # Run program, test for exit code, and capture output
    _ = runInCollege(capsys)
    # test that correct creation output appears 10 times
    assert 10 <= main.InCollegeAppManager("test.db").db_manager.fetch('SELECT COUNT(*) FROM accounts;')[0]

def test_search_by_last_name_uni_major(monkeypatch, capsys):
    __create_user_account()
    expectedOut = "Users found"

    # create a StringIO object and set it as the test input

    #login
    userIn = '1\na\n!!!Goodpswd0\n2\n'
    #search by name
    userIn += '1\nlname\nn\n'
    #search by uni
    userIn += '2\nUniversity\nn\n'
    #search by major
    userIn += '3\nCSE\nn\n'

    #exit program
    userIn += 'q\nq\nq\n'

    choiceInput = StringIO(userIn)

    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)

    # Run the program and capture program input
    capture = runInCollege(capsys)

    # compare expected output to actual output
    assert 3 == capture.out.count(expectedOut)

def test_send_recive_notify_store_friend_request(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Below is the expected output
    expectedOut1 = "Friend request sent to b successfully!"
    expectedOut2 = "You have [1] new friend request!"
    expectedOut3 = "You have successfully added a to your network!"
    expectedOut4 = "1 | a"

    # create a StringIO object and set it as the test input
    #log in as a
    userIn = "2\nb\n!!!Goodpswd0\nfname\nlname\nusf\nCSE\n1\na\n!!!Goodpswd0\n"
    #send request to b
    userIn += "2\n3\nCSE\ny\n1\n"
    #log out of a
    userIn += "q\nq\n"
    #log in as b
    userIn += "1\nb\n!!!Goodpswd0\n"
    #accept request from a, as b
    userIn += "7\n3\n1\ny\n1\n1\n"
    #check that a and b are friends
    userIn += "q\n1\n"
    #log out and quit
    userIn += 'q\nq\nq\nq\nq\nq\nq\n'

    choiceInput = StringIO(userIn)

    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)

    # Run the program and capture program input
    capture = runInCollege(capsys)

    print(capture)

    # compare expected output to actual output
    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out
    assert expectedOut3 in capture.out
    assert expectedOut4 in capture.out
