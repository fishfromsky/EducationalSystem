from django.contrib import admin
from .models import School, Stu_table, Teacher, Lesson, Open_lesson, \
    Option_lesson, Teacher_Login, Student_Login, Supersuser, \
    present_semester, Note_table, School_Note_table, Teacher_Note_table


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
    list_display = ('xh', 'xm', 'xb', 'csrq', 'jg', 'sjhm', 'yxh', 'note_status')
    ordering = ('-xh',)


@admin.register(Teacher)
class TeacherAdmin(admin.ModelAdmin):
    list_display = ('gh', 'xm', 'xb', 'csrq', 'xl', 'jbgz', 'yxh', 'note_status')
    ordering = ('-gh',)


@admin.register(Lesson)
class LessonAdmin(admin.ModelAdmin):
    list_display = ('kh', 'km', 'xf', 'xs', 'yxh', 'rule_ps', 'rule_ks')
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
    list_display = ('xq', 'xk', 'dqxq', 'cjxq_ps', 'cjxq_ks')
    ordering = ('-id',)


@admin.register(Note_table)
class Note_tableAdmin(admin.ModelAdmin):
    list_display = ('id','gh', 'kh', 'xq', 'status', 'content', 'created_time')
    ordering = ('-id',)


@admin.register(School_Note_table)
class SchoolNotetableAdmin(admin.ModelAdmin):
    list_display = ('id', 'xq', 'status', 'content', 'created_time')
    ordering = ('-id',)


@admin.register(Teacher_Note_table)
class TeacherNotetable(admin.ModelAdmin):
    list_display = ('id', 'xq', 'status', 'content', 'created_time')
    ordering = ('-id',)
