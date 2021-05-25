from datetime import datetime
from flask import Flask, render_template, jsonify
import tempfile
import time
import os
import subprocess

app = Flask(__name__)    # Create an instance of the class for our use


@app.route("/")
def home():
    return render_template("home.html")


@app.route("/about/")
def about():
    return render_template("about.html")


@app.route("/contact/")
def contact():
    return render_template("contact.html")


@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name=None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )


@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")


@app.route("/api/fill/<size>")
def fill(size=None):
    temp_name = next(tempfile._get_candidate_names())
    start_time = time.time()
    bs = os.environ['BS']
    output_dir = os.environ['OUTPUT_DIRECTORY']
    os.makedirs(output_dir, exist_ok=True)

    data = {'count': size, 'bs': bs,
            'output': f'{output_dir}/{temp_name}', 'input': '/dev/urandom'}

    command = f"dd if={data['input']} bs={data['bs']} count={data['count']} of={data['output']}"
    print(command)
    data['command'] = command
    stdout = run_dd(command)
    elapsed_time = time.time() - start_time
    data['elapsed_time'] = elapsed_time
    data['stdout'] = str(stdout)

    return jsonify(data)


def run_dd(cmd):
    #dd = Popen(cmd.split(' '), stderr=PIPE)
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return err
