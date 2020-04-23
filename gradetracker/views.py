from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
# new stuff
from .models import Course, CourseForm, Student, GradeCategory, Assignment, SingularGradeItem
from django.contrib.auth.models import User
from django.core.exceptions import ObjectDoesNotExist
import sys
from decimal import Decimal
import re
import requests
import json


# in gradetracker directory
# Create your views here.

class TestView(TemplateView):
    template_name = 'gradetracker/test.html'


# Create and add a new course
def add(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
            # finishedCourse = request.POST.get('enrolled')
            # if finishedCourse == "False":
            #     finishedCourse = "True"
            # else:
            #     finishedCourse = "False"
            # verifiedClass = request.POST.get('verified')
                if (request.POST.get('submitOrCancel')=="0"):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                includeInGPA = request.POST.get('included')
                professorEmail = request.POST.get('email')
                Average_From_VAgrades = request.POST.get('VAavg')
                courseTitle = request.POST.get('courseTitle')
                # Call the helper function to check VAGrades for course verification
                course_verification_obj = verify_course_and_get_avg(courseTitle)
                numCredits = request.POST.get('credits')
                targetGrade = request.POST.get('goal')
                current_student = request.user.student
                new_course = Course()
                # new_course.Finished_Course = finishedCourse
                # Add the course VAGrades verification
                new_course.Verified_Class = bool(course_verification_obj["avg"])
                new_course.Average_From_VAgrades = Decimal(course_verification_obj["avg"]) if new_course.Verified_Class else None

                new_course.Include_In_GPA = includeInGPA
                new_course.Professor_Email = professorEmail
                new_course.name = course_verification_obj["course_name"]
                new_course.number_Of_Credits = numCredits
                new_course.target_Grade = targetGrade
                new_course.student_It_Belongs_To = current_student
            

                request.user.student.save()
                new_course.save()

                # Update student's cumulative credits
                update_student_numCredits(request.user.id)
            except Exception as e:
                return render(request, 'gradetracker/add.html', {'error_message': "PEANUT " + str(e)})
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
        else:
            return render(request, 'gradetracker/add.html', )
    else:
        # if the user is not authenticated
        return redirect('gradetracker:index')

def verify_course_and_get_avg(course_name):
    """
    Parse course name string and check with VAGrades API if there exists a course with that name. Return course average (rounded to 3 decimal places).

    courseName -- (str) Name of user entered course name. May contain spaces.

    returns a dictionary {"avg": avg_grade, "course_name": adjusted_name} if it exists on VAGrades. Returns {"avg": 0, "course_name": same_name} otherwise.
    Where adjusted_name is the name of the course after removing spaces and converting to upper case if necessary (e.g, "cs 3240 " --> "CS3240").
    This is for VAGrades API naming conventions.
    """
    # UVA Course Regex
    # uva_course_pattern = re.compile("^([A-Za-z]{2,4} *[0-9]{4})$")

    # If the course name matches UVA Course naming conventions
    course_name = course_name.strip()
    if re.match(r"^([A-Za-z]{2,4} *[0-9]{4})$", course_name):

        letters = course_name[:-4].strip().upper()
        numbers = course_name[-4:].strip()
        # Make a request to VAGrades API
        r = requests.get(url = "https://vagrades.com/api/uvaclass/" + letters + numbers)
        course_data = r.json()

        # If there exists a course with that name on VAGrades
        if course_data != {'sections': []}:
            return {"course_name": letters+numbers, "avg": round(float(course_data['course']['avg']*100/4), 2)}

    else:
        return {"course_name": course_name, "avg": 0}


def gradecat(request, course_id=None):
    if request.user.is_authenticated:
        # If the course exists and belongs to the user
        if Course.objects.filter(id=course_id).exists() and Course.objects.get(id=course_id).student_It_Belongs_To.user==request.user:
            theCourse = Course.objects.get(id=course_id)
            if request.method == 'POST':
                if (request.POST.get('submitOrCancel')=="0"):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                # courseTitle = request.POST.get('courseTitle')
                gradeCategoryN = request.POST.get('name')
                weight = request.POST.get('weight')
                try:
                    new_gradecat = GradeCategory(name=gradeCategoryN, weightage=weight, courseItBelongsTo=theCourse)
                    new_gradecat.save()
                except Exception as e:
                    return render(request, 'gradetracker/gradecat.html', {'error_message': "HELLO " + str(e), 'course_id' : course_id})
                getAverage(course_id)
                return CourseOverview(request, course_id)
            else:
                return render(request, 'gradetracker/gradecat.html', {'course' : theCourse})
        # If the user is authenticated but the course does not exist or belong to that user, render the dashboard
        else:
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    else:
        # if the user is not authenticated
        return redirect('gradetracker:index')

class IndexView(TemplateView):
    template_name = 'gradetracker/index.html'


def addAssignment(request, course_id=None):
    if request.user.is_authenticated:
        # If the course exists and belongs to the user
        if Course.objects.filter(id=course_id).exists() and Course.objects.get(id=course_id).student_It_Belongs_To.user==request.user:
            theCourse = Course.objects.get(pk=course_id)
            grade_categories = GradeCategory.objects.all().filter(courseItBelongsTo=theCourse)
            context = {'theCourse' : theCourse,
                    'grade_categories' : grade_categories,
                    'course' : theCourse}
            if request.method == 'POST':
                try:
                    if (request.POST.get('submitOrCancel')=="0"):
                        return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                    name = request.POST.get('assignmentName')
                    percentage = request.POST.get('weight')
                    notification = request.POST.get('notify')
                    gradeCatID = request.POST.get('categoryChoice')
                    new_assignment = Assignment()
                    new_assignment.name = name
                    new_assignment.gradePercentage = percentage
                    new_assignment.notifyStudentOrNot = notification
                    new_assignment.gradeCategoryItBelongsTo = GradeCategory.objects.get(id=gradeCatID)
                    new_assignment.save()
                    getAverage(course_id)
                    
                    # update student's GPA
                    update_student_GPA(request.user.id)
                except Exception as e:
                    return render(request, 'gradetracker/addAssignment.html', {'theCourse' : theCourse, 'grade_categories' : grade_categories, 'course_id' : course_id, 'error_message' : "BIG ERROR " + str(e)})
                return CourseOverview(request, course_id)
            else:
                return render(request, 'gradetracker/addAssignment.html', context)
        
        # If the user is authenticated but the course does not exist or belong to that user, render the dashboard
        else:
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    else:
        # if the user is not authenticated
        return redirect('gradetracker:index')



def CourseDashboard(request):
    # Render the course dashboard of the authenticated user
    if request.user.is_authenticated:
        coursesAndTheirCategories={}
        showReportCardOrNot = False
        for course in Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user)):
            cats = GradeCategory.objects.all().filter(courseItBelongsTo=course)
            if (course.avgGrade != None and course.Include_In_GPA):
                showReportCardOrNot = True
            if (len(cats)>=1):
                coursesAndTheirCategories[course]=[]   
            for cat in cats:
                coursesAndTheirCategories[course].append(cat)
        

        context = {
            'username': request.user,
            'student': Student.objects.get(user_id=request.user.id),
            'courses_list': Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user)),
            'cum': Student.objects.all().get(user=request.user).cumulativeCredits,
            'coursesAndTheirCategories': coursesAndTheirCategories,
            'showReportCardOrNot': showReportCardOrNot
        }
        return render(request, "gradetracker/dashboard.html", context)
    else:
        return HttpResponseRedirect(reverse("google_login"))


