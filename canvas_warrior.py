## Canvas Interface to Taskwarrior
# Finds all open assignments on Canvas, imports them to Taskwarrior tasks
# User can override wait date, due date, and project

import requests
import json
from datetime import datetime

# Authentication (currently using user generated token)
# TODO: Switch this to OAUTH
from pathlib import Path
home = str(Path.home())
try:
    f=open("{0}/canvas_access.token".format(home), "r")
except:
    print('FATAL: api_token not found or no read permissions in {0}/canvas_access.token'.format(home))
    exit()
else: 
    if f.mode == 'r':
        api_token = f.read().rstrip()
        [line.rstrip('\n') for line in api_token]
        print('api_token = {0}'.format(api_token))

# Common URL to all requests
api_url_base = 'http://canvas.colorado.edu/api/v1/'


# Common Auth header to all requests
headers = { 'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(api_token)}

# Fetch User Courses
def get_courses():
    api_url = '{0}courses'.format(api_url_base)
    courses = requests.get(api_url, headers=headers)

    if courses.status_code == 200:
        return json.loads(courses.content.decode('utf-8'))
    else:
        return None


# Fetch User Assignments for a Course
def get_assignments(course):
    course_id = course['id']
    api_url = '{0}courses/{1}/assignments'.format(api_url_base, course_id)
    assignments = requests.get(api_url, headers=headers)

    if assignments.status_code == 200:
        return json.loads(assignments.content.decode('utf-8'))
    else:
        return None


# Check if Assignment is in taskwarrior
def taskwarrior(course_id, assignment_id):
    uuid = str(course_id) + str(assignment_id)
    #check for uuid in taskwarrior files todo or completed
    #if its there check dates?
       #if dates and uuid good return None
       #else check with user to update dates?
    #else return something?
    return


# True if enrolled as student, false if not
def student_enrolled(course):
    return (course.get('access_restricted_by_date') == None and
            course['enrollments'][0]['type'] == 'student' and
            course['enrollments'][0]['enrollment_state'] == 'active')


# True if assignment not due yet or no due date, false if passed
def assignment_not_yet_due(assignment):
    now = datetime.now()
    due_date = assignment.get('due_at')

    if due_date == None:
        return_value = True     #No due date, return true
    elif datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ') > now:
        return_value = True     #Not yet due, return true
    else:
        print("\tassign: ", assignment['name'])
        print("\t\tnow: ", now)
        print("\t\tdue: ", datetime.strptime(due_date, '%Y-%m-%dT%H:%M:%SZ'))
        return_value = False    #Due already, return false

    return return_value


# Main Work
courses = get_courses()
# print(json.dumps(courses, indent=2, separators=(',', ': ')))

# Iterate Over Courses and Get Assignments
for course in courses:
    if student_enrolled(course):
        print(course['name'])
        assignments = get_assignments(course)

        for assignment in assignments:
            if assignment_not_yet_due(assignment):
                print('\t{0}'.format(assignment['name']))
                print('\t\t{0}'.format(assignment['unlock_at']))
                print('\t\t{0}'.format(assignment['due_at']))
                print('\t\t{0}'.format(assignment['id']))
