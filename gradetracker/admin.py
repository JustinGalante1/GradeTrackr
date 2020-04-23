from django.contrib import admin

from .models import Student, Course, GradeCategory, Assignment, SingularGradeItem

# Register your models here.

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(GradeCategory)
admin.site.register(Assignment)
admin.site.register(SingularGradeItem)