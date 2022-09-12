
# module imports
import json, threading, os, time
import tkinter as tk
from tkinter import ttk

# some neat utility functions

def dictAppend(addThis, toThis, overwrite=0):
    composite = {k:v for k,v in toThis.items()}
    
    existingKeys = toThis.keys()
    for key in addThis.keys():
        if key in existingKeys and overwrite == 0:
            continue
        toThis[key] = addThis[key]

def textGrab(textWidget):
    text = textWidget.get(1.0, 'end')[:-1]
    return text

def textClear(widget):
    widget.delete(1.0, 'end')

def textInsert(widget, insertion):
    widget.insert(1.0, insertion)

def textAppend(widget, appendage):
    widget.insert('end', appendage)

def cleanEdges(string):
    dirty = [" ","\t","\n"]
    while True:
        if len(string) == 0:
            return string
        if string[0] in dirty:
            string = string[1:]
        else:
            break
    while True:
        if len(string) == 0:
            return string
        if string[-1] in dirty:
            string = string[:-1]
        else:
            break
    return string

# setting colors
tkinterDefaultColor = '#F0F0F0'
# to change a color, just change the colors below. here you can get color codes: https://www.color-hex.com/
normalColor = 'black'
textColor = '#ff59cf'
highlightColor = 'dark grey'#'#db6ebc'

# styling (and sometimes other settings)
bgfg = {'bg':normalColor, 'fg':textColor, 'bd':1}
selectColors = {'selectbackground':normalColor, 'selectforeground':'dark grey'}

textSettings = {'insertbackground':'white', 'height':'20', 'font':('comic sans', '10'), 'width':50}
labelSettings = {'font':('comic sans', '10')}
frameSettings = {'bg':normalColor, 'padx':5}
listboxSettings = {'width':50, 'selectmode':'extended'}
entrySettings = {'insertbackground':'white', 'width':50}
buttonSettings = labelSettings

for toThis, addThese in zip((textSettings, listboxSettings, entrySettings, labelSettings),
                           ([bgfg,selectColors], [bgfg,selectColors], [bgfg,selectColors], [bgfg])):
    for addThis in addThese:
        dictAppend(addThis, toThis)

root = tk.Tk()
root.geometry('700x500')
root.configure(background = 'black')
root.title('imma move some files dawg')


### actually adding the widgets of the app

# frame that contains everything
mainFrame = tk.Frame(root, **frameSettings)

# for typing the source and destination
sourceVar = tk.StringVar(root, value=os.getcwd())
sourceEntry = tk.Entry(mainFrame, textvariable=sourceVar, **entrySettings)

destinationVar = tk.StringVar(root, value='')
destinationEntry = tk.Entry(mainFrame, textvariable=destinationVar, **entrySettings)

# for showing where each file goes
travelText = tk.Text(mainFrame, **textSettings)

# shows the file list
filelistFrame = tk.Frame(mainFrame, **frameSettings)
fileListboxVar = tk.StringVar(filelistFrame, value=os.listdir(sourceVar.get()))
fileListbox = tk.Listbox(filelistFrame, listvariable=fileListboxVar, **listboxSettings)

currentDirVar = tk.StringVar(root, value=sourceVar.get())
currentDir = tk.Entry(filelistFrame, textvariable=currentDirVar, **entrySettings)

# for adding the files to the textbox, and for sending the files
addButton = tk.Button(mainFrame, text='click here or press Enter to add to textbox', **buttonSettings)
sendButton = tk.Button(mainFrame, text='click here to send the files', **buttonSettings)
moveUpButton = tk.Button(filelistFrame, text='click here or press Escape to move up a directory', **buttonSettings)

currentDir.pack()
fileListbox.pack()
moveUpButton.pack()

# puts text into travelText, which sendFunction() will interpret and use to send files to their locations
def addFunction():
    # helper function
    def addLine(string):
        textAppend(travelText, string)
        textAppend(travelText, '\n')
        
    for n in fileListbox.curselection():
        fileName = fileListbox.get(n)
        source = sourceVar.get()
        destination = destinationVar.get()

        addLine(f'file name = {fileName}')
        addLine(f'source = {source}')
        addLine(f'destination = {destination}')
        addLine('----------')

