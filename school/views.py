from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Stu_table, School, Teacher, Lesson, Open_lesson, Option_lesson, \
    Student_Login, Teacher_Login, Supersuser, present_semester, Note_table, School_Note_table, Teacher_Note_table
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import json
from django.core import serializers
from django.db import connection
from django.db.models import Q


def Login(request):
    context = {}
    school_list = School.objects.all()
    context['school_list'] = school_list
    return render(request, './superuser/login.html', context)


def Main(request):
    return render(request, './superuser/main.html', {})


@require_http_methods(['POST'])
def Main_Get(request):
    response = {}
    semester = request.POST.get('semester')
    stu_count = Option_lesson.objects.filter(xq=semester).values('xh_id').count()
    teacher_count = Open_lesson.objects.filter(xq=semester).values('gh_id').count()
    cursor = connection.cursor()
    cursor.execute("select xm,count(xh_id) from school_teacher tb1,school_option_lesson tb2 "
                   "where tb1.gh=tb2.gh_id and xq='"+semester+"' group by tb1.gh order by 2 desc;")
    teacher_love = cursor.fetchall()
    cursor.execute("select km,count(xh_id) from school_option_lesson tb1,school_lesson tb2 where tb1.kh_id=tb2.kh "
                   "and xq='"+semester+"' group by kh_id order by 2 desc;")
    lesson_love = cursor.fetchall()
    cursor.execute("select count(kh_id), mc from school_open_lesson tb1, school_lesson tb2, school_school tb3 where "
                   "tb3.yxh=tb2.yxh_id and tb2.kh=tb1.kh_id and xq='"+semester+"' group by yxh_id order by 1 desc;")
    school_love = cursor.fetchall()
    cursor.execute("select count(xh_id),mc from school_school tb1,school_lesson tb2,school_option_lesson tb3 where "
                   "tb1.yxh=tb2.yxh_id and tb2.kh=tb3.kh_id and xq='"+semester+"' group by tb1.yxh order by 1 desc;")
    school_count = cursor.fetchall()
    response['stu_count'] = stu_count
    response['teacher_count'] = teacher_count
    lesson_count = Open_lesson.objects.filter(xq=semester).all().count()
    response['lesson_count'] = lesson_count
    response['teacher_love'] = list(teacher_love)[:5] if len(list(teacher_love)) > 5 else list(teacher_love)
    response['lesson_love'] = list(lesson_love)[:5] if len(list(lesson_love)) > 5 else list(lesson_love)
    response['school_love'] = list(school_love)
    response['school_count'] = list(school_count)
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Register(request):
    response = {}
    number = request.POST.get('number')
    name = request.POST.get('name')
    role = request.POST.get('role')
    password = request.POST.get('password')
    school = request.POST.get('school')
    if role == '学生注册':
        if Student_Login.objects.filter(xh=number, xm=name).count():
            response['message'] = 'Exist'
            response['code'] = -1
        elif Stu_table.objects.filter(xh=number, xm=name, yxh=school).count() == 0:
            response['message'] = 'stu_error'
            response['code'] = -2
        else:
            print(number, name, password, school)
            student = Student_Login(xh=Stu_table(xh=number), xm=name, password=password,
                                    yxh=School(yxh=school))
            student.save()
            response['message'] = 'success'
            response['code'] = 0
    else:
        if Teacher_Login.objects.filter(gh=number, xm=name).count():
            response['message'] = 'Exist'
            response['code'] = -1
        elif Teacher.objects.filter(gh=number, xm=name, yxh=school).count() == 0:
            response['message'] = 'tea_error'
            response['code'] = -2
        else:
            teacher = Teacher_Login(gh=Teacher(gh=number), xm=name,
                                    password=password, yxh=School(yxh=school))
            teacher.save()
            response['message'] = 'success'
            response['code'] = 0

    return JsonResponse(response)


@require_http_methods(['POST'])
def LoginInterface(request):
    response = {}
    number = request.POST.get('number')
    username = request.POST.get('username')
    password = request.POST.get('password')
    role = request.POST.get('role')
    if role == 'student':
        if Student_Login.objects.filter(xh=number, xm=username, password=password).count():
            response['message'] = 'studentsuccess'
            response['code'] = 0
        else:
            response['message'] = 'studenterror'
            response['code'] = -1
    elif role == 'teacher':
        if Teacher_Login.objects.filter(gh=number, xm=username, password=password).count():
            response['message'] = 'teachersuccess'
            response['code'] = 0
        else:
            response['message'] = 'teachererror'
            response['code'] = -1
    else:
        if Supersuser.objects.filter(number=number, username=username, password=password).count():
            response['message'] = 'supersuccess'
            response['code'] = 0
        else:
            response['message'] = 'supererror'
            response['code'] = -1
    return JsonResponse(response)


