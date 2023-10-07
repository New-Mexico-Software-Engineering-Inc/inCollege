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
    # Below is the expected output from ///
    expectedOut1 = "Enter unique username: \n"
    expectedOut2 = "Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n"
    expectedOut3 = "Enter your first name: \n"
    expectedOut4 = "Enter your last name: \n"
    expectedOut5 = "Enter your university: \n"
    expectedOut6 = "Enter your major: \n"

    # create a StringIO object and set it as the test input
    #create 2 users for later testing
    choiceInput = StringIO('2\nuser1\n!!!Goodpassword0\nfirstname1\nlastname1\nUniversity\nCSE\n2\nuser2\n!!!Goodpassword0\nfirstname2\nlastname2\nUniversity\nCSE\nq\n')

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

