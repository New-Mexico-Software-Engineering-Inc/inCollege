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
