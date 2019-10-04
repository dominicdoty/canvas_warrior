## Canvas Interface to Taskwarrior
# Finds all open assignments on Canvas, imports them to Taskwarrior tasks
# User can override wait date, due date, and project

import requests
import json

api_token = '' # TODO: Add a way to get this from a command line arg or something for now
api_url_base = 'http://canvas.example.com/api/v1/'


headers = {'Content-Type': 'application/json',
            'Authorization': 'Bearer {0}'.format(api_token)}

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