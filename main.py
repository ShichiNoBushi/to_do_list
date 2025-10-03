from datetime import datetime
import json

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

def main():
    to_do_list = load_list()

    print("Loading list:")
    to_do_print(to_do_list)

    print("\nResetting file:")
    reset_file()
    to_do_list = load_list()
    to_do_print(to_do_list)

    to_do_add(to_do_list, To_Do_Item(0, "Buy groceries", datetime.strptime("2025 Oct 2", "%Y %b %d"), datetime.strptime("2025 Oct 3", "%Y %b %d")))
    to_do_add(to_do_list, To_Do_Item(1, "Call Mom", datetime.strptime("2025 Oct 1", "%Y %b %d"), datetime.strptime("2025 Oct 2", "%Y %b %d")))
    to_do_add(to_do_list, To_Do_Item(2, "Finish Python project", datetime.strptime("2025 Oct 1", "%Y %b %d"), datetime.strptime("2025 Oct 31", "%Y %b %d")))

    print("\nFull list:")
    to_do_print(to_do_list)

    to_do_list[1].finish()

    print("\nAfter one task finished:")
    to_do_print(to_do_list)

    print("\nTo JSON:")
    print(to_json(to_do_list))

    print("\nFrom JSON:")
    to_do_print(to_do_list)

    print("\nFilter pending only:")
    to_do_print(to_do_list, pending_only = True)

    print("\nFilter finished only")
    to_do_print(to_do_list, finished_only = True)

    to_do_remove(to_do_list, to_do_list[1])

    print("\nRemoved one:")
    to_do_print(to_do_list)

    print("\nSaving list...")
    save_list(to_do_list)

if __name__ == "__main__":
    main()
