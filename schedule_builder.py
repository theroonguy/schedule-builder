import json
from datetime import datetime
import api_interface as api
import visualizer as viz
import random

""" SCHEDULE BUILDER -- Notes

An Activity is a course or some extracurricular activity that will take up time in the schedule.
An Activity can have one or more Blocks that occur throughout the week.

TO DO:
[ ] If schedule is incomplete, try again with different starting section
[ ] Prefer against certain days
[ ] Prioritize professors for every class
[ ] Mark some sections as confirmed
[ ] Prioritize club/work out/study/free times
[ ] Preferred last class time

Algorithm ideas:
- Rank every possible option in priority, which will determine order.
- Required: course selection, semester, FC option

Options for priorities:
- earliest_class: [time]
- latest_class: [time]
- professor: [course_id, professor name]
- section: [section_id]
- extra: [start_time, end_time]
- free_day: [day]

"""

# courses = ["MATH141", "ENES113", "PHYS260", "CHEM135", "ENES100"]
# courses = ["MATH141", "ENES102", "PHYS235", "CHEM135", "CHEM136"]
# random.shuffle(courses)
courses = []
semester = "202308"
FC = False      # Freshmen connection

# priority_list = [
#     {"priority": "latest_class", "value": ["2:00pm"]},
#     {"priority": "earliest_class", "value": ["8:00am"]}
# ]

priority = 0

schedule = {
    "M": [],
    "Tu": [],
    "W": [],
    "Th": [],
    "F": []
}

def jprint(obj):
    # create a formatted string of the Python JSON object
    text = json.dumps(obj, sort_keys=True, indent=4)
    print(text)

def add_section(section_id, constraints):
    """Adds a new section from section_id. Returns new section object."""
    new_section = Class(section_id)
    new_section.add_courses()
    if new_section.check_conflicts(constraints):
        # If there are no conflicts, add to schedule.
        new_section.add_blocks_to_schedule()
        return new_section

def find_section(course, constraints=None):
    """Runs through available sections for a course until it finds one with no conflicts.
    course: self explanatory
    constraints: List of constraints from the priority list that will affect section search."""
    sections = api.get_course(course)['sections']
    for sect in sections:
        new_sect = add_section(sect, constraints)
        if new_sect:
            print('Section found: ', new_sect.id)
            return new_sect
    print('No sections compatible.')
    return False

def convert_datetime(datetime_str):
    format = '%I:%M%p'
    date = datetime.strptime(datetime_str, format)
    return date

def overlap(first_inter, second_inter):
    latest_start = max(first_inter['starting_time'], second_inter['starting_time'])
    earliest_end = min(first_inter['ending_time'], second_inter['ending_time'])
    delta = (earliest_end - latest_start)
    if delta.seconds >= 0 and delta.days == 0:
        return delta.seconds
    return False

def visualize():
    viz.gen_text(schedule)
    viz.visualize()

class Activity():
    """Base class for activities that take up blocks of time."""
    def __init__(self, id, desc="", blocks=None):
        self.id = id
        self.desc = desc
        self.blocks = blocks
    
    def add_blocks_to_schedule(self):
        """Adds all local blocks of time into the schedule"""
        for block in self.blocks:
            schedule[block['day']].append(block)

    def get_blocks_inters(self, day=None):
        """Returns all the time intervals for its own blocks, or for a specific day."""
        
        inters = []
        if not day:
            for day in schedule:
                for block in self.blocks:
                    if block['day'] == day:
                        inters.append({
                            "starting_time": block['start_time'],
                            "ending_time": block['end_time']})
        else:
            for block in self.blocks:
                if block['day'] == day:
                    inters.append({
                        "starting_time": block['start_time'],
                        "ending_time": block['end_time']})
        
        return inters

    def del_self(self, err=""):
        """Deletes self and removes all blocks from the schedule"""
        print(f" ({self.id}) ERROR: {err}")

        for day in schedule:
            for i in range(len(schedule[day])):
                if schedule[day][i]['id'] == self.id:
                    schedule[day].pop(i)
        
        del self

