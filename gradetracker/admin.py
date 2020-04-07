from django.contrib import admin

from .models import Student, Course, GradeCategory

# Register your models here.

admin.site.register(Student)
admin.site.register(Course)
admin.site.register(GradeCategory)
