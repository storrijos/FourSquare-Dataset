from flask import Flask, render_template, redirect, flash, request, url_for, jsonify
import random

from flask_bootstrap import Bootstrap
import tablib
from flask_util_js import FlaskUtilJs
import json

import os
from werkzeug.utils import secure_filename
import pandas as pd
from src.Map.traj_plot import plot_k_trajs_web
from src.Processing.pre_process import ProcessData

app = Flask(__name__)
Bootstrap(app)
fujs = FlaskUtilJs(app)

files_tag = {}
users_colors = {}

UPLOAD_FOLDER = '/tmp'
ALLOWED_EXTENSIONS = {'txt', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_fujs():
    return dict(fujs=fujs)

def get_random_hex():
    random_number = random.randint(0, 16777215)
    # convert to hexadecimal
    hex_number = str(hex(random_number))
    # remove 0x and prepend '#'
    return '#' + hex_number[2:]

def assign_user_color(users):
    for user in users:
        users_colors[str(user)] = get_random_hex()

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:neighbor_id>')
def index(neighbor_id=None):
    if request.method == 'POST':
        tag = request.form['tag']
        files = request.files.getlist('input-b3[]')
        if len(files) > 0:
            if files[0].filename == '':
                flash('No selected file')
                return redirect(request.url)

            if files and allowed_file(files[0].filename):

                tag = request.form['tag']
                files_uploaded = {}

                similarity = None
                for file in files:
                    old_name = ""
                    filename = secure_filename(file.filename)
                    filename_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                    #file.save(filename_path)
                    file.save(os.path.join(app.config['UPLOAD_FOLDER'], file.filename))

                    ###Read number of columns
                    infile = open(filename_path, 'r')
                    firstLine = infile.readline()
                    number_of_columns = len(firstLine.split())

                    if number_of_columns == 3:
                        files_uploaded['similarity'] = filename_path
                        if not tag:
                            tag = filename_path
                    elif number_of_columns == 5:
                        files_uploaded['dataset'] = filename_path
                        old_name = filename
                    else:
                        files_uploaded['trajs'] = filename_path


                if 'dataset' in files_uploaded and 'trajs' not in files_uploaded:
                    new_name = str(files_uploaded['dataset'][:-4]) + "trajs.txt"
                    print(new_name)
                    if not os.path.exists(new_name):
                        out = ProcessData.loadAndCleanDataset(files_uploaded['dataset'], new_name)
                        print(out)
                        files_uploaded['trajs'] =  new_name
                    else:
                        files_uploaded['trajs'] =  new_name

                        #files_tag[tag]['trajs'] = new_name

                files_tag[tag] = files_uploaded
        print(tag)
        if tag in files_tag:
            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], files_tag[tag]['similarity']), delim_whitespace=True, header=None)
            df.columns = ["user_id", "neighbor_id", "similarity"]

            users = df['user_id'].unique()
            assign_user_color(users)

            neighbors = df[df['user_id'] == neighbor_id][["neighbor_id", "similarity"]].reset_index()

            neighbors2 = str(df.to_json(orient='records'))
            return render_template('index.html', users=users, neighbors=neighbors, neighbors_json=neighbors2, files=list(files_tag.keys()), users_colors=users_colors, tag= tag)

    return render_template('index.html')

@app.route('/map/<tag>/<int:user_id>/<int:k>', methods=['GET', 'POST'])
def map(tag, user_id, k):
    if request.method == 'POST':

        neighbors = request.json
        output_url = 'map' + str(user_id) + str(k) + '.html'

        print(files_tag)
        print(tag)

        trajs = plot_k_trajs_web(user_id, files_tag[tag]['trajs'], files_tag[tag]['similarity'], 'templates/maps/' + output_url, k, users_colors)
        return jsonify(neighbors)


@app.route('/traj/<mapa>')
def traj(mapa):
    return render_template('maps/' + str(mapa))

if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.debug = True

    app.run(debug=True)