class Class(Activity):
    """Activity subclass for Classes."""

    def __init__(self, id, desc="", blocks=None):
        super().__init__(id, desc, blocks)
        section_info = api.get_section(section_id=self.id)
        self.instructors = section_info[0]['instructors']
        self.blocks=[]

    def add_block(self, day, building, room, start_time, end_time):
        """Adds a time block to self."""
        block = {
            "id": self.id,
            "day": day,
            "building": building,
            "room": room,
            "start_time": start_time,
            "end_time": end_time
        }
        self.blocks.append(block)

    def add_courses(self):
        """Uses the UMD API to add all classes of specified section through time blocks."""
        section_info = api.get_section(section_id=self.id)
        
        for i in range(len(section_info[0]['meetings'])):       # insert all classes into the Class class
            meeting = section_info[0]['meetings'][i]
            if not meeting['days'] == '':
                start = convert_datetime(meeting['start_time'])
                end = convert_datetime(meeting['end_time'])
                if "M" in meeting['days']: self.add_block("M", meeting['building'], meeting['room'], start, end)
                if "Tu" in meeting['days']: self.add_block("Tu", meeting['building'], meeting['room'], start, end)
                if "W" in meeting['days']: self.add_block("W", meeting['building'], meeting['room'], start, end)
                if "Th" in meeting['days']: self.add_block("Th", meeting['building'], meeting['room'], start, end)
                if "F" in meeting['days']: self.add_block("F", meeting['building'], meeting['room'], start, end)

    def check_conflicts(self, constraints):
        """Checks for various conflicts. If there are no conflicts, returns True. Else, returns False.
        - Conflicts with earliest preferred time
        - Conflicts with Freshman Connection option
        - Conflicts with some other time block in the schedule"""
        # loop through every other activity and its time interval and compare it with its own
        
        if self.del_if_FC():
            return False

        # repeat for every day of the week
        for day in schedule:
            act_inters = self.get_blocks_inters(day)
            
            try:
                for constraint in constraints:
                    if constraint['priority'] == 'earliest_class':
                        too_early = self.is_too_early(day, convert_datetime(constraint['value'][0]))
                        if too_early:
                            self.del_self(f"Starts {too_early} seconds too early"); return False
                    elif constraint['priority'] == "latest_class":
                        too_late = self.is_too_late(day, convert_datetime(constraint['value'][0]))
                        if too_late:
                            self.del_self(f"Ends {too_late} seconds too late"); return False
            except: pass

            # # match against earliest time
            # for act_inter in act_inters:
            #     if (act_inter['starting_time'] - earliest_class).seconds >= 0 and (act_inter['starting_time'] - earliest_class).days == 0:
            #         continue
            #     else: 
            #         self.del_self(f"Starts {(3600*24) - (act_inter['starting_time'] - earliest_class).seconds} too early"); return False

            # # check for freshmen connection
            # if not FC:
            #     if self.id.split("-")[1].startswith("FC"):
            #         self.del_self("FC class"); return False

            # get all intervals for other activities
            other_inters = []
            for block in schedule[day]:       # loop through other activities on that day
                if not block['id'] == self.id:
                    other_inters.append({
                        "starting_time": block['start_time'],
                        "ending_time": block['end_time']})
            
            # compare for conflicts
            for act_inter in act_inters:
                for other_inter in other_inters:
                    ol = overlap(act_inter, other_inter)
                    if ol:
                        self.del_self(f"Overlapping {ol} seconds."); return False        # conflicts with other classes
                    
        return True

    def del_if_FC(self):
        # check for freshmen connection
        if not FC:
            if self.id.split("-")[1].startswith("FC"):
                self.del_self("FC class"); return True

    def is_too_early(self, day, boundary):
        # match against earliest time
        for act_inter in self.get_blocks_inters(day):
            if (act_inter['starting_time'] - boundary).seconds >= 0 and (act_inter['starting_time'] - boundary).days == 0:
                return False
            else: 
                return (3600*24) - (act_inter['starting_time'] - boundary).seconds

    def is_too_late(self, day, boundary):
        # match against latest time
        for act_inter in self.get_blocks_inters(day):
            if (boundary - act_inter['ending_time']).seconds >= 0 and (boundary - act_inter['ending_time']).days == 0:
                return False
            else: 
                return (3600*24) - (boundary - act_inter['ending_time']).seconds

class Extra(Activity):
    """Activity subclass for extracurricular activities."""

    def __init__(self, id, desc="", blocks=None):
        super().__init__(id, desc, blocks)

        self.blocks = []

    def add_block(self, day, start_time, end_time, location=""):
        block = {
            "id": self.id,
            "day": day,
            "start_time": start_time,
            "end_time": end_time,
            "location": location
        }
        self.blocks.append(block)
        schedule[day].append(block)

# workout = Extra('workout', "work out at eppley rec center")
# workout.add_block("Tu", convert_datetime("9:50am"), convert_datetime("8:30pm"), "Eppley Rec Center")

earliest_class = convert_datetime("8:00am")

# if priority_list[priority]['priority'] == "earliest_class":
#     print(f"PRIORITY {priority}: Earliest class at {priority_list[priority]['value'][0]}")
#     earliest_class = convert_datetime(priority_list[priority]['value'][0])

def search(courses, priority_list, semester, FC):
    courses = courses
    semester = semester
    FC = FC

    for i in enumerate(priority_list):
        print(f"Priority {i}: {priority_list[i[0]]['priority']}")

    success = True

    for course in courses:      # loop through all courses
        # all constraints are considered at first
        priority = len(priority_list)
        found = False
        while not found:        # if the section is not found, try again with less constraints
            try:
                new_section = find_section(course, priority_list[0:priority])
            except: new_section = find_section(course)

            if new_section: # if a section cannot be found with current constraints
                found = True
            else:
                if priority == -1:
                    print('priorities are too constraining')
                    success = False
                    break
                print('could not find with priority ', priority_list[0:priority])
                priority -= 1

    if success:
        visualize()