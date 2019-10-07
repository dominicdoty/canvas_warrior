# canvas_warrior
CLI interface between [Canvas](https://www.instructure.com/canvas/) API and Taskwarrior

## What it Does
Uses the Canvas API to fetch all assignments for a user where:
 * The user is a student in the course (not TA/Instructor)
 * The assignment has no due date, or is not yet due
 * The assignment has not yet been submitted

It then interactively works with the user to create a task for each assignment, assigning:
 * Task name
 * Project
 * Due date
 * Wait date

Desired additions after core functionality is achieved include:
 * Checking submitted, past due, and dateless assignments against taskwarrior to update existing tasks
 * A non-interactive mode, with options to print all changes that would be made, and to make those changes accepting all default values

## Setup
### API URL
Right now the API URL for University of Colorado, Boulder is hardcoded in. You will need to change it to your URL.

### Development API Key
The script currently uses [developer keys](https://canvas.instructure.com/doc/api/file.developer_keys.html) while its under development and not meant for general distribution. It expects the key to be in ~/canvas_access.token .

Eventually I will move to OAUTH once the script works correctly.

### Taskwarrior Config
Need to add to .taskrc:
 * uda.canvas.type=string
 * uda.canvas.label=Canvas UUID

This allows tracking of associations between canvas assignments and taskwarrior tasks. Later I'll add a check/add for this in the script.