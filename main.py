from datetime import datetime
import json
import argparse

class To_Do_Item:
    def __init__(self, tid, task, start, target):
        self.tid = tid
        self.task = task
        self.start = start
        self.target = target
        self.finished = False
    
    def __str__(self):
        if self.finished:
            finished_str = "Finished"
        else:
            finished_str = "Pending"

        start_str = datetime.strftime(self.start, "%Y %b %d %H:%M")
        target_str = datetime.strftime(self.target, "%Y %b %d %H:%M")
        
        return f"{self.tid} {self.task} [{finished_str}] (Start: {start_str}, Target: {target_str})"

    def __repr__(self):
        return self.task
    
    def finish(self):
        self.finished = True

    def to_dict(self):
        return {
            "tid": self.tid,
            "task": self.task,
            "start": self.start.isoformat(),
            "target": self.target.isoformat(),
            "finished": self.finished
        }
    
    @classmethod
    def from_dict(cls, data):
        item = cls(
            tid = data["tid"],
            task = data["task"],
            start = datetime.fromisoformat(data["start"]),
            target = datetime.fromisoformat(data["target"])
        )
        item.finished = data.get("finished", False)

        return item

def to_do_add(td_list, item):
    td_list[item.tid] = item

def to_do_remove(td_list, item):
    if item.tid in td_list:
        del td_list[item.tid]

def to_do_print(td_list, pending_only = False, finished_only = False):
    td_sorted = sorted(td_list.values(), key=lambda i: i.start)

    if pending_only and finished_only:
        print("Pending only and finished only filters both True. Select only one or neither.")
        return

    for i in td_sorted:
        if pending_only and not i.finished:
            print(i)
        elif finished_only and i.finished:
            print(i)
        elif not pending_only and not finished_only:
            print(i)

def to_json(td_list):
    json_safe_list = [item.to_dict() for item in td_list.values()]

    return json.dumps(json_safe_list, indent = 4)

def from_json(json_str):
    json_safe_list = json.loads(json_str)

    return {int(tid): To_Do_Item.from_dict(item) for tid, item in json_safe_list}

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
    open(filename, "w").close()

def get_args():
    parser = argparse.ArgumentParser(description = "To Do List Manager")

    subparsers = parser.add_subparsers(dest = "command")

    add_parser = subparsers.add_parser("add", help = "Add a new task")
    add_parser.add_argument("task", type = str, help = "Task description")
    add_parser.add_argument("--start", type = parse_datetime, default = datetime.now(), help = "Start time (YYYY-MM-DD [HH:MM])")
    add_parser.add_argument("--target", type = parse_datetime, required = True, help = "Target time (YYYY-MM-DD [HH:MM])")

    rm_parser = subparsers.add_parser("remove", help = "Remove a task")
    rm_parser.add_argument("tid", type = int, help = "Task ID")

    finish_parser = subparsers.add_parser("finish", help = "Mark a task finished")
    finish_parser.add_argument("tid", type = int, help = "Task ID")

    list_parser = subparsers.add_parser("list", help = "List tasks")
    list_parser.add_argument("--pending", action = "store_true", help = "Show only pending tasks")
    list_parser.add_argument("--finished", action = "store_true", help = "Show only finished tasks")

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
        new_item = To_Do_Item(new_id, args.task, args.start, args.target)
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
    elif args.command == "list":
        if len(to_do_list) > 0:
            to_do_print(to_do_list, pending_only = args.pending, finished_only = args.finished)
        else:
            print("To do list empty.")
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
