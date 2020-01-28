from django.db import models
from django.core.validators import MaxValueValidator, MinValueValidator


class School(models.Model):
    yxh = models.CharField(max_length=10, primary_key=True)
    mc = models.CharField(max_length=50)
    dz = models.CharField(max_length=50, null=True)
    lxdh = models.CharField(max_length=20, null=True)

    def __str__(self):
        return self.yxh


class Stu_table(models.Model):
    xh = models.CharField(max_length=10, primary_key=True)
    xm = models.CharField(max_length=30)
    xb = models.CharField(max_length=10, null=True)
    csrq = models.DateField(null=True)
    jg = models.CharField(max_length=30, null=True)
    sjhm = models.CharField(max_length=30, null=True)
    yxh = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.xh


class Teacher(models.Model):
    gh = models.CharField(max_length=10, primary_key=True)
    xm = models.CharField(max_length=20)
    xb = models.CharField(max_length=10, null=True)
    csrq = models.DateField(null=True)
    xl = models.CharField(max_length=20, null=True)
    jbgz = models.DecimalField(max_digits=6, decimal_places=2, null=True)
    yxh = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return self.gh


class Teacher_Login(models.Model):
    gh = models.ForeignKey(Teacher, on_delete=True, primary_key=True)
    xm = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    yxh = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return Teacher.objects.get(gh=self.gh).gh


class Student_Login(models.Model):
    xh = models.ForeignKey(Stu_table, on_delete=models.CASCADE, primary_key=True)
    xm = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    yxh = models.ForeignKey(School, on_delete=models.CASCADE)

    def __str__(self):
        return Stu_table.objects.get(xh=self.xh).xh


class Supersuser(models.Model):
    number = models.CharField(max_length=50, primary_key=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)

    def __str__(self):
        return self.number


class Lesson(models.Model):
    kh = models.CharField(max_length=10, primary_key=True)
    km = models.CharField(max_length=50)
    xf = models.SmallIntegerField(default=4)
    xs = models.SmallIntegerField(default=40)
    yxh = models.ForeignKey(School, on_delete=models.CASCADE)
    rule_ps = models.PositiveSmallIntegerField(default=3)
    rule_ks = models.PositiveSmallIntegerField(default=7)

    def __str__(self):
        return self.kh


class Open_lesson(models.Model):
    xq = models.CharField(max_length=50)
    sksj = models.CharField(max_length=50)
    kh = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    gh = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    class Meta:
        index_together = ["xq", "kh", "gh"]

    def __str__(self):
        return self.xq


class Option_lesson(models.Model):
    xh = models.ForeignKey(Stu_table, on_delete=models.CASCADE)
    xq = models.CharField(max_length=50)
    kh = models.ForeignKey(Lesson, on_delete=models.CASCADE)
    gh = models.ForeignKey(Teacher, on_delete=models.CASCADE)
    pscj = models.SmallIntegerField(null=True, validators=[MaxValueValidator(100), MinValueValidator(1)])
    kscj = models.SmallIntegerField(null=True, validators=[MaxValueValidator(100), MinValueValidator(1)])
    zpcj = models.SmallIntegerField(null=True, validators=[MaxValueValidator(100), MinValueValidator(1)])
    class Meta:
        index_together = ["xh", "xq", "kh", "gh"]


class present_semester(models.Model):
    xq = models.CharField(max_length=50)
    xk = models.CharField(max_length=5)
    dqxq = models.CharField(max_length=5)
    cjxq_ps = models.CharField(max_length=5, default='0')
    cjxq_ks = models.CharField(max_length=5, default='0')


