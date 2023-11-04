# Sprint 6 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Jonathan Koch, Austin Martin, Ryan Martinez
# Date created: 10/25/2023
# Last Update: 10/28/2023

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
    main.InCollegeAppManager("test.db")
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
def __create_user_account():
    try:
        main.InCollegeAppManager("test.db")._create_account('a', '!!!Goodpswd0', 'fname', 'lname', 'University', 'Major')
    except Exception as e:
        print(e)

def __create_user_account2():
    try:
        main.InCollegeAppManager("test.db")._create_account('b', '!!!Goodpswd0', 'fname2', 'lname2', 'University', 'Major')
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
