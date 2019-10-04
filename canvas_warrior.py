## Canvas Interface to Taskwarrior
# Finds all open assignments on Canvas, imports them to Taskwarrior tasks
# User can override wait date, due date, and project

import requests
import json

api_token =  # TODO: Add a way to get this from a command line arg or something for now
api_url_base = 'http://canvas.colorado.edu/api/v1/'

headers = { 'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(api_token)}

def get_courses():
    api_url = '{0}courses'.format(api_url_base)
    courses = requests.get(api_url, headers=headers)

    if courses.status_code == 200:
        return json.loads(courses.content.decode('utf-8'))
    else:
        return None


def get_assignments(course_id):
    api_url = '{0}courses/{1}/assignments'.format(api_url_base, course_id)
    courses = requests.get(api_url, headers=headers)

    if courses.status_code == 200:
        return json.loads(courses.content.decode('utf-8'))
    else:
        return None


def get_quizzes(course_id):
    api_url = '{0}courses/{1}/quizzes'.format(api_url_base, course_id)
    courses = requests.get(api_url, headers=headers)

    if courses.status_code == 200:
        return json.loads(courses.content.decode('utf-8'))
    else:
        return None


courses = get_courses()
print(courses.id)
# for k, v in courses['course_id'].items():
    # print('{0}:{1}'.format(k,v))


# example request
# curl https://<canvas>/api/v1/courses/<course_id>/quizzes \
#      -H 'Authorization: Bearer <token>'

# courses
# GET /api/v1/courses

# assignments
# GET /api/v1/courses/:course_id/assignments
# GET /api/v1/courses/:course_id/assignment_groups/:assignment_group_id/assignments

# quizzes
# GET /api/v1/courses/:course_id/quizzes


## References
# https://www.digitalocean.com/community/tutorials/how-to-use-web-apis-in-python-3
# https://docs.python-guide.org/scenarios/json/

# https://canvas.instructure.com/doc/api/all_resources.html
# https://canvas.instructure.com/doc/api/all_resources.html#method.courses.index
# https://canvas.instructure.com/doc/api/all_resources.html#method.assignments_api.index
# https://canvas.instructure.com/doc/api/all_resources.html#method.quizzes/quizzes_api.index