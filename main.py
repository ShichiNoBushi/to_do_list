from datetime import datetime
import json
import argparse
import os

class To_Do_Item:
    PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3} # Map converting priority names to numerical values
    PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High"} # Map converting values to names

    def __init__(self, tid, task, start, target, updated = datetime.now(), priority = "medium", tags = None):
        self.tid = tid # ID number of task
        self.task = task # Description of task
        self.start = start # When task was initiated at time created or other designated time
        self.target = target # Target completion time for the task
        self.updated = updated # When the task was last created or edited
        self.finished = None # Time when the task was completed or None if unfinished
        self.priority = To_Do_Item.PRIORITY_MAP.get(priority.lower(), 2) # Priority of task
        self.tags = tags if tags else [] # Tags for groups of tasks
    
    # Generate long string representing the to do task
    def __str__(self):
        # "Finished" and time finished or "Pending"
        if self.finished is not None:
            finished_str = f"Finished {datetime.strftime(self.finished, '%Y %b %d %H:%M')}"
        else:
            finished_str = "Pending"

        priority_label = To_Do_Item.PRIORITY_LABELS[self.priority] # Label for priority (Low, Medium, or High)
        start_str = datetime.strftime(self.start, "%Y %b %d %H:%M") # Time the task began in YYYY Month-abbreviated DD HH:MM (24-hour) format
        target_str = datetime.strftime(self.target, "%Y %b %d %H:%M") # Target time for the task
        updated_str = datetime.strftime(self.updated, "%Y %b %d %H:%M") # Time the task was last updated
        tags_str = ", ".join(self.tags) # List of group tags
        
        return f"{self.tid} {self.task} [{finished_str}] (Priority: {priority_label}, Start: {start_str}, Target: {target_str}, Last updated: {updated_str})\n    Tags: {tags_str}"

    # Short-hand for task
    def __repr__(self):
        return self.task
    
    # Edits task with optional fields
    def edit(self, task = None, target = None, priority = None, tags = None):
        # Change task description
        if task is not None:
            self.task = task
        
        # Change target time
        if target is not None:
            if target < self.start:
                print("Warning: Target time is before the start time.")
            self.target = target

        # Change priority
        if priority is not None:
            self.priority = To_Do_Item.PRIORITY_MAP.get(priority.lower(), self.priority)

        # Change tags
        if tags is not None:
            self.tags = tags

        # Note when updated
        self.updated = datetime.now()
        print(f"Task {self.tid} updated at {self.updated.strftime('%Y-%m-%d %H:%M')}")
    
    # Mark task is completed at current time
    def finish(self):
        if self.finished is None:
            self.finished = datetime.now()
            self.updated = datetime.now()

    # Convert task to a dictionary to become JSON compatible
    def to_dict(self):
        return {
            "tid": self.tid,
            "task": self.task,
            "start": self.start.isoformat(),
            "target": self.target.isoformat(),
            "updated": self.updated.isoformat(),
            "finished": self.finished.isoformat() if self.finished else None,
            "priority": self.priority,
            "tags": self.tags
        }
    
    # Convert from JSON dictionary to task object
    @classmethod
    def from_dict(cls, data):
        priority_value = data.get("priority", 2)
        item = cls(
            tid = data["tid"],
            task = data["task"],
            start = datetime.fromisoformat(data["start"]),
            target = datetime.fromisoformat(data["target"]),
            updated = datetime.fromisoformat(data["updated"]),
            priority = To_Do_Item.PRIORITY_LABELS[priority_value].lower(),
            tags = data["tags"]
        )
        fin = data.get("finished")
        item.finished = datetime.fromisoformat(fin) if fin else None

        return item

# Add task to To Do List
def to_do_add(td_list, item):
    td_list[item.tid] = item

# Remove task from To Do List
def to_do_remove(td_list, item):
    if item.tid in td_list:
        del td_list[item.tid]

