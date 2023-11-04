# Sprint 6 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Austin Martin,
# Date created: 11/2/2023
# Last Update: 11/2/2023

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


def test_plus_account_message_anybody_and_its_received(monkeypatch, capsys):
    clear_accounts()
    __create_user_account_plus()
    __create_user_account_standard()
    __create_user_account_standard2()

    userIn = ""

    # login to plus account, see all active accounts, message new account
    userIn += "1\na\n!!!Goodpswd0\n8\n1\n2\n3\nTest Message\nq\nq\nq\n"

    # sign into new standard account, verify message was sent, exit
    userIn += "1\nc\n!!!Goodpswd0\n8\nq\nq\nq\n"

    # expect to see an option to have message sent to anyone, but only works for plus members
    expectedOut1 = "View the list of all users (Plus)"

    # since this member is a plus member, we expect to see all 3 accounts presented like below
    expectedOut2 = "Name: fname lname, ID: 1, University: University, Major: Major"
    expectedOut3 = "Name: fname2 lname2, ID: 2, University: University2, Major: Major2"
    expectedOut4 = "Name: fname3 lname3, ID: 3, University: University3, Major: Major3"

    # after sending the message to user c, user c should see the sender and the message
    expectedOut5 = "message ID"
    expectedOut6 = "sender"
    expectedOut7 = "message"
    expectedOut8 = "Test Message"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)
    print(capture.out)

    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out
    assert expectedOut3 in capture.out
    assert expectedOut4 in capture.out
    assert expectedOut5 in capture.out
    assert expectedOut6 in capture.out
    assert expectedOut7 in capture.out
    assert expectedOut8 in capture.out

def test_standard_can_only_send_messages_to_friends(monkeypatch, capsys):
    clear_accounts()
    __create_user_account_plus()
    __create_user_account_standard()
    __create_user_account_standard2()

    # sign in as user b, send friend request to user c (both standard accounts)
    userIn = ""
    userIn += "1\nb\n!!!Goodpswd0\n2\n1\nlname3\ny\n1\nq\nq\n"

    # sign into user c, accept request
    userIn += "1\nc\n!!!Goodpswd0\n6\n3\n1\ny\n1\n1\n1\nq\nq\n"

    # navigate to message menu, attempt to view all users (fails), then send a message to your friend b
    userIn += "8\n1\n2\n1\n1\nTest Message\nq\nq\nq\n"

    # sign back in as b, verify message sent by friend appears
    userIn += "1\nb\n!!!Goodpswd0\n8\nq\nq\nq\n"

    # expect to see a failure message when trying to see all users as a standard account
    expectedOut1 = "Only plus members may view the list of all users"

    # expect to see the friend's message actually shows up when receiving friend checks their message menu
    expectedOut2 = "message ID"
    expectedOut3 = "sender"
    expectedOut4 = "message"
    expectedOut5 = "Test Message"

    # expect to see the friends list printed when sending message to a friend, so b's account info is shown
    expectedOut6 = "b"
    expectedOut7 = "fname2"
    expectedOut8 = "lname2"
    expectedOut9 = "University2"
    expectedOut10 = "Major2"
    expectedOut11 = "No Profile Posted"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out
    assert expectedOut3 in capture.out
    assert expectedOut4 in capture.out
    assert expectedOut5 in capture.out
    assert expectedOut6 in capture.out
    assert expectedOut7 in capture.out
    assert expectedOut8 in capture.out
    assert expectedOut9 in capture.out
    assert expectedOut10 in capture.out
    assert expectedOut11 in capture.out

def test_signup_asked_plus_and_payment_disclaimer(monkeypatch, capsys):
    clear_accounts()

    userIn = ""

    # create new account option, enter credentials, then quit
    userIn += "2\nd\n!!!Goodpswd0\nd\nlast\nuniv\nmaj\nn\nq\n"

    # expect to see an option asking to sign up for plus, and a disclaimer stating it costs $10/month
    expectedOut = "Would you like to create a plus account?(y/n)\nYou will be charged 10$ a month"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    assert expectedOut in capture.out

def test_select_and_read_message(monkeypatch, capsys):
    clear_accounts()
    __create_user_account_plus()
    __create_user_account_plus2()

    userIn = ""

    # sign into account d (plus), send message to account a, then sign out
    userIn += "1\nd\n!!!Goodpswd0\n8\n1\n2\n1\nTest Message Works\nq\nq\nq\n"

    # sign into account a, view message and sender fully, then exit
    userIn += "1\na\n!!!Goodpswd0\n8\n3\n1\nq\nq\nq\n"

    # expect to see actual message printed, as well as a signature showing sender
    expectedOut1 = "Test Message Works"
    expectedOut2 = "- d"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin',userInput)

    capture = runInCollege(capsys)

    print(capture.out)
    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out