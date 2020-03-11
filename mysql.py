'''
批量向数据库中插入数据
'''
import pymysql
import random


def Insert(conn):
    cs1 = conn.cursor()
    query = "select id from school_option_lesson"
    cs1.execute(query)
    result = list(cs1.fetchall())
    for i in range(0, len(result)-1):
        number = result[i][0]
        cs1.execute("select zpcj from school_option_lesson where id=%d;" % number)
        num = cs1.fetchall()[0][0]
        if num is not None:
            if num < 60:
                credit = 0.0
            elif 60 <= num <= 63:
                credit = 1.3
            elif 64 <= num <= 67:
                credit = 1.5
            elif 68 <= num <= 71:
                credit = 2.0
            elif 72 <= num <= 74:
                credit = 2.3
            elif 75 <= num <= 77:
                credit = 2.7
            elif 77 <= num <= 81:
                credit = 3.0
            elif 82 <= num <= 84:
                credit = 3.3
            elif 85 <= num <= 89:
                credit = 3.7
            else:
                credit = 4.0
            cs1.execute("update school_option_lesson set credit=%f where id=%d" % (credit, number))
    conn.commit()
    cs1.close()
    conn.close()


if __name__ == '__main__':
    conn = pymysql.connect(
        host='127.0.0.1',
        port=3306,
        user='root',
        passwd='godj123!@#',
        db='school1'
    )
    Insert(conn)

