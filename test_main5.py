# Sprint 5 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Herbert J Keels, Ryan Martinez
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

def test_create_and_view_profile(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    userIn = "1\na\n!!!Goodpswd0\n8\n1\n4th year computer science student\ncomputer science\nuniversity of south florida\n"
    userIn += "Hello! I am a senior computer science student at USF, and I am looking for a full-time job as a software engineer.\n"
    userIn += "Software Engineer Intern\nGoogle\n05/2022\n08/2022\nNew York\n"
    userIn += "Responsible for contributing to software design and development. Collaborated with a team to create secure and reliable software solutions.\n"
    userIn += "Software Engineer Intern\nAmazon\n05/2021\n08/2021\nWashington\n"
    userIn += "Responsible for contributing to software design and development. Collaborated with a team to create secure and reliable software solutions.\n"
    userIn += "Data Analyst Intern\nCiti Bank\n05/2020\n08/2020\nNew York\n"
    userIn += "Responsible for exploring and investigating business performance to gain insight and drive business planning.\n"
    userIn += "Alonso High School\nHigh School Diploma\n2016-2020\nyes\n1\nq\nq\nq\n"

    choiceInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', choiceInput)

    expectedOut = "fname lname's Profile\n-------------------------------\nUsername:\n----\na\n\n"
    expectedOut += "Title:\n----\n4Th Year Computer Science Student\n\nMajor:\n----\nComputer Science\n\nUniversity:\n----\nUniversity Of South Florida\n\n"
    expectedOut += "About fname lname:\n----\nHello! I am a senior computer science student at USF, and I am looking for a full-time job as a software engineer.\n\n"
    expectedOut += "Job 1:\n----\nTitle:\nSoftware Engineer Intern\nEmployer:\nGoogle\nDate Started:\n05/2022\nDate Ended:\n08/2022\nLocation:\nNew York\nJob Description:\n"
    expectedOut += "Responsible for contributing to software design and development. Collaborated with a team to create secure and reliable software solutions.\n\n\n"
    expectedOut += "Job 2:\n----\nTitle:\nSoftware Engineer Intern\nEmployer:\nAmazon\nDate Started:\n05/2021\nDate Ended:\n08/2021\nLocation:\nWashington\nJob Description:\n"
    expectedOut += "Responsible for contributing to software design and development. Collaborated with a team to create secure and reliable software solutions.\n\n\n"
    expectedOut += "Job 3:\n----\nTitle:\nData Analyst Intern\nEmployer:\nCiti Bank\nDate Started:\n05/2020\nDate Ended:\n08/2020\nLocation:\nNew York\nJob Description:\n"
    expectedOut += "Responsible for exploring and investigating business performance to gain insight and drive business planning.\n\n\n"
    expectedOut += "Education:\n----\nSchool Name:\nAlonso High School\nDegree:\nHigh School Diploma\nYears Attended:\n2016-2020\n"

    capture = runInCollege(capsys)

    assert expectedOut in capture.out

def test_incomplete_profile(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    userIn = "1\na\n!!!Goodpswd0\n8\n1\n4th year computer science student\ncomputer science\nuniversity of south florida\n"
    userIn += "\n\n\n\n\nyes\n1\nq\nq\nq\n"
    
    choiceInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', choiceInput)

    expectedOut = "fname lname's Profile\n-------------------------------\nUsername:\n----\na\n\nTitle:\n----\n4Th Year Computer Science Student\n\n"
    expectedOut += "Major:\n----\nComputer Science\n\nUniversity:\n----\nUniversity Of South Florida\n\nAbout fname lname:\n----\n\n\nEducation:\n"
    expectedOut += "----\nSchool Name:\n\nDegree:\n\nYears Attended:\n\n"

    capture = runInCollege(capsys)

    assert expectedOut in capture.out

def test_update_profile(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    userIn = "1\na\n!!!Goodpswd0\n8\n1\n4th year computer science student\ncomputer science\nuniversity of south florida\n"
    userIn += "\n\n\n\n\nyes\n1\n2\n1\n4th year cybersecurity student\n2\n2\ncybersecurity\n2\n3\nuniversity of central florida\n"
    userIn += "2\n4\nHello! I am a senior cybersecurity student at UCF, and I am looking for a full-time job.\n"
    userIn += "2\n5\n1\nCybersecurity Internship\nGoogle\n05/2022\n08/2022\nNew York\ncybersecurity internship.\n2\n6\n"
    userIn += "High School\nHigh School Diploma\n2016-2020\n1\nq\nq\nq\n"
    
    choiceInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', choiceInput)

    expectedOut1 = "fname lname's Profile\n-------------------------------\nUsername:\n----\na\n\nTitle:\n----\n4Th Year Computer Science Student\n\n"
    expectedOut1 += "Major:\n----\nComputer Science\n\nUniversity:\n----\nUniversity Of South Florida\n\nAbout fname lname:\n----\n\n\nEducation:\n"
    expectedOut1 += "----\nSchool Name:\n\nDegree:\n\nYears Attended:\n\n"
    
    expectedOut2 = "Profile updated successfully!" # should appear 6 times

    expectedOut3 = "fname lname's Profile\n-------------------------------\nUsername:\n----\na\n\nTitle:\n----\n4Th Year Cybersecurity Student\n\n"
    expectedOut3 += "Major:\n----\nCybersecurity\n\nUniversity:\n----\nUniversity Of Central Florida\n\nAbout fname lname:\n----\n"
    expectedOut3 += "Hello! I am a senior cybersecurity student at UCF, and I am looking for a full-time job.\n\n"
    expectedOut3 += "Job 1:\n----\nTitle:\nCybersecurity Internship\nEmployer:\nGoogle\nDate Started:\n05/2022\nDate Ended:\n08/2022\nLocation:\n"
    expectedOut3 += "New York\nJob Description:\ncybersecurity internship.\n\n\nEducation:\n----\nSchool Name:\nHigh School\n"
    expectedOut3 += "Degree:\nHigh School Diploma\nYears Attended:\n2016-2020\n\n"

    capture = runInCollege(capsys)

    assert expectedOut1 in capture.out
    assert 6 == capture.out.count(expectedOut2)
    assert expectedOut3 in capture.out

def test_view_friend_profile(monkeypatch, capsys):

    expectedOut1 = 'View Profile'
    expectedOut2 = 'No Profile Posted'


    #clear accounts
    clear_accounts()

    input = ''
    #create three accounts
    input+= '2\na\n!!!Goodpswd0\na\na\na\na\n'
    input +='2\nb\n!!!Goodpswd0\nb\nb\nb\nb\n'
    input +='2\nc\n!!!Goodpswd0\nc\nc\nc\nc\n'

    #b creates a profile and sends a friend request to a
    #log in as b
    input+='1\nb\n!!!Goodpswd0\n'
    #create profile
    input+='8\n1\n4th year computer science student\ncomputer science\nuniversity of south florida\nHello!\n\n"Alonso High School\nHigh School Diploma\n2016-2020\nyes\nq\n'
    #send friend request
    input+='2\n1\na\ny\n1\n'
    #log out
    input+='q\nq\n'

    #c only sends a friend request to a
    #log in as c
    input += '1\nc\n!!!Goodpswd0\n'
    #send friend request
    input += '2\n1\na\ny\n1\n'
    #log out
    input += 'q\nq\n'

    #a accepts all requests, and atempts to view all profiles
    #log in as a
    input += '1\na\n!!!Goodpswd0\n'
    #accept friend requests
    input += '7\n3\n1\ny\n1\n1\n1\ny\n1\n1\nq\n'
    #view friends
    input += '1\n1\n'

    #quit
    input+='q\nq\nq\nq\nq\nq\nq\nq\nq\n'

    choiceInput = StringIO(input)
    monkeypatch.setattr('sys.stdin', choiceInput)
    capture = runInCollege(capsys)

    print(capture.out)
    #assert that (assert once)
    #b has a profile
    assert expectedOut1 in capture.out
    #c does not
    assert expectedOut2 in capture.out
