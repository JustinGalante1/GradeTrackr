from django.db import models
from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.forms import ModelForm


class SingularGradeItem(models.Model):
    gradePercentage = models.DecimalField(max_digits=5, decimal_places=2)
    datetimeWhenInputted = models.DateTimeField(auto_now=False, auto_now_add=True)
    didGradeGoUp = models.BooleanField(null=True)  # true means it went up compared to last stored value

    def __str__(self):
        return str(self.gradePercentage)

    # whichStudentsSemesterGPAisThis = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="semGPA",
    #                                                    null=True)
    # whichStudentsCumulativeGPAisThis = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="cumGPA",
    #                                                      null=True),

    # whichGradeCategorysAvgGradeIsThis = models.ForeignKey(GradeCategory, on_delete=models.CASCADE,
    #                                                       related_name="gradeCategory", null=True)

    # student_It_Belongs_To = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="stud")


class Student(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    cumulativeCredits = models.DecimalField(max_digits=4, decimal_places=1, default=0)
    cumulativeGPA = models.ForeignKey(SingularGradeItem, on_delete=models.CASCADE, related_name="cumGPA", null=True)

    def __str__(self):
        return self.user.username


@receiver(post_save, sender=User)
def create_user_student(sender, instance, created, **kwargs):
    if created:
        Student.objects.create(user=instance)


class Course(models.Model):
    # isLookingForGroupForThisClass = models.BooleanField(default=False)
    Finished_Course = models.BooleanField(default=False)  # do we track this course or is this a legacy course?
    Verified_Class = models.BooleanField(default=False)  # is this an official Lou's List class we have found?
    Include_In_GPA = models.BooleanField(
        default=True)  # is this class used in GPA calculation or is it just a fork of a class someone uses purely for "what if" tracking purposes?

    Professor_Email = models.EmailField(null=True)  # if verified class, then we should be able to get this info
    Average_From_VAgrades = models.DecimalField(max_digits=6, decimal_places=2,
                                                null=True)  # if verified we should be able to scrape grade from VAgrades.com

    name = models.CharField(max_length=100)  # either searchable name from Lou's List or enter your own, <100 characters
    number_Of_Credits = models.DecimalField(max_digits=2,
                                            decimal_places=1)  # because now they have half credit courses or something?

    target_Grade = models.DecimalField(max_digits=5, decimal_places=2,
                                       null=True)  # for assholes who want a target grade of a 100.00%

    student_It_Belongs_To = models.ForeignKey(Student, on_delete=models.CASCADE, related_name="courses")
    avgGrade = models.ForeignKey(SingularGradeItem, on_delete=models.CASCADE, related_name="avgGrade", null=True)

    def __str__(self):
        return self.name


class GradeCategory(models.Model):
    name = models.CharField(max_length=100)
    weightage = models.DecimalField(max_digits=4,
                                    decimal_places=2)  # wont work for grade categories that are worth 100% of the class. Hopefully this is never an issue

    courseItBelongsTo = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="categories")
    avgCategoryGrade = models.ForeignKey(SingularGradeItem, on_delete=models.CASCADE, related_name="avgCategoryGrade", null=True)
    
    
    @property
    def assignments(self):
            return Assignment.objects.all().filter(gradeCategoryItBelongsTo = self)


    def __str__(self):
        return self.name 




class GradeCategoryForm(ModelForm):
    class Meta:
        model = GradeCategory
        fields = ['name', 'weightage', 'courseItBelongsTo']


class CourseForm(ModelForm):
    class Meta:
        model = Course
        fields = ['Finished_Course', 'Verified_Class', 'Include_In_GPA', 'Professor_Email',
                  'Average_From_VAgrades', 'name', 'number_Of_Credits', 'target_Grade', 'student_It_Belongs_To']



class Assignment(models.Model):  # abstract name, could be exam or quiz or anything that is worth something
    gradePercentage = models.DecimalField(max_digits=5, decimal_places=2, null=True)
    name = models.CharField(max_length=100)

    gradeCategoryItBelongsTo = models.ForeignKey(GradeCategory, on_delete=models.CASCADE, related_name="assignments")

    def __str__(self):
        return self.name