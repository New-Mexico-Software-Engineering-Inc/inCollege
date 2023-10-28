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
    cursor.execute("UPDATE SQLITE_SEQUENCE SET SEQ=0;")
    conn.commit()
    conn.close()

# clear all tables in database
def __create_user_account():
    try:
        main.InCollegeAppManager("test.db")._create_account('a', '!!!Goodpswd0', 'fname', 'lname', 'University', 'Major')
    except Exception as e:
        print(e)

def __create_user_account2():
    try:
        main.InCollegeAppManager("test.db")._create_account('b', '!!!Goodpswd0', 'fname2', 'lname2', 'University', 'Major')
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
    userIn = '1\na\n!!!Goodpswd0\n1\n'

    # now we will try to create 5 jobs so we will loop the following inputs 5 times for each list entry
    # 2 - post a job, then enter all criteria, then 2 - post a job, then enter all criteria, ...
    for i in range(5):
        userIn += f'2\n{jobTitles[i]}\n{jobDescriptions[i]}\n{requiredSkill[i]}\n{longDescriptions[i]}\n'
        userIn += f'{employers[i]}\n{locations[i]}\n{salaries[i]}\n'

    # then logout and exit the program
    userIn += 'q\nq\nq\n'
    print(userIn)
    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)
    _ = runInCollege(capsys)

    userIn = '1\na\n!!!Goodpswd0\n' # sign in
    userIn +='1\n1\nJob\na\n' # Search for all jobs
    # then logout and exit the program
    userIn += 'q\nq\nq\n'
    # return
    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)
    capture = runInCollege(capsys)
    
    for (job, desc, salary, employer)  in zip(jobTitles, jobDescriptions, salaries, employers):
        assert job in capture.out, 'Unsucessful in finding jobs'
        assert desc in capture.out, 'Unsucessful in finding jobs'
        assert str(salary) in capture.out, 'Unsucessful in finding jobs'
        assert employer in capture.out, 'Unsucessful in finding jobs'