def SignIn(request):
    # Render the course dashboard of the authenticated user
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    else:
        return redirect('gradetracker:index')  # HttpResponseRedirect(reverse("google_login"))


def delete_course(request, course_id=None):
    """
    delete the requested course. Only if the user is authenticated.
    """
    
    if request.user.is_authenticated:
        
        # if the course exists
        if Course.objects.filter(id=course_id).exists():
            course_to_delete = Course.objects.get(id=course_id)
            # If the course belongs to the user who is trying to delete the course.
            current_student = request.user.student
            if course_to_delete.student_It_Belongs_To==current_student:
                # delete the course
                current_student.save()
                course_to_delete.delete()

                # Update student's cumulative credits
                update_student_numCredits(request.user.id)

                # update student's GPA
                update_student_GPA(request.user.id)

        return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    
    # otherwise, prompt the user to login
    else:
        return redirect('gradetracker:index')

def gpaInclude(request):
    
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                course = Course.objects.get(id=request.POST.get('courseToAffect'))
                print(course.Include_In_GPA, file=sys.stderr)
                course.Include_In_GPA= not (course.Include_In_GPA)

                request.user.student.save()
                course.save()


                # Update student's cumulative credits
                update_student_numCredits(request.user.id)

                # update student's GPA
                update_student_GPA(request.user.id)
                print(course.Include_In_GPA, file=sys.stderr)

                return CourseDashboard(request)
            except Exception as e:
                return render(request, 'gradetracker/dashboard.html', {'error_message': "PEANUT " + str(e)})
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
        else:
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    else:
        # if the user is not authenticated
        return redirect('gradetracker:index')

