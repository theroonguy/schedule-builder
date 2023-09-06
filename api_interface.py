import requests

def get_course(id):
    """Returns info about a course from its id through JSON."""
    dept = ''.join([i for i in id if not i.isdigit()])  # strips digits from course name to get department  

    response = requests.get(f"https://api.umd.io/v1/courses?dept_id={dept}")

    for i in range(len(response.json())):
        if response.json()[i]['course_id'] == id:
            return response.json()[i]

def get_prof(name):
    """Gets info about a professor from their name."""
    response = requests.get(f"https://api.umd.io/v1/professors?name={name}")

    return response.json()

def get_course_profs(course, semester):
    """Returns list of professors who are teaching the specified course during the current semester.
    """
    professors = []

    response = requests.get(f"https://api.umd.io/v1/professors?course_id={course}")
    for professor in response.json():
        for i in range(len(professor['taught'])):
            if professor['taught'][i]['semester'] == semester and professor['taught'][i]['course_id'] == course:
                prof_name = professor['name']
                if not prof_name in professors: professors.append(prof_name)
    
    return professors

def get_section(section_id):
    """Returns info about a section from its ID"""
    response = requests.get(f"https://api.umd.io/v1/courses/sections/{section_id}")
    return response.json()
