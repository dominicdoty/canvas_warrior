## Canvas Interface to Taskwarrior
# Finds all open assignments on Canvas, imports them to Taskwarrior tasks
# User can override wait date, due date, and project

import requests
import json

# Authentication (currently using user generated token)
# TODO: Switch this to OAUTH
from pathlib import Path
home = str(Path.home())
try:
    f=open("{0}/canvas_access.token".format(home), "r")
except:
    print("FATAL: api_token not found or no read permissions in ~/canvas_access.token")
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
def get_assignments(course_id):
    api_url = '{0}courses/{1}/assignments'.format(api_url_base, course_id)
    assignments = requests.get(api_url, headers=headers)

    if assignments.status_code == 200:
        return json.loads(assignments.content.decode('utf-8'))
    else:
        return None


# Fetch User Quizzes for a Course
def get_quizzes(course_id):
    api_url = '{0}courses/{1}/quizzes'.format(api_url_base, course_id)
    quizzes = requests.get(api_url, headers=headers)

    if quizzes.status_code == 200:
        return json.loads(quizzes.content.decode('utf-8'))
    else:
        return None


# Main Work
courses = get_courses()
print(json.dumps(courses, indent=2, separators=(',', ': ')))

# Iterate Over Courses and Get Assignments
# for course in courses:
#     if course.get('access_restricted_by_date', 0) != 'true':
#         print(course['name'])
        # assignments = get_assignments(course['id'])
        # for assignment in assignments:
        #     print('\t{0}'.format(assignment['name']))
        #     print('\t\t{0}'.format(assignment['unlock_at']))
        #     print('\t\t{0}'.format(assignment['due_at']))
        #     print('\t\t{0}'.format(assignment['id']))
