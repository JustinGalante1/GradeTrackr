from django.test import TestCase, Client
from gradetracker.models import Student, Course, GradeCategory, Assignment, SingularGradeItem, User
import gradetracker.views 

class GradeTrackerTestCase(TestCase):
    def setUp(self):
        #need to settle some primary keys/identifiers before using this, must figure out user/student authentication model first

        # Keep a list of users existing in the database before the tests
        self.users_before = list(User.objects.values_list('id', flat=True).order_by('id'))
        print ("users before tests:", self.users_before)

    def tearDown(self):
        # Get the list of all users after the tests.
        users_after = list(User.objects.values_list('id', flat=True).order_by('id'))
        print ("users after tests:", users_after)
 
        # Calculate the set difference.
        users_to_remove = sorted(list(set(users_after) - set(self.users_before)))
        print ("users to remove after tests:", users_to_remove)
 
        # Delete that difference from the database.
        User.objects.filter(id__in=users_to_remove).delete()

    
    def test_set_some_default_grade_averages_to_a_course(self):
        # Create a user (and thus a student)
        test_user = User.objects.create_user(username='testuser', password='12345')
        student1 = Student.objects.all().filter(user=Student.objects.get(user=test_user))[0]

        class1 = Course.objects.create(name="APMA 3100: Probability", number_Of_Credits=3, student_It_Belongs_To=student1)
        category1 = GradeCategory.objects.create(name="Exams",weightage=45, courseItBelongsTo=class1)

        gradesSoFar = [87,90,86,96]
        gradesThatShouldveBeenAdded = []
        for grade in gradesSoFar:
            Assignment.objects.create(name="Exam "+str(gradesSoFar.index(grade)+1), gradePercentage=grade, gradeCategoryItBelongsTo=category1)

        for item in (category1.assignments.all()):
            gradesThatShouldveBeenAdded.append(item.gradePercentage)
        

        self.assertEqual(gradesThatShouldveBeenAdded, gradesSoFar)


    # def test_update_semester_GPA(self):
    #     # Create a user (and thus a student)
    #     test_user = User.objects.create_user(username='testuser', password='12345')
    #     student1 = Student.objects.all().filter(user=Student.objects.get(user=test_user))[0]

    #     SingularGradeItem.objects.create(gradePercentage=3.5, whichStudentsSemesterGPAisThis=student1)
    #     SingularGradeItem.objects.create(gradePercentage=3.7, whichStudentsSemesterGPAisThis=student1)
    #     #TODO write helper function to get latest GPA before setting, and set the boolean of current grade to be up or down

    #     self.assertEqual (float(student1.semGPA.latest('datetimeWhenInputted').gradePercentage),3.7)


    def test_this_course_belongs_to_this_student(self):
        # Create a user (and thus a student)
        test_user = User.objects.create_user(username='testuser', password='12345')
        student1 = Student.objects.all().filter(user=Student.objects.get(user=test_user))[0]

        class1 = Course.objects.create(name="APMA 3100: Probability", number_Of_Credits=3, student_It_Belongs_To=student1)

        self.assertEqual(class1.student_It_Belongs_To,student1)

    def test_this_GradeCategory_belongs_to_this_class(self):
        semesterGPA = SingularGradeItem.objects.create(gradePercentage=3.5)
        cumulativeGPA = SingularGradeItem.objects.create(gradePercentage=3.5)
        # Create a user (and thus a student)
        test_user = User.objects.create_user(username='testuser', password='12345')
        student1 = Student.objects.all().filter(user=Student.objects.get(user=test_user))[0]

        class1 = Course.objects.create(name="APMA 3100: Probability", number_Of_Credits=3, student_It_Belongs_To=student1)
        category1 = GradeCategory.objects.create(name="Exams",weightage=45, courseItBelongsTo=class1)

        self.assertEqual(category1.courseItBelongsTo,class1)

    # def test_this_student_averageGPA_when_assignments_added(self):

    #     test_user = User.objects.create_user(username='testuser', password='12345')
    #     student1 = Student.objects.all().filter(user=Student.objects.get(user=test_user))[0]

    #     class1 = Course.objects.create(name="ECON3020", number_Of_Credits=3, student_It_Belongs_To=student1)
    #     category1 = GradeCategory.objects.create(name="Exams",weightage=50, courseItBelongsTo=class1)
    #     category2 = GradeCategory.objects.create(name="Homework",weightage=50, courseItBelongsTo=class1)
    #     assignment1 = Assignment.objects.create(name="Exam 1", gradePercentage=80,gradeCategoryItBelongsTo=category1)
    #     assignment2 = Assignment.objects.create(name="Exam 2", gradePercentage=90,gradeCategoryItBelongsTo=category1)
    #     assignment3 = Assignment.objects.create(name="HW 1", gradePercentage=100,gradeCategoryItBelongsTo=category2)

    #     # Update GPA
    #     # student1.cumulativeCredits += 3
    #     gradetracker.views.getAverage(class1.id)
    #     gradetracker.views.update_student_numCredits(student1.user.id)

    #     gradetracker.views.update_student_GPA(student1.user.id)

    #     expected_cumulativeGPA1 = SingularGradeItem.objects.create(gradePercentage=3.7, didGradeGoUp = True)
        
    #     print("student1:", student1)
    #     print("student1.cumulativeCredits :", student1.cumulativeCredits)
    #     print("student1.cumulativeGPA :", student1.cumulativeGPA)
    #     print("student1.cumulativeGPA.gradePercentage :", student1.cumulativeGPA.gradePercentage)
    #     self.assertEqual(student1.cumulativeGPA.gradePercentage, expected_cumulativeGPA1.gradePercentage)
    #     self.assertEqual(student1.cumulativeGPA.didGradeGoUp, expected_cumulativeGPA1.didGradeGoUp)


    #     class2 = Course.objects.create(name="ECON3720", number_Of_Credits=4, student_It_Belongs_To=student1)
    #     category3 = GradeCategory.objects.create(name="Quizzes",weightage=60, courseItBelongsTo=class2)
    #     category4 = GradeCategory.objects.create(name="Problem Sets",weightage=40, courseItBelongsTo=class2)
    #     assignment4 = Assignment.objects.create(name="Quiz 1", gradePercentage=80,gradeCategoryItBelongsTo=category3)
    #     assignment5 = Assignment.objects.create(name="Quiz 2", gradePercentage=90,gradeCategoryItBelongsTo=category3)
    #     assignment6 = Assignment.objects.create(name="Problem Set 1", gradePercentage=70,gradeCategoryItBelongsTo=category4)
    #     assignment6 = Assignment.objects.create(name="Problem Set 2", gradePercentage=90,gradeCategoryItBelongsTo=category4)


    #     # Add some classes and update GPA again
    #     # student1.cumulativeCredits += 4
    #     gradetracker.views.getAverage(class2.id)
    #     gradetracker.views.update_student_numCredits(student1.user.id)

    #     gradetracker.views.update_student_GPA(student1.user.id)
    #     expected_cumulativeGPA2 = SingularGradeItem.objects.create(gradePercentage=3.7, didGradeGoUp = False)

    #     self.assertEqual(student1.cumulativeGPA.gradePercentage, expected_cumulativeGPA2.gradePercentage)
    #     self.assertEqual(student1.cumulativeGPA.didGradeGoUp, expected_cumulativeGPA2.didGradeGoUp)


    #     self.assertEqual(category1.courseItBelongsTo,class1)

