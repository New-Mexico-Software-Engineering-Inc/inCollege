# Sprint 3 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Emin Mahmudzade, Jonathan Koch
# Date created: 09/30/2023
# Last Update: 10/1/2023
import sqlite3
import json
import pytest
import main
from io import StringIO
import re
import os
os.system('clean')

with open('./data/menus.json', 'r') as f:
    menus = json.load(f)['menus']

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

def __create_user_account():
    try:
        main.InCollegeAppManager("test.db")._create_account('a', '!!!Goodpswd0', 'fname', 'lname', 'University', 'Major')
    except Exception as e:
        print(e)

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

# Test case to check the functionality of Important Links menu
def test_Important_Links(monkeypatch, capsys):
    # Retrieve expected output for each menu item
    expectedOut = menus['important_links']  # Retrieve content for the 11th menu item
    expectedOut1 = menus['copyright_policy']  # Retrieve content for the 12th menu item
    expectedOut2 = menus['about']  # Retrieve content for the 13th menu item
    expectedOut3 = menus['accessibility']  # Retrieve content for the 14th menu item
    expectedOut4 = menus['agreement']  # Retrieve content for the 15th menu item
    # Expected outputs for specific menu options
    expectedOut5 = "Privacy Policy\n-------------------------------\n1. Read Privacy Policy\n2. Guest Controls\nq. Quit\n"
    expectedOut5_1 = menus['languages']  # Retrieve content for the 8th menu item
    expectedOut5_2 = "InCollege Email Notifications: On"
    expectedOut5_2_1 = "InCollege SMS Notifications: On"
    expectedOut5_2_2 = "InCollege Targeted Advertising: On"
    expectedOut5_2_3 = "Not signed in - cannot alter settings"
    expectedOut6 = menus['cookies']  # Retrieve content for the 16th menu item
    expectedOut7 = menus['copyright_notice']  # Retrieve content for the 17th menu item
    expectedOut8 = menus['privacy_policy']  # Retrieve content for the 18th menu item
    expectedOuta = menus['languages']   # Retrieve content for the 9th menu item

    # Set user input for the test scenario
    userInput = StringIO("6\n1\n2\n3\n4\n5\n1\n2\nq\n6\n7\n8\n9\na\nq\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)

    # Run the program and capture the output
    capture = runInCollege(capsys)

    # Assert that each expected output is present in the captured output
    assert expectedOut in capture.out
    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out
    assert expectedOut3 in capture.out
    assert expectedOut4 in capture.out
    assert expectedOut5 in capture.out
    assert expectedOut5_1 in capture.out
    assert expectedOut5_2 in capture.out
    assert expectedOut5_2_1 in capture.out
    assert expectedOut5_2_2 in capture.out
    assert expectedOut5_2_3 in capture.out
    assert expectedOut6 in capture.out
    assert expectedOut7 in capture.out
    assert expectedOut8 in capture.out
    assert expectedOuta in capture.out

# Test case to check the functionality of turning off guest controls
def test_Change_Guest_Controls_off(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Expected outputs for different scenarios
    expectedOut_def = " InCollege Email Notifications: On\n   InCollege SMS Notifications: On\nInCollege Targeted Advertising: On"
    expectedOut_1st_iteration = "Email notifications successfully turned off."
    expectedOut_2nd_iteration = "SMS notifications successfully turned off."
    expectedOut_3rd_iteration = "Targeted Advertising successfully turned off."

    # Set user input for the test scenario
    userInput = StringIO("1\na\n!!!Goodpswd0\n6\n9\ny\n1\ny\n2\ny\n3\nn\nq\nq\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)

    # Run the program and capture the output
    capture = runInCollege(capsys)

    # Assert that each expected output is present in the captured output
    assert expectedOut_def in capture.out
    assert expectedOut_1st_iteration in capture.out
    assert expectedOut_2nd_iteration in capture.out
    assert expectedOut_3rd_iteration in capture.out

# Test case to check the functionality of turning on guest controls
def test_Change_Guest_Controls_on(monkeypatch, capsys):
    # Expected outputs for different scenarios
    expectedOut_def = " InCollege Email Notifications: Off\n   InCollege SMS Notifications: Off\nInCollege Targeted Advertising: Off"
    expectedOut_1st_iteration = "Email notifications successfully turned on."
    expectedOut_2nd_iteration = "SMS notifications successfully turned on."
    expectedOut_3rd_iteration = "Targeted Advertising successfully turned on."

    # Set user input for the test scenario
    userInput = StringIO("1\na\n!!!Goodpswd0\n6\n9\ny\n1\ny\n2\ny\n3\nn\nq\nq\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)

    # Run the program and capture the output
    capture = runInCollege(capsys)

    # Assert that the expected outputs are present in the captured output
    assert expectedOut_def in capture.out
    assert expectedOut_1st_iteration in capture.out
    assert expectedOut_2nd_iteration in capture.out
    assert expectedOut_3rd_iteration in capture.out
 
# Test case to check the functionality of changing language to Spanish
def test_Change_Language_to_Spanish(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Expected outputs for different scenarios
    expectedOut_def = "1. English\n2. Spanish"
    expectedOut_1st_iteration = "Language successfully switched to Spanish."

    # Set user input for the test scenario
    userInput = StringIO("1\na\n!!!Goodpswd0\n6\na\ny\n2\nn\nq\nq\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)

    # Run the program and capture the output
    capture = runInCollege(capsys)

    # Assert that the expected outputs are present in the captured output
    assert expectedOut_def in capture.out
    assert expectedOut_1st_iteration in capture.out

# Test case to check the functionality of changing language to English
def test_Change_Language_to_English(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Expected outputs for different scenarios
    expectedOut_def = "1. English\n2. Spanish"
    expectedOut_1st_iteration = "Language successfully switched to English."

    # Set user input for the test scenario
    userInput = StringIO("1\na\n!!!Goodpswd0\n6\na\ny\n1\nn\nq\nq\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)

    # Run the program and capture the output
    capture = runInCollege(capsys)

    # Assert that the expected outputs are present in the captured output
    assert expectedOut_def in capture.out
    assert expectedOut_1st_iteration in capture.out
    
# Test case to check the functionality of Useful Links menu
def test_Useful_Links(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Retrieve expected output for specific menu items
    expectedOut = menus['general_help']  # Retrieve content for the 3rd menu item
    expectedOut1 = "We're here to help!"  # Expected message for the 1st menu option
    expectedOut2 = "In College: Welcome to In College, the world's largest college student network with many users in many countries and territories worldwide!"  # Expected message for the 2nd menu option
    expectedOut3 = "In College Pressroom: Stay on top of the latest news, updates, and reports"  # Expected message for the 3rd menu option
    
    # Set user input for the test scenario
    userInput = StringIO("4\n1\n1\n2\n3\n4\n5\n6\nq\n2\n3\n4\nq\nq\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)
    
    # Run the program and capture the output
    capture = runInCollege(capsys)
    
    # Assert that each expected output is present in the captured output
    assert expectedOut in capture.out
    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out
    assert expectedOut3 in capture.out

# Test case to check the functionality of deleting user settings
def test_Delete_Settings(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    # Expected outputs for different scenarios
    expectedOut1 = "successfully turned off"  # Expected message when user settings are deleted
    expectedOut2 = " InCollege Email Notifications: On\n   InCollege SMS Notifications: On\nInCollege Targeted Advertising: On"  # Expected user settings before deletion

    # Set user input for the test scenario
    userInput = StringIO("1\na\n!!!Goodpswd0\n6\n9\ny\n2\nn\nq\nq\nq\n2\ne\n!!!Goodpswd0\nfname1\nlname1\n1\na\n!!!Goodpswd0\n6\n9\ny\n2\nn\nq\nq\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)
    
    # Run the program and capture the output
    capture = runInCollege(capsys)
    print(capture)

    # Assert that the expected outputs are present in the captured output
    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out

def test_Useful_Links_After_Login(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    # Set user input for the test scenario
    userInput = StringIO("1\na\n!!!Goodpswd0\n5\n1\nq\nq\nq\nq\n")
    
    monkeypatch.setattr('sys.stdin', userInput)

    # Run the program and capture the output
    capture = runInCollege(capsys)
    out = capture.out[capture.out.lower().index("successfully logged in"):capture.out.lower().index("succesfully logged out")].lower()
    with open('debug.log', 'w') as f:
        f.write(out)
    # Assert that the expected outputs are present in the captured output
    assert "sign up" not in out
    assert "useful links" in out
    
def test_General_Links_Options(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    # Set user input for the test scenario
    userInput = StringIO("4\n1\n7\nq\nq\nq\nq\n")
    
    monkeypatch.setattr('sys.stdin', userInput)

    # Run the program and capture the output
    capture = runInCollege(capsys)
    out =capture.out.lower()
    context = re.search(r"sign in/sign up(.*\n){2}", out)
    assert context is not None, 'Failed Searching for Sign Up.'
    out = out[context.end()::]
    for option in ('login', 'create an account', 'quit'):
        assert option in out
