from queue import Queue
from csv import DictReader, DictWriter
from threading import Condition


CONDITION_OBJECT = Condition()
DATABASE_FIELDNAMES = ["name", "latest_post_time", "latest_post_url"]


def database_processor():
    while True:
        CONDITION_OBJECT.acquire()
        CONDITION_OBJECT.wait()
        if not database.add_queue.empty():
            _add_site(database.add_queue.get())
            database.add_queue.task_done()
        elif not database.update_queue.empty():
            _update_site(database.update_queue.get())
            database.update_queue.task_done()
        elif not database.remove_queue.empty():
            _remove_site(database.remove_queue.get())
            database.remove_queue.task_done()
        CONDITION_OBJECT.release()
    assert False


class DatabaseManager:
    def __init__(self):
        self.add_queue = Queue(0)
        self.update_queue = Queue(0)
        self.remove_queue = Queue(0)
        self.sites = []
        with open("sites.csv", "r") as file:
            reader = DictReader(file)
            for row in reader:
                self.sites.append(row)

    def add_site(self, post):
        self.add_queue.put(post)

    def update_site(self, post):
        self.update_queue.put(post)

    def remove_site(self, site_name: str):
        self.remove_queue.put(site_name)


database = DatabaseManager()


def _add_site(post):
    with open("sites.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=DATABASE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(post)


def _update_site(post):
    found = False
    for i, row in enumerate(database.sites):
        if post["name"] == row["name"]:
            database.sites[i] = post
            found = True
            break

    if not found:
        return

    with open("sites.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=DATABASE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(database.sites)


def _remove_site(site_name):
    found = False
    for i, row in enumerate(database.sites):
        if site_name == row["name"]:
            database.sites.pop(i)
            found = True
            break

    if not found:
        return

    with open("sites.csv", "w", newline="") as file:
        writer = DictWriter(file, fieldnames=DATABASE_FIELDNAMES)
        writer.writeheader()
        writer.writerows(database.sites)
