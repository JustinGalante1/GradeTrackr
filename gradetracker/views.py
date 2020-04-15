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


# in gradetracker directory
# Create your views here.

class TestView(TemplateView):
    template_name = 'gradetracker/test.html'


# Create and add a new course
def add(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            try:
                finishedCourse = request.POST.get('enrolled')
                if finishedCourse == "False":
                    finishedCourse = "True"
                else:
                    finishedCourse = "False"
                verifiedClass = request.POST.get('verified')
                includeInGPA = request.POST.get('included')
                professorEmail = request.POST.get('email')
                VAGradeAvg = request.POST.get('VAavg')
                courseTitle = request.POST.get('courseTitle')
                numCredits = request.POST.get('credits')
                targetGrade = request.POST.get('goal')
                current_student = request.user.student
                new_course = Course()
                new_course.Finished_Course = finishedCourse
                new_course.Verified_Class = verifiedClass
                new_course.Include_In_GPA = includeInGPA
                new_course.Professor_Email = professorEmail
                new_course.Average_From_VAgrades = VAGradeAvg
                new_course.name = courseTitle
                new_course.number_Of_Credits = numCredits
                new_course.target_Grade = targetGrade
                new_course.student_It_Belongs_To = current_student
                new_course.save()
            except Exception as e:
                return render(request, 'gradetracker/add.html', {'error_message': "HELLO " + str(e)})
            return HttpResponseRedirect(reverse('gradetracker:dashboard'))
        else:
            return render(request, 'gradetracker/add.html', )
    else:
        # if the user is not authenticated
        return redirect('gradetracker:index')


def gradecat(request, course_id=None):
    if request.user.is_authenticated:
        # If the course exists and belongs to the user
        if Course.objects.filter(id=course_id).exists() and Course.objects.get(id=course_id).student_It_Belongs_To.user==request.user:
            theCourse = Course.objects.get(id=course_id)
            if request.method == 'POST':
                # courseTitle = request.POST.get('courseTitle')
                gradeCategoryN = request.POST.get('name')
                weight = request.POST.get('weight')
                try:
                    new_gradecat = GradeCategory(name=gradeCategoryN, weightage=weight, courseItBelongsTo=theCourse)
                    new_gradecat.save()
                except Exception as e:
                    return render(request, 'gradetracker/gradecat.html', {'error_message': "HELLO " + str(e), 'course_id' : course_id})
                return CourseOverview(request, course_id)
            else:
                return render(request, 'gradetracker/gradecat.html', {'course' : theCourse})
        # If the user is authenticated but the course does not exist or belong to that user, render the dashboard
        else:
            return CourseDashboard(request)
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
                    name = request.POST.get('assignmentName')
                    percentage = request.POST.get('weight')
                    notification = request.POST.get('notify')
                    gradeCatID = request.POST.get('categoryChoice')
                    dueDate = request.POST.get('date')
                    new_assignment = Assignment()
                    new_assignment.name = name
                    new_assignment.gradePercentage = percentage
                    new_assignment.notifyStudentOrNot = notification
                    new_assignment.gradeCategoryItBelongsTo = GradeCategory.objects.get(id=gradeCatID)
                    new_assignment.dueDate = dueDate
                    new_assignment.save()
                    getAverage(course_id)
                except Exception as e:
                    return render(request, 'gradetracker/addAssignment.html', {'theCourse' : theCourse, 'grade_categories' : grade_categories, 'course_id' : course_id, 'error_message' : "BIG ERROR " + str(e)})
                return HttpResponseRedirect(reverse('gradetracker:dashboard'))
            else:
                return render(request, 'gradetracker/addAssignment.html', context)
        
        # If the user is authenticated but the course does not exist or belong to that user, render the dashboard
        else:
            return CourseDashboard(request)
    else:
        # if the user is not authenticated
        return redirect('gradetracker:index')



def CourseDashboard(request):
    # Render the course dashboard of the authenticated user
    if request.user.is_authenticated:
    #    Get all the courses associated with that user (as a student)
        context = {
            'username': request.user,
            'courses_list': Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user))
        }
        return render(request, "gradetracker/dashboard.html", context)
    else:
        return HttpResponseRedirect(reverse("google_login"))


