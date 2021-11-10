from flask import Blueprint
from utilities import setCount
from flask import request, jsonify, session
from settings import siteSettings
from pathlib import Path
from os import listdir, remove, mkdir
from os.path import exists

tasks_api = Blueprint('tasks_api', __name__)
userName=siteSettings()

@tasks_api.route("/getMyTasks")
def getTasks():
    """Returns a string
    
    Gets the list of tasks for the current user and serves them
    """
    returnString=Path('../tasks/index.html').read_text()
    fileList = listdir('../tasks/'+userName+'/')
    for file in fileList:
        returnString+=Path('../tasks/'+userName+'/'+file).read_text()
    return returnString

@tasks_api.route("/modTask/<taskName>")
def modTask(taskName):
    file='../tasks/'+userName+'/'+taskName+'.html'
    string = Path(file).read_text()
    if string.find("checked") == -1:
        string=string.replace('<input type="checkbox">','<input type="checkbox" checked>')
    else:
        string=string.replace('<input type="checkbox" checked>','<input type="checkbox">')
    with open(file,'w') as f:
        f.write(string)
    return string
    
@tasks_api.route("/addTask")
def addTask():
    return Path('../tasks/taskform.html').read_text()
    
@tasks_api.route("/saveTask", methods=['PUT','POST'])
def saveTask():
    taskName=request.form.get('taskName')
    count=len(listdir('../tasks/'+userName+'/'))+1
    while exists('../tasks/'+userName+'/c'+setCount(count)+'.html'):
        count+=1
    count=setCount(count)
    file='../tasks/'+userName+'/c'+count+'.html'
    string='<div id="pc'+count+'"><div class="taskContainer" id="c'+count+'" hx-get="/modTask/c'+count+'" hx-target="#pc'+count+'" hx-swap="outerHTML" hx-trigger="click"><input type="checkbox"> '+taskName+' </div><button hx-delete="/delTask/c'+count+'" hx-target="#pc'+count+'" >x</button></div>'
    with open(file,'w') as f:
        f.write(string)
    data=Path(file).read_text()
    return data
    
@tasks_api.route("/delTask/<taskName>", methods=['DELETE'])
def delTask(taskName):
    file='../tasks/'+userName+'/'+taskName+'.html'
    remove(file)
    return ""