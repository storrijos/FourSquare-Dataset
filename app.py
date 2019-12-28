from flask import Flask, render_template, redirect, flash, request, url_for, jsonify

from flask_bootstrap import Bootstrap
import tablib
from flask_util_js import FlaskUtilJs

import os
from werkzeug.utils import secure_filename
import pandas as pd
from src.Map.traj_plot import plot_k_trajs_web

app = Flask(__name__)
Bootstrap(app)
fujs = FlaskUtilJs(app)

files_tag = {}

UPLOAD_FOLDER = '/tmp/'
ALLOWED_EXTENSIONS = {'txt', 'csv'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.context_processor
def inject_fujs():
    return dict(fujs=fujs)

@app.route('/', methods=['GET', 'POST'])
@app.route('/<int:neighbor_id>')
def index(neighbor_id=None):
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        #file = request.files['file']

        files = request.files.getlist("file")

        # if user does not select file, browser also
        # submit an empty part without filename
        if files[0].filename == '':
            flash('No selected file')
            return redirect(request.url)

        if files and allowed_file(files[0].filename):

            tag = request.form['tag']

            similarity = None
            for file in files:
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                files_tag.setdefault(tag, []).append(file.filename)
                if "similarity" in file.filename:
                    similarity = filename

            df = pd.read_csv(os.path.join(app.config['UPLOAD_FOLDER'], similarity), delim_whitespace=True, header=None)
            df.columns = ["user_id", "neighbor_id", "similarity"]

            users = df['user_id'].unique()
            neighbors = df[df['user_id'] == neighbor_id][["neighbor_id", "similarity"]].reset_index()

            neighbors2 = str(df.to_json(orient='records'))

            return render_template('index.html', users=users, neighbors=neighbors, neighbors_json=neighbors2, files=list(files_tag.keys()))

    return render_template('index.html')

@app.route('/map/<int:user_id>/<int:k>', methods=['GET', 'POST'])
def map(user_id, k):
    if request.method == 'POST':

        neighbors = request.json
        output_url = 'map' + str(user_id) + str(k) + '.html'

        trajs = plot_k_trajs_web(user_id, 'file4.txt', 'similarity_output_dtw.txt', 'templates/maps/' + output_url, k)
        return jsonify(neighbors)


@app.route('/traj/<mapa>')
def traj(mapa):
    return render_template('maps/' + str(mapa))

if __name__ == "__main__":
    app.run(debug=True)
