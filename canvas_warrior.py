## Canvas Interface to Taskwarrior
# Finds all open assignments on Canvas, imports them to Taskwarrior tasks
# User can override wait date, due date, and project

import requests
import json
import subprocess
import time
from packaging import version
from datetime import datetime
from pathlib import Path


#####################################
##          FUNCTIONS
#####################################

# Yes or no from: https://gist.github.com/garrettdreyfus/8153571
def yes_or_no(question, default):
    if default:
        yes_no_string = " (Y/n): "
    else:
        yes_no_string = " (y/N): "

    while "the answer is invalid":
        reply = str(input(question + yes_no_string)).lower().strip()
        if reply[:1] == "y":
            return True
        elif reply[:1] == "n":
            return False
        elif reply[:1] == "":
            return default


# Check if taskwarrior version is greater than or equal to some version
def check_taskwarrior_version(check_version):
    try:
        process_result = subprocess.run(
            ["task", "--version"], capture_output=True, timeout=2, encoding="utf-8"
        )
    except:
        print(
            "FATAL: 'task --version' timed out. Try it yourself and see what goes wrong"
        )
    else:
        if version.parse(process_result.stdout) < version.parse(check_version):
            print(
                "WARNING: taskwarrior version is older than the one used to develop this script. Behavior isn't guaranteed."
            )


# Returns JSON of all pending and waiting tasks
def tasks_fetch():
    try:
        task_proc = subprocess.run(
            ["task", "status:pending", "or", "status:waiting", "export"],
            capture_output=True,
            timeout=2,
        )
    except:
        print("FATAL: 'task export' timed out. Try it yourself and see what goes wrong")
        exit()
    else:
        return json.loads(task_proc.stdout)


# Returns a dict of settings from ~/.task/canvas.json
def settings_fetch():
    home = str(Path.home())
    try:
        f = open("{0}/.task/canvas.json".format(home), "r")
    except:
        print("ERROR: No 'canvas.json' config found in '~/.task'")
        exit()
    else:
        if f.mode == "r":
            settings_raw = f.read()
            settings = json.loads(settings_raw)
        else:
            print("ERROR: Cannot read 'canvas.json' in '~/.task'")
            settings = None

    f.close()
    return settings


# Writes json of associations between course id and project tag to canvas.json
def settings_put(settings):
    home = str(Path.home())
    try:
        f = open("{0}/.task/canvas.json".format(home), "w")
    except:
        print("WARNING: Failed to write 'canvas.json' config in '~/.task'")
    else:
        f.write(json.dumps(settings, indent=3, separators=(",", ": ")))

    f.close()


# Recursive API GET, following header links as long as 'next' exists
def recursive_api_fetch(url, headers):
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data_set = json.loads(response.content.decode("utf-8"))

        if response.links.get("next"):
            next_data = recursive_api_fetch(response.links["next"]["url"], headers)
            data_set = data_set + next_data
    else:
        time.sleep(0.2)
        return recursive_api_fetch(url, headers=headers)

    return data_set


# Fetch User Courses
def get_courses():
    api_url = "{0}courses".format(api_url_base)
    return recursive_api_fetch(api_url, headers=headers)


# Fetch User Assignments for a Course
def get_assignments(course):
    course_id = course["id"]
    api_url = "{0}courses/{1}/assignments".format(api_url_base, course_id)
    return recursive_api_fetch(api_url, headers=headers)


# True if enrolled as student, false if not
def student_enrolled(course):
    return (
        course.get("access_restricted_by_date") == None
        and course["enrollments"][0]["type"] == "student"
        and course["enrollments"][0]["enrollment_state"] == "active"
    )


# True if assignment not due yet or no due date, false if passed
def assignment_not_yet_due(assignment):
    now = datetime.now()
    due_date = assignment.get("due_at")

    if due_date == None:
        return_value = True  # No due date, return true
    elif datetime.strptime(due_date, "%Y-%m-%dT%H:%M:%SZ") > now:
        return_value = True  # Not yet due, return true
    else:
        return_value = False  # Due already, return false

    return return_value


# True if assignment has been submitted
def assignment_submitted(assignment):
    course_id = assignment["course_id"]
    assignment_id = assignment["id"]
    url = "{0}courses/{1}/assignments/{2}/submissions/self".format(
        api_url_base, course_id, assignment_id
    )
    submission = recursive_api_fetch(url, headers=headers)

    if submission["workflow_state"] == "unsubmitted":
        return False
    else:
        return True


# Check if Assignment is in taskwarrior
def task_exists(assignment, taskwarrior_data):
    canv_uuid = "C" + str(assignment["course_id"]) + "A" + str(assignment["id"])
    # check for uuid in taskwarrior
    for task in task_json:
        if task.get("canvas") == canv_uuid:
            # Task exists
            return task

    return False


