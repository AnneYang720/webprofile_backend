from flask import Flask,request
import megengine.tools.load_network_and_run
import tempfile
import shutil
import subprocess

if __name__ == "__main__":
    mge = tempfile.NamedTemporaryFile(delete=False)
    mge.close()
    shutil.copyfile('../demo/resnet50.mge',mge.name)
    print("mge ")
    print(mge.name)

    data = tempfile.NamedTemporaryFile(delete=False)
    data.close()
    shutil.copyfile('../demo/resnet50.pickle',data.name)

    p = subprocess.Popen('python -m megengine.tools.load_network_and_run '+ mge.name+' --load-input-data '+data.name+' --profile profile.txt --iter 5', stdout=subprocess.PIPE, shell=True)


