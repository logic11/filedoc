from flask import Blueprint
from utilities import setCount
from settings import siteSettings
from flask import request, jsonify, session
from pathlib import Path
from os import listdir, remove, mkdir
from os.path import exists

notes_api = Blueprint('notes_api', __name__)
userName=siteSettings()
@notes_api.route("/notes/getMyNotes")
def getMyNotes():
    returnString="<a hx-get='/remElement' hx-trigger='load' hx-target='#sub_nav'></a><h1>My Notes</h1><button hx-get='addNote' hx-target='#noteContentArea'>+</button><div id='noteContentArea'>"
    fileList = listdir('../notes/'+userName+'/')
    returnString+='<ul>'
    for file in fileList:
        fileContent=Path('../notes/'+userName+'/'+file).read_text()
        returnString+='<li><a hx-get="/notes/getNote/'+file.replace(".html","")+'" hx-target="#noteContentArea">'+fileContent[fileContent.find("<h2 id='noteTitle'>")+19:fileContent.find("</h2>")]+'</a></li>'
    returnString+='</ul></div>'
    return returnString

@notes_api.route("/notes/getNote/<noteId>")
def getNote(noteId):
    return Path("../notes/"+userName+"/"+noteId+".html").read_text().replace("<div name='noteContent' id='noteContent'>","<pre><div name='noteContent' id='noteContent'>").replace("</div>","</div></pre>")

@notes_api.route("/notes/editNote/<noteId>")
def editNote(noteId):
    noteContent=Path("../notes/"+userName+"/"+noteId+".html").read_text().replace("<div id='"+noteId+"Content'","<form hx-get='/notes/saveNote/"+noteId+"'").replace("<h2 id='noteTitle'>", "<input type='text' name='noteTitle' value='").replace("</h2>","'>").replace("<div name='noteContent'","<textarea rows='40' name='noteContent'").replace("</div>","</textarea>").replace("</div>","</form>").replace("editNote","saveNote").replace("Edit Note","Save Note").replace("hx-get","hx-post")
    return noteContent

@notes_api.route("/notes/saveNote/<noteId>", methods=['POST'])
def saveNote(noteId):
    noteTitle=request.form.get('noteTitle')
    noteContent=request.form.get('noteContent')
    return ""

@notes_api.route("/notes/addNote")
def addNote():
    return Path("../notes/noteForm.html").read_text()
    
@notes_api.route("/notes/createNote",methods=['POST'])
def createNote():
    noteTitle=request.form.get('noteTitle')
    count=len(listdir('../notes/'+userName+'/'))+1
    noteContent=request.form.get('noteContent')
    while exists('../notes/'+userName+'/n'+setCount(count)+'.html'):
        count+=1
    count=setCount(count)
    file='../notes/'+userName+'/n'+count+'.html'
    string="<div id='n"+count+"Content'>\n\t<h2 id='noteTitle'>"+noteTitle+"</h2>\n\t<div name='noteContent' id='noteContent'>\n"+noteContent+"</div>\n\t<button hx-get='/notes/editNote/n"+count+"' hx-target='#n"+count+"Content'>Edit Note</button> <button hx-target='#noteContentArea' hx-delete='/notes/deleteNote/n"+count+"'>Delete Note</button>\n\t</div>"
    with open(file,'w') as f:
        f.write(string)
    data=Path(file).read_text()
    return data

@notes_api.route("/notes/deleteNote/<noteId>",methods=['DELETE'])
def deleteNote(noteId):
    file='../notes/'+userName+'/'+noteId+'.html'
    remove(file)
    return ""