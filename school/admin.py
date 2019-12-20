from django.contrib import admin
from .models import School, Stu_table, Teacher, Lesson, Open_lesson, \
    Option_lesson, Teacher_Login, Student_Login, Supersuser, present_semester


@admin.register(Teacher_Login)
class TeacherLoginAdmin(admin.ModelAdmin):
    list_display = ('gh', 'xm', 'password', 'yxh')
    ordering = ('-gh',)


@admin.register(Student_Login)
class StudentLoginAdmin(admin.ModelAdmin):
    list_display = ('xh', 'xm', 'password', 'yxh')
    ordering = ('-xh',)


@admin.register(Supersuser)
class SuperuserAdmin(admin.ModelAdmin):
    list_display = ('number', 'username', 'password')
    ordering = ('-number',)


@admin.register(School)
class SchoolAdmin(admin.ModelAdmin):
   list_display = ('yxh', 'mc', 'dz', 'lxdh')
   ordering = ('-yxh',)


@admin.register(Stu_table)
class Stu_tableAdmin(admin.ModelAdmin):
    list_display = ('xh', 'xm', 'xb', 'csrq', 'jg', 'sjhm', 'yxh')
    ordering = ('-xh',)

@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('gh', 'xm', 'xb', 'csrq', 'xl', 'jbgz', 'yxh')
    ordering = ('-gh',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('kh', 'km', 'xf', 'xs', 'yxh')
    ordering = ('-kh',)


@admin.register(Open_lesson)
class Open_lessonAdmin(admin.ModelAdmin):
    list_display = ('xq', 'kh', 'gh', 'sksj')


@admin.register(Option_lesson)
class Option_lessonAdmin(admin.ModelAdmin):
    list_display = ('xh', 'xq', 'kh', 'gh', 'pscj', 'kscj', 'zpcj')
    ordering = ('-zpcj',)


@admin.register(present_semester)
class present_semesterAdmin(admin.ModelAdmin):
    list_display = ('xq', 'xk', 'dqxq')
    ordering = ('-id',)
