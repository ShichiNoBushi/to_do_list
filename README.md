# To Do List

## Description
This is a simple project to learn and practice programming in Python and perhaps other languages. It functions as a database to add tasks to a to do list, set target dates, and update if they are finished.

## Quick Start
Make sure Python 3 is installed on the computer running this program. Then in your command line navigate to the root directory and enter "python3 main.py" into the command line followed by arguments listed under Usage.

## Usage
The following arguments have function with the program. Use "--help" for a list with short descriptions.

* "add (task)": adds the task to the to do list and saves it; new tasks are created as "pending"
    - "--start (date/time)": sets the start time of the task; defaults to current date and time; enter time in YYYY-MM-DD HH:MM 24-hour format; date or time may be entered alone defaulting to midnight or current date
    - "--target (date/time)": sets the target time of the task; entry for target is required; enter time in YYYY-MM-DD HH:MM 24-hour format; date or time may be entered alone defaulting to midnight or current date

* "remove (task id)": removes task from to do list by designated Task ID number (use "list" for tasks with ID numbers) and saves list

* "finish (task id)": marks task as finished by designated Task ID number (use "list" for tasks with ID numbers) and saves list

* "list": prints as list of tasks in to do list sorted by start time; optional filters
    - "--pending": filters list to pending unfinished tasks
    - "--finished": filters list to finished tasks

* "remind": prints a list of tasks within designated or default timespan or past target time
    - "--hours": Sets timespan in hours (default: 24 hours, accepts decimal values)

* "clear (passcode)": clears the file to do list is saved to; requires passcode to execute
