# Sprint 6 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Jonathan Koch
# Date created: 10/25/2023
# Last Update: 10/25/2023

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

def test_search_for_job(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    # we will attempt to create 5 jobs, so here are lists corresponding to the necessary entries for 5 jobs
    jobTitles = ['Job A', 'Job B', 'Job C', 'Job D', 'Job E']
    jobDescriptions = ['Desc A', 'Desc B', 'Desc C', 'Desc D', 'Desc E']
    requiredSkill = ['Skill A', 'Skill B', 'Skill C', 'Skill D', 'Skill E']
    longDescriptions = ['long Desc A', 'long Desc B', 'long Desc C', 'long Desc D', 'long Desc E']
    employers = ['employer A', 'employer B', 'employer C', 'employer D', 'employer E']
    locations = ['Location A', 'Location B', 'Location C', 'Location D', 'Location E']
    salaries = [100.0, 200.0, 300.0, 400.0, 500.0]

    # first we must login with an existing account
    userIn = '1\na\n!!!Goodpswd0\n'

    # now we will try to create 5 jobs so we will loop the following inputs 5 times for each list entry
    # 4 - post a job, then enter all criteria, then 4 - post a job, then enter all criteria, ...
    for i in range(5):
        userIn += f'4\n{jobTitles[i]}\n{jobDescriptions[i]}\n{requiredSkill[i]}\n{longDescriptions[i]}\n'
        userIn += f'{employers[i]}\n{locations[i]}\n{salaries[i]}\n'

    # then logout and exit the program
    userIn += 'q\nq\n'
    print(userIn)
    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)
    _ = runInCollege(capsys)

    userIn = '1\na\n!!!Goodpswd0\n' # sign in
    userIn +='1\nJob\na\n' # Search for all jobs
    # then logout and exit the program
    userIn += 'q\nq\n'
    # return
    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)
    capture = runInCollege(capsys)
    
    for (job, desc, salary, employer)  in zip(jobTitles, jobDescriptions, salaries, employers):
        assert job in capture.out, 'Unsucessful in finding jobs'
        assert desc in capture.out, 'Unsucessful in finding jobs'
        assert str(salary) in capture.out, 'Unsucessful in finding jobs'
        assert employer in capture.out, 'Unsucessful in finding jobs'