# Returns 'task import' ready JSON of an assignment
def create_task(assignment):
    canv_course_id = str(assignment["course_id"])
    project_tag = settings.get(canv_course_id)
    canv_assign_id = str(assignment["id"])
    canv_uuid = "C" + canv_course_id + "A" + canv_assign_id
    canv_name = assignment["name"]

    if assignment["due_at"] == None:
        canv_due_date = datetime.today()
    else:
        canv_due_date = datetime.strptime(assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ")

    if assignment["due_at"] == None:
        canv_wait_date = datetime.today()
    else:
        canv_wait_date = datetime.strptime(
            assignment["unlock_at"], "%Y-%m-%dT%H:%M:%SZ"
        )

    task = {}

    # Get User Inputs or take defaults
    task["description"] = input("Description [{0}]: ".format(canv_name)) or canv_name
    task["project"] = input("Project [{0}]: ".format(project_tag)) or project_tag
    task["canvas"] = canv_uuid
    task["due"] = input("Due Date [{0}]: ".format(canv_due_date)) or datetime.strftime(
        canv_due_date, "%Y-%m-%d %H:%M:%S"
    )
    task["wait"] = input(
        "Wait Date [{0}]: ".format(canv_wait_date)
    ) or datetime.strftime(canv_wait_date, "%Y-%m-%d %H:%M:%S")

    # Check for Changing Course-Project Associations and Update Config File
    if task["project"] != project_tag:
        settings[canv_course_id] = task["project"]

    # TODO: Handle this with taskwarrior date styles (friday, today, etc) cause this stinks
    # Reformat User Date Overrides
    task["due"] = datetime.strptime(task["due"], "%Y-%m-%d %H:%M:%S")
    task["wait"] = datetime.strptime(task["wait"], "%Y-%m-%d %H:%M:%S")
    task["due"] = datetime.strftime(task["due"], "%Y%m%dT%H%M%SZ")
    task["wait"] = datetime.strftime(task["wait"], "%Y%m%dT%H%M%SZ")

    return task


# Returns an updated task JSON after working with the user
def task_update(assignment, existing_task):
    canv_name = assignment["name"]
    project_tag = settings.get(str(assignment["course_id"]))
    print("\nChecking Existing Assignment {0}".format(canv_name))

    updated_task = existing_task
    updated_flag = False

    # Check against existing task_json
    if existing_task["description"] != canv_name:
        if yes_or_no(
            "\tDescription New:{0}, Curr:{1}, Update?".format(
                canv_name, existing_task["description"]
            ),
            False,
        ):
            updated_task["description"] = canv_name
            updated_flag = True

    if existing_task["project"] != project_tag:
        if yes_or_no(
            "\tProject New:{0}, Curr:{1}, Update?".format(
                project_tag, existing_task["project"]
            ),
            False,
        ):
            updated_task["project"] = project_tag
            updated_flag = True

    # TODO: Fix this so it can give due dates to tasks that don't have one yet
    if assignment["due_at"] != None and existing_task.get("due") != None:
        canv_due_date = datetime.strptime(assignment["due_at"], "%Y-%m-%dT%H:%M:%SZ")
        task_due_date = datetime.strptime(existing_task["due"], "%Y%m%dT%H%M%SZ")
        if task_due_date != canv_due_date:
            if yes_or_no(
                "\tDue Date New:{0}, Curr:{1}, Update?".format(
                    canv_due_date, task_due_date
                ),
                False,
            ):
                updated_task["due"] = datetime.strftime(canv_due_date, "%Y%m%dT%H%M%SZ")
                updated_flag = True

    if assignment["unlock_at"] != None and existing_task.get("wait") != None:
        canv_wait_date = datetime.strptime(
            assignment["unlock_at"], "%Y-%m-%dT%H:%M:%SZ"
        )
        task_wait_date = datetime.strptime(existing_task["wait"], "%Y%m%dT%H%M%SZ")
        if task_wait_date != canv_wait_date:
            if yes_or_no(
                "\tUnlock At New:{0}, Curr:{1}, Update?".format(
                    canv_wait_date, task_wait_date
                ),
                False,
            ):
                updated_task["wait"] = datetime.strftime(
                    canv_wait_date, "%Y%m%dT%H%M%SZ"
                )
                updated_flag = True

    if updated_flag:
        return updated_task
    else:
        return None


#####################################
##          MAIN
#####################################

check_taskwarrior_version("2.5.1")  # check if old version
settings = settings_fetch()  # get settings file
api_token = settings["api_token"]  # easy API token name
api_url_base = settings["api_url"]  # easy API URL
task_json = tasks_fetch()  # get taskwarrior waiting and pending tasks
import_tasks = []  # declare empty array of tasks to add

# Common Auth header to all requests
headers = {
    "Content-Type": "application/json",
    "Authorization": "Bearer {0}".format(api_token),
}

# Fetch User Courses
courses = get_courses()

# Iterate Over Courses and Get Assignments
# TODO: Parallelize all this to hide API latency
for course in courses:
    if student_enrolled(course):
        assignments = get_assignments(course)

        for assignment in assignments:
            existing_task = task_exists(assignment, task_json)
            if existing_task:
                # Task already exists, update its dates and stuff?
                updated_task = task_update(assignment, existing_task)
                import_tasks += [updated_task] if updated_task is not None else []
            else:
                # Task does not exist
                if assignment_not_yet_due(assignment) and not assignment_submitted(
                    assignment
                ):
                    # Not yet due + not submitted, add
                    import_tasks.append(create_task(assignment))

# Check for changes to project associations and rewrite if so
settings_put(settings)

print(import_tasks)

# Add tasks to taskwarrior
if len(import_tasks) == 0:
    print("\nNothing to Import")
else:
    subprocess.run(["task", "import"], input=json.dumps(import_tasks), encoding="utf-8")
