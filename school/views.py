from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import Stu_table, School, Teacher, Lesson, Open_lesson, Option_lesson, \
    Student_Login, Teacher_Login, Supersuser, present_semester
from django.core.paginator import Paginator
from django.urls import reverse
from django.views.decorators.http import require_http_methods
import json
from django.core import serializers
from django.db import connection


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
    stu_count = Option_lesson.objects.filter(xq=semester).values('xh_id').distinct().count()
    teacher_count = Open_lesson.objects.filter(xq=semester).values('gh_id').distinct().count()
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
    return render(request, './teacher/t_index.html', {})


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
        if status == '1':
            response['status'] = 1
            response['semester'] = semester
            response['message'] = 'success'
            response['code'] = 0
        else:
            response['status'] = 0
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
    response['message'] = 'suucess'
    response['code'] = 0
    return JsonResponse(response)