def duplicate_course(request, course_id=None):

    # if the user is authenticated
    if request.user.is_authenticated:

        # if the course exists
        if Course.objects.filter(id=course_id).exists():
            courseToDuplicate = Course.objects.get(id=course_id)
            gradeCategoriesToDuplicate = courseToDuplicate.categories.all()
            # If the course belongs to the user who is trying to duplicate the course.
            if courseToDuplicate.student_It_Belongs_To.user==request.user:
                newCourse = Course(
                                Verified_Class=courseToDuplicate.Verified_Class, Include_In_GPA=False,
                                Professor_Email=courseToDuplicate.Professor_Email,
                                Average_From_VAgrades=courseToDuplicate.Average_From_VAgrades, name=courseToDuplicate.name,
                                number_Of_Credits=courseToDuplicate.number_Of_Credits,
                                target_Grade=courseToDuplicate.target_Grade,
                                student_It_Belongs_To=courseToDuplicate.student_It_Belongs_To,avgGrade=courseToDuplicate.avgGrade)
                newCourse.save()
                #trying to duplicate grade categories and assignments
                for category in gradeCategoriesToDuplicate:
                    newGradecat = GradeCategory(name=category.name, weightage=category.weightage, courseItBelongsTo=newCourse, avgCategoryGrade=category.avgCategoryGrade)
                    newGradecat.save()
                    assingmentsToDuplicate = category.assignments.all()
                    for assignment in assingmentsToDuplicate:
                        new_assignment = Assignment(gradePercentage=assignment.gradePercentage, name=assignment.name, gradeCategoryItBelongsTo=newGradecat)
                        new_assignment.save()
                    #getAverage(course_id)
                
        return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    
    # otherwise, prompt the user to login.
    else:
        return redirect('gradetracker:index')


def getAverage(course_id=None):
    
    theCourse = Course.objects.get(pk=course_id)
    grade_categories = theCourse.categories.all()
    grades_and_their_weights = []
    
    for category in grade_categories:
        
        list_of_assignments_in_categories = category.assignments.all()
        average_grade = 0
        
        for assignment in list_of_assignments_in_categories:
            average_grade += assignment.gradePercentage
        if (len(list_of_assignments_in_categories)!=0):
            average_grade /= len(list_of_assignments_in_categories)
            grades_and_their_weights.append((float(category.weightage), float(average_grade)))
        else:
            average_grade = 0


        
        if (category.avgCategoryGrade == None):
            avgCategoryGrade = SingularGradeItem.objects.create(gradePercentage=average_grade, didGradeGoUp=None)
            category.avgCategoryGrade = avgCategoryGrade
        else:
            if (category.avgCategoryGrade.gradePercentage < average_grade):
                category.avgCategoryGrade.didGradeGoUp = True
            elif (category.avgCategoryGrade.gradePercentage == average_grade):
                print("bruh",file=sys.stderr)
                category.avgCategoryGrade.didGradeGoUp = True
            else:
                category.avgCategoryGrade.didGradeGoUp = False
            category.avgCategoryGrade.gradePercentage = average_grade

        print("(INSIDE getAverage)", "Did the grade go up?", category.avgCategoryGrade.didGradeGoUp, file=sys.stderr)
        print("(INSIDE getAverage)", "Category name:", category, file=sys.stderr)

        category.avgCategoryGrade.save()
        category.save()

        


    average_class_grade = 0
    for item in grades_and_their_weights:
        average_class_grade += item[0]*item[1]/100

    if (theCourse.avgGrade == None):
        avgGrade = SingularGradeItem.objects.create(gradePercentage=average_class_grade, didGradeGoUp=True)
        theCourse.avgGrade = avgGrade
    else:
        print("(INSIDE getAverage)", "GradePercentage of the course:", theCourse.avgGrade.gradePercentage, file=sys.stderr)
        if (theCourse.avgGrade.gradePercentage < average_class_grade):
            theCourse.avgGrade.didGradeGoUp = True
        elif (theCourse.avgGrade.gradePercentage == average_class_grade):
            theCourse.avgGrade.didGradeGoUp = True
        else:
            theCourse.avgGrade.didGradeGoUp = False
    
    theCourse.avgGrade.gradePercentage = average_class_grade
        #print(theCourse.avgGrade.gradePercentage, file=sys.stderr)
    
    theCourse.avgGrade.save()
    theCourse.save()


