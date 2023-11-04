from db_sqlite import db
from prompt_toolkit import PromptSession, prompt
import os

class Todo:
    def __init__(self):
        self.db = db("todo")
        self.list = 1

    def add_user(self, username, password):
        self.db.insert("users", {"username": username, "password": password})

    def rm_user(self, username, password):
        self.db.delete("users", {"username": username, "password": password})

    def check_task(self, task):
        self.task_title = self.db.select("tasks", columns=["task"], conditions={"task_id": task,"list_id": self.list})
        self.task_done = self.db.select("tasks", columns=["done"], conditions={"task_id": task,"list_id": self.list})

        if self.task_done and self.task_done[0][0] == False:
            self.db.update("tasks", {"done": True}, {"task_id": task})
            return "Task is now marked as done."
        else:
            return "Task is already done."

    def update_task(self, task, title, status=None):
        try:
            self.db.update("tasks", {"task": title}, {"task_id": task})
            return "Task is updated."
        except Exception as e:
            print(f"Exception occurred: {e}")
            return "An exception occurred while updating the task."

    def rm_task(self, task):
        try:
            self.db.delete("tasks", {"task_id":task})
            return "Task is removed."
        except Exception as e:
            print(f"Exception occurred: {e}")
            return "An exception occurred while deleting the task."

    def get_tasks(self):
        self.task_data = self.db.select(
            "tasks",
            columns=["task_id", "task", "due_date"],
            conditions={"list_id": self.list, "done": False}
        )
        return self.task_data

    def get_finished_tasks(self):
        self.task_title = self.db.select("tasks", columns=["task_id", "task", "due_date"], conditions={"list_id": self.list, "done": True})
        return self.task_title

    def change_list(self, list_id):
        list_exists = self.db.select("lists", columns=["list_id"], conditions={"list_id": list_id})

        if list_exists:
            self.list = list_id
            return f"Switched to list {self.list}."
        else:
            return f"List {self.list} does not exist."

    def print_tasks(self):
        self.unfinished_tasks = self.get_tasks()
        self.finished_tasks = self.get_finished_tasks()

        # Check if there are any tasks, and set a default task_id_width if not
        if not (self.finished_tasks or self.unfinished_tasks):
            task_id_width = 1
        else:
            task_id_width = max(len(str(task[0])) for task in self.finished_tasks + self.unfinished_tasks)

        task_format = f"{{:{task_id_width}}}  {{:<30}}  until: {{}}"

        print("\nFinished tasks:\n")
        for task in self.finished_tasks:
            print(task_format.format(task[0], task[1], task[2]))

        print("\nUnfinished tasks:\n")
        for task in self.unfinished_tasks:
            print(task_format.format(task[0], task[1], task[2]))


    def create_task(self, title, date=None):
        try:
            if date != None:
                self.db.insert("tasks", {"list_id":self.list, "task":title, "done":False, "due_date":date})
                return "Task created successfully."
            else:
                self.db.insert("tasks", {"list_id":self.list, "task":title, "done":False})
                return "Task created successfully."
        except Exception as e:
            print(f"Exception occurred: {e}")
            return "An exception occurred while creating the task."

    def search_tasks(self, keyword):
        matching_tasks = self.db.select("tasks", columns=["task_id", "task"], conditions={"list_id": self.list, "task LIKE ?": f"%{keyword}%"})
        return matching_tasks

    def set_due_date(self, task_id, due_date):
        try:
            self.db.update("tasks", {"due_date": due_date}, {"task_id": task_id})
            return "Due date set successfully."
        except Exception as e:
            print(f"Exception occurred: {e}")
            return "An exception occurred while setting due date."

    def print_help(self):
        print("\nCommands:")
        help_text = [
            ("help", "Display this help menu"),
            ("done <task_id>", "Mark a task as done"),
            ("remove <task_id>", "Remove a task"),
            ("update <task_id> <new_title>", "Update a task's title"),
            ("create <new_task_title>", "Create a new task"),
            ("list <list_id>", "Switch to a different list"),
            ("exit", "Exit the todo tool")
        ]
        max_command_length = max(len(command) for command, _ in help_text)
        
        for command, description in help_text:
            print(f"{command:<{max_command_length}}: {description}")

    def create_list(self, list_title):
        self.db.insert("lists", {"list_name":list_title})
        return "List successfully created."