def test_search_applied_or_not(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    __create_user_account2()

    #log into account a, post Job A
    userIn = "1\na\n!!!Goodpswd0\n1\n2\nJob A\nDesc A\nSkill A\nLong Desc A\nEmployer A\nLocation A\n100.0\n"
    #post Job B, log out
    userIn += "2\nJob B\nDesc B\nSkill B\nLong Desc B\nEmployer B\nLocation B\n200.0\nq\nq\n"
    #log into account b, sign up for Job A
    userIn += "1\nb\n!!!Goodpswd0\n1\n3\n1\n01/01/0001\n02/02/0002\nTesting Testing Testing\n"
    #search for jobs not applied to, search for jobs already applied to, log out, quit
    userIn += "1\nJob\n1\n1\nJob\n2\nq\nq\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    expectedSearchApplied = "1. Search Jobs You've Applied For"
    expectedSearchNotApplied = "2. Search Jobs You Haven't Applied For"
    expectedJobAppliedFound = "Jobs Found\n-------------------------------\nTitle: Job A\nDescription: Desc A\n"
    expectedJobAppliedFound += "Employer: Employer A\nSalary: 100.0\nPosted By: fname lname\nApplied For: True\nJob ID: 1\n\n"
    expectedJobNotAppliedFound = "Jobs Found\n-------------------------------\nTitle: Job B\nDescription: Desc B\n"
    expectedJobNotAppliedFound += "Employer: Employer B\nSalary: 200.0\nPosted By: fname lname\nApplied For: False\nJob ID: 2\n\n"

    #capture output
    capture = runInCollege(capsys)

    #test that the requirements are prompted to the user
    assert expectedSearchApplied in capture.out
    assert expectedSearchNotApplied in capture.out
    assert expectedJobAppliedFound in capture.out
    assert expectedJobNotAppliedFound in capture.out

def test_search_applied_status(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    __create_user_account2()

    #log into account a, post Job A
    userIn = "1\na\n!!!Goodpswd0\n1\n2\nJob A\nDesc A\nSkill A\nLong Desc A\nEmployer A\nLocation A\n100.0\n"
    #post Job B, log out
    userIn += "2\nJob B\nDesc B\nSkill B\nLong Desc B\nEmployer B\nLocation B\n200.0\nq\nq\n"
    #log into account b, sign up for Job A
    userIn += "1\nb\n!!!Goodpswd0\n1\n3\n1\n01/01/0001\n02/02/0002\nTesting Testing Testing\n"
    #display all jobs, log out
    userIn += "1\n\na\nq\nq\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    #program is expected to print out two jobs: one the current user has applied for and one the current user has not applied for
    #program is expected to print out "Applied For: " followed by True if the current user applied for the job and False otherwise
    expectedJobsFound = "Jobs Found\n-------------------------------\nTitle: Job A\nDescription: Desc A\n"
    expectedJobsFound += "Employer: Employer A\nSalary: 100.0\nPosted By: fname lname\nApplied For: True\nJob ID: 1\n\n"
    expectedJobsFound += "Title: Job B\nDescription: Desc B\nEmployer: Employer B\nSalary: 200.0\nPosted By: fname lname\nApplied For: False\nJob ID: 2\n\n"
    
    #capture output
    capture = runInCollege(capsys)

    assert expectedJobsFound in capture.out 

def test_job_titles(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    #log into account a, post Job A
    userIn = "1\na\n!!!Goodpswd0\n1\n2\nJob A\nDesc A\nSkill A\nLong Desc A\nEmployer A\nLocation A\n100.0\n"
    #post Job B
    userIn += "2\nJob B\nDesc B\nSkill B\nLong Desc B\nEmployer B\nLocation B\n200.0\n"
    #search for a job, cancel, quit, and logout
    userIn += "1\n\nq\nq\nq\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    #titles of jobs currently posted are to be displayed when searching for a job
    expectedTitlesOutput = "Titles of Jobs Currently Posted\n-------------------------------\nJob A\nJob B"

    #capture output
    capture = runInCollege(capsys)
    
    #test that the job titles were displayed to the screen
    assert expectedTitlesOutput in capture.out

def test_application_requirements(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    __create_user_account2()

    #log into account a, post a job, log out
    userIn = "1\na\n!!!Goodpswd0\n1\n2\nJob A\nDesc A\nSkill A\nLong Desc A\nEmployer A\nLocation A\n100.0\nq\nq\n"
    #log into account b, sign up for job, log out
    userIn += "1\nb\n!!!Goodpswd0\n1\n3\n1\n01/01/0001\n02/02/0002\nTesting Testing Testing\nq\nq\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    #expected requirements for job application
    expectedGraduationPrompt = "Please Enter your Graduation Date (dd/mm/yyyy):"
    expectedStartDatePrompt = "Please Enter your Available Start Date (dd/mm/yyyy):"
    expectedExplainPrompt = "Tell us About Yourself and why you want the job:"

    #capture output
    capture = runInCollege(capsys)

    #test that the requirements are prompted to the user
    assert expectedGraduationPrompt in capture.out
    assert expectedStartDatePrompt in capture.out
    assert expectedExplainPrompt in capture.out

def test_cannot_apply_twice(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    __create_user_account2()


    # expected output when we apply for same job a second time
    expectedOut = "Error Applying for Job:"
    # expected output when we successfully apply the first time
    expectedOut2 = "Successfully Applied for the job."

    # test items to post for job
    jobStuff = ["Test", "Test Description", "Test Skill", "Test Description", "Test", "Test", "200"]

    # job id, grad date, start date, description
    appStuff = ["01/01/0001", "02/02/0002", "Testing Testing Testing"]

    userIn = "1\na\n!!!Goodpswd0\n1\n2\n"

    for i in jobStuff:
        userIn += f"{i}\n"

    userIn += "q\nq\n1\nb\n!!!Goodpswd0\n1\n3\n1\n"

    for i in appStuff:
        userIn += f"{i}\n"

    userIn += "3\n1\n\nq\nq\nq\n"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    print(capture.out)

    assert expectedOut in capture.out
    assert expectedOut2 in capture.out

def test_cannot_apply_to_own_posting(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    # expected output when we apply for same job a second time
    expectedOut = "Error Applying for Job:"
    expectedOut2 = "Cannot apply to your own posting."

    # test items to post for job
    jobStuff = ["Test", "Test Description", "Test Skill", "Test Description", "Test", "Test", "200"]

    userIn = "1\na\n!!!Goodpswd0\n1\n2\n"

    for i in jobStuff:
        userIn += f"{i}\n"

    userIn += "3\n1\nq\nq\nq\n"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    print(capture.out)

    assert expectedOut in capture.out
    assert expectedOut2 in capture.out

def test_save_a_job(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    __create_user_account2()

    #log into account a, post Job A, log out
    userIn = "1\na\n!!!Goodpswd0\n1\n2\nJob A\nDesc A\nSkill A\nLong Desc A\nEmployer A\nLocation A\n100.0\nq\nq\n"
    #log into account b, save Job A, log out
    userIn += "1\nb\n!!!Goodpswd0\n1\n5\n1\nq\nq\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    expectedJobDetails = "Job Details\n-------------------------------\nTitle: Job A\nDescription: Desc A\nEmployer: Employer A\n"
    expectedJobDetails += "Salary: 100.0\nPosted By: fname lname\nApplied For: False\nJob ID: 1\n"
    expectedSaveJobSuccess = "Job saved successfully!"

    #capture output
    capture = runInCollege(capsys)
    
    #test that the job details and the job saved success message were displayed
    assert expectedJobDetails in capture.out
    assert expectedSaveJobSuccess in capture.out

def test_display_saved_jobs(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    __create_user_account2()

    #log into account a, post Job A, log out
    userIn = "1\na\n!!!Goodpswd0\n1\n2\nJob A\nDesc A\nSkill A\nLong Desc A\nEmployer A\nLocation A\n100.0\nq\nq\n"
    #log into account b, save Job A, display saved jobs, log out
    userIn += "1\nb\n!!!Goodpswd0\n1\n5\n1\n6\nn\nq\nq\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    expectedSavedJobs = "Jobs You Have Saved\n-------------------------------\nTitle: Job A\nDescription: Desc A\nID: 1\n"

    #capture output
    capture = runInCollege(capsys)

    #test that the saved jobs were displayed to the screen
    assert expectedSavedJobs in capture.out

def test_unsave_a_job(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()
    __create_user_account2()

    #log into account a, post Job A, log out
    userIn = "1\na\n!!!Goodpswd0\n1\n2\nJob A\nDesc A\nSkill A\nLong Desc A\nEmployer A\nLocation A\n100.0\nq\nq\n"
    #log into account b, save Job A, display saved jobs and unsave Job A, log out
    userIn += "1\nb\n!!!Goodpswd0\n1\n5\n1\n6\ny\n1\nq\nq\nq\n"

    userInput = StringIO(userIn)
    monkeypatch.setattr('sys.stdin', userInput)

    expectedUnsaveJobPrompt = "Do you wish to unsave a job? (y/n) "
    expectedJobIDPrompt = "Enter the ID of the job you want to unsave (or enter q to cancel): "
    expectedSuccessfulUnsaveMessage = "Job with ID 1 has been unmarked as saved."

    #capture output
    capture = runInCollege(capsys)

    #test that the user was asked if they wanted to unsave a job
    assert expectedUnsaveJobPrompt in capture.out
    #test that the user was prompted for the Job ID of the job they wish to unsave
    assert expectedJobIDPrompt in capture.out
    #test that a successful message was displayed after the user unsaved a job
    assert expectedSuccessfulUnsaveMessage in capture.out

def test_post_10_jobs(monkeypatch, capsys):
    clear_accounts()
    __create_user_account()

    # will occur 10 times for 10 successful job postings
    expectedOut1 = "Successfully Posted Job."
    # will occur once for failed 11th posting
    expectedOut2 = "All jobs have been created. Please come back later."

    jobTest = ["a", "b" , "c", "d" , "e", "f", "g" ,"h", "i", "j", "h"]
    jobSalaries = ["1", "2" , "3", "4" , "5", "6", "7" ,"8", "9", "10", "11"]

    userIn = "1\na\n!!!Goodpswd0\n1\n"

    for i in range(11):
        userIn += f"2\n{jobTest[i]}\n{jobTest[i]}\n{jobTest[i]}\n{jobTest[i]}\n{jobTest[i]}\n{jobTest[i]}\n{jobSalaries[i]}\n"

    userIn += "q\nq\nq\n"

    userInput = StringIO(userIn)

    monkeypatch.setattr('sys.stdin', userInput)

    capture = runInCollege(capsys)

    assert 10 == capture.out.count(expectedOut1)
    assert 1 == capture.out.count(expectedOut2)