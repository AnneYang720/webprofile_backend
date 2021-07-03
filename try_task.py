from flask import Flask,request
import megengine.tools.load_network_and_run
app = Flask(__name__)

@app.route('/')
def hello_world():
    return 'hello world'

@app.route('/task/create', methods=['POST'])
def task_create():
    uploaded_files = request.files.getlist("file[]")
    mge = uploaded_files[0]
    data = uploaded_files[1]
    return 



if __name__ == '__main__':
    app.run(host='127.0.0.1',port=5000,debug=True)