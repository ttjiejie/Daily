from flask import Flask, request, render_template_string
import mysql.connector

app = Flask(__name__)

# 数据库配置
db_config = {
    'user': 'root',
    'password': '@TT12345yy..',
    'host': 'localhost',
    'database': 'test',
    'raise_on_warnings': True
}


# 登录页面
@app.route('/')
def login_page():
    html_template = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <title>示例——登录</title>
  </head>
  <body>
    <form action="./login" method="post">
      用户名：<input type="text" name="username" />
      密     码: <input type="password" name="password" />
      <input type="submit" value="登录" />
    </form>
    <br/>
    <!-- 
    <form action="./showtext" method="post">
      评     论：<input type="text" name="content" />
      <input type="submit" value="提交评论" />
    </form>
    <br/>
     -->
  </body>
</html>
    """
    return render_template_string(html_template)


# 处理登录请求
@app.route('/login', methods=['POST'])
def login():
    username = request.form.get('username')
    password = request.form.get('password')

    try:
        # 连接数据库
        conn = mysql.connector.connect(**db_config)
        cursor = conn.cursor()

        # 查询用户信息
        query = "SELECT * FROM users WHERE username = %s AND password = %s"
        cursor.execute(query, (username, password))
        user = cursor.fetchone()

        if user:
            success_template = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <title>登录成功</title>
    <meta http-equiv="pragma" content="no-cache">
    <meta http-equiv="cache-control" content="no-cache">
    <meta http-equiv="expires" content="0">    
    <meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
    <meta http-equiv="description" content="This is my page">
    <!--
    <link rel="stylesheet" type="text/css" href="styles.css">
    -->
  </head>

  <body>
       Login Success!<br/>
  </body>
</html>
            """
            return render_template_string(success_template)
        else:
            failure_template = """
<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 4.01 Transitional//EN">
<html>
  <head>
    <title>登录失败</title>
    <meta http-equiv="pragma" content="no-cache">
    <meta http-equiv="cache-control" content="no-cache">
    <meta http-equiv="expires" content="0">    
    <meta http-equiv="keywords" content="keyword1,keyword2,keyword3">
    <meta http-equiv="description" content="This is my page">
    <!--
    <link rel="stylesheet" type="text/css" href="styles.css">
    -->
  </head>

  <body>
        Login Error!<br/>
  </body>
</html>
            """
            return render_template_string(failure_template)

    except mysql.connector.Error as err:
        print(f"Error: {err}")
        return "Database error occurred"
    finally:
        if conn.is_connected():
            cursor.close()
            conn.close()


if __name__ == '__main__':
    app.run(debug=True)