def SignIn(request):
    # Render the course dashboard of the authenticated user
    if request.user.is_authenticated:
    #   Get all the courses associated with that user (as a student)
        context = {
            'username': request.user,
            'courses_list': Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user))
        }
        return render(request, "gradetracker/dashboard.html", context)
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
            if course_to_delete.student_It_Belongs_To.user==request.user:
                course_to_delete.delete()

        return CourseDashboard(request)
    
    # otherwise, prompt the user to login
    else:
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
                newCourse = Course(Finished_Course=courseToDuplicate.Finished_Course,
                                Verified_Class=courseToDuplicate.Verified_Class, Include_In_GPA=False,
                                Professor_Email=courseToDuplicate.Professor_Email,
                                Average_From_VAgrades=courseToDuplicate.Average_From_VAgrades, name=courseToDuplicate.name,
                                number_Of_Credits=courseToDuplicate.number_Of_Credits,
                                target_Grade=courseToDuplicate.target_Grade,
                                student_It_Belongs_To=courseToDuplicate.student_It_Belongs_To)
                newCourse.save()
                #trying to duplicate grade categories and assignments
                for category in gradeCategoriesToDuplicate:
                    newGradecat = GradeCategory(name=category.name, weightage=category.weightage, courseItBelongsTo=newCourse)
                    newGradecat.save()
                    assingmentsToDuplicate = category.assignments.all()
                    for assignment in assingmentsToDuplicate:
                        new_assignment = Assignment(gradePercentage=assignment.gradePercentage, notifyStudentOrNot=assignment.notifyStudentOrNot, name=assignment.name, dueDate=assignment.dueDate, gradeCategoryItBelongsTo=newGradecat)
                        new_assignment.save()
                            #getAverage(course_id)

        return CourseDashboard(request)
    
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
        average_grade /= len(list_of_assignments_in_categories)
        grades_and_their_weights.append((float(category.weightage), float(average_grade)))

    average_class_grade = 0
    for item in grades_and_their_weights:
        average_class_grade += item[0]*item[1]/100

    if (theCourse.avgGrade == None):
        avgGrade = SingularGradeItem.objects.create(gradePercentage=average_class_grade, didGradeGoUp=True)
        theCourse.avgGrade = avgGrade
    else:
        theCourse.avgGrade.didGradeGoUp = (theCourse.avgGrade.gradePercentage < average_class_grade)
        print(theCourse.avgGrade.didGradeGoUp, file=sys.stderr)
        print(average_class_grade, file=sys.stderr)
        theCourse.avgGrade.gradePercentage = average_class_grade
        print(theCourse.avgGrade.gradePercentage, file=sys.stderr)
    
    theCourse.avgGrade.save()
    theCourse.save()


def CourseOverview(request, course_id=None):
    # Render the details of the course that the authenticated user clicks
    if request.user.is_authenticated:
        # if the course exists and belongs to the user 
        if Course.objects.filter(id=course_id).exists() and Course.objects.get(id=course_id).student_It_Belongs_To.user==request.user:

            # Get the course that the user wants to expand
            course_to_display = Course.objects.get(id=course_id)

            # Get all the grade categories associated with that course
            grade_categories = GradeCategory.objects.all().filter(courseItBelongsTo=course_to_display).values()

            # Get all the assignments associated with that grade category

            # dict that will contain all the assignments indexed by the grade category they belong to
            category_assignments = {}


            for category in grade_categories:
                # Add all the assignments belonging to a category to the dictionary at that category's key
                category_assignments[category.get('name')] = Assignment.objects.all().filter(gradeCategoryItBelongsTo=category.get('id'))

            # Get all the courses associated with that user (as a student)
            context = {
                'course': course_to_display,
                'grade_categories': grade_categories,
                'category_assignments': category_assignments
            }
            return render(request, "gradetracker/course.html", context)

        # If the course does not exist or does not belong to the user, render the user's dashboard
        else:
            return CourseDashboard(request)
    
    # If the user is not authenticated
    return redirect('gradetracker:index')


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
                # delete the category and display the course overview page
                return CourseOverview(request, course.id)

        return CourseDashboard(request)
    
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
                # delete the category and display the course overview page
                return CourseOverview(request, course.id)

        return CourseDashboard(request)
    
    # otherwise, prompt the user to login
    else:
        return redirect('gradetracker:index')
