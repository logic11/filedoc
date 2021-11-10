from settings import siteSettings
import json
import secrets
import utilities
from flask import Flask, request, jsonify, session
from pathlib import Path
from os import listdir, remove, mkdir
from os.path import exists
from builtins import bytes
from NotesApi import notes_api
from TasksApi import tasks_api
import bcrypt

app = Flask(__name__, static_url_path='/static')

app.register_blueprint(notes_api)
app.register_blueprint(tasks_api)

app.secret_key=secrets.token_urlsafe(16)
userName=siteSettings()

@app.route("/")
def docsIndex():
    return Path('../index.html').read_text()
    
@app.route("/navbar")
def navbar():
    """ Returns a string
    
    Takes the list of apps in this project and builds a navbar out of them. Also adds the team and generic options (generics are the admin menu, the tasklist and the personal notes menu
    """
    navitems="<ul class='navbar'>\n\t<li><a hx-trigger='click' hx-get='/appName/team/index' hx-target='#content_area' hx-push-url='true'>Team</a></li>"
    apps=Path("./apps.txt").read_text().split(":")
    for app in apps:
        app=app.split("-")
        navitems+="\n\t<li><a hx-trigger='click' hx-get='/appName/"+app[0]+"/index' hx-target='#content_area' hx-push-url='true'>"+app[1]+"</a></li>"
    if 'loggedIn' in session:
        if session['loggedIn']:
            navitems+="\n\t<li><a hx-get='/getMyTasks' hx-target='#content_area' hx-trigger='click' hx-push-url='true'>Tasks</a></li>\n\t<li><a hx-get='/notes/getMyNotes' hx-trigger='click' hx-target='#content_area' hx-push-url='true'>My Notes</a></li>"
    navitems+="\n\t<li><a hx-get='/admin' hx-target='#content_area' hx-trigger='click' hx-push-url='true'>Admin</a></li>\n</ul>"
    return navitems

@app.route("/remElement")
def remElement():
    """ Returns a blank element.
    
    Useful for things like clearing navbars
    """
    return ""
    
@app.route("/appName/<appName>/<page>")
def appIndex(appName, page):
    """Returns a string
    
    Gets the content of a single page in an app document and serves it to the browser
    """
    return Path('../'+appName+'/'+page+'.html').read_text()
    
@app.route("/getChrome/<appName>")
def getChrome(appName):
    """Returns a string
    
    Gets the navbar for the current app and serves it.
    """
    if appName=="null":
        return ""
    return Path('../chrome/'+appName+'/navbar.html').read_text()

@app.route("/admin")
def admin():
    if exists('./pass'):
        if 'loggedIn' in session:
            if session['loggedIn']:
                return Path('../admin/index.html').read_text()
            else:
                return Path("../admin/loginForm.html").read_text()
        else:
            session['loggedIn']=False
            return Path("../admin/loginForm.html").read_text()
    else:
        return Path("../admin/setupForm.html").read_text()

@app.route("/admin/addApp")
def addApp():
    if 'loggedIn' in session:
        if session['loggedIn']:
            return Path("../admin/addAppForm.html").read_text()
    return "Authorization Needed"
    
@app.route("/admin/createApp", methods=['POST'])
def createApp():
    if 'loggedIn' in session:
        if session['loggedIn']:
            appName=[request.form.get('appName'),request.form.get('displayName')]
            #Add app to the apps list
            appsList=Path("./apps.txt").read_text()
            appsList+=":"+appName[0]+'-'+appName[1]
            with open("apps.txt",'w') as f:
                f.write(appsList)
            #Create the app pages
            mkdir("../"+appName[0])
            fileList=[['index',appName[1]+" Home"],['issues','Issues'],['interface','Interface'],['servers','Servers'],['db','Database'],['sla','SLA'],['contact','Contact'],['notes','Notes']]
            start=True
            for file in fileList:
                with open("../"+appName[0]+"/"+file[0]+".html", 'w') as f:
                    if start:
                        f.write("<h1 hx-get='/getChrome/"+appName[0]+"' hx-trigger='load' hx-target='#sub_nav'>"+file[1]+"</h1>\n<h2>Introduction</h2>")
                    else:
                        f.write("<h1>"+file[1]+"</h1>")
                start=False
            #Create the default app Nav
            mkdir("../chrome/"+appName[0])
            with open("../chrome/"+appName[0]+"/navbar.html", 'w') as f:
                f.write("""
<ul class="navbar">
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/index" hx-target="#content_area" hx-push-url="true">"""+appName[1]+""" Home</a></li>
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/issues" hx-target="#content_area" hx-push-url="true">Common issues</a></li>
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/interface" hx-target="#content_area" hx-push-url="true">Interfaces</a></li>
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/servers" hx-target="#content_area" hx-push-url="true">Servers</a></li>
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/db" hx-target="#content_area" hx-push-url="true">Databases</a></li>
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/sla" hx-target="#content_area" hx-push-url="true">SLA</a></li>
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/contact" hx-target="#content_area" hx-push-url="true">Contact</a></li>
	<li><a hx-trigger="click" hx-get="/appName/"""+appName[0]+"""/notes" hx-target="#content_area" hx-push-url="true">Notes</a></li>
</ul>
                """)
            return "<a hx-get='/navbar' target='#navBar'></a>Created "+appName[1]
    return "Authorization Needed"

@app.route("/logOut")
def logOut():
    if 'loggedIn' in session:
        if session['loggedIn']:
            session['loggedIn']=False
    return '<span hx-get="/navbar" hx-trigger="load"></span>'
    
@app.route("/setup", methods=['POST'])
def setup():
    if exists('./pass'):
        return "Setup has already been completed"
    salt = bcrypt.gensalt()
    passString=bcrypt.hashpw(request.form.get('passwd').encode(),salt)
    file='./pass'
    with open(file,'wb') as f:
        f.write(passString)
    return "Setup Complete"
        
@app.route("/login", methods=['POST'])
def login():
    storePass=Path("./pass").read_text().encode()
    salt = bcrypt.gensalt()
    myPass=request.form.get('password').encode()
    if bcrypt.checkpw(myPass,storePass) and request.form.get('username')== userName:
        session['loggedIn']=True
        return Path('../admin/index.html').read_text()
    else:
        session['loggedIn']=False
        return "Authentication Error"