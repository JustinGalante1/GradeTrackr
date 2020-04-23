import requests
import json
import re

def verify_course_and_get_avg(course_name):
    """
    Parse course name string and check with VAGrades API if there exists a course with that name. Return course average (rounded to 3 decimal places).

    courseName -- (str) Name of user entered course name. May contain spaces.

    returns the course average if it exists on VAGrades. Returns 0 otherwise.
    """
    # UVA Course Regex
    # uva_course_pattern = re.compile("^([A-Za-z]{2,4} *[0-9]{4})$")

    # If the course name matches UVA Course naming conventions
    course_name = course_name.strip()
    if re.match(r"^([A-Za-z]{2,4} *[0-9]{4})$", course_name):
        

        letters = course_name[:-4].strip().upper()
        numbers = course_name[-4:].strip()
        # Make a request to VAGrades API
        URL = "https://vagrades.com/api/uvaclass/"

        r = requests.get(url = "https://vagrades.com/api/uvaclass/" + letters + numbers)
        course_data = r.json()

        # If there exists a course with that name on VAGrades
        if course_data != {'sections': []}:
            return round(course_data['course']['avg'], 3)
    return 0





course_name = "CS3240"

print(verify_course_and_get_avg(course_name))

# r = requests.get(url = URL+course_name) 


# data = r.json()

# print(course_name, "average:",  round(data['course']['avg'], 3))

# # def getCourseInfo(course_name):
# #     """
# #     Take a course name and return information about it as a python dict
# #     """


# s = "CS   3240"

print("round(3.2324, 2):", round(3.2324, 2))

