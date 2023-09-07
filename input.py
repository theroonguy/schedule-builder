import schedule_builder
import random

courses = ["MATH141", "ENES100", "PHYS235", "CHEM135", "CHEM136"]
# random.shuffle(courses)
semester = "202308"
FC = False      # Freshmen connection

priority_list = [
    {"priority": "earliest_class", "value": ["11:00am"]}
]

schedule_builder.search(courses, priority_list, semester, FC)