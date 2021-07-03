from flask import Flask #从flask包中导入Flask类
app = Flask(__name__)#将Flask类的实例 赋值给名为 app 的变量。这个实例成为app包的成员。



if __name__ == '__main__':
    app.run()