def CourseOverview(request, course_id=None):
    # Render the details of the course that the authenticated user clicks
    if request.user.is_authenticated:
        # if the course exists and belongs to the user 
        if Course.objects.filter(id=course_id).exists() and Course.objects.get(id=course_id).student_It_Belongs_To.user==request.user:


            context = {
                'course': categoryHelperFunction(course_id)[2],
                'grade_categories': categoryHelperFunction(course_id)[0],
                'category_assignments': categoryHelperFunction(course_id)[1],
                'va_grades_link' : "https://vagrades.com/uva/" + categoryHelperFunction(course_id)[2].name            
            }
            return render(request, "gradetracker/course.html", context)

        # If the course does not exist or does not belong to the user, render the user's dashboard
        else:
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    
    # If the user is not authenticated
    return redirect('gradetracker:index')

def categoryHelperFunction(course_id):
    # Get the course that the user wants to expand
    course_to_display = Course.objects.get(id=course_id)

    # Get all the grade categories associated with that course
    grade_categories = GradeCategory.objects.all().filter(courseItBelongsTo=course_to_display)

    # Get all the assignments associated with that grade category

    # dict that will contain all the assignments indexed by the grade category they belong to
    category_assignments = {}


    for category in grade_categories.values():
    # Add all the assignments belonging to a category to the dictionary at that category's key
        category_assignments[category.get('name')] = Assignment.objects.all().filter(gradeCategoryItBelongsTo=category.get('id'))
    
    return (grade_categories,category_assignments,course_to_display)

def delete_category(request, category_id=None):
    """
    delete the requested grade category. Only if the user is authenticated.
    TODO we probably want to delete all assignments associated with a category when we delete the category
    """
    
    if request.user.is_authenticated:
        
        # if the category exists
        if GradeCategory.objects.filter(id=category_id).exists():
            category_to_delete = GradeCategory.objects.get(id=category_id)
            # Get the course it belongs to
            course = category_to_delete.courseItBelongsTo 

            # If the course belongs to the user who is trying to delete the category.
            if course.student_It_Belongs_To.user==request.user:
                category_to_delete.delete()
                getAverage(course.id)
                # delete the category and display the course overview page
                getAverage(course.id)
                update_student_GPA(request.user)
                return CourseOverview(request, course.id)

        return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    
    # otherwise, prompt the user to login
    else:
        return redirect('gradetracker:index')


def delete_assignment(request, assignment_id=None):
    """
    delete the requested assignment. Only if the user is authenticated.
    """
    
    if request.user.is_authenticated:
        
        # if the category exists
        if Assignment.objects.filter(id=assignment_id).exists():
            # Get the assignment that we want to delete
            assignment_to_delete = Assignment.objects.get(id=assignment_id)
            # Get the course it belongs to
            course = assignment_to_delete.gradeCategoryItBelongsTo.courseItBelongsTo 

            # If the course belongs to the user who is trying to delete the category.
            if course.student_It_Belongs_To.user==request.user:
                assignment_to_delete.delete()
                getAverage(course.id)

                update_student_GPA(request.user)
                # delete the category and display the course overview page
                return CourseOverview(request, course.id)

        return HttpResponseRedirect(reverse('gradetracker:dashboard'))
    
    # otherwise, prompt the user to login
    else:
        return redirect('gradetracker:index')

def edit_assignment(request, assignment_id=None):
    if request.user.is_authenticated:

        if request.method == 'POST':
            try:
                course_id = request.POST.get('courseID')
                if (request.POST.get('submitOrCancel')=="0"):
                    return HttpResponseRedirect(request.META.get('HTTP_REFERER'))
                print(request.POST.get('submitOrCancel'), file=sys.stderr)
                name = request.POST.get('assignmentName')
                percentage = request.POST.get('weight')
                

                assignmentToModify = Assignment.objects.get(id=assignment_id)
                    
                assignmentToModify.name = name
                assignmentToModify.gradePercentage = percentage
                assignmentToModify.save()
                getAverage(course_id)
                # Update the student's GPA
                update_student_GPA(request.user)

            except Exception as e:
                return render(request, 'gradetracker/addAssignment.html', {'error_message' : "BIG ERROR " +str(e)})
            return CourseOverview(request, course_id)
        else:
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
        
    else:
        # if the user is not authenticated
        return redirect('gradetracker:index')



