"""数据库项目 URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include, re_path
from school import views
import school.urls

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.Index, name="Index"),
    path('<str:content>', views.Index_search, name='IndexSearch'),
    path('main/', views.Main, name="Main"),
    path('school/', views.SchoolTable, name="SchoolTable"),
    path('school/<str:content>', views.SchoolTable_Search, name='SchoolSearch'),
    path('teacher/', views.TeacherTable, name="TeacherTable"),
    path('teacher/<str:content>', views.TeacherTable_search, name='TeacherSearch'),
    path('lesson/', views.LessonTable, name="LessonTable"),
    path('lesson/<str:content>', views.LessonTable_search, name="LessonSearch"),
    path('open_lesson/', views.Open_Lesson_Table, name="OpenTable"),
    path('open_lesson/<str:content>', views.Open_Lesson_Table_search, name="OpenTableSearch"),
    path('editstudent/', views.EditStudent, name="Editstudent"),
    path('editstudent/<str:content>', views.EditStudent_search, name='EditStudentSearch'),
    path('select_lesson/', views.Select_Lesson, name="Select_lesson"),
    path('select_lesson/<str:content>', views.Select_Lesson_search, name='Select_lesson_search'),
    path('editschool/', views.Editschool, name="Editschool"),
    path('editschool/<str:content>', views.EditSchool_Search, name='EditSchoolSearch'),
    path('api/', include(school.urls)),
    path('editteacher/', views.EditTeacher, name="EditTeacher"),
    path('editteacher/<str:content>', views.EditTeacher_search, name='EditTeacherSearch'),
    path('editlesson/', views.EditLesson, name="EditLesson"),
    path('editlesson/<str:content>', views.EditLesson_search, name='EditLessonSearch'),
    path('edit_open_lesson/', views.Edit_Openlesson, name="EditOpenLesson"),
    path('edit_open_lesson/<str:content>', views.Edit_Openlesson_search, name='EditOpenLessonSearch'),
    path('edit_option_lesson/', views.EditOptionLesson, name="EditOptionLesson"),
    path('edit_option_lesson/<str:content>', views.EditOptionLesson_search, name='EditOptionLessonSearch'),
    path('login/', views.Login, name="Login"),
    path('t_/', views.T_Index, name="T_Index"),
    path('s_/', views.S_Index, name="S_Index"),
    path('register/', views.Register, name='Register'),
    path('t_lesson/<str:number>/<str:semester>', views.t_Lesson, name="t_Lesson"),
    path('t_select/<str:number>/<str:semester>', views.t_select_lesson, name='t_Select_Lesson'),
    path('t_register/<str:number>/<str:semester>', views.Grade, name="Grade"),
    path('t_grade/<str:number>/<str:semester>/<str:lesson>', views.Register_Grade, name="RegisterGrade"),
    path('t_grade_check/<str:number>/<str:semester>/<str:lesson>', views.Check_grade, name="Check_grade"),
    path('t_select/<str:number>/<str:semester>/<str:content>', views.Select_Lesson_Search, name="Select_Search"),
    path('t_grade_check/<str:number>/<str:semester>/<str:lesson>/<str:content>', views.Check_Grade_search,
         name='Check_search'),
    path('t_grade/<str:number>/<str:semester>/<str:lesson>/<str:content>', views.Register_Grade_search,
         name="RegisterGradeSearch")
]
