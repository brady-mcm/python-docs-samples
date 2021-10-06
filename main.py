# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START gae_python38_app]
# [START gae_python3_app]
from flask import Flask, request, redirect
import os, json
from google.cloud import datastore
from datetime import datetime

dataclient = datastore.Client()
# If `entrypoint` is not defined in app.yaml, App Engine will look for an app
# called `app` in `main.py`.
app = Flask(__name__)

@app.route('/')
def hello():
    addVisitor()
    ent = dataclient.key('data', 'posts')
    posts = dataclient.get(key=ent)
    article = ""
    with open('article.html', 'r') as page:
        article = page.read()
        html =""
    if posts:
        for post in posts['posts']:
            array = json.loads(post)
            raw = article.replace("!content!", array[0])
            raw = raw.replace("!title!", array[1])
            raw = raw.replace("!time!", array[2])
            html += raw
        with open('main.html', 'r') as page:
            main = page.read()
        return main.replace("!articles!", html)
    else:
        return 'No Posts! Go to /editor and make your first post!'

@app.route('/version')
def versA():
    addVisitor()
    return 'This is app version B!'

@app.route('/instance')
def getid():
    addVisitor()
    instanceid = os.getenv('GAE_INSTANCE')
    return str(instanceid)

@app.route('/version-id')
def getversionid():
    addVisitor()
    versionid = os.getenv('GAE_VERSION')
    return str(versionid)

def addVisitor():
    ent = dataclient.key('data', 'visitors')
    total = dataclient.get(key=ent)
    if total:
        total['total'] +=1
        dataclient.put(total)
    else:
        total = datastore.Entity(key=ent)
        total['total'] = 0
        dataclient.put(total)

@app.route('/visitors')
def getVisitor():
    addVisitor()
    ent = dataclient.key('data','visitors')
    total = dataclient.get(key=ent)
    if total:
        return 'Total visitors: ' + str(total['total'])
    else:
        return 'Total Broke!'

@app.route('/editor')
def edit_page():
    addVisitor()
    with open('editor.html', 'r') as page:
        return page.read()

@app.route('/submit', methods = ['POST'])
def submit_post():
    addVisitor()
    password = request.form['pass']
    if password == "P@ssW0rd!":
        content = request.form['content']
        title = request.form['title']
        time = str(datetime.utcnow())
        post = json.dumps([content, title, time])
        ent = dataclient.key('data', 'posts')
        posts = dataclient.get(key=ent)
        if posts:
            posts['posts'] = [post] + posts['posts']
            dataclient.put(posts)
        else:
            posts = datastore.Entity(key=ent)
            posts['posts'] = [post]
            dataclient.put(posts)
        return redirect('/')    
    else:
        return redirect('/')    

if __name__ == '__main__':
    # This is used when running locally only. When deploying to Google App
    # Engine, a webserver process such as Gunicorn will serve the app. This
    # can be configured by adding an `entrypoint` to app.yaml.
    app.run(host='127.0.0.1', port=8080, debug=True)
# [END gae_python3_app]
# [END gae_python38_app]
