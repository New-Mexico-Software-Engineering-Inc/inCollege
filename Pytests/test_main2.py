# Week 2 Pytests

import sqlite3
import pytest
import main
from io import StringIO


# function to run the inCollege program and return program output
def runInCollege(capsys):
    # Run the program, and collect the system exit code
    with pytest.raises(SystemExit) as e:
        main.inCollegeAppManager().Run()

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
    userInput = StringIO("2\na\nbadpassword\naustin\nmartin\n4\n")
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys);

    assert expectedPrompt in capture.out;


# function to test that the play demo video option is there and the video plays
def test_demoVideo(monkeypatch, capsys):
    # this message will show in the options on home screen
    expectedOut = "Play Demo Video\n"

    # this message will show when the video plays successfully
    expectedOut2 = "Video is playing\n"

    # input will select option 5 to play video then option 4 to quit the program
    userInput = StringIO("5\n4\n")

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # the video option must appear in output
    assert expectedOut in capture.out
    # the video playing message must appear
    assert expectedOut2 in capture.out


# test if the search by name function on home screen works correctly when user exists
def test_searchByNameSucces(monkeypatch, capsys):
    # we expect to see a return stating that this user does have an account
    expectedOut = "looks like they have an account\n"

    # the inputs will be to select search for a person, enter first name, enter last name, then exit
    userInput = StringIO("3\nfname1\nlname1\n4\n")

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    assert expectedOut in capture.out


# test if the search by name function on home screen works correctly when user does not exist
def test_searchByNameFailure(monkeypatch, capsys):
    # we expect to see this output as the user does not exist in the system
    expectedOut = "sorry, they are not part of the InCollege system yet\n"

    # the input will be to select search for a person, enter bad first name, enter bad last name, then exit
    userInput = StringIO("3\nfname6\nlname6\n4\n")

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    assert expectedOut in capture.out


# Checking if Sucess Story shown on main page
def test_SucessStory(monkeypatch, capsys):
    expectedOut = "\n\n Meet Sarah, a recent graduate who turned her dreams into reality with inCollege! \n Sarah joined inCollege during her final year, leveraging its vast network to connect with industry professionals.\n Through insightful discussions and mentorship, she honed her skills and gained invaluable advice. \n Thanks to inCollege, Sarah secured her dream job as a marketing strategist at a leading tech company immediately after graduation.\n Her journey from student to success story is proof that inCollege is the ultimate launchpad for your career! \n #CareerSuccess \n #inCollegeImpact \n "
    # create a StringIO object and set it as the test input:
    # 4-exit
    userInput = StringIO("4\n")
    # Set the stdin stream as our desired input
    monkeypatch.setattr('sys.stdin', userInput)
    # Run the program and capture program input
    capture = runInCollege(capsys)
    # ensure the program displayed the successful login message
    assert expectedOut in capture.out


# Test that the delete function correctly deletes an account
def test_DeleteSuccess(monkeypatch, capsys):
    # we expect to see both of the following prompted when an account is deleted
    expectedOut = "we are sorry to see you go"

    # we expect to see this message prompted when we try to sign in with the now delted account
    expectedOut2 = "Incorrect username / password, please try again"

    userIn = ""

    # this input will prompt the deletion of an account
    # 1 - login, enter credentials, 5 - delete account, verify with y twice
    userIn += "1\ne\nGoBulls28!\n5\ny\ny\n"

    # now we attempt to login with the same credentials
    userIn += "1\ne\nGoBulls28!\n"

    # after doing this test, we recreate the account and end the program
    userIn += "2\ne\nGoBulls28!\nfname5\nlname5\n4\n"

    userInput = StringIO(userIn)

    # setup input to be the created string
    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    # test that both of the expected outputs have been printed, showing a successful deletion of the account specified
    assert expectedOut in capture.out
    assert expectedOut2 in capture.out