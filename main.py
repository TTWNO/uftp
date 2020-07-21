from flask import Flask, render_template, send_file, redirect, request
from werkzeug.utils import secure_filename
from werkzeug.routing import PathConverter

from os import listdir
from os.path import isfile, join

import os
import sys

app = Flask(__name__)

ROOT_FTP_DIR = '.'

class EverythingConverter(PathConverter):
    regex = '.*?'

app.url_map.converters['everything'] = EverythingConverter

def make_file_listing_dict(dirname):
    files = listdir(dirname)
    types = list(map(lambda f: "f" if isfile(join(dirname, f)) else "d", files))
    return dict(zip(files, types))

@app.route('/')
def test():
    return redirect('/show/')

@app.route('/show/<everything:dire>')
def get_dir(dire):
    # set path to ROOT_FTP_DIR if no path specified
    dire = ROOT_FTP_DIR if dire == '' else join(ROOT_FTP_DIR, dire)
    zipped_files = make_file_listing_dict(dire)
    
    return render_template('list.html', files=zipped_files, root=f'{dire}')

@app.route('/download/<everything:fname>')
def download_file(fname):
    return send_file(fname)

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        directory = request.form.get('dir')
        filename = secure_filename(file.filename)
        file.save(join(ROOT_FTP_DIR, directory, filename))
        return redirect('show/' + directory)
    else:
        return "NO GET ALLOWED FOR UPLOAD"

@app.route('/delete', methods=['POST'])
def delete_file():
    if request.method == 'POST':
        dire = request.form.get('directory')
        dirorfile = request.form.get('filename')
        deltype = request.form.get('type')
        fullp = join(ROOT_FTP_DIR, dire, dirorfile)
        if deltype == 'file':
            os.remove(fullp)
        elif deltype == 'directory':
            os.rmdir(fullp)
        return redirect('show/' + request.form.get('directory'))
