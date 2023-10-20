# Sprint 5 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Herbert J Keels,
# Date created: 10/20/2023
# Last Update: 10/20/2023

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
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('''
    DELETE FROM accounts;
    ''')
    conn.commit()
    conn.close()

# clear all tables in database
def __create_user_account():
    try:
        main.InCollegeAppManager()._create_account('a', '!!!Goodpswd0', 'fname', 'lname', 'University', 'Major')
    except Exception as e:
        print(e)

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

