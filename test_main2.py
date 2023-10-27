# Sprint 2 Test Cases
# The functions use monkeypatch to mock input and capsys to capture output
# Created by: Austin Martin, Emin Mahmudzade
# Date created: 09/22/2023
# Last Update: 09/24/2023

import sqlite3
import pytest
import main
from io import StringIO
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

# function to test that first and last names are asked for when creating an account
def test_asksForNames(monkeypatch, capsys):
    # this message should print when attempting to create account, now asking for names
    expectedPrompt = "Enter unique username: \n"
    expectedPrompt += ("Enter your password (minimum of 8 characters, maximum of 12 characters, at least one capital letter, one digit, one special character): \n")
    expectedPrompt += "Enter your first name: \nEnter your last name: \n"

    # the user input below will navigate to attempt to create an account,
    # and then enter information that will not allow for a successful creation
    userInput = StringIO("2\na\nbadpassword\naustin\nmartin\nUni\nCSE\nq\n")
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys);

    assert expectedPrompt in capture.out;


# function to test that the play demo video option is there and the video plays
def test_demoVideo(monkeypatch, capsys):
    # this message will show in the options on home screen
    expectedOut = "Play Demo Video\n"

    # this message will show when the video plays successfully
    expectedOut2 = "Video is playing\n"

    # input will select option 5 to play video then option q to quit the program
    userInput = StringIO("5\nq\n")

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # the video option must appear in output
    assert expectedOut in capture.out
    # the video playing message must appear
    assert expectedOut2 in capture.out


# test if the search by name function on home screen works correctly when user exists
#outdated
"""
def test_searchByNameSuccess(monkeypatch, capsys):
    # we expect to see a return stating that this user does have an account
    expectedOut = "Looks like they have an account!\n"

    # the inputs will be to select search for a person, enter first name, enter last name, then exit
    userInput = StringIO("3\nfname1\nlname1\nq\n")

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    assert expectedOut in capture.out
    
    def test_searchByNameFailure(monkeypatch, capsys):
    # we expect to see this output as the user does not exist in the system
    expectedOut = "Sorry, they are not part of the InCollege system yet.\n"

    # the input will be to select search for a person, enter bad first name, enter bad last name, then exit
    userInput = StringIO("3\nfname6\nlname6\nq\n")

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    assert expectedOut in capture.out

"""



# test if the search by name function on home screen works correctly when user does not exist


# Checking if Sucess Story shown on main page
def test_SucessStory(monkeypatch, capsys):
    expectedOut = "Meet Sarah, a recent graduate who turned her dreams into reality with InCollege! \n Sarah joined InCollege during her final year, leveraging its vast network to connect with industry professionals.\n Through insightful discussions and mentorship, she honed her skills and gained invaluable advice. \n Thanks to InCollege, Sarah secured her dream job as a marketing strategist at a leading tech company immediately after graduation.\n Her journey from student to success story is proof that InCollege is the ultimate launchpad for your career! \n #CareerSuccess \n #InCollegeImpact"
    # create a StringIO object and set it as the test input:
    # 4-exit
    userInput = StringIO("q\n")
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', userInput)
    # Run the program and capture program input
    capture = runInCollege(capsys)
    # ensure the program displayed the successful login message
    assert expectedOut in capture.out


# Test that the delete function correctly deletes an account
def test_DeleteSuccess(monkeypatch, capsys):
    clear_accounts()
    # we expect to see both of the following prompted when an account is deleted
    expectedOut = "We are sorry to see you go!"

    # we expect to see this message prompted when we try to sign in with the now delted account
    expectedOut2 = "Incorrect username / password, please try again"

    userIn = ""

    # this input will prompt the deletion of an account
    # 1 - login, enter credentials, 7 - delete account, verify with y twice
    userIn += "2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n9\ny\ny\n"

    # now we attempt to login with the same credentials
    userIn += "1\na\n!!!Goodpswd0\n"

    # after doing this test, we recreate the account and end the program
    userIn += "2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\nq\n"

    userInput = StringIO(userIn)

    # setup input to be the created string
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # test that both of the expected outputs have been printed, showing a successful deletion of the account specified
    assert expectedOut in capture.out
    assert expectedOut2 in capture.out

"""
def test_FindUsersOnceLoggedIn(monkeypatch, capsys):
    # expect to see that the person we searched already exists within the inCollege system
    expectedOut = "Looks like they have an account!"

    # set input to login, then search for their friend by name, then logout and exit
    userIn = "1\na\n!!!Goodpswd0\n2\nfname2\nlname2\nq\nq\n"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # test that the friend was successfully found after logging in
    assert expectedOut in capture.out

"""
# test for finding users while logged in


