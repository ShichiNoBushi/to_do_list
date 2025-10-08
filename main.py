from datetime import datetime
import json
import argparse
import os

class To_Do_Item:
    PRIORITY_MAP = {"low": 1, "medium": 2, "high": 3}
    PRIORITY_LABELS = {1: "Low", 2: "Medium", 3: "High"}

    def __init__(self, tid, task, start, target, updated = datetime.now(), priority = "medium", tags = None):
        self.tid = tid
        self.task = task
        self.start = start
        self.target = target
        self.updated = updated
        self.finished = None
        self.priority = To_Do_Item.PRIORITY_MAP.get(priority.lower(), 2)
        self.tags = tags if tags else []
    
    def __str__(self):
        if self.finished is not None:
            finished_str = f"Finished {datetime.strftime(self.finished, '%Y %b %d %H:%M')}"
        else:
            finished_str = "Pending"

        priority_label = To_Do_Item.PRIORITY_LABELS[self.priority]
        start_str = datetime.strftime(self.start, "%Y %b %d %H:%M")
        target_str = datetime.strftime(self.target, "%Y %b %d %H:%M")
        updated_str = datetime.strftime(self.updated, "%Y %b %d %H:%M")
        tags_str = ", ".join(self.tags)
        
        return f"{self.tid} {self.task} [{finished_str}] (Priority: {priority_label}, Start: {start_str}, Target: {target_str}, Last updated: {updated_str})\n    Tags: {tags_str}"

    def __repr__(self):
        return self.task
    
    def edit(self, task = None, target = None, priority = None, tags = None):
        if task is not None:
            self.task = task
        
        if target is not None:
            if target < self.start:
                print("Warning: Target time is before the start time.")
            self.target = target

        if priority is not None:
            self.priority = To_Do_Item.PRIORITY_MAP.get(priority.lower(), self.priority)

        if tags is not None:
            self.tags = tags

        self.updated = datetime.now()
        print(f"Task {self.tid} updated at {self.updated.strftime('%Y-%m-%d %H:%M')}")
    
    def finish(self):
        if self.finished is None:
            self.finished = datetime.now()
            self.updated = datetime.now()

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

def to_do_add(td_list, item):
    td_list[item.tid] = item

def to_do_remove(td_list, item):
    if item.tid in td_list:
        del td_list[item.tid]

def to_do_print(td_list, pending_only = False, finished_only = False, priority = 0, tags = None):
    td_sorted = sorted(td_list.values(), key=lambda i: (-i.priority, i.start))

    if pending_only and finished_only:
        print("Pending only and finished only filters both True. Select only one or neither.")
        return

    for i in td_sorted:
        is_pending_match = (not finished_only and (not pending_only or i.finished is None))
        is_finished_match = (not pending_only and (not finished_only or i.finished is not None))
        is_status_match = is_pending_match or is_finished_match

        is_priority_match = (priority == 0 or i.priority == priority)
        is_tag_match = (tags is None or all(tag in i.tags for tag in tags))

        if is_status_match and is_priority_match and is_tag_match:
            print(i)

def to_do_reminders(td_list, timespan_hours = 24):
    now = datetime.now()
    upcoming = []

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

    if len(upcoming) == 0:
        print("No upcoming or overdue tasks.")
        return
    
    for item, remaining, status in sorted(upcoming, key = lambda x: x[1]):
        print(f"{item.task}: {status} (Target: {item.target.strftime('%Y %b %d %H:%M')})")

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

def to_json(td_list):
    json_safe_list = [item.to_dict() for item in td_list.values()]

    return json.dumps(json_safe_list, indent = 4)

def from_json(json_str):
    json_safe_list = json.loads(json_str)

    return {item["tid"]: To_Do_Item.from_dict(item) for item in json_safe_list}

def save_list(td_list, filename = "tasks.json"):
    with open(filename, "w") as f:
        json.dump([item.to_dict() for item in td_list.values()], f, indent = 4)

def load_list(filename = "tasks.json"):
    try:
        with open(filename, "r") as f:
            data = json.load(f)
        return {item["tid"]: To_Do_Item.from_dict(item) for item in data}
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        return {}
    
def reset_file(filename = "tasks.json"):
    if os.path.exists(filename):
        os.remove(filename)

