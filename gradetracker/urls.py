from django.contrib import admin
from django.urls import include, path
from . import views
import personaldashboard

app_name = 'gradetracker'
urlpatterns = [
    path('home', personaldashboard.views.HomeView.as_view(), name="home"),
    path('index', views.IndexView.as_view(), name='index'),
    path('addCourse/', views.addCourse, name='addCourse'),
    path('test/', views.TestView.as_view(), name='test'),
    path('addAssignment/', views.addAssignment, name='addAssignment'),
]
