# {%ONLY POST%}
import pymysql
import sys

from CgiTool.ArgTool import ArgCgi


class QueryCgi(ArgCgi):
    def handle(self) -> None:
        try:
            cnx = pymysql.connect(user='root', password='Abcde12345', host='localhost', database='sim_http_test')
        except:
            self.add_output('result', f'数据库连接失败！')
            return
        try:
            input_id = int(self['input_id'])
        except ValueError as e:
            result_text = '错误的id格式！'
        else:
            cursor = cnx.cursor()
            query = f"SELECT * FROM student WHERE id={input_id}"
            cursor.execute(query)

            result = cursor.fetchall()
            if result:
                result_stu = result[0]
                result_text = f'查询成功!<br>学号：{result_stu[0]}<br>姓名：{result_stu[1]}<br>班级：{result_stu[2]}'
            else:
                result_text = f'未查询到该学生。'
            # 关闭连接
            cursor.close()
        cnx.close()
        self.add_output('result', result_text)


if __name__ == '__main__':
    QueryCgi(sys.argv).run()
