# -*- coding: utf-8 -*-

import os
from flask import (
        Blueprint, flash, request, redirect, render_template, url_for
)
from werkzeug.utils import secure_filename

import librosa
import librosa.display
import scipy
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

bp = Blueprint("freqspec_builder", __name__)

GRAPH_FOLDER = "static/freqspec_graphs"
UPLOAD_FOLDER = "app/user_sounds"
ALLOWED_EXTENSIONS = {"mp3", "wav"}

def allowed_file(filename):
    return '.' in filename and \
filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def freqspec_graph(audio_path, save_path, dpi=80, width=1000, height=500):
    audio, sampling_rate = librosa.load(audio_path)
    n = len(audio)
    yf = 2/n * np.abs(scipy.fft.fft(audio)[:n//2])
    xf = np.array([k*sampling_rate/n for k in range(n//2)])
    fig, ax = plt.subplots(figsize=(width/dpi, height/dpi), dpi=dpi)
    ax.plot(xf, yf)
    plt.grid()
    plt.title("The highest magnitude({:.2f}) is reached at {:.0f}Hz frequency".format(
        np.max(yf), np.argmax(yf)*sampling_rate/n))
    plt.xlabel("Frequency(Hz)")
    plt.ylabel("Magnitude")
    plt.savefig(save_path, dpi=dpi)

@bp.route("/", methods=("GET", "POST"))
def freqspec_builder():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            flash('No file part')
            return redirect(request.url)
        
        file = request.files['file']
        
        # if user does not select file, browser also
        # submit an empty part without filename
        if file.filename == '':
            flash('No selected file')
            return redirect(request.url)
        
        if not allowed_file(file.filename):
            flash(
                'Unsupported extencion. The only supported extencions are ".mp3", ".wav".'
            )
            return redirect(request.url)
        
        if file:
            filename = secure_filename(file.filename)
            filepath = UPLOAD_FOLDER+"/"+filename
            file.save(filepath)
            graphpath = GRAPH_FOLDER+"/"+filename.rsplit('.', 1)[0]+\
                str(np.random.randint(99))+".png"
            freqspec_graph(filepath, "app/"+graphpath)
            os.remove(filepath)
            return render_template("result.html", 
                                   file_name=filename, 
                                   graph_path=graphpath)
    
    #size control of freqspec_graphs folder
    freqspec_graphs_files = [f for f in os.listdir("app/"+GRAPH_FOLDER) \
                             if os.path.isfile("app/"+GRAPH_FOLDER+"/"+f)]
    freqspec_graphs_size = sum(os.path.getsize("app/"+GRAPH_FOLDER+"/"+f) \
                               for f in freqspec_graphs_files)
    if freqspec_graphs_size/1e+6 >= 200:
        for f in freqspec_graphs_files:
            os.remove("app/"+GRAPH_FOLDER+"/"+f)
        
    return render_template("upload.html")