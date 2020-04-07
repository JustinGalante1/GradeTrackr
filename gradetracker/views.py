from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render, redirect
from django.views.generic import TemplateView
# new stuff
from .models import Course, CourseForm, Student, GradeCategory
from django.contrib.auth.models import User


# in gradetracker directory
# Create your views here.

class TestView(TemplateView):
    template_name = 'gradetracker/test.html'


def addCourse(request):
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
<<<<<<< HEAD
            return render(request, 'gradetracker/addCourse.html', {'error_message': "HELLO " + str(e)})
        return HttpResponseRedirect(reverse('gradetracker:index'))
=======
            return render(request, 'gradetracker/add.html', {'error_message': "HELLO " + str(e)})
        return HttpResponseRedirect(reverse('gradetracker:dashboard'))
>>>>>>> master
    else:
        return render(request, 'gradetracker/addCourse.html', )


def addAssignment(request):
    return render(request, 'gradetracker/addAssignment.html', )

def gradecat(request):
    if request.method == 'POST':
        courseTitle = request.POST.get('courseTitle')
        gradeCategoryN = request.POST.get('name')
        weight = request.POST.get('weight')
        try:
            current_course = Course.objects.get(name = courseTitle)
            new_gradecat = GradeCategory(name = gradeCategoryN, weightage = weight, courseItBelongsTo = current_course)
            new_gradecat.save()
        except Exception as e:
            return render(request, 'gradetracker/gradecat.html', {'error_message': "HELLO " + str(e)})
        return redirect('gradetracker:index')
    else:
        return render(request, 'gradetracker/gradecat.html',)

class IndexView(TemplateView):
    template_name = 'gradetracker/index.html'

    
def CourseDashboard(request):
    # Render the course dashboard of the authenticated user
    if request.user.is_authenticated:
        print(request.user)
        # TODO Get all the courses associated with that user (as a student)
        context = {
        'username' : request.user,
        'courses_list' : Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user))
    }
        return render(request, "gradetracker/dashboard.html", context)
    else:
        return HttpResponseRedirect(reverse("google_login"))

def SignIn(request):
    # Render the course dashboard of the authenticated user
    if request.user.is_authenticated:
        print(request.user)
        # TODO Get all the courses associated with that user (as a student)
        context = {
        'username' : request.user,
        'courses_list' : Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user))
    }
        return render(request, "gradetracker/dashboard.html", context)
    else:
        return redirect('gradetracker:index')#HttpResponseRedirect(reverse("google_login"))

def delete_course(request, course_id=None):
    course_to_delete = Course.objects.get(id=course_id)
    course_to_delete.delete()

    context = {
        'username' : request.user,
        'courses_list' : Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user))
    }

    return render(request, "gradetracker/dashboard.html", context)

def duplicate_course(request, course_id=None):
    courseToDuplicate = Course.objects.get(id=course_id)
    newCourse = Course(Finished_Course=courseToDuplicate.Finished_Course,Verified_Class=courseToDuplicate.Verified_Class, Include_In_GPA=False, Professor_Email=courseToDuplicate.Professor_Email, Average_From_VAgrades=courseToDuplicate.Average_From_VAgrades, name = courseToDuplicate.name, number_Of_Credits=courseToDuplicate.number_Of_Credits, target_Grade=courseToDuplicate.target_Grade, student_It_Belongs_To=courseToDuplicate.student_It_Belongs_To)
    newCourse.save()

    context = {
        'username' : request.user,
        'courses_list' : Course.objects.all().filter(student_It_Belongs_To=Student.objects.get(user=request.user))
    }

    return render(request, "gradetracker/dashboard.html", context)