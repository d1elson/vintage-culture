from flask import Flask, Response, render_template, redirect, request, jsonify, session
from flask_cors import CORS
import requests
import random
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/go')
def go():
    return redirect(
        "https://open.spotify.com/intl-pt/album/0uj28c7dMMgO59Jzx84bSE?si=mdhMx9yVTrGLJfvNpC1EdQ"
    )


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