# test that we can create up to 5 jobs
def test_Post5Jobs(monkeypatch, capsys):
    clear_accounts()

    # we expect to see that the job was successfully posted 5 times when we try to post 5 jobs
    expectedOut = "Successfully Posted Job."

    userIn = ''

    # we will attempt to create 5 jobs, so here are lists corresponding to the necessary entries for 5 jobs
    jobTitles = ['Job A', 'Job B', 'Job C', 'Job D', 'Job E']
    jobDescriptions = ['Desc A', 'Desc B', 'Desc C', 'Desc D', 'Desc E']
    requiredSkill = ['Skill A', 'Skill B', 'Skill C', 'Skill D', 'Skill E']
    longDescriptions = ['long Desc A', 'long Desc B', 'long Desc C', 'long Desc D', 'long Desc E']
    employers = ['employer A', 'employer B', 'employer C', 'employer D', 'employer E']
    locations = ['Location A', 'Location B', 'Location C', 'Location D', 'Location E']
    salaries = [100.0, 200.0, 300.0, 400.0, 500.0]

    # first we must login with an existing account
    userIn += '2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n'

    # now we will try to create 5 jobs so we will loop the following inputs 5 times for each list entry
    # 4 - post a job, then enter all criteria, then 4 - post a job, then enter all criteria, ...
    for i in range(5):
        userIn += f'4\n{jobTitles[i]}\n{jobDescriptions[i]}\n{requiredSkill[i]}\n{longDescriptions[i]}\n'
        userIn += f'{employers[i]}\n{locations[i]}\n{salaries[i]}\n'

    # then logout and exit the program
    userIn += 'q\nq\n'

    # set the system to take the created input string as the user input
    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # since we created 5 jobs, we should see the successful job posting message 5 times
    assert 5 == capture.out.count(expectedOut)


# test that trying to post a 6th job fails
# !!!!!! this test must be ran after test_Post5Jobs to ensure that 5 jobs are already posted !!!!!!
def test_Post6thJobFails(monkeypatch, capsys):
    return # This constraint has been lifted
    # clear_accounts()
    # for a failed job posting, we expect to see the following error occur
    expectedOut = 'All jobs have been created. Please come back later.'

    # the list below holds all values to create a 6th job
    jobEntries = ['title', 'desc', 'skill', 'long desc', 'employer', 'location', 200.0]

    # setup input string to sign in under a created account and then select to post a job using command 4
    userIn = '2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n4\n'

    # add all of the necessary job entries to the user input string
    for i in range(7):
        userIn += f'{jobEntries[i]}\n'

    # then logout using q and exit using q
    userIn += 'q\nq\n'

    # set user input to come from the created input string
    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # test that the expected failure message appears in the output
    assert expectedOut in capture.out

# test for checking quit to main
def test_ReturnMain(monkeypatch, capsys):
    clear_accounts()
    # expect to see returning to main after log out
    expectedOut = "Video is playing\n"
    # set input to login,log out and exit
    userIn = "2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\nq\n5\nq\n"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # test that the the option for returning main page works
    assert expectedOut in capture.out


# test for checking job posting asks for all parametrs
def test_PostJob(monkeypatch, capsys):
    clear_accounts()

    # the list below holds all values to create a job
    jobEntries = ['title', 'desc', 'skill', 'long desc', 'employer', 'location', 200.0]

    # for job posting option , all this parametrs should be asked
    expectedOut = "Enter the job title:"
    expectedOut1 = "Enter the job description:"
    expectedOut2 = "Enter the required skill name:"
    expectedOut3 = "Enter a long description for the skill:"
    expectedOut4 = "Enter the employer:"
    expectedOut5 = "Enter the location:"
    expectedOut6 = "Enter the salary:"


    # set input to login, check for post job button and exit
    userIn = "2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n4\n"

    # add all of the necessary job entries to the user input string
    for i in range(7):
        userIn += f'{jobEntries[i]}\n'
    userIn += "q\nq\n"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # test that the the user gets asked for all parametrs
    assert expectedOut in capture.out
    assert expectedOut1 in capture.out
    assert expectedOut2 in capture.out
    assert expectedOut3 in capture.out
    assert expectedOut4 in capture.out
    assert expectedOut5 in capture.out
    assert expectedOut6 in capture.out


# testing if not number input for salary gives an error
def test_NotNumberSalary(monkeypatch, capsys):
    clear_accounts()
    # the list below holds all values to create a job
    jobEntries = ['title', 'desc', 'skill', 'long desc', 'employer', 'location', 'NotNumber']

    # for job posting option , all this parametrs should be asked
    expectedOut = "Please enter a number for salary"

    # set input to login, check for post job button and exit
    userIn = "2\na\n!!!Goodpswd0\nfirstname\nlastname\nUniversity\nMajor\n1\na\n!!!Goodpswd0\n4\n"

    # add all of the necessary job entries to the user input string
    for i in range(7):
        userIn += f'{jobEntries[i]}\n'
    userIn += "q\nq\n"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # test that the user inputs not number in salary parametr
    assert expectedOut in capture.out