def get_args():
    parser = argparse.ArgumentParser(description = "To Do List Manager")

    subparsers = parser.add_subparsers(dest = "command")

    add_parser = subparsers.add_parser("add", help = "Add a new task")
    add_parser.add_argument("task", type = str, help = "Task description")
    add_parser.add_argument("--priority", type = str, default = "Medium", help = "Priority of task (High, Medium, or Low)")
    add_parser.add_argument("--start", type = parse_datetime, default = None, help = "Start time (YYYY-MM-DD [HH:MM])")
    add_parser.add_argument("--target", type = parse_datetime, required = True, help = "Target time (YYYY-MM-DD [HH:MM])")
    add_parser.add_argument("--tags", type = str, default = "", help = "Tags for task groups (seperate multiples by commas)")

    rm_parser = subparsers.add_parser("remove", help = "Remove a task")
    rm_parser.add_argument("tid", type = int, help = "Task ID")

    finish_parser = subparsers.add_parser("finish", help = "Mark a task finished")
    finish_parser.add_argument("tid", type = int, help = "Task ID")

    edit_parser = subparsers.add_parser("edit", help = "Edit an existing task")
    edit_parser.add_argument("tid", type = int, help = "Task ID")
    edit_parser.add_argument("--task", type = str, default = None, help = "Task description")
    edit_parser.add_argument("--priority", type = str, default = None, help = "Priority of task (High, Medium, or Low)")
    edit_parser.add_argument("--target", type = parse_datetime, default = None, help = "Target time (YYYY-MM-DD [HH:MM])")
    edit_parser.add_argument("--tags", type = str, default = None, help = "Tags for task groups (seperate multiples by commas)")

    list_parser = subparsers.add_parser("list", help = "List tasks")
    list_parser.add_argument("--pending", action = "store_true", help = "Show only pending tasks")
    list_parser.add_argument("--finished", action = "store_true", help = "Show only finished tasks")
    list_parser.add_argument("--priority", type = str, default = "all", choices = ["low", "medium", "high", "all"], help = "Filter by priority (High, Medium, or Low)")
    list_parser.add_argument("--tags", type = str, default = "", help = "Filter by group tags (seperate multiples by commas)")

    reminder_parser = subparsers.add_parser("remind", help = "List tasks soon or overdue")
    reminder_parser.add_argument("--hours", type = float, default = 24, help = "Time window in hours for upcoming tasks")

    clear_parser = subparsers.add_parser("clear", help = "Clears list of tasks (requires code)")
    clear_parser.add_argument("--passcode", type = int, required = True, help = "Passcode to clear list")

    return parser.parse_args()

def parse_datetime(value):
    formats = [
        "%Y-%m-%d %H:%M",
        "%Y-%m-%d",
        "%H:%M"
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
    to_do_list = load_list()

    args = get_args()

    if args.command == "add":
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
        if args.tid in to_do_list:
            rm_item = to_do_list[args.tid]
            to_do_remove(to_do_list, rm_item)
            print(f"Removed task: {rm_item}")
            save_list(to_do_list)
        else:
            print(f"Task ID not in list: {args.tid}")
    elif args.command == "finish":
        if args.tid in to_do_list:
            fin_item = to_do_list[args.tid]
            fin_item.finish()
            print(f"Finished task: {fin_item}")
            save_list(to_do_list)
        else:
            print(f"Task ID not in list: {args.tid}")
    elif args.command == "edit":
        if args.tid in to_do_list:
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
        if len(to_do_list) > 0:
            if args.priority == "all":
                priority = 0
            else:
                priority = To_Do_Item.PRIORITY_MAP[args.priority]
            tags = [tag.strip() for tag in args.tags.split(",") if tag.strip()]
            to_do_print(to_do_list, pending_only = args.pending, finished_only = args.finished, priority = priority, tags = tags)
        else:
            print("To do list empty.")
    elif args.command == "remind":
        to_do_reminders(to_do_list, timespan_hours = args.hours)
    elif args.command == "clear":
        if args.passcode == 1234:
            reset_file()
            print("File cleared.")
        else:
            print("Incorrect passcode.")

    else:
        print("Command not recognized")

if __name__ == "__main__":
    main()
