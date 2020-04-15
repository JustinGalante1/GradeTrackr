from django.contrib import admin
from django.urls import include, path, re_path
from . import views
import personaldashboard

app_name = 'gradetracker'
urlpatterns = [
    #path('home', personaldashboard.views.HomeView.as_view(), name="home"),
    path('index', views.IndexView.as_view(), name='index'),
    path('add', views.add, name='add'),
    path('test/', views.TestView.as_view(), name='test'),
    path('dashboard/', views.CourseDashboard, name='dashboard'),
    path('', views.SignIn, name='signin'),
    # path('addAssignment/', views.addAssignment, name='addAssignment'),
    # path('gradecat', views.gradecat, name='gradecat'),
    re_path(r'^delete-course/(?P<course_id>\d+)/$', views.delete_course, name='delete_course'),
    re_path(r'^duplicate-course/(?P<course_id>\d+)/$', views.duplicate_course, name='duplicate_course'),
    re_path(r'^course-overview/(?P<course_id>\d+)/$', views.CourseOverview, name='course_overview'),
    re_path(r'^addAssignment/(?P<course_id>\d+)/$', views.addAssignment, name='addAssignment'),
    re_path(r'^gradecat/(?P<course_id>\d+)/$', views.gradecat, name='gradecat'),
    re_path(r'^delete-category/(?P<category_id>\d+)/$', views.delete_category, name='delete_category'),
    re_path(r'^delete-assignment/(?P<assignment_id>\d+)/$', views.delete_assignment, name='delete_assignment')
]
