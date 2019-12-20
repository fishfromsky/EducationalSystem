'''
批量向数据库中插入数据
'''
import pymysql
import random


def Mysql(conn):

    cur = conn.cursor()
    cur.execute("select xh from school_stu_table")
    result = cur.fetchall()
    numberlist = []
    for data in result:
        numberlist.append(data[0])

    lessonlist = []
    cur.execute("select gh_id,kh_id,xq from school_open_lesson")
    result1 = cur.fetchall()
    for data in result1:
        lessonlist.append(list(data))

    return numberlist, lessonlist


def Insert(conn, numberlist, lessonlist):
    number_length = len(numberlist)
    lesson_length = len(lessonlist)
    combineList = []
    pscjList = [80, 90, 95, 87, 89, 78, 59, 49, 55, 99, 97]
    cs1 = conn.cursor()
    for i in range(400):
        if i % 50 == 0:
            print(i)
        index = random.randint(0, len(pscjList) - 1)
        query = "insert into school_option_lesson(xh_id,xq,kh_id,gh_id,pscj,kscj,zpcj) values (%s,%s,%s,%s,%s,%s,%s);"
        index_number = random.randint(0, number_length-1)
        index_lesson = random.randint(0, lesson_length-1)
        if [index_number, index_lesson] not in combineList:
            combineList.append([index_number, index_lesson])
            xh_id = numberlist[index_number]
            xq = lessonlist[index_lesson][2]
            kh_id = lessonlist[index_lesson][1]
            gh_id = lessonlist[index_lesson][0]
            pscj = pscjList[index]
            kscj = pscjList[index]
            zpcj = pscjList[index]
            values = (xh_id, xq, kh_id, gh_id, pscj, kscj, zpcj)
            cs1.execute(query, values)
    conn.commit()
    cs1.close()
    conn.close()


if __name__ == '__main__':
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='123456',
        db='school1'
    )
    numbers, lessons = Mysql(conn)
    Insert(conn, numbers, lessons)

