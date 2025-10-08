# To Do List

## Description
This is a simple project to learn and practice programming in Python and perhaps other languages. It functions as a database to add tasks to a to do list, set target dates, and update if they are finished.

## Quick Start
Make sure Python 3 is installed on the computer running this program. Then in your command line navigate to the root directory and enter "python3 main.py" into the command line followed by arguments listed under Usage.

## Usage
The following arguments have function with the program. Use "--help" for a list with short descriptions.

### "add (task)": adds the task to the to do list and saves it; new tasks are created as "pending"
* "--start (date/time)": sets the start time of the task; defaults to current date and time; enter time in YYYY-MM-DD HH:MM 24-hour format; date or time may be entered alone defaulting to midnight or current date
* "--target (date/time)": sets the target time of the task; entry for target is required; enter time in YYYY-MM-DD HH:MM 24-hour format; date or time may be entered alone defaulting to midnight or current date
* "--priority (Low/Medium/High)": set priority of task (low, medium, or high; default medium)
* "--tags (list)": set a list of tags for groups of tasks; tasks may have multiple tags seperated by commas (,)

```
python3 main.py add "Finish Python project" --target 2025-10-31 18:00 --priority high --tags work,python
```

### "remove (task id)": removes task from to do list designated by Task ID number (use "list" for tasks with ID numbers) and saves list

```
python3 main.py remove 1
```

### "edit (task id)": edit existing task with optional fields replacing corresponding values; notes time task is updated
* "--task (description)": sets the description of the task
* "--target (date/time)": sets the target time of the task; enter time in YYYY-MM-DD HH:MM 24-hour format; date or time may be entered alone defaulting to midnight or current date; gives warning if target time is before start time
* "--priority (Low/Medium/High)": set priority of task (low, medium, or high)
* "--tags (list)": set a list of tags for groups of tasks; tasks may have multiple tags seperated by commas (,)

```
python3 main.py edit 2 --priority High --tags home,family
```

### "finish (task id)": marks task as finished at the current date and time designated by Task ID number (use "list" for tasks with ID numbers) and saves list

```
python3 main.py remove 3
```

### "list": prints as list of tasks in to do list sorted by start time; optional filters
* "--pending": filters list to pending unfinished tasks
* "--finished": filters list to finished tasks
* "--priority": filter by task priority (low, medium, high, or all; default all)
* "--tags": filter by all tags matching with tags in tasks, multiples seperated by commas (,)

```
python3 main.py list --pending --priority high --tags work
```

### "remind": prints a list of tasks within designated or default timespan or past target time
* "--hours": Sets timespan in hours (default: 24 hours, accepts decimal values)

```
python3 main.py remind --hours 12
```

### "clear (passcode)": clears the file to do list is saved to; requires passcode to execute

## Features

* Add, remove, and finish tasks
* Priority and tag filtering
* JSON persistence and automatic saving
* Reminder for upcoming or overdue tasks

## Future Improvements

* Editing tasks
* GUI
* Notifications
