from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.views import generic
from django.shortcuts import render
from django.views.generic import TemplateView
# new stuff
from .models import Course, CourseForm, Student
from django.contrib.auth.models import User


# new stuff

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
            return render(request, 'gradetracker/addCourse.html', {'error_message': "HELLO " + str(e)})
        return HttpResponseRedirect(reverse('gradetracker:index'))
    else:
        return render(request, 'gradetracker/addCourse.html', )


def addAssignment(request):
    return render(request, 'gradetracker/addAssignment.html', )


class IndexView(TemplateView):
    template_name = 'gradetracker/index.html'
