# Sprint 1 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Ryan Martinez, Austin Martin 
# Date created: 09/15/2023
# Last Update: 09/24/2023
import sqlite3
import pytest
import main
from io import StringIO
import uuid
import os
os.system('clean')

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

# function to verify that there are 3 options on Homepage, and ensure user is prompted with selection
def test_HomepageOptions(monkeypatch, capsys):
    # Below is the expected output from the homescreen after the user exits
    expectedOut = "1. Log in\n2. Create a new account\n3. Find someone you know\n4. Useful Links\n5. Play Demo Video\n6. InCollege Important Links\nq. Quit"

    # create a StringIO object and set it as the test input 
    choiceInput = StringIO('q\n')
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)
    # Run the program and capture program input
    captured = runInCollege(capsys)
    # compare expected output to actual output
    assert expectedOut in captured.out


# this test verifies that when option 2 is selected, to create an account,
# that the program prompts the user to enter a username and password
# the actual success or failure of the account creation will be tested in next test
def test_CreateAccount(monkeypatch, capsys):
    clear_accounts()
    # these two prompts will be printed in a correct run
    expected = "You have successfully created an account!"
    # set input to select create account option (2), then enter username 
    # then enter password, and first and last name, then to quit after account is attempted to
    # be created (3)
    uname = str(uuid.uuid4())
    userInput = StringIO(f'2\n{uname}\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\nq\n')
    monkeypatch.setattr('sys.stdin', userInput)

    # Run program, test for exit code, and capture output
    capture = runInCollege(capsys)

    # verify that the two prompts are within the output
    assert expected in capture.out


# test that all of the presented cases of weak passwords will fail
# to create an account - passwords must be minimum of 8 chars, max of 12 chars,
# contain at least 1 capital letter, digit, and special character
def test_PasswordStrength(monkeypatch, capsys):
    clear_accounts()
    userName = 'a'
    # the passwords are all fine except for the one specified flaw:
    # too short, too long, no capital, no digit, no special char
    weakPW= ["Abcde1!", "Abcdefghijk1!", "gobulls24!", "GoBulls!", "GoBulls24"]
    fNameTest = "austin"
    lNameTest = "martin"
    University = "University"
    Major = "CSE"

    userIn = ""

    # create input sequence that will attempt to make an account
    # with all 5 of these weak passwords
    # enter 2 to create account, username, weakPW1, 2, username, weakPW2, ...
    for i in range(5):
        userIn += f"2\n{userName}\n{weakPW[i]}\n{fNameTest}\n{lNameTest}\n{University}\n{Major}\n"

    # exit program after testing
    userIn += "q\n"

    # we expect to see this prompt 5 times, 1 for each weak password
    expected = "Invalid password. Please ensure it meets the requirements."

    # we should not see any successful account creation prompts
    notExpected = "Successfully Created Account."

    userInput = StringIO(userIn)
    monkeypatch.setattr("sys.stdin", userInput)

    # Run program, test for exit code, and capture output
    capture = runInCollege(capsys)

    # test that the expected output occured 5 total times, demonstrating
    # that all 5 attempted passwords were too weak
    assert 5 == capture.out.count(expected)

    # test that there is no occurence of a account creation statement
    assert notExpected not in capture.out

# updated for first and last names on 9/21/23
# test when database is empty, and this will create 5 accounts and
# test that each is able to log in with the created credentials

def test_Create5Accounts(monkeypatch, capsys):
    # Clear accounts table to make room for 5 new accounts
    clear_accounts()

    userList = ["a", "b", "c", "d", "e"]
    pw = "!!!Goodpswd0"
    fname = "fname"
    lname = "lname"
    uni = "University"
    major = "CSE"

    expectedCreation = "\nYou have successfully created an account!\nLog in to start using InCollege."
    expectedLoginSuccess = "\nYou have successfully logged in."

    # create input string to create 10 and login 10 times

    userIn = ""
    for i in range(5):
        userIn += f"2\n{userList[i]}\n{pw}\n{fname}\n{lname}\n{uni}\n{major}\n"

    # loop to verify login works correctly for all 10 following same process as above

    for i in range(5):
        userIn += f"1\n{userList[i]}\n{pw}\nq\n"

    # ends program
    userIn += "q\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    # Run program, test for exit code, and capture output
    capture = runInCollege(capsys)

    # test that correct creation output appears 5 times
    assert 5 == capture.out.count(expectedCreation)

    # test successful login occurs 5 times, once for each created account
    assert 5 == capture.out.count(expectedLoginSuccess)

# run this test immediately after test_create5Accounts so that 5
# accounts are already created, then we will test that attempting
# to create a 6th account does not result in a successful creation
# !!! test must be done after test_create5Accounts so that all !!!
# !!! 5 available user accounts have already been made         !!!

"""
def test_Create6thAccountFails(monkeypatch, capsys):
    # expect this message to prompt when creation fails:
    expectedCreationFailed = "Error While Creating Account:\n All permitted accounts have been created. Please come back later."

    # expect this message to prompt when sign in fails
    expectedLoginFailed = "Incorrect username / password, please try again"

    # create user inputs to create a new account, user: f, pw: GoBulls29!
    # and to then attempt to login with this account information
    userIn = "2\nf\nGoBulls29!\n\naustin\nmartin\n1\nf\nGoBulls29!\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    # Run program, test for exit code, and capture output
    capture = runInCollege(capsys)

    # test that account failed to create
    assert expectedCreationFailed in capture.out

    # test that login attempt with 6th account credentials fails
    assert expectedLoginFailed in capture.out
"""


