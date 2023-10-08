# Sprint 4 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Herbert J Keels,
# Date created: 10/06/2023
# Last Update: 

import sqlite3
import json
import pytest
import main
from io import StringIO
import re
from io import StringIO

# clear all tables in database
conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
    DELETE FROM settings;
    ''')
conn.commit()

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
        DELETE FROM accounts;
        ''')
conn.commit()

conn = sqlite3.connect('users.db')
cursor = conn.cursor()
cursor.execute('''
        DELETE FROM jobs;
        ''')
conn.commit()
conn.close()

with open('./data/menus.json', 'r') as f:
    menus = json.load(f)['menus']

# function to run the inCollege program and return program output
def runInCollege(capsys):
    # Run the program, and collect the system exit code
    with pytest.raises(SystemExit) as e:
        main.InCollegeAppManager().Run()

    # verify the exit code is 0
    assert e.type == SystemExit
    assert e.value.code == 0

    # return the program's output
    return capsys.readouterr()

def test_request_university_and_major_upon_signup(monkeypatch, capsys):
    # Clear tables to make room for 10 new accounts
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM accounts;
    ''')
    cursor.execute('''
    DELETE FROM friend_requests;
    ''')
    cursor.execute('''
    DELETE FROM friendship;
    ''')
    conn.commit()
    conn.close()

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
    # Clear tables to make room for 10 new accounts
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM accounts;
    ''')
    cursor.execute('''
    DELETE FROM friend_requests;
    ''')
    cursor.execute('''
    DELETE FROM friendship;
    ''')
    conn.commit()
    conn.close()

    userList = ["a", "b", "c", "d", "e","f","g","h","i","j"]
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
    capture = runInCollege(capsys)

    # test that correct creation output appears 10 times
    assert 10 == capture.out.count(expectedCreation)

    # test successful login occurs 10 times, once for each created account
    assert 10 == capture.out.count(expectedLoginSuccess)

def test_search_by_last_name_uni_major(monkeypatch, capsys):
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

def test_friend_request_functionality(monkeypatch, capsys):
    # Below is the expected output
    expectedOut1 = "Friend request sent"
    expectedOut2 = "You have [1] new friend request!"
    expectedOut3 = "You have successfully added a to your network!"
    expectedOut4 = "1 | a          | fname        | lname       | University   | CSE"
    expectedOut5 = "1 | b          | fname        | lname       | University   | CSE"
    expectedOut6 = "1. Accept\n2. Reject\nq. Quit"
    expectedOut7 = "Would you like to manage your requests?"

    # create a StringIO object and set it as the test input
    #log in as a
    userIn = "1\na\n!!!Goodpswd0\n"
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
    #log out
    userIn += 'q\nq\n'
    #log back in as a
    userIn += "1\na\n!!!Goodpswd0\n"
    #check that a is friends with b
    userIn += "7\n1\n"
    #end program
    userIn += "q\nq\nq\n"

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
    assert expectedOut5 in capture.out
    assert expectedOut6 in capture.out
    assert expectedOut7 in capture.out

