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

    