## Use SingularGradeItem.objects.create(gradePercentage=x) to set:
# a student's semester GPA = SingularGradeItem.objects.create(gradePercentage=3.5, whichStudentsSemesterGPAisThis=student1)
# a student's cumulative GPA = SingularGradeItem.objects.create(gradePercentage=3.5, whichStudentsCumulativeGPAisThis=student1)
# a student's class grade = SingularGradeItem.objects.create(gradePercentage=95, whichCoursesAvgGradeIsThis=course1)
# a student's class's grade category average = SingularGradeItem.objects.create(gradePercentage=95, whichGradeCategorysAvgGradeIsThis=category1)

# These above all have histories associated with them, which is why they are done in this way. Multiple SingularGradeObjects will exist for a student's many datapoints
# Individual assignments do not have histories associated. Your exam #1 grade does not fluctuate (even with regrades, it really isn't a super concerning and volatile grade metric)
# Individual assignments use the Assignment class

# Helper functions will be written so that after an Assignment is created, that grade percolates upwards in a student's data model
# This means a new Assignment will create a new SingularGradeItem for an updated grade category average, which will create a new one for course grade average, then for semester GPA, then cumulative GPA...
# These objects are all assigned to the specific student's data model from top to bottom
# Assignment -> SingularGradeItem -> SingularGradeItem -> SingularGradeItem -> SingularGradeItem


    # def test_correct_class_grade_reported(self):
    #     student1 = Student.objects.create(semesterGPA="",cumulativeGPA="")
    #     class1 = Course.objects.create(name="APMA 3100: Probability", numOfCredits=3, studentItBelongsTo=student1)
    #     category1 = GradeCategory.objects.create(name="Exams",weightage=50, courseItBelongsTo=class1)
    #     category2 = GradeCategory.objects.create(name="Homework",weightage=50, courseItBelongsTo=class1)
    #     assignment1 = Assignment.objects.create(name="Exam 1", gradePercentage=80,gradeCategoryItBelongsTo=category1)
    #     assignment2 = Assignment.objects.create(name="Exam 2", gradePercentage=90,gradeCategoryItBelongsTo=category1)
    #     assignment3 = Assignment.objects.create(name="HW 1", gradePercentage=100,gradeCategoryItBelongsTo=category2)

    #     #algorithm: get a class, get its categories, in each category get the avg grade, add to a list of tuples [(category weight : category grade),...] then iterate and calculate grade

    #     gradesAndTheirWeights=[]

    #     listOfCategoriesInClass = class1.categories.all()
    #     for category in listOfCategoriesInClass: #this code calculates grade per category
    #         listOfAssignmentsInCategory = category.assignments.all()
    #         gradeAvg=0
    #         for assignment in listOfAssignmentsInCategory:
    #             gradeAvg+=assignment.gradePercentage
    #         gradeAvg/=len(listOfAssignmentsInCategory)
    #         gradesAndTheirWeights.append((float(category.weightage),float(gradeAvg)))
        
    #     avgClassGrade=0
    #     for item in gradesAndTheirWeights: #this code calculates grade average
    #         avgClassGrade+=item[0]*item[1]/100
        
    #     self.assertEqual(92.5,avgClassGrade)

            




        