def Index(request):
    context = {}
    student_list = Stu_table.objects.all()
    paginator = Paginator(student_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/index.html', context)


def Index_search(request, content):
    context = {}
    student_list = Stu_table.objects.filter(Q(xm__contains=content) | Q(xh__contains=content) | Q(jg__contains=content)
                                            | Q(sjhm__contains=content))
    paginator = Paginator(student_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/index_search.html', context)


def SchoolTable(request):
    context  ={}
    school_list = School.objects.all()
    paginator = Paginator(school_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/school.html', context)


def SchoolTable_Search(request, content):
    context = {}
    school_list = School.objects.filter(Q(mc__contains=content) | Q(dz__contains=content) | Q(lxdh__contains=content))
    paginator = Paginator(school_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/school_search.html', context)


@require_http_methods(['POST'])
def Register_student(request):
    response = {}
    number = request.POST.get('number')
    name = request.POST.get('stu_name')
    phone = request.POST.get('phone')
    gender = request.POST.get('gender')
    address = request.POST.get('address')
    time = request.POST.get('time')
    school = request.POST.get('school')
    if Stu_table.objects.filter(xh=number).count():
        response['code'] = -1
        response['message'] = 'ExistError'
    else:
        response['code'] = 0
        response['message'] = 'success'
        student = Stu_table(xh=number, xm=name, xb=gender, csrq=time, jg=address, sjhm=phone, yxh=School(yxh=school))
        student.save()
    return JsonResponse(response)


def Amend_Student(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        name = request.POST.get('stu_name')
        phone = request.POST.get('phone')
        gender = request.POST.get('gender')
        address = request.POST.get('address')
        time = request.POST.get('time')
        school = request.POST.get('school')
        student = Stu_table(xh=number, xm=name, xb=gender, csrq=time, jg=address, sjhm=phone, yxh=School(yxh=school))
        student.save()
        return redirect(reverse('Editstudent'))


def TeacherTable(request):
    context = {}
    teacher_list = Teacher.objects.all()
    paginator = Paginator(teacher_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/teacher.html', context)


def TeacherTable_search(request, content):
    context = {}
    teacher_list = Teacher.objects.filter(Q(xm__contains=content) | Q(gh__contains=content))
    paginator = Paginator(teacher_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/teacher_search.html', context)


def LessonTable(request):
    context = {}
    lesson_list = Lesson.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list
    context['credit'] = 4
    context['time'] = 40

    return render(request, './superuser/lesson.html', context)


def LessonTable_search(request, content):
    context = {}
    lesson_list = Lesson.objects.filter(Q(kh__contains=content) | Q(km__contains=content))
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list
    context['credit'] = 4
    context['time'] = 40

    return render(request, './superuser/lesson_search.html', context)


def Open_Lesson_Table(request):
    context = {}
    lesson_list = Open_lesson.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/open_lesson.html', context)


def Open_Lesson_Table_search(request, content):
    context = {}
    lesson_list = Open_lesson.objects.filter(Q(xq__contains=content) | Q(kh__kh__contains=content) |
                                             Q(gh__gh__contains=content) | Q(sksj__contains=content))
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/open_lesson_search.html', context)


def EditStudent(request):
    context = {}
    lesson_list = Stu_table.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/editstudent.html', context)


def EditStudent_search(request, content):
    context = {}
    student_list = Stu_table.objects.filter(Q(xm__contains=content) | Q(xh__contains=content) | Q(jg__contains=content)
                                            | Q(sjhm__contains=content))
    paginator = Paginator(student_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/editstudent_search.html', context)


def Select_Lesson(request):
    context = {}
    lesson_list = Option_lesson.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/option_lesson.html', context)


def Select_Lesson_search(request, content):
    context = {}
    lesson_list = Option_lesson.objects.filter(Q(xh__xh__contains=content) | Q(xq__contains=content) |
                                               Q(gh__gh__contains=content) | Q(kh__kh__contains=content))
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/option_lesson_search.html', context)

def Delete_stu(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        student = Stu_table.objects.get(xh=number)
        student.delete()
        return redirect(reverse('Editstudent'))


@require_http_methods(["POST"])
def Add_school(request):
    response = {}
    number = request.POST.get('number')
    name = request.POST.get('school_name')
    address = request.POST.get('address')
    phone = request.POST.get('phone')
    if School.objects.filter(yxh=number).count():
        response['code'] = -1
        response['message'] = 'ExistError'
    else:
        response['code'] = 0
        response['message'] = 'success'
        school = School(yxh=number, mc=name, dz=address, lxdh=phone)
        school.save()
    return JsonResponse(response)


def Amend_School(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        name = request.POST.get('school_name')
        address = request.POST.get('address')
        phone = request.POST.get('phone')
        school = School(yxh=number, mc=name, dz=address, lxdh=phone)
        school.save()
        return redirect(reverse('Editschool'))


def Editschool(request):
    context = {}
    lesson_list = School.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/editschool.html', context)


def EditSchool_Search(request, content):
    context = {}
    school_list = School.objects.filter(Q(mc__contains=content) | Q(dz__contains=content) | Q(lxdh__contains=content))
    paginator = Paginator(school_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/editschool_search.html', context)


def Delete_School(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        school = School.objects.get(yxh=number)
        school.delete()
        return redirect(reverse('Editschool'))


@require_http_methods(["POST"])
def Add_Teacher(request):
    response = {}
    number = request.POST.get('number')
    name = request.POST.get('teacher_name')
    gender = request.POST.get('gender')
    time = request.POST.get('time')
    study = request.POST.get('study')
    money = request.POST.get('money')
    school = request.POST.get('school')
    school_yxh = School.objects.get(yxh=school)
    if Teacher.objects.filter(gh=number).count():
        response['message'] = 'ExistError',
        response['code'] = -1
    else:
        teacher = Teacher(gh=number, xm=name, xb=gender, csrq=time, xl=study, jbgz=money, yxh=school_yxh)
        teacher.save()
        response['message'] = 'success'
        response['code'] = 0

    return JsonResponse(response)


def EditTeacher(request):
    context = {}
    lesson_list = Teacher.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/editteacher.html', context)


def EditTeacher_search(request, content):
    context = {}
    teacher_list = Teacher.objects.filter(Q(xm__contains=content) | Q(gh__contains=content))
    paginator = Paginator(teacher_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/editteacher_search.html', context)


def Amend_Teacher(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        name = request.POST.get('teacher_name')
        gender = request.POST.get('gender')
        study = request.POST.get('study')
        time = request.POST.get('time')
        money = request.POST.get('money')
        school = request.POST.get('school')
        teacher = Teacher(gh=number, xm=name, xb=gender, csrq=time, xl=study, jbgz=money, yxh=School(yxh=school))
        teacher.save()
        return redirect(reverse("EditTeacher"))


def Delete_Teacher(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        teacher = Teacher.objects.get(gh=number)
        teacher.delete()
        return redirect(reverse('EditTeacher'))


def EditLesson(request):
    context = {}
    lesson_list = Lesson.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list
    context['credit'] = 4
    context['hours'] = 40

    return render(request, './superuser/editlesson.html', context)


def EditLesson_search(request, content):
    context = {}
    lesson_list = Lesson.objects.filter(Q(kh__contains=content) | Q(km__contains=content))
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list
    context['credit'] = 4
    context['time'] = 40

    return render(request, './superuser/editlesson_search.html', context)


@require_http_methods(['POST'])
def Add_Lesson(request):
    response = {}
    number = request.POST.get('number')
    name = request.POST.get('name')
    credit = request.POST.get('credit')
    hours = request.POST.get('hours')
    school = request.POST.get('school')
    if Lesson.objects.filter(kh=number).count():
        response['message'] = 'ExistError'
        response['code'] = -1
    else:
        lesson = Lesson(kh=number, km=name, xf=credit, xs=hours, yxh=School(yxh=school))
        lesson.save()
        response['message'] = 'success'
        response['code'] = 0
    return JsonResponse(response)


def AmendLesson(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        name = request.POST.get('lesson_name')
        credit = request.POST.get('credit')
        hours = request.POST.get('hours')
        school = request.POST.get('school')
        lesson = Lesson(kh=number, km=name, xf=credit, xs=hours, yxh=School(yxh=school))
        lesson.save()
        return redirect(reverse('EditLesson'))


def DeleteLesson(request):
    if request.method == 'POST':
        number = request.POST.get('number')
        lesson = Lesson(kh=number)
        lesson.delete()
        return redirect(reverse('EditLesson'))


@require_http_methods(['POST'])
def Add_openlesson(request):
    response = {}
    semester = request.POST.get('semester')
    lesson_number = request.POST.get('lesson_number')
    teacher_number = request.POST.get('teacher_number')
    hours = request.POST.get('hours')
    if Lesson.objects.filter(kh=lesson_number).count() == 0:
        response['message'] = 'LessonError'
        response['code'] = -1
    elif Teacher.objects.filter(gh=teacher_number).count() == 0:
        response['message'] = 'TeacherError'
        response['code'] = -2
    elif Open_lesson.objects.filter(xq=semester, kh=lesson_number, gh=teacher_number, sksj=hours).count():
        response['message'] = 'OpenExist'
        response['code'] = -3
    else:
        lesson = Open_lesson(xq=semester, kh=Lesson(kh=lesson_number), gh=Teacher(gh=teacher_number), sksj=hours)
        lesson.save()
        response['message'] = 'success'
        response['code'] = 0
    return JsonResponse(response)


def Edit_Openlesson(request):
    context = {}
    lesson_list = Open_lesson.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/edit_open_lesson.html', context)


def Edit_Openlesson_search(request, content):
    context = {}
    lesson_list = Open_lesson.objects.filter(Q(xq__contains=content) | Q(kh__kh__contains=content) |
                                             Q(gh__gh__contains=content) | Q(sksj__contains=content))
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/edit_open_lesson_search.html', context)


@require_http_methods(['POST'])
def Amend_openlesson(request):
    response = {}
    semester_ori = request.POST.get('semester_ori')
    lesson_id_ori = request.POST.get('lesson_id_ori')
    teacher_id_ori = request.POST.get('teacher_id_ori')
    hours_ori = request.POST.get('hours_ori')
    semester = request.POST.get('semester')
    lesson_number = request.POST.get('lesson_number')
    teacher_number = request.POST.get('teacher_number')
    hours = request.POST.get('hours')
    if Lesson.objects.filter(kh=lesson_number).count() == 0:
        response['message'] = 'LessonError'
        response['code'] = -1
    elif Teacher.objects.filter(gh=teacher_number).count() == 0:
        response['message'] = 'TeacherError'
        response['code'] = -2
    elif Open_lesson.objects.filter(xq=semester, kh=lesson_number, gh=teacher_number, sksj=hours).count():
        response['message'] = 'OpenExist'
        response['code'] = -3
    else:
        lesson = Open_lesson.objects.filter(xq=semester_ori, kh=Lesson(kh=lesson_id_ori),
                                            gh=Teacher(gh=teacher_id_ori), sksj=hours_ori).first()
        lesson.xq = semester
        lesson.kh = Lesson(kh=lesson_number)
        lesson.gh = Teacher(gh=teacher_number)
        lesson.sksj = hours
        lesson.save()
        response['message'] = 'success'
        response['code'] = 0
    return JsonResponse(response)


def Delete_Openlesson(request):
    if request.method == 'POST':
        semester = request.POST.get('semester')
        lesson_id = request.POST.get('lesson_id')
        teacher_id = request.POST.get('teacher_id')
        hours = request.POST.get('hours')
        lesson = Open_lesson.objects.filter(xq=semester, kh=Lesson(kh=lesson_id),
                                            gh=Teacher(gh=teacher_id), sksj=hours).first()
        lesson.delete()
        return redirect(reverse('EditOpenLesson'))


@require_http_methods(['POST'])
def Add_Optionlesson(request):
    response = {}
    stu_number = request.POST.get('stu_number')
    semester = request.POST.get('semester')
    lesson_number = request.POST.get('lesson_number')
    teacher_number = request.POST.get('teacher_number')
    pscj = request.POST.get('pscj')
    kscj = request.POST.get('kscj')
    zpcj = request.POST.get('zpcj')
    if pscj == "":
        pscj = None
    if kscj == "":
        kscj = None
    if zpcj == "":
        zpcj = None
    if Option_lesson.objects.filter(xh=Stu_table(xh=stu_number), xq=semester,
                                    kh=Lesson(kh=lesson_number), gh=Teacher(gh=teacher_number)).count():
        response['message'] = 'ExistError'
        response['code'] = -1
    elif Open_lesson.objects.filter(xq=semester, kh=Lesson(kh=lesson_number), gh=Teacher(gh=teacher_number)).count() == 0:
        response['message'] = 'LessonError'
        response['code'] = -2
    else:
        lesson = Option_lesson(xh=Stu_table(xh=stu_number), xq=semester, kh=Lesson(kh=lesson_number),
                               gh=Teacher(gh=teacher_number), pscj=pscj, kscj=kscj, zpcj=zpcj)
        lesson.save()
        response['message'] = 'success'
        response['code'] = 0
    return JsonResponse(response)


def EditOptionLesson(request):
    context = {}
    lesson_list = Option_lesson.objects.all()
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/edit_option_lesson.html', context)


def EditOptionLesson_search(request, content):
    context = {}
    lesson_list = Option_lesson.objects.filter(Q(xh__xh__contains=content) | Q(xq__contains=content) |
                                               Q(gh__gh__contains=content) | Q(kh__kh__contains=content))
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    school_list = School.objects.all()
    context['school_list'] = school_list

    return render(request, './superuser/edit_option_lesson_search.html', context)


@require_http_methods(['POST'])
def Amend_Optionlesson(request):
    response = {}
    student_id_ori = request.POST.get('student_id_ori')
    semester_ori = request.POST.get('semester_ori')
    lesson_id_ori = request.POST.get('lesson_id_ori')
    teacher_id_ori = request.POST.get('teacher_id_ori')
    stu_number = request.POST.get('stu_number')
    semester = request.POST.get('semester')
    lesson_number = request.POST.get('lesson_number')
    teacher_number = request.POST.get('teacher_number')
    pscj = request.POST.get('pscj')
    kscj = request.POST.get('kscj')
    zpcj = request.POST.get('zpcj')
    if pscj == "":
        pscj = None
    if kscj == "":
        kscj = None
    if zpcj == "":
        zpcj = None
    if Open_lesson.objects.filter(xq=semester, kh=Lesson(kh=lesson_number), gh=Teacher(gh=teacher_number)).count() == 0:
        response['message'] = 'LessonError'
        response['code'] = -1
    else:
        lesson = Option_lesson.objects.filter(xh=Stu_table(xh=student_id_ori), xq=semester_ori, kh=Lesson(kh=lesson_id_ori),
                               gh=Teacher(gh=teacher_id_ori)).first()
        lesson.xh = Stu_table(xh=stu_number)
        lesson.xq = semester
        lesson.kh = Lesson(kh=lesson_number)
        lesson.gh = Teacher(gh=teacher_number)
        lesson.pscj = pscj
        lesson.kscj = kscj
        lesson.zpcj = zpcj
        lesson.save()
        response['message'] = 'success'
        response['code'] = 0
    return JsonResponse(response)


def Delete_OptionLesson(request):
    if request.method == 'POST':
        student_number = request.POST.get('stu_number')
        semester = request.POST.get('semester')
        lesson_number = request.POST.get('lesson_id')
        teacher_number = request.POST.get('teacher_id')
        lesson = Option_lesson.objects.filter(xh=Stu_table(xh=student_number), xq=semester,
                                              kh=Lesson(kh=lesson_number), gh=Teacher(gh=teacher_number)).first()
        lesson.delete()
        return redirect(reverse('EditOptionLesson'))


def T_Index(request):
    context = {}
    return render(request, './teacher/t_index.html', context)


def S_Index(request):
    return render(request, './superuser/s_index.html', {})


@require_http_methods(['POST'])
def Get_Status(request):
    response = {}
    semester_list = present_semester.objects.all()
    response['result'] = json.loads(serializers.serialize('json', semester_list))
    response['message'] = 'success'
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Change_status(request):
    response = {}
    semester = request.POST.get('semester')
    lesson = present_semester.objects.get(xq=semester)
    lesson.xk = '1'
    lesson.save()
    response['message'] = 'success'
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Ensure_status(request):
    response = {}
    if present_semester.objects.filter(dqxq='1').count():
        semester = present_semester.objects.get(dqxq='1').xq
        status = present_semester.objects.get(dqxq='1').xk
        grade_status = present_semester.objects.get(dqxq='1').cjxq_ps
        grade_status_ks = present_semester.objects.get(dqxq='1').cjxq_ks
        if status == '1':
            response['status'] = 1
            response['grade'] = grade_status
            response['grade_ks'] = grade_status_ks
            response['semester'] = semester
            response['message'] = 'success'
            response['code'] = 0
        else:
            response['status'] = 0
            response['grade'] = grade_status
            response['grade_ks'] = grade_status_ks
            response['semester'] = semester
            response['message'] = 'success'
            response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Delete_status(request):
    response = {}
    semester = request.POST.get('semester')
    lesson = present_semester.objects.get(xq=semester)
    lesson.xk = '0'
    lesson.save()
    response['message'] = 'success'
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Change_present_semester(request):
    response = {}
    semester = request.POST.get('semester')
    semester_ori = request.POST.get('semester_ori')
    sem_ori = present_semester.objects.get(xq=semester_ori)
    sem = present_semester.objects.get(xq=semester)
    sem_ori.dqxq = '0'
    sem.dqxq = '1'
    sem_ori.save()
    sem.save()
    response['message'] = 'success'
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Init_Teacher(request):
    response = {}
    semester_list = present_semester.objects.all()
    semester = present_semester.objects.get(dqxq='1').xq
    response['semester'] = semester
    response['semester_list'] = json.loads(serializers.serialize('json', semester_list))
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Get_Teacher_status(request):
    response = {}
    cursor = connection.cursor()
    semester = request.POST.get('semester')
    number = request.POST.get('number')
    cursor.execute("select count(kh_id),xq from school_open_lesson where gh_id='"+number+"' group by xq")
    open_lessons = cursor.fetchall()
    cursor.execute("select count(xh_id) from school_option_lesson tb1,school_open_lesson tb2 where"
                                " tb2.gh_id=tb1.gh_id and tb2.kh_id=tb1.kh_id and tb2.xq=tb1.xq and tb1.gh_id="
                                "'"+number+"' and tb1.xq='"+semester+"';")
    stu_number = list(cursor.fetchall())[0][0]
    lesson_number = Open_lesson.objects.filter(xq=semester).filter(gh_id=number).values('kh_id').count()

    cursor.execute("select count(xh_id),mc from school_option_lesson tb1, school_stu_table tb2,school_school "
                   "tb3 where tb1.xh_id=tb2.xh and tb2.yxh_id=tb3.yxh and gh_id='"+number+"' and xq='"+semester+"' group by yxh_id;")
    stu_distribution = cursor.fetchall()
    cursor.execute("select count(xh_id),xq from school_option_lesson where gh_id='"+number+"' group by xq")
    semester_list = cursor.fetchall()
    cursor.execute("select count(xh_id),jg from school_option_lesson tb1,school_stu_table tb2 where tb1.xh_id=tb2.xh "
                   "and gh_id='"+number+"' and xq='"+semester+"' group by jg;")
    location_list = cursor.fetchall()
    semesters = Option_lesson.objects.all().values('xq').distinct()
    response['open_lessons'] = list(open_lessons)
    response['stu_distribute'] = list(stu_distribution)
    response['stu_number'] = stu_number
    response['lesson_number'] = lesson_number
    response['semester_list'] = semester_list
    response['semesters'] = list(semesters)
    response['locations'] = list(location_list)
    response['code'] = 0
    return JsonResponse(response)


def t_Lesson(request, number, semester):
    context = {}
    lesson_list = Open_lesson.objects.filter(gh_id=number, xq=semester)
    paginator = Paginator(lesson_list, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/lesson.html', context)


def t_select_lesson(request, number, semester):
    context = {}
    cursor = connection.cursor()
    cursor.execute("select xh,xm,kh,km,mc,sksj from school_option_lesson tb1,school_open_lesson tb2,school_lesson tb3,"
                   "school_school tb4,school_stu_table tb5 where tb5.xh=tb1.xh_id and tb4.yxh=tb3.yxh_id and tb3.kh"
                   "=tb1.kh_id and tb2.kh_id=tb1.kh_id and tb2.gh_id=tb1.gh_id and tb2.xq=tb1.xq and tb1.gh_id='"+number
                   +"' and tb1.xq='"+semester+"';")
    lesson_list = cursor.fetchall()
    paginator = Paginator(list(lesson_list), 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './teacher/select_lesson.html', context)


def Grade(request, number, semester):
    context = {}
    cursor = connection.cursor()
    cursor.execute("select kh,km,sksj from school_open_lesson tb1,school_lesson tb2 where tb1.kh_id=tb2.kh and"
                   " tb1.gh_id='"+number+"' and tb1.xq='"+semester+"';")
    lesson_list = cursor.fetchall()
    paginator = Paginator(list(lesson_list), 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './teacher/grade.html', context)


def Register_Grade(request, number, semester, lesson):
    context = {}
    cursor = connection.cursor()
    cursor.execute("select xh,xm,kh,km,pscj,kscj,zpcj from school_option_lesson tb1,school_stu_table tb2,school_lesson"
                   " tb3 where tb1.xh_id=tb2.xh and "
                   "tb1.kh_id=tb3.kh and gh_id='"+number+"' and xq='"+semester+"' and kh_id='"+lesson+"';")
    lesson_list = cursor.fetchall()
    paginator = Paginator(list(lesson_list), 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/grade_register.html', context)


def Check_grade(request, number, semester, lesson):
    context = {}
    cursor = connection.cursor()
    cursor.execute("select xh,xm,mc,pscj,kscj,zpcj from school_stu_table tb1,school_school tb2,school_option_lesson tb3"
                   " where tb1.xh=tb3.xh_id and tb2.yxh=tb1.yxh_id and tb3.gh_id='"+number+"' and tb3.xq='"+semester+"'"
                    " and kh_id='"+lesson+"';")
    lesson_list = cursor.fetchall()
    paginator = Paginator(list(lesson_list), 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/grade_check.html', context)


@require_http_methods(['POST'])
def Save_grade(request):
    response = {}
    stu_number = request.POST.get('stu_num')
    lesson_number = request.POST.get('lesson_num')
    tea_number = request.POST.get('tea_num')
    grade = Option_lesson.objects.get(xh_id=Stu_table(xh=stu_number),
                                      kh_id=Lesson(kh=lesson_number), gh_id=Teacher(gh=tea_number))
    grade.pscj = request.POST.get('pscj')
    grade.kscj = request.POST.get('kscj')
    grade.zpcj = request.POST.get('zpcj')
    grade.save()
    response['message'] = 'success'
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Get_Percent(request):
    response = {}
    lesson_number = request.POST.get('lesson')
    lesson = Lesson.objects.get(kh=lesson_number)
    rule_ps = lesson.rule_ps
    rule_ks = lesson.rule_ks
    response['message'] = 'success'
    response['code'] = 0
    response['rule_ps'] = rule_ps
    response['rule_ks'] = rule_ks
    return JsonResponse(response)


@require_http_methods(['POST'])
def Start_Grade_register_PS(request):
    response = {}
    grade = present_semester.objects.get(dqxq='1')
    grade.cjxq_ps = '1'
    grade.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Stop_Grade_register_PS(request):
    response = {}
    grade = present_semester.objects.get(dqxq='1')
    grade.cjxq_ps = '0'
    grade.save()
    response['message'] = 'success'
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Judge_grade_register(request):
    response = {}
    grade = present_semester.objects.get(dqxq='1')
    if grade.cjxq_ps == '1':
        response['result'] = 1
    else:
        response['result'] = 0
    if grade.cjxq_ks == '1':
        response['result_ks'] = 1
    else:
        response['result_ks'] = 0
    response['message'] = 'success'
    response['code'] = 0
    return JsonResponse(response)


@require_http_methods(['POST'])
def Start_Grade_Register_KS(request):
    response = {}
    grade = present_semester.objects.get(dqxq='1')
    grade.cjxq_ks = '1'
    grade.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Stop_Grade_Register_KS(request):
    response = {}
    grade = present_semester.objects.get(dqxq='1')
    grade.cjxq_ks = '0'
    grade.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


def Select_Lesson_Search(request, number, semester, content):
    context = {}
    cursor = connection.cursor()
    cursor.execute("select xh,xm,kh,km,mc,sksj from school_option_lesson tb1,school_open_lesson tb2,school_lesson tb3,"
                   "school_school tb4,school_stu_table tb5 where tb5.xh=tb1.xh_id and tb4.yxh=tb3.yxh_id and tb3.kh="
                   "tb1.kh_id and tb2.kh_id=tb1.kh_id and tb2.gh_id=tb1.gh_id and tb2.xq=tb1.xq and tb1.gh_id='"+number
                   +"' and tb1.xq='"+semester+"' and (xm like '"+content+"%' or xm like '%"+content+"' or xm like '%"+content+"%');")
    lesson_list = cursor.fetchall()
    paginator = Paginator(list(lesson_list), 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './teacher/select_search_lesson.html', context)


def Check_Grade_search(request,number,semester,lesson,content):
    context = {}
    cursor = connection.cursor()
    cursor.execute("select xh,xm,mc,pscj,kscj,zpcj from school_stu_table tb1,school_school tb2,school_option_lesson tb3"
                   " where tb1.xh=tb3.xh_id and tb2.yxh=tb1.yxh_id and tb3.gh_id='"+number+"' and tb3.xq='"+semester+"'"
                    " and kh_id='"+lesson+"' and ( xm like '%"+content+"' or xm like '"+content+"%' or xm like '%"+content+"%');")
    lesson_list = cursor.fetchall()
    paginator = Paginator(list(lesson_list), 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/grade_check_search.html', context)


def Register_Grade_search(request, number, semester, lesson, content):
    context = {}
    cursor = connection.cursor()
    cursor.execute("select xh,xm,kh,km,pscj,kscj,zpcj from school_option_lesson tb1,school_stu_table tb2,school_lesson"
                   " tb3 where tb1.xh_id=tb2.xh and "
                   "tb1.kh_id=tb3.kh and gh_id='"+number+"' and xq='"+semester+"' and kh_id='"+lesson+"' and ( xm like"
                  " '%"+content+"' or xm like '"+content+"%' or xm like '%"+content+"%');")
    lesson_list = cursor.fetchall()
    paginator = Paginator(list(lesson_list), 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number
    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/grade_register_search.html', context)


def Get_note(request):
    context = {}
    note_list = School_Note_table.objects.all()
    paginator = Paginator(note_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/school_note.html', context)


def Get_Note_Search(request, content):
    context = {}
    note_list = School_Note_table.objects.filter(Q(content__contains=content))
    paginator = Paginator(note_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/school_note_search.html', context)


@require_http_methods(['POST'])
def Send_School_Note(request):
    response = {}
    xq = request.POST.get('xq')
    content = request.POST.get('content')
    note = School_Note_table(xq=xq, content=content)
    note.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Delete_Note(request):
    response = {}
    id = request.POST.get('id')
    note = School_Note_table.objects.get(id=id)
    note.delete()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Save_Note(request):
    response = {}
    id = request.POST.get('id')
    content = request.POST.get('content')
    note = School_Note_table.objects.get(id=id)
    note.content = content
    note.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Save_teacher_Note(request):
    response = {}
    id = request.POST.get('id')
    content = request.POST.get('content')
    note = Teacher_Note_table.objects.get(id=id)
    note.content = content
    note.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Save_Student_Note(request):
    response = {}
    id = request.POST.get('id')
    content = request.POST.get('content')
    note = Note_table.objects.get(id=id)
    note.content = content
    note.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Delete_Teacher_Note(request):
    response = {}
    id = request.POST.get('id')
    note = Teacher_Note_table.objects.get(id=id)
    note.delete()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Delete_Student_Note(request):
    response = {}
    id = request.POST.get('id')
    note = Note_table.objects.get(id=id)
    note.delete()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


def Get_Teacher_Note(request, gh, xq):
    context = {}
    note = Note_table.objects.filter(gh_id=gh, xq=xq)
    paginator = Paginator(note, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/student_note.html', context)


@require_http_methods(['POST'])
def T_Send_Note(request):
    response = {}
    gh = request.POST.get('gh')
    kh = request.POST.get('kh')
    xq = request.POST.get('xq')
    content = request.POST.get('content')
    if Teacher.objects.filter(gh=gh).count() == 0:
        response['code'] = -2
        response['message'] = 'DoseNotSuccess'
    elif Open_lesson.objects.filter(gh_id=gh, xq=xq, kh_id=kh).count() == 0:
        response['code'] = -1
        response['message'] = 'DoseNotExist'
    else:
        note = Note_table(gh_id=Teacher(gh=gh), kh_id=Lesson(kh=kh), xq=xq, content=content)
        note.save()
        response['code'] = 0
        response['message'] = 'success'
    return JsonResponse(response)


@require_http_methods(['POST'])
def Send_Teacher_Note(request):
    response = {}
    xq = request.POST.get('xq')
    content = request.POST.get('content')
    note = Teacher_Note_table(xq=xq, content=content)
    note.save()
    response['code'] = 0
    response['message'] = 'success'
    return JsonResponse(response)


def T_Search_Note(request, gh, xq, content):
    context = {}
    note = Note_table.objects.filter(gh_id=Teacher(gh=gh)).filter(xq=xq)\
        .filter(Q(kh__kh__contains=content) | Q(content__contains=content))
    paginator = Paginator(note, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './teacher/note_search.html', context)


def Get_School_Note_teacher(request):
    context = {}
    note_list = Teacher_Note_table.objects.all()
    paginator = Paginator(note_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/teacher_note.html', context)


def Get_School_Note_Teacher_Search(request, content):
    context = {}
    note_list = Teacher_Note_table.objects.filter(Q(content__contains=content))
    paginator = Paginator(note_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/teacher_note_search.html', context)


def Get_School_Note_student(request):
    context = {}
    note_list = Note_table.objects.all()
    paginator = Paginator(note_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/student_note.html', context)


def Get_School_Note_student_Search(request, content):
    context = {}
    note_list = Note_table.objects.filter(Q(content__contains=content))
    paginator = Paginator(note_list, 20)
    page_num = request.GET.get('page', 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './superuser/student_note_search.html', context)


def T_Get_School_Note(request, xq):
    context = {}
    note = School_Note_table.objects.filter(xq=xq)
    paginator = Paginator(note, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/school_note.html', context)


def Get_School_to_teacher_note(request, xq):
    context = {}
    note = Teacher_Note_table.objects.filter(xq=xq)
    paginator = Paginator(note, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/teacher_note.html', context)


def T_Get_School_Note_Search(request, xq, content):
    context = {}
    note = School_Note_table.objects.filter(xq=xq) \
        .filter(Q(content__contains=content))
    paginator = Paginator(note, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range

    return render(request, './teacher/school_note_search.html', context)


def Get_School_to_teacher_note_Search(request, xq, content):
    context = {}
    note = Teacher_Note_table.objects.filter(xq=xq).filter(Q(content__contains=content))
    paginator = Paginator(note, 20)
    page_num = request.GET.get("page", 1)
    page_of_list = paginator.get_page(page_num)
    current_page_num = page_of_list.number

    page_range = list(range(max(current_page_num - 2, 1), current_page_num)) + \
                 list(range(current_page_num, min(current_page_num + 2, paginator.num_pages) + 1))

    if page_range[0] - 1 >= 2:
        page_range.insert(0, '...')
    if paginator.num_pages - page_range[-1] >= 2:
        page_range.append('...')

    if page_range[0] != 1:
        page_range.insert(0, 1)
    if page_range[-1] != paginator.num_pages:
        page_range.append(paginator.num_pages)

    context['page_of_list'] = page_of_list
    context['page_range'] = page_range
    return render(request, './teacher/teacher_note_serach.html', context)