# Print To Do List according to filters and sorting criteria
def to_do_print(td_list, pending_only = False, finished_only = False, priority = 0, tags = None, sort_fields = None):
    if sort_fields is None or len(sort_fields) == 0:
        sort_fields = ["priority", "start"] # default sort by priority and start date

    # Function to pass as sorting key
    def sort_key(item):
        key = []
        for field in sort_fields:
            if field == "priority": # descending priority
                key.append(-item.priority)
            elif field == "start": # start time
                key.append(item.start)
            elif field == "target": # target time
                key.append(item.target)
            elif field == "updated": # time last updated
                key.append(item.updated)
            elif field == "task": # task description
                key.append(item.task.lower())
            elif field == "tid": # task id
                key.append(item.tid)

        return tuple(key)

    td_sorted = sorted(td_list.values(), key = sort_key)

    # Alert if contradicting filters are both true
    if pending_only and finished_only:
        print("Pending only and finished only filters both True. Select only one or neither.")
        return

    # Print if item meets filter criteria
    for i in td_sorted:
        # If item matches finished status or not a critical filter
        is_pending_match = (not finished_only and (not pending_only or i.finished is None))
        is_finished_match = (not pending_only and (not finished_only or i.finished is not None))
        is_status_match = is_pending_match or is_finished_match

        # If item matches priority or not a critical filter
        is_priority_match = (priority == 0 or i.priority == priority)
        # If item matches tags or not a critical filter
        is_tag_match = (tags is None or all(tag in i.tags for tag in tags))

        # Print if item matches all criteria
        if is_status_match and is_priority_match and is_tag_match:
            print(i)

# Print tasks that are close to target date or overdue
def to_do_reminders(td_list, timespan_hours = 24):
    now = datetime.now()
    upcoming = []

    # Print message for each item with close taarget or overdue
    for item in td_list.values():
        if item.finished is None:
            remaining = item.target - now
            hours_left = remaining.total_seconds() / 3600

            if hours_left <= 0:
                status = f"OVERDUE by {format_timedelta(-remaining)}"
                upcoming.append((item, remaining, status))
            elif hours_left <= timespan_hours:
                status = f"Due in {format_timedelta(remaining)}"
                upcoming.append((item, remaining, status))

    # Message if no time critical tasks
    if len(upcoming) == 0:
        print("No upcoming or overdue tasks.")
        return
    
    for item, remaining, status in sorted(upcoming, key = lambda x: x[1]):
        print(f"{item.task}: {status} (Target: {item.target.strftime('%Y %b %d %H:%M')})")