def clean():
    if os.name == "nt":  # Windows
        os.system("cls")
    else:  # Unix/Linux/Mac
        os.system("clear")

def main():
    global todo
    clean()
    todo = Todo()
    session = PromptSession()

    while True:
        todo.print_tasks()
        try:
            action = session.prompt("\n\nAction (H for Help): ")

            if action.lower() == "h" or action.lower() == "help":
                clean()
                todo.print_help()
                status = "Help displayed."

            elif action.startswith("done") or action.startswith("check") or action.startswith("finish"):
                parts = action.split()
                if len(parts) == 2 and parts[1].isdigit():
                    task_id = int(parts[1])
                    status = todo.check_task(task_id)
                    clean()
                else:
                    status = "Invalid input. Use 'done <task_id>'"

            elif action.startswith("remove") or action.startswith("delete") or action.startswith("rm"):
                parts = action.split()
                if len(parts) == 2 and parts[1].isdigit():
                    task_id = int(parts[1])
                    status = todo.delete_task(task_id)
                    clean()
                else:
                    status = "Invalid input. Use 'remove <task_id>'"

            elif action.startswith("update"):
                parts = action.split(maxsplit=3)
                if len(parts) >= 4 and parts[1].isdigit():
                    task_id = int(parts[1])
                    action_type = parts[2]
                    value = parts[3]
                    if action_type == "title":
                        status = todo.update_task(task_id, value)
                        clean()

                    elif action_type == "date":
                        status = todo.set_due_date(task_id, value)
                        clean()

                    else:
                        status = "Invalid input. Use 'update <task_id> title <new_title>' or 'update <task_id> date <new_date>'"
                else:
                    status = "Invalid input. Use 'update <task_id> <new_title>' or 'update <task_id> date <new_date>'"

            elif action.startswith("create"):
                parts = action.split(maxsplit=2)
                if len(parts) == 3:
                    date, title = parts[1], parts[2]
                    if date.lower() != "none":
                        status = todo.create_task(title, date)
                    else:
                        status = todo.create_task(title)
                elif len(parts) == 2:
                    title = parts[1]
                    status = todo.create_task(title)
                else:
                    status = "Invalid input. Use 'create <due_date> <new_title>' or 'create <new_title>'"
                clean()



            elif action.startswith("list"):
                parts = action.split(maxsplit=1)
                if len(parts) == 2 and parts[1].isdigit():
                    list_id = int(parts[1])
                    status = todo.change_list(list_id)
                    clean()
                elif len(parts) >= 3:
                    action = parts[1]
                    title = " ".join(parts[2:])
                    if action == "new" or action == "create":
                        status = todo.create_list(title)
                else:
                    status = "Invalid input. Use 'list <list_id>'"

            elif action.lower() == "user":
                parts = action.split()
                if len(parts) == 3 and parts[2] == "add":
                    passwd_nr1 = prompt("Password: ", is_password=True)
                    passwd_nr2 = prompt("Confirm Password: ", is_password=True)
                    todo.add_user(parts[1], passwd_nr2)  # Adjusted method call

                elif len(parts) == 3 and (parts[2] == "rm" or parts[2] == "remove" or parts[2] == "delete"):
                    passwd_nr1 = prompt("Password: ", is_password=True)
                    passwd_nr2 = prompt("Confirm Password: ", is_password=True)
                    todo.rm_user(parts[1], passwd_nr2)  # Adjusted method call

                elif len(parts) == 2 and parts[1] == "add":
                    username = prompt("Username: ")
                    passwd_nr1 = prompt("Password: ", is_password=True)
                    passwd_nr2 = prompt("Confirm Password: ", is_password=True)
                    todo.add_user(username, passwd_nr2)  # Adjusted method call

                elif len(parts) == 2 and (parts[1] == "rm" or parts[1] == "remove" or parts[1] == "delete"):
                    username = prompt("Username: ")
                    passwd_nr1 = prompt("Password: ", is_password=True)
                    passwd_nr2 = prompt("Confirm Password: ", is_password=True)
                    todo.rm_user(username, passwd_nr2)  # Adjusted method call

            elif action.lower() == "exit":
                break

            else:
                status = "Invalid action"

        except Exception as ex:
                status = f"An error occurred\n{ex}"

        finally:
            todo.print_tasks()


if __name__ == '__main__':
    main()