# test attempts to login with incorrect credentials 25 times, testing for any
# limit on login attempts within that range
def test_LoginLimit(monkeypatch, capsys):
    # expect this same response each time, prompting another login
    # no different message suggesting a locked account will appear
    expected = "Incorrect username / password, please try again"

    userIn = ""

    # adds same repeated input to string 25 times to test continued login
    for i in range(25):
        userIn += "1\na\nRandomPW1!\n"

    # add 4 to end program
    userIn += "q\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)
    
    # Run program, test for exit code, and capture output
    capture = runInCollege(capsys)

    # test that the expected message occured 25 times, 1 for each attempt
    assert 25 == capture.out.count(expected)


# function to verify that the program outputs a successful login message after logging in
def test_SuccessfulLogin(monkeypatch, capsys):
    clear_accounts()
    userIn = "2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\nq\nq\n"
    # successful login message after logging in we expect from the program
    expectedLoginSuccess = "You have successfully logged in"
    # create a StringIO object and set it as the test input:
    choiceInput = StringIO(userIn)
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)
    # Run the program and capture program input
    captured = runInCollege(capsys)
    # ensure the program displayed the successful login message
    print(captured)
    assert expectedLoginSuccess in captured.out

# function to verify that the program outputs a failed login message after inputting incorrect login credentials
def test_FailedLogin(monkeypatch, capsys):
    # failed login message we expect from the program after inputting incorrect login credentials
    expectedLoginFailed= "Incorrect username / password, please try again"

    # create a StringIO object and set it as the test input:
    # 1-login, "a"-username, "b"-password, 3-exit
    choiceInput = StringIO('1\na\nb\nq\n')
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)
    # Run the program and capture program input
    captured = runInCollege(capsys)
    # ensure the program displayed the failed login message
    assert expectedLoginFailed in captured.out

# function to verify that the skills menu has 5 made up skills
def test_SkillsMenu(monkeypatch, capsys):
    clear_accounts()
    # array to compare program output to help ensure that the skills menu has 5 made up skills
    expectedFiveSkills = ["Skill 1", "Skill 2", "Skill 3", "Skill 4", "Skill 5"]
    # create a StringIO object and set it as the test input:
    # 1-login, "a"-username, "GoBulls24!"-password, 3-Skills menu, 1-skill #1, 3-Skills menu, 2-skill #2, 
    # 3-Skills menu, 3-skill #3, 3-Skills menu, 4-skill #4, 3-Skills menu, 5-skill #5, q-Logout, 4-exit
    choiceInput = StringIO("2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n3\n1\n3\n2\n3\n3\n3\n4\n3\n5\nq\nq\n")
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)
    # Run the program and capture program input
    captured = runInCollege(capsys)
    # ensure the output contains skills 1-5
    for skill in expectedFiveSkills:
        assert skill in captured.out
    
    # ensure the program says "Under Construction" when each skill is selected
    assert 5 == captured.out.count("\nUnder Construction\n")

# function to verify that the skills menu has an option to not select a skill
def test_QuitSkillsMenu(monkeypatch, capsys):
    # the expected output when "q" is selected; verify that the program is sent back to the login menu
    expectedQuitOutput = "\nq: Quit\n\nPlease Select a Skill:"
    # create a StringIO object and set it as the test input:
    # 1-login, "a"-username, "GoBulls24!"-password, 3-Skills menu, "q"-option to quit, q-Logout, q-exit
    choiceInput = StringIO("2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n3\nq\nq\nq\n")
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)
    # Run the program and capture program input
    captured = runInCollege(capsys)
    # ensure the output contains skills 1-5
    assert expectedQuitOutput in captured.out

# function to test that the job search option exists in the login menu and when selected shows "Under Construction"
def test_JobSearch(monkeypatch, capsys):
    return # Functionality has been added
    # the login menu expected after logging in that shows the "search for a job option" and displays "Under Construction" when selected
    expectedOut = "\nUnder Construction\n"
    # create a StringIO object and set it as the test input:
    # 1-login, "a"-username, "GoBulls24!"-password, 1-"search for a job" option, q-Logout, q-exit
    choiceInput = StringIO("2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n1\nq\nq\n")
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)
    # Run the program and capture program input
    captured = runInCollege(capsys)
    # ensure the program displayed the "search for a job" option in the login menu and displayed "Under Construction" when selected
    assert expectedOut in captured.out

    clear_accounts()


"""
**********************************************************************************************
TEST NO LONGER UTILIZED AS THE FUNCTION OF "find someone you know" HAS BEEN 
IMPLEMENTED AND NO LONGER SHOWS AN UNDER CONSTRUCTION MESSAGE WHEN SELECTED
THE NEW FUNCTIONALITY HAS BEEN TESTED IN test_Main2.py
**********************************************************************************************
# function to test that the "find someone you know" option exists in the login menu and when selected shows "Under Construction"
def test_FindSomeone(monkeypatch, capsys):
    # the login menu expected after logging in that shows the "find someone you know" option and displays "Under Construction" when selected
    expectedOut = "\nUnder Construction\n"
    # create a StringIO object and set it as the test input:
    # 1-login, "a"-username, "GoBulls24!"-password, 2-"find someone you know" option, q-Logout, 3-exit
    choiceInput = StringIO('1\na\nGoBulls24!\n2\nq\n4\n')
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', choiceInput)
    # Run the program and capture program input
    captured = runInCollege(capsys)
    # ensure the program displayed the "find someone you know" option in the login menu and displayed "Under Construction" when selected
    assert expectedOut in captured.out
"""
