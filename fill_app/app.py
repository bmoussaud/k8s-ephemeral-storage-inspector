from json2html import *
from flask import Flask
from datetime import datetime
from flask import Flask, render_template, jsonify, render_template_string
import tempfile
import time
import os
import subprocess
import pykube
import pprint

import operator
from kubernetes import config
from kubernetes.client import Configuration
from kubernetes.client.api import core_v1_api
from kubernetes.client.rest import ApiException
from kubernetes.stream import stream
from urllib.parse import urlencode


class VolumeManager:
    def __init__(self, config_file=None):
        print(
            f"----------------- LOAD  K8S_API {config_file} ----------------------")

        if config_file == 'K8S':
            print("k8s load_incluster_config")
            config.load_incluster_config()
            print("pykube from_service_account")
            self._api = pykube.HTTPClient(
                pykube.KubeConfig.from_service_account())
        else:
            print("load_external")
            config.load_kube_config(config_file=config_file)
            self._api = pykube.HTTPClient(
                pykube.KubeConfig.from_file(config_file))

        self._core_v1 = core_v1_api.CoreV1Api()

    def k8s_api(self):
        return self._api

    def run(self):

        pods_with_empty_dir_mounted_volumes = []

        running_pods = pykube.Pod.objects(self.k8s_api()).filter(
            namespace=pykube.query.all_,
            field_selector={"status.phase": "Running"}
        )

        for pod in running_pods:
            volumes = pod.obj['spec']['volumes']
            emptyDir = self._containsEmptyDir(volumes)
            if emptyDir is None:
                continue

            results = self.containers_using(
                pod.obj['spec']['containers'], emptyDir)
            for v in results:
                data = {'pod': pod.obj['metadata']['name'], 'container': v,
                        'path': results[v], 'namespace': pod.obj['metadata']['namespace'], 'nodeName': pod.obj['spec']['nodeName']}
                pods_with_empty_dir_mounted_volumes.append(data)

        # pprint.pprint(pods_with_empty_dir_mounted_volumes)
        for pod in pods_with_empty_dir_mounted_volumes:
            pod['command'] = "df -h {path}".format(**pod)
            pod['command_file'] = "ls -lh {path}".format(**pod)
            pod['kubectl'] = "kubectl exec {pod} -n {namespace} -- {command}".format(
                **pod)

        mesured_pods = self.execute(pods_with_empty_dir_mounted_volumes)
        pprint.pprint(mesured_pods)
        return mesured_pods

    def execute(self, pods):
        mesured_pods = []
        for pod in pods:
            data_storage = {'storage-Filesystem': 'NA', 'storage-1K-blocks': 'NA', 'storage-Used': 'NA',
                            'storage-Available': 'NA', 'storage-used_percent': 'NA', 'storage-mounted': 'NA', 'storage-ls': 'NA'}
            print("execute {pod}...{command}".format(**pod))

            # DF
            resp = stream(self._core_v1.connect_get_namespaced_pod_exec,
                          pod['pod'],
                          pod['namespace'],
                          command=pod['command'].split(),
                          stderr=True, stdin=False,
                          stdout=True, tty=False)
            print("Response: " + resp)
            data = resp.splitlines()
            if (len(data) > 0):
                print("Response: " + data[1])
                info = data[1].split()

                resp_ls = stream(self._core_v1.connect_get_namespaced_pod_exec,
                                 pod['pod'],
                                 pod['namespace'],
                                 command=pod['command_file'].split(),
                                 stderr=True, stdin=False,
                                 stdout=True, tty=False)
                data_storage = {'storage-Filesystem': info[0], 'storage-1K-blocks': info[1], 'storage-Used': info[2],
                                'storage-Available': info[3], 'storage-used_percent': info[4], 'storage-mounted': info[5], 'storage-ls': resp_ls.splitlines()}

            pod.update(data_storage)
            del pod['command']
            del pod['command_file']
            mesured_pods.append(pod)
        return mesured_pods

    def _containsEmptyDir(self, volumes):
        for volume in volumes:
            if 'emptyDir' in volume:
                return volume
        return None

    def containers_using(self, containers, volume):
        # print('containers_using')
        mountedVolumePaths = {}
        for container in containers:
            # pprint.pprint(containers)
            volumeMounts = container.get('volumeMounts', [])            
            for mountedVolume in volumeMounts:
                if mountedVolume['name'] == volume['name']:
                    # print(mountedVolume)
                    mountedVolumePaths[container['name']
                                       ] = mountedVolume['mountPath']
        return mountedVolumePaths


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

    data['stdout'] = str(stdout).splitlines()
    return jsonify(data)


@app.route("/api/df")
def dump(size=None):
    bs = os.environ['BS']
    output_dir = os.environ['OUTPUT_DIRECTORY']
    os.makedirs(output_dir, exist_ok=True)

    data = {'output_dir': output_dir}

    command = f"df -h {output_dir}"
    print(command)
    data['command'] = command
    stdout = run_df(command)

    data['stdout_df'] = str(stdout).splitlines()

    command = f"ls -lrth {output_dir}"
    print(command)
    data['command'] = command
    stdout = run_ls(command)

    data['stdout_ls'] = str(stdout).splitlines()
    return jsonify(data)


def run_dd(cmd):
    #dd = Popen(cmd.split(' '), stderr=PIPE)
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE,
                         stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return err


def run_df(cmd):
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return out


def run_ls(cmd):
    p = subprocess.Popen(cmd.split(' '), stdout=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return out


@app.route("/api/inspect")
def inspect():
    if os.environ['ENGINE'] == 'K8S':
        config_file = 'K8S'
    else:
        config_file = "kubeconfig-aws-front.yml"

    volumeManager = VolumeManager(config_file)
    data = volumeManager.run()
    return jsonify(data)


@app.route("/inspect")
def inspect_gui():
    if os.environ['ENGINE'] == 'K8S':
        config_file = 'K8S'
    else:
        config_file = "kubeconfig-aws-front.yml"

    volumeManager = VolumeManager(config_file)
    json_data = volumeManager.run()
    table = json2html.convert(json=json_data)
    # print(table)
    # return render_template_string(
    #    table
    # )
    return render_template(
        "inspect.html",
        table=table,
        date=datetime.now()
    )