def update_student_GPA(student_user_id):
    """
    Update a student's cumulative GPA. This is to be called whenever an assignment is added/edited/deleted. 
    Or to be called whenever a Student changes what course to include in GPA.

    """
    student_to_update = Student.objects.get(user_id=student_user_id)

    # Get all courses associated with that student where the course is to be included in the GPA
    student_courses_gpa = Course.objects.filter(student_It_Belongs_To=student_to_update).filter(Include_In_GPA = True)

    
    if student_to_update.cumulativeCredits != 0:

        # print("Student has some creds...")
        grade_points = 0
        active_creds = 0
        for course in student_courses_gpa:
            # Check if the course has any grade associated with it.
            four_scale = 0
            if course.avgGrade is None:
                four_scale = 0
            elif 60 <= course.avgGrade.gradePercentage < 63:
                four_scale = 0.7
            elif 63 <= course.avgGrade.gradePercentage < 67:
                four_scale = 1.0
            elif 67 <= course.avgGrade.gradePercentage < 70:
                four_scale = 1.3
            elif 70 <= course.avgGrade.gradePercentage < 73:
                four_scale = 1.7
            elif 73 <= course.avgGrade.gradePercentage < 77:
                four_scale = 2.0
            elif 77 <= course.avgGrade.gradePercentage < 80:
                four_scale = 2.3
            elif 80 <= course.avgGrade.gradePercentage < 83:
                four_scale = 2.7
            elif 83 <= course.avgGrade.gradePercentage < 87:
                four_scale = 3.0
            elif 87 <= course.avgGrade.gradePercentage < 90:
                four_scale = 3.3
            elif 90 <= course.avgGrade.gradePercentage < 93:
                four_scale = 3.7
            elif 93 <= course.avgGrade.gradePercentage:
                four_scale = 4.0

            print("(INSIDE update_student_GPA)", "Got a", four_scale, "in this class:", course.name)
            grade_points += int(course.number_Of_Credits) * four_scale
            active_creds += course.number_Of_Credits
        
        new_gpa = round(grade_points/int(active_creds), 2)

        if (student_to_update.cumulativeGPA == None):
            print("(INSIDE update_student_GPA)", "Student:", student_to_update, "; Cumulative GPA is None?", student_to_update.cumulativeGPA == None)
            cumulativeGPA = SingularGradeItem.objects.create(gradePercentage=new_gpa, didGradeGoUp=None)
            student_to_update.cumulativeGPA = cumulativeGPA
        else:
            if (student_to_update.cumulativeGPA.gradePercentage < new_gpa):
                student_to_update.cumulativeGPA.didGradeGoUp = True
            elif (student_to_update.cumulativeGPA.gradePercentage == new_gpa):
                student_to_update.cumulativeGPA.didGradeGoUp = True
            else:
                student_to_update.cumulativeGPA.didGradeGoUp = False
            student_to_update.cumulativeGPA.gradePercentage = new_gpa


        student_to_update.cumulativeGPA.save()
        student_to_update.save()

        print("(INSIDE update_student_GPA)", "Student:", student_to_update, "; Cumulative GPA is None?", student_to_update.cumulativeGPA == None)




def update_student_numCredits(student_user_id):
    """
    Update a student's cumulative credits. This will count the credits of the courses the student wants to track and update the
    Student's cumulative credits field.

    """

    student_to_update = Student.objects.get(user_id=student_user_id)

    # Get all courses associated with that student where the course is to be included in the GPA
    student_courses_gpa = Course.objects.filter(student_It_Belongs_To=student_to_update).filter(Include_In_GPA = True)

    active_creds = 0
    for course in student_courses_gpa:
        active_creds += course.number_Of_Credits

    print("(INSIDE update_student_numCredits)", "Student:", student_to_update, "; Credits:", active_creds)
    student_to_update.cumulativeCredits = Decimal(active_creds)
    student_to_update.save()