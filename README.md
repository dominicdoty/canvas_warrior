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
All user settings are in ~/.task/canvas.json in json format. Below are example settings.

### API URL
"api_url":"http://canvas.colorado.edu/api/v1/"

### Development API Key
The script currently uses [developer keys](https://canvas.instructure.com/doc/api/file.developer_keys.html) while its under development and not meant for general distribution.

"api_token":"randomfaketoken~asdfasdfasdfasdfasdf"

### Course - Project Associations
The script will look for course id numbers in this file and use them to auto assign projects in taskwarrior. This is optional since the script will fill these in on its own as you use it.

"51572":"PCB_Class"

### Taskwarrior Config
This script uses user defined attributes in taskwarrior. Taskwarrior will preserve our attributes even if it doesn't know what they are though, so this step is optional.

Add to .taskrc:
 * uda.canvas.type=string
 * uda.canvas.label=Canvas UUID