# interprets the sending instructions in travelText and sends files
def sendFunction():
    code = textGrab(travelText)

    def interpretString(string):
        things = ['file name', 'source', 'destination']
        for thing in things:
            if f'{thing} = ' in string:
                return [thing, cleanEdges(string.partition(f'{thing} = ')[2])]
        return ['none', 'none']
    
    sections = code.split('----------')
    codeSections = []
    # codeSections will contain {source:string, destination:string} dictionaries that ill use to send files
    for section in sections:
        ignore = 0
        codeD = {}
        # remove surrounding whitespaces
        section = cleanEdges(section)
        for line in section.split('\n'):
            key, value = interpretString(line)
            codeD[key] = value
            
        if codeD == {'none':'none'}:
            continue

        # fill in 'none' for missing, to prevent errors
        things = ['file name', 'source', 'destination']
        for thing in things:
            if thing not in codeD:
                ignore = 1
                codeD[thing] = 'none'
                
        if ignore:
            continue
            
        codeD['source'] = codeD['source'] + '\\' + codeD['file name']
        codeD['destination'] = codeD['destination'] + '\\' + codeD['file name']
        del codeD['file name']
        codeSections.append(codeD)

    sentFiles = []
    for d in codeSections:
        if d['source'] in sentFiles:
            print(f'ignored {d["source"]}, because it was already in the list')
            continue

        # the line that actually sends a file to its destination
        # vvvvvvvv
        os.rename(d['source'], d['destination'])
        # ^^^^^^^^

        
        print(f'sent {d["source"]} to {d["destination"]}\n')
        sentFiles.append(d['source'])

def getListboxChoice(listbox):
    index = listbox.curselection()[0]
    choice = listbox.get(index)
    return choice
# for "moving into folder" on double click
def onDouble(event):
    selection = sourceVar.get() + '\\' + getListboxChoice(event.widget)
    if os.path.isdir(selection):
        sourceVar.set(selection)
        updateSD()
    else:
        addFunction()    

def moveUp():
    path = sourceVar.get()
    upperPath = '\\'.join(path.split('\\')[:-1])
    
    sourceVar.set(upperPath)
    updateSD()

fileListbox.bind('<Double-Button-1>', onDouble)
sendButton.config(command=sendFunction)
moveUpButton.config(command=moveUp)

addButton.config(command=addFunction)
# for a hotkey system
def onKeyPress(event):
    # requires:
    # - root.bind('<KeyRelease>', onKeyPress)
    # - hotkeys = {function1, function2}
    pressed = event.keysym
    if pressed in hotkeys:
        hotkeys[pressed]()

def updateSD():
    source = sourceVar.get()
    fileListboxVar.set(os.listdir(source))
    currentDirVar.set(source)

    currentDir.xview('end')

def pasteCurrentS():
    sourceEntry.delete(0, 'end')
    sourceEntry.insert(0, currentDirVar.get())
    sourceEntry.xview('end')

def pasteCurrentD():
    destinationEntry.delete(0, 'end')
    destinationEntry.insert(0, currentDirVar.get())
    destinationEntry.xview('end')

sourceEntry.bind('<Return>', lambda *args:updateSD())
fileListbox.bind('<Return>', lambda *args:addFunction())
fileListbox.bind('<Escape>', lambda *args:moveUp())

sourceEntry.bind('<KeyRelease-F1>', lambda *args:pasteCurrentS())
destinationEntry.bind('<KeyRelease-F1>', lambda *args:pasteCurrentD())

def applyLayout(layout):
    for i in range(len(layout)):
        for j in range(len(layout[i])): 
            if layout[i][j] == None:
                continue
            layout[i][j].grid(row=i,column=j)

mainFrameLayout = [
    [sourceEntry],
    [destinationEntry],
    [tk.Label(mainFrame, text=' (you can F1 to replace with current directory)', **labelSettings)],
    [filelistFrame, travelText],
    [addButton, sendButton]
    ]

applyLayout(mainFrameLayout)

mainFrame.pack()

updateSD()

root.mainloop()

















