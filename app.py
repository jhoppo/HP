from flask import Flask, request, jsonify, redirect, url_for, render_template, abort
import os
from werkzeug.utils import secure_filename

def SelectionSort(ls,nums, orderByDirection='Ascending'):
    for i in range(len(nums)):
        limit_ind = i
        for j in range(i+1, len(nums)):
            if orderByDirection == 'Ascending':
                if nums[j] < nums[limit_ind]: limit_ind = j
            elif orderByDirection == 'Descending':
                if nums[j] > nums[limit_ind]: limit_ind = j
            else:
                return False

        nums[i], nums[limit_ind] = nums[limit_ind], nums[i]
        ls[i], ls[limit_ind] = ls[limit_ind], ls[i]
    return ls



UPLOAD_FOLDER = './file'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.route('/')
def index():
    return 'index'

@app.route('/file/<path:localSystemFilePath>', methods=['GET','POST', 'PATCH', 'DELETE'])
def watchPath(localSystemFilePath=''):
    def uploadFile(method):
        if request.method == 'DELETE':
            f = request.form['file']
            fPath = os.path.join(reqPath, f)
            try:
                os.remove(fPath)
                return 'File Deleted'
            except:
                return 'File Not Found'
        else:
            if not os.path.exists(reqPath) :
                os.makedirs(reqPath)
                if request.files == {}:
                    return "Folder Created"
            f = request.files['file']
            fn = secure_filename(f.filename)
            fPath = os.path.join(reqPath, fn)
            if method == 'POST':
                if os.path.isfile(fPath):
                    return "File existed"
                else:
                    f.save(fPath)
                return 'File Uploaded'
            elif method == 'PATCH':
                f.save(fPath)
                return 'File up to dated'

    reqPath = f"/{localSystemFilePath}"
    if request.method == 'GET':
        if os.path.isfile(reqPath):
            with open(reqPath, 'rb') as f:
                data = f.read()
            return data
        elif os.path.isdir(reqPath):
            orderBy=request.args.get('orderBy')
            orderByDirection=request.args.get('orderByDirection')
            filterByName=request.args.get('filterByName')
            ls = [i if os.path.isfile(f"{reqPath}/{i}") else f"{i}/" for i in os.listdir(reqPath)]
            # filter name
            if filterByName != None:
                lsFiltered = []
                for i in ls:
                    if filterByName in i:
                        lsFiltered.append(i)
                ls = lsFiltered
            # orderBy
            if orderBy == 'lastModified':
                seq = [ os.stat(f"{reqPath}/{i}").st_mtime for i in ls ]
            elif orderBy == 'size':
                seq = [ os.stat(f"{reqPath}/{i}").st_size for i in ls ]
            else:
                seq = [i for i in ls]
            # order Direction
            if orderByDirection == None:
                orderByDirection = 'Ascending'
            lsSorted = SelectionSort(ls=ls,nums=seq,orderByDirection=orderByDirection)

            data = {"isDirectory": 'true',
                    "files": lsSorted
                    }
            return data
        else:
            abort(404)
    else:
        return uploadFile(method=request.method)

if __name__ == "__main__":
    app.run('0.0.0.0', debug=True)