# Format time into largest significant time units days > hours > minutes
def format_timedelta(delta):
    total_seconds = int(abs(delta.total_seconds()))
    days, remainder = divmod(total_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes = remainder // 60

    if days > 0:
        return f"{days} days {hours} hours"
    elif hours > 0:
        return f"{hours} hours {minutes} minutes"
    else:
        return f"{minutes} minutes"

# Convert To Do List into JSON format
def to_json(td_list):
    json_safe_list = [item.to_dict() for item in td_list.values()]

    return json.dumps(json_safe_list, indent = 4)

# Convert from JSON format into list
def from_json(json_str):
    json_safe_list = json.loads(json_str)

    return {item["tid"]: To_Do_Item.from_dict(item) for item in json_safe_list}

# Save list to JSON file
def save_list(td_list, filename = "tasks.json"):
    with open(filename, "w") as f:
        json.dump([item.to_dict() for item in td_list.values()], f, indent = 4)

# Load list from JSON file
def load_list(filename = "tasks.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return {item["tid"]: To_Do_Item.from_dict(item) for item in data}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    
# Erase file
def reset_file(filename = "tasks.json"):
    if os.path.exists(filename):
        os.remove(filename)

# Get arguments from command line
def get_args():
    parser = argparse.ArgumentParser(description = "To Do List Manager")

    subparsers = parser.add_subparsers(dest = "command")

    # add [task] --priority --start --target --tags
    add_parser = subparsers.add_parser("add", help = "Add a new task")
    add_parser.add_argument("task", type = str, help = "Task description")
    add_parser.add_argument("--priority", type = str, default = "Medium", help = "Priority of task (High, Medium, or Low)")
    add_parser.add_argument("--start", type = parse_datetime, default = None, help = "Start time (YYYY-MM-DD [HH:MM])")
    add_parser.add_argument("--target", type = parse_datetime, required = True, help = "Target time (YYYY-MM-DD [HH:MM])")
    add_parser.add_argument("--tags", type = str, default = "", help = "Tags for task groups (seperate multiples by commas)")

    # remove [tid]
    rm_parser = subparsers.add_parser("remove", help = "Remove a task")
    rm_parser.add_argument("tid", type = int, help = "Task ID")

    # finish [tid]
    finish_parser = subparsers.add_parser("finish", help = "Mark a task finished")
    finish_parser.add_argument("tid", type = int, help = "Task ID")

    # edit [tid] --task --priority --target --tags
    edit_parser = subparsers.add_parser("edit", help = "Edit an existing task")
    edit_parser.add_argument("tid", type = int, help = "Task ID")
    edit_parser.add_argument("--task", type = str, default = None, help = "Task description")
    edit_parser.add_argument("--priority", type = str, default = None, help = "Priority of task (High, Medium, or Low)")
    edit_parser.add_argument("--target", type = parse_datetime, default = None, help = "Target time (YYYY-MM-DD [HH:MM])")
    edit_parser.add_argument("--tags", type = str, default = None, help = "Tags for task groups (seperate multiples by commas)")

    # list --pending --finished --priority --tags --sort
    list_parser = subparsers.add_parser("list", help = "List tasks")
    list_parser.add_argument("--pending", action = "store_true", help = "Show only pending tasks")
    list_parser.add_argument("--finished", action = "store_true", help = "Show only finished tasks")
    list_parser.add_argument("--priority", type = str, default = "all", choices = ["low", "medium", "high", "all"], help = "Filter by priority (High, Medium, or Low)")
    list_parser.add_argument("--tags", type = str, default = "", help = "Filter by group tags (seperate multiples by commas)")
    list_parser.add_argument("--sort", type = str, default = "priority", help = "Sorting criteria by multiple fields in order of priority (seperate multiples by commas)")

    # remind --hours
    reminder_parser = subparsers.add_parser("remind", help = "List tasks soon or overdue")
    reminder_parser.add_argument("--hours", type = float, default = 24, help = "Time window in hours for upcoming tasks")

    # clear --passcode
    clear_parser = subparsers.add_parser("clear", help = "Clears list of tasks (requires code)")
    clear_parser.add_argument("--passcode", type = int, required = True, help = "Passcode to clear list")

    return parser.parse_args()

# Parse datetime from date and time or date or time alone
def parse_datetime(value):
    formats = [
        "%Y-%m-%d %H:%M", # date and time
        "%Y-%m-%d", # date only
        "%H:%M" # time only
    ]

    for fmt in formats:
        try:
            dt = datetime.strptime(value, fmt)
            if fmt == "%H:%M":
                today = datetime.now()
                dt = dt.replace(year = today.year, month = today.month, day = today.day)
            return dt
        except ValueError:
            continue
    raise ValueError(f"Invalid datetime format: {value}. Expected YYYY-MM-DD HH:MM, YYYY-MM-DD, or HH:MM.")

def main():
    to_do_list = load_list() # Load from file

    args = get_args() # Get command line arguments

    if args.command == "add":
        # Add new task
        new_id = max(to_do_list.keys(), default = -1) + 1
        tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
        start = args.start or datetime.now()
        new_item = To_Do_Item(
            tid = new_id,
            task = args.task,
            start = start,
            target = args.target,
            priority = args.priority,
            tags = tags
        )
        to_do_add(to_do_list, new_item)
        print(f"Added new task: {new_item}")
        save_list(to_do_list)
    elif args.command == "remove":
        # Remove task
        if args.tid in to_do_list:
            rm_item = to_do_list[args.tid]
            to_do_remove(to_do_list, rm_item)
            print(f"Removed task: {rm_item}")
            save_list(to_do_list)
        else:
            print(f"Task ID not in list: {args.tid}")
    elif args.command == "finish":
        # Mark task finished
        if args.tid in to_do_list:
            fin_item = to_do_list[args.tid]
            fin_item.finish()
            print(f"Finished task: {fin_item}")
            save_list(to_do_list)
        else:
            print(f"Task ID not in list: {args.tid}")
    elif args.command == "edit":
        # Edit task with provided values
        if args.tid in to_do_list:
            # List of tags or None
            if args.tags is not None:
                tags_value = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
            else:
                tags_value = None
            
            to_do_list[args.tid].edit(args.task, args.target, args.priority, tags_value)
            save_list(to_do_list)
            print(f"Edited task: {to_do_list[args.tid]}")
        else:
            print(f"Task ID not in list: {args.tid}")
    elif args.command == "list":
        # Print list of tasks with filters and sorted
        if len(to_do_list) > 0:
            if args.priority == "all":
                priority = 0
            else:
                priority = To_Do_Item.PRIORITY_MAP[args.priority]
            tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
            sort_fields = [s.strip().lower() for s in args.sort.split(",") if s.strip()]
            to_do_print(to_do_list, pending_only = args.pending, finished_only = args.finished, priority = priority, tags = tags, sort_fields = sort_fields)
        else:
            print("To do list empty.")
    elif args.command == "remind":
        # Print reminders
        to_do_reminders(to_do_list, timespan_hours = args.hours)
    elif args.command == "clear":
        # Erase file
        if args.passcode == 1234:
            reset_file()
            print("File cleared.")
        else:
            print("Incorrect passcode.")

    else:
        print("Command not recognized")

if __name__ == "__main__":
    main()
