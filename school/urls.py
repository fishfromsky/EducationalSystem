from django.contrib import admin
from django.urls import path
from . import views


urlpatterns = [
    path('addteacher/', views.Add_Teacher, name="AddTeacher"),
    path('addschool/', views.Add_school, name="AddSchool"),
    path('amendschool/', views.Amend_School, name="AmendSchool"),
    path('delete_school/', views.Delete_School, name="DeleteSchool"),
    path('delete_stu/', views.Delete_stu, name="DeleteStu"),
    path('addstudent/', views.Register_student, name="Register_student"),
    path('amendstudent/', views.Amend_Student, name="AmendStudent"),
    path('amendteacher/', views.Amend_Teacher, name='AmendTeacher'),
    path('delete_teacher/', views.Delete_Teacher, name="DeleteTeacher"),
    path('addlesson/', views.Add_Lesson, name='AddLesson'),
    path('amendlesson/', views.AmendLesson, name='AmendLesson'),
    path('deletelesson/', views.DeleteLesson, name="DeleteLesson"),
    path('addopenlesson/', views.Add_openlesson, name="AddOpenLesson"),
    path('amendopenlesson/', views.Amend_openlesson, name="AmendOpenLesson"),
    path('deleteopenlesson/', views.Delete_Openlesson, name="DeleteOpenLesson"),
    path('addoptionlesson/', views.Add_Optionlesson, name="AddOptionLesson"),
    path('amendoptionlesson/', views.Amend_Optionlesson, name="AmendOptionLesson"),
    path('deleteoptionlesson/', views.Delete_OptionLesson, name="DeleteOptionLesson"),
    path('login/', views.LoginInterface, name="LoginInterface"),
    path('get_status/', views.Get_Status, name="Get_Status"),
    path('change_status/', views.Change_status, name="Change_status"),
    path('ensure_status/', views.Ensure_status, name="Ensure_status"),
    path('stop_status/', views.Delete_status, name="Stop_status")
]