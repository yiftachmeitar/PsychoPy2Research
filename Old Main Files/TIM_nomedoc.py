 #!/usr/bin/env python2
"""Display images from a specified folder and present them to the subject."""
# GalbraithHeat2.py
# Created 11/09/15 by DJ based on DistractionTask_practice_d3.py
# Updated 11/10/15 by DJ - cleaned up comments
# Adapted 7/7/2020 by JG - Heat Anticipation Task: change stimuli and timings
# Updated 7/16/20 by DJ - pickle->psydat extension, .JPG image extension, set flip time to now after instructions
# Updated 7/29/20 by DJ - added VAS that's persistent throughout block, fixed color order, removed trial responses, simplified params
# Updated 8/20/20 by JG - created functions for output
# Updated 8/31/20 by JG - changed visuals, added heat input, added VAS pre, mid, post, modified instructions to start over

from psychopy import core, gui, data, event, sound, logging 
import pandas as pd
# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.
from psychopy.tools.filetools import fromFile, toFile # saving and loading parameter files
import time as ts, numpy as np # for timing and array operations
from scipy.integrate import simps
from numpy import trapz
import os, glob
#import AppKit, os, glob # for monitor size detection, files - could not import on windows
import BasicPromptTools # for loading/presenting prompts and questions
import RatingScales
import random # for randomization of trials
import string
import math
import socket
import devices
from devices import Pathway

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = False;
newParamsFilename = 'GalbraithHeatParams.psydat'

# Declare primary task parameters.
params = {
# Declare stimulus and response parameters
    'nTrials': 8,            # number of trials in each block (sets of squares)
    'nBlocks': 6,             # number of blocks - need time to move electrode in between
    'stimDur': 4,             # time when stimulus is presented (in seconds)
    'painDur': 10,             # time of heat sensation (in seconds)
    'ISI': 0,                 # time between when one stimulus disappears and the next appears (in seconds)
    'tStartup': 5,            # pause time before starting first stimulus
# declare prompt and question files
    'skipPrompts': False,     # go right to the scanner-wait page
    'promptDir': 'Text/',     # directory containing prompts and questions files
    'promptFile': 'HeatAnticipationPrompts.txt', # Name of text file containing prompts 
    'questionFile': 'Text/AnxietyScale.txt', # Name of text file containing Q&As
    'questionDownKey': '1',   # move slider left
    'questionUpKey':'2',      # move slider right
    'questionDur': 999.0,
    'vasStepSize': 0.5,       # how far the slider moves with a keypress (increase to move faster)
    'textColor': 'dimgray',      # black in rgb255 space or gray in rgb space
    'PreVasMsg': "Let's do some rating scales.",             # Text shown BEFORE each VAS except the final one
    'introPractice': 'Questions/PracticeRating.txt', #Name of text file containing practice rating scales
    'moodQuestionFile1': 'Questions/ERVas1RatingScales.txt', # Name of text file containing mood Q&As presented before run
    'moodQuestionFile2': 'Questions/ERVasRatingScales.txt', # Name of text file containing mood Q&As presented after 3rd block
    'moodQuestionFile3': 'Questions/ERVas4RatingScales.txt', # Name of text file containing mood Q&As presented after run
    'questionSelectKey':'3', # select answer for VAS
    'questionSelectAdvances': True, # will locking in an answer advance past an image rating?
    'vasTextColor': 'dimgray', # color of text in both VAS types (-1,-1,-1) = black
    'vasMarkerSize': 0.1,   # in norm units (2 = whole screen)
    'vasLabelYDist': 0.1,   # distance below line that VAS label/option text should be, in norm units
# declare display parameters
    'fullScreen': False,       # run in full screen mode?
    'screenToShow': 0,        # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,       # size of cross, in pixels
    'fixCrossPos': [0,0],     # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
    'screenColor':(217,217,217), # in rgb255 space: (r,g,b) all between 0 and 255 - light grey
# parallel port parameters
    'sendPortEvents': True, # send event markers to biopac computer via parallel port
    'portAddress': 0xE050,  # 0xE050,  0x0378,  address of parallel port
    'codeBaseline': 144,     # parallel port code for baseline period 
    'codeFixation': 143,     #parallel port code for fixation period
    'codeVAS': 142,
    'convExcel': 'tempConv.xlsx',  #excel file with temp to binary code mappings

}

# save parameters - isn't working on personal laptop
if saveParams:
    dlgResult = gui.fileSaveDlg(prompt='Save Params...',initFilePath = os.getcwd() + '/Params', initFileName = newParamsFilename,
        allowed="PICKLE files (.psydat)|.psydat|All files (.*)|")
    newParamsFilename = dlgResult
    if newParamsFilename is None: # keep going, but don't save
        saveParams = False
    else:
        toFile(newParamsFilename, params) # save it!

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #
# scriptName = os.path.basename(__file__)
# scriptName = os.path.splitext(scriptName)[0] #% remove extension/
scriptName = 'TIM_nomedoc.py'
try: # try to get a previous parameters file
    expInfo = fromFile('%s-lastExpInfo.psydat'%scriptName)
    expInfo['session'] +=1 # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'],'Load...']
    expInfo['Version'] = 1
    expInfo['LHeat'] = 36.0
    expInfo['MHeat'] = 41.0
    expInfo['HHeat'] = 46.0
except: # if not there then use a default set
    expInfo = {
        'subject':'1', 
        'session': 1, 
        'Version': 1,
        'LHeat': '36.0',
        'MHeat': '41.0',
        'HHeat': '46.0',
        'skipPrompts':False, 
        'paramsFile':['DEFAULT','Load...']}
# overwrite params struct if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename,'Load...']

#present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','session','Version','LHeat','MHeat','HHeat','skipPrompts','paramsFile'])
if not dlg.OK:
    core.quit() # the user hit cancel, so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file',tryFilePath=os.getcwd(),
        allowed="PICKLE files (.psydat)|.psydat|All files (.*)|")
    expInfo['paramsFile'] = dlgResult[0]
# load parameter file
if expInfo['paramsFile'] not in ['DEFAULT', None]: # otherwise, just use defaults.
    # load params file
    params = fromFile(expInfo['paramsFile'])


# transfer skipPrompts from expInfo (gui input) to params (logged parameters)
params['skipPrompts'] = expInfo['skipPrompts']

# print params to Output
# print 'params = {'
# for key in sorted(params.keys()):
#     print "   '%s': %s"%(key,params[key]) # print each value as-is (no quotes)
# print '}'
    
# save experimental info
toFile('%s-lastExpInfo.psydat'%scriptName, expInfo)#save params to file for next time

#make a log file to save parameter/event  data
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime()) # add the current time
filename = '%s-%s-%d-%s'%(scriptName,expInfo['subject'], expInfo['session'], dateStr) # log filename
logging.LogFile((filename+'.log'), level=logging.INFO)#, mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s'%filename)
logging.log(level=logging.INFO, msg='subject: %s'%expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s'%expInfo['session'])
logging.log(level=logging.INFO, msg='version: %s'%expInfo['Version'])
logging.log(level=logging.INFO, msg='LHeat: %s'%expInfo['LHeat'])
logging.log(level=logging.INFO, msg='MHeat: %s'%expInfo['MHeat'])
logging.log(level=logging.INFO, msg='HHeat: %s'%expInfo['HHeat'])
logging.log(level=logging.INFO, msg='date: %s'%dateStr)
# log everything in the params struct
for key in sorted(params.keys()): # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s'%(key,params[key])) # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')


# ========================== #
# ===== GET SCREEN RES ===== #
# ========================== # can't use AppKit on windows

# kluge for secondary monitor
#if params['fullScreen']: 
#    screens = AppKit.NSScreen.screens()
#    screenRes = (int(screens[params['screenToShow']].frame().size.width), int(screens[params['screenToShow']].frame().size.height))
#    screenRes = [1920, 1200]
#    if params['screenToShow']>0:
#        params['fullScreen'] = False
#else:
#    screenRes = [800,600]

screenRes = [1024,768]


# ==================================== #
# == SET UP PARALLEL PORT AND MEDOC == #
# ==================================== #
#
#if params['sendPortEvents']:
#    from psychopy import parallel
#    port = parallel.ParallelPort(address=params['portAddress'])
#    port.setData(0) # initialize to all zeros
#else:
#    print("Parallel port not used.")
#
#
#my_pathway = Pathway(ip='10.150.254.8',port_number=20121)
#
#Check status of medoc connection
#response = my_pathway.status()
#print(response)



# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
from psychopy import visual

# Initialize deadline for displaying next frame
tNextFlip = [0.0] # put in a list to make it mutable (weird quirk of python variables) 

#create clocks and window
globalClock = core.Clock()#to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor', screen=params['screenToShow'], units='deg', name='win',color=params['screenColor'],colorSpace='rgb255')
win.setMouseVisible(False)
# create fixation cross
fCS = params['fixCrossSize'] # size (for brevity)
fCP = params['fixCrossPos'] # position (for brevity)
fixation = visual.TextStim(win, pos = [0,0], text = 'SAFE', font = 'Helvetica Bold', color = 'skyblue', alignHoriz = 'center', bold = True, height = 3)
fixationReady = visual.TextStim(win, pos = [0,0], text = 'GET READY', font = 'Helvetica Bold', color = 'gray', alignHoriz = 'center', bold = True, height = 3,wrapWidth=500)
fixationCross = visual.ShapeStim(win,lineColor='#000000',lineWidth=5.0,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');
# create text stimuli
message1 = visual.TextStim(win, pos=[0,+.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='topMsg', text="aaa",units='norm')
message2 = visual.TextStim(win, pos=[0,-.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='bottomMsg', text="bbb",units='norm')

# load VAS Qs & options
[questions,options,answers] = BasicPromptTools.ParseQuestionFile(params['questionFile'])
print('%d questions loaded from %s'%(len(questions),params['questionFile']))

# get stimulus files
promptImage = 'TIMprompt2.jpg'
stimImage = visual.ImageStim(win, pos=[0,0], name='ImageStimulus',image = promptImage, units='pix')

color_list = [1,2,3,4,1,2,3,4] #1-green, 2-yellow, 3-red, 4-black, ensure each color is presented twice at random per block
random.shuffle(color_list)

#for "random" black heat - l,m,h
randBlack = [0,0,0,0,1,1,1,1,2,2,2,2]
random.shuffle(randBlack)
randBlackCount = 0
sleepRand = [0, 0.5, 1, 1.5, 2]

#for "random" ITI 8-12 avg 10 sec
painITI = 0
painISI = [8,9,11,12,8,9,11,12]
random.shuffle(painISI)


# read questions and answers from text files
[topPrompts,bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptDir']+params['promptFile'])
print('%d prompts loaded from %s'%(len(topPrompts),params['promptFile']))

[questions_vas1,options_vas1,answers_vas1] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile1'])
print('%d questions loaded from %s'%(len(questions_vas1),params['moodQuestionFile1']))

[questions_vas2,options_vas2,answers_vas2] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile2'])
print('%d questions loaded from %s'%(len(questions_vas2),params['moodQuestionFile2']))

[questions_vas3,options_vas3,answers_vas3] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile3'])
print('%d questions loaded from %s'%(len(questions_vas3),params['moodQuestionFile3']))

[questions_prac,options_prac,answers_prac] = BasicPromptTools.ParseQuestionFile(params['introPractice'])
print('%d questions loaded from %s'%(len(questions_prac),params['introPractice']))


listlist = []

excelTemps = pd.read_excel(params['convExcel'])

# ============================ #
# ======= SUBFUNCTIONS ======= #
# ============================ #

# increment time of next window flip
def AddToFlipTime(tIncrement=1.0):
    tNextFlip[0] += tIncrement

# flip window as soon as possible
def SetFlipTimeToNow():
    tNextFlip[0] = globalClock.getTime()
    
def WaitForFlipTime():
    while (globalClock.getTime()<tNextFlip[0]):
        keyList = event.getKeys()
        # Check for escape characters
        for key in keyList:
            if key in ['q','escape']:
                CoolDown()

def GrowingSquare(color, block, trial, ratings):
    global painITI
    version = expInfo['Version']
    if color == 1:
        col = 'darkseagreen'
    elif color == 2:
        col = 'khaki'
    elif color == 3:
        col = 'lightcoral'
    elif color == 4:
        col = 'black'
    else:
        col = 'gray'
    trialStart = globalClock.getTime()
    phaseStart = globalClock.getTime()
    rect = visual.Rect(win=win, units = 'norm', size = 0.1, fillColor = col, lineColor = col, lineWidth = 20)
    rect.draw()
    fixationCross.lineColor = 'lightgrey'
    fixationCross.draw()
    WaitForFlipTime()
    if col is not 'gray':
        SetPort(color, 1, block)
    fixation.autoDraw = False
    win.flip()
    if version is 2:
        for i in range(180):
            timer = core.Clock()
            timer.add(0.0665)
            while timer.getTime() < 0:
                rect.draw()
                fixationCross.draw()
                win.flip()
                # get new keys
                newKeys = event.getKeys(keyList=['q','escape'],timeStamped=globalClock)
                # check each keypress for escape keys
                if len(newKeys)>0:
                    for thisKey in newKeys: 
                        if thisKey[0] in ['q','escape']: # escape keys
                            CoolDown() # exit gracefully
            rect.size = rect.size + 0.0216
            print("rect size:")
            print(rect.size)
            rect.draw()
            fixationCross.draw()
            win.flip()
            if col is not 'gray':
                BehavFile(globalClock.getTime(),block+1,trial+1,color,globalClock.getTime()-trialStart,"square",globalClock.getTime()-phaseStart,ratings.getRating())
            ++i
    else:
        for i in range (4):
            timer = core.Clock()
            timer.add(params['stimDur'])
            while timer.getTime() < 0:
                rect.draw()
                fixationCross.draw()
                win.flip()
                if col is not 'gray':
                    BehavFile(globalClock.getTime(),block+1,trial+1,color,globalClock.getTime()-trialStart,"square",globalClock.getTime()-phaseStart,ratings.getRating())

                # get new keys
                newKeys = event.getKeys(keyList=['q','escape'],timeStamped=globalClock)
                # check each keypress for escape keys
                if len(newKeys)>0:
                    for thisKey in newKeys: 
                        if thisKey[0] in ['q','escape']: # escape keys
                            CoolDown() # exit gracefully
            rect.size = rect.size + 0.972
            print("rect size:")
            print(rect.size)
            rect.draw()
            fixationCross.draw()
            win.flip()
            ++i
    if col is not 'gray':
        #SetPort(color, 2, block)
        phaseStart = globalClock.getTime()
        tNextFlip[0] = globalClock.getTime() + (params['painDur'])
        #my_pathway.start()
        #make sure can update rating scale while delaying onset of heat pain
        timer = core.Clock()
        timer.add(3 + random.sample(sleepRand,1)[0])
        while timer.getTime() < 0:
            rect.draw()
            fixationCross.draw()
            win.flip()
            BehavFile(globalClock.getTime(),block+1,trial+1,color,globalClock.getTime()-trialStart,"full",globalClock.getTime()-phaseStart,ratings.getRating())
            # get new keys
            newKeys = event.getKeys(keyList=['q','escape'],timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys)>0:
                for thisKey in newKeys: 
                    if thisKey[0] in ['q','escape']: # escape keys
                        CoolDown() # exit gracefully

        #my_pathway.trigger()
        #give medoc time to give heat before signalling to stop
        timer = core.Clock()
        timer.add(5)
        while timer.getTime() < 0:
            rect.draw()
            fixationCross.draw()
            win.flip()
            BehavFile(globalClock.getTime(),block+1,trial+1,color,globalClock.getTime()-trialStart,"full",globalClock.getTime()-phaseStart,ratings.getRating())
            # get new keys
            newKeys = event.getKeys(keyList=['q','escape'],timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys)>0:
                for thisKey in newKeys: 
                    if thisKey[0] in ['q','escape']: # escape keys
                        CoolDown() # exit gracefully

        #response = my_pathway.stop()
        # Flush the key buffer and mouse movements
        event.clearEvents()
        # Wait for relevant key press or 'painDur' seconds
        while (globalClock.getTime()<tNextFlip[0]): # until it's time for the next frame
            rect.draw()
            fixationCross.draw()
            win.flip() # to update rating scale
            BehavFile(globalClock.getTime(),block+1,trial+1,color,globalClock.getTime()-trialStart,"full",globalClock.getTime()-phaseStart,ratings.getRating())
            # get new keys
            newKeys = event.getKeys(keyList=['q','escape'],timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys)>0:
                for thisKey in newKeys: 
                    if thisKey[0] in ['q','escape']: # escape keys
                        CoolDown() # exit gracefully
    return trialStart, phaseStart


# Send parallel port event
def SetPortData(data):
    if params['sendPortEvents']:
        logging.log(level=logging.EXP,msg='set port %s to %d'%(format(params['portAddress'],'#04x'),data))
        #port.setData(data)
        print(data)
    else:
        print('Port event: %d'%data)



#use color, size, and block to calculate data for SetPortData
def SetPort(color, size, block):
    global randBlackCount
    SetPortData((color-1)*6**2 + (size - 1)*6 + (block - 1))
    if size == 1:
        if color == 1:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['LHeat']))]
            logging.log(level=logging.EXP,msg='set medoc %s'%(code.iat[0,1]))
        elif color == 2:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['MHeat']))]
            logging.log(level=logging.EXP,msg='set medoc %s'%(code.iat[0,1]))
        elif color == 3:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['HHeat']))]
            logging.log(level=logging.EXP,msg='set medoc %s'%(code.iat[0,1]))
        elif color == 4:
            if randBlack[randBlackCount] == 2:
                code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['HHeat']))]
                logging.log(level=logging.EXP,msg='set medoc %s'%(code.iat[0,1]))
                randBlackCount += 1
            elif randBlack[randBlackCount] == 1:
                code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['MHeat']))]
                logging.log(level=logging.EXP,msg='set medoc %s'%(code.iat[0,1]))
                randBlackCount += 1
            elif randBlack[randBlackCount] == 0:
                code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['LHeat']))]
                logging.log(level=logging.EXP,msg='set medoc %s'%(code.iat[0,1]))
                randBlackCount += 1
#        response = my_pathway.program(code.iat[0,1])
#        my_pathway.start()
#        my_pathway.trigger()



# Handle end of a session

def RunVas(questions,options,pos=(0.,-0.25),scaleTextPos=[0.,0.25],questionDur=params['questionDur'],isEndedByKeypress=params['questionSelectAdvances'],name='Vas'):
    
    # wait until it's time
    WaitForFlipTime()
    
    # Show questions and options
    [rating,decisionTime,choiceHistory] = RatingScales.ShowVAS(questions,options, win, questionDur=questionDur, \
        upKey=params['questionUpKey'], downKey=params['questionDownKey'], selectKey=params['questionSelectKey'],\
        isEndedByKeypress=isEndedByKeypress, textColor=params['vasTextColor'], name=name, pos=pos,\
        scaleTextPos=scaleTextPos, labelYPos=pos[1]-params['vasLabelYDist'], markerSize=params['vasMarkerSize'],\
        tickHeight=1,tickLabelWidth = 0.9)
    
    # Update next stim time
    if isEndedByKeypress:
        SetFlipTimeToNow() # no duration specified, so timing creep isn't an issue
    else:
        AddToFlipTime(questionDur*len(questions)) # add question duration * # of questions


def PersistentScale(question, options, win, name='Question', textColor='black',pos=(0.,0.),stepSize=1., scaleTextPos=[0.,0.45], 
                  labelYPos=-0.27648, markerSize=0.1, tickHeight=0.0, tickLabelWidth=0.0, questionDur=float('inf'), isEndedByKeypress=True, 
                  downKey='down',upKey='up',selectKey='enter', hideMouse=True, repeatDelay=0.5):
    # import packages
    from psychopy import visual # for ratingScale
    import numpy as np # for tick locations
    from pyglet.window import key # for press-and-hold functionality

    # set up
    nQuestions = len(question)
    rating = [None]*nQuestions
    decisionTime = [None]*nQuestions
    choiceHistory = [[0]]*nQuestions
    # Set up pyglet key handler
    keyState=key.KeyStateHandler()
    win.winHandle.push_handlers(keyState)
    # Get attributes for key handler (put _ in front of numbers)
    if downKey[0].isdigit():
        downKey_attr = '_%s'%downKey
    else:
        downKey_attr = downKey
    if upKey[0].isdigit():
        upKey_attr = '_%s'%upKey
    else:
        upKey_attr = upKey


    for iQ in range(nQuestions):
        # Make triangle
        markerStim = visual.ShapeStim(win,lineColor=textColor,fillColor=textColor,vertices=((-markerSize/2.,markerSize*np.sqrt(5./4.)),(markerSize/2.,markerSize*np.sqrt(5./4.)),(0,0)),units='norm',closeShape=True,name='triangle');
        
        tickMarks = np.linspace(0,100,len(options[iQ])).tolist()
        if tickLabelWidth==0.0: # if default value, determine automatically to fit all tick mark labels
          tickWrapWidth = (tickMarks[1]-tickMarks[0])*0.9/100 # *.9 for extra space, /100 for norm units
        else: # use user-specified value
          tickWrapWidth = tickLabelWidth;
        
        # Create ratingScale
        ratingScale = visual.RatingScale(win, scale=question[iQ], \
          low=0., high=100., markerStart=50., precision=1., labels=options[iQ], tickMarks=tickMarks, tickHeight=tickHeight, \
          marker=markerStim, markerColor=textColor, markerExpansion=1, singleClick=False, disappear=False, \
          textSize=0.8, textColor=textColor, textFont='Helvetica Bold', showValue=False, \
          showAccept=False, acceptKeys=selectKey, acceptPreText='key, click', acceptText='accept?', acceptSize=1.0, \
          leftKeys=downKey, rightKeys=upKey, respKeys=(), lineColor=textColor, skipKeys=[], \
          mouseOnly=False, noMouse=hideMouse, size=1.0, stretch=1.5, pos=pos, minTime=0.4, maxTime=np.inf, \
          flipVert=False, depth=0, name=name, autoLog=True)
        # Fix text wrapWidth
        for iLabel in range(len(ratingScale.labels)):
          ratingScale.labels[iLabel].wrapWidth = tickWrapWidth
          ratingScale.labels[iLabel].pos = (ratingScale.labels[iLabel].pos[0],labelYPos)
          ratingScale.labels[iLabel].alignHoriz = 'center'
        # Move main text
        ratingScale.scaleDescription.pos = scaleTextPos

        # Display until time runs out (or key is pressed, if specified)
        win.logOnFlip(level=logging.EXP, msg='Display %s%d'%(name,iQ))
        tStart = ts.time()
        while (ts.time()-tStart)<questionDur:
            # Look for keypresses
            if keyState[getattr(key,downKey_attr)]: #returns True if left key is pressed
                tPress = ts.time()
                valPress = ratingScale.markerPlacedAt
                keyPressed = downKey_attr
                step = -stepSize
            elif keyState[getattr(key,upKey_attr)]: #returns True if the right key is pressed
                tPress = ts.time()
                valPress = ratingScale.markerPlacedAt
                keyPressed = upKey_attr
                step = stepSize
            else:
                keyPressed = None

            # Handle sliding for held keys
            while (keyPressed is not None) and ((ts.time()-tStart)<questionDur):
                # update time
                durPress = ts.time()-tPress
                # update display
                ratingScale.draw()
                win.flip()
                # check for key release
                if keyState[getattr(key,keyPressed)]==False:
                    break
                # Update marker
                if durPress>repeatDelay:
                    ratingScale.markerPlacedAt = valPress + (durPress-repeatDelay)*step*60 # *60 for refresh rate
                    ratingScale.markerPlacedAt = max(ratingScale.markerPlacedAt,ratingScale.low)
                    ratingScale.markerPlacedAt = min(ratingScale.markerPlacedAt,ratingScale.high)
            # Check for response
            if isEndedByKeypress and not ratingScale.noResponse:
                break
            # Redraw
            ratingScale.draw()
            win.flip()

        # Log outputs
        rating[iQ] = ratingScale.getRating()
        decisionTime[iQ] = ratingScale.getRT()
        choiceHistory[iQ] = ratingScale.getHistory()

        # if no response, log manually
        if ratingScale.noResponse:
            logging.log(level=logging.DATA,msg='RatingScale %s: (no response) rating=%g'%(ratingScale.name,rating[iQ]))
            logging.log(level=logging.DATA,msg='RatingScale %s: rating RT=%g'%(ratingScale.name,decisionTime[iQ]))
            logging.log(level=logging.DATA,msg='RatingScale %s: history=%s'%(ratingScale.name,choiceHistory[iQ]))

    
    return ratingScale
    
def RunMoodVas(questions,options,name='MoodVas'):
    
    # Wait until it's time
    WaitForFlipTime()

    SetPortData(params['codeBaseline'])
    # display pre-VAS prompt
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts([params['PreVasMsg']],["Press any button to continue."],win,message1,message2)
    
    # Display this VAS
    RunVas(questions,options,questionDur=float("inf"), isEndedByKeypress=True,name=name)
    
    BasicPromptTools.RunPrompts(["For the next minute or so, we're just going to get some baseline measures."],["You can rest during this time."],win,message1,message2)
    tNextFlip[0] = globalClock.getTime()
    
    # display fixation before first stimulus
    fixation.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    # wait until it's time to show screen
    WaitForFlipTime()
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(60)

def CoolDown():
    
    # Stop drawing ratingScale (if it exists)
    try:
        anxSlider.setAutoDraw(False)
    except:
        print('ratingScale does not exist.')
    # Stop drawing stimImage (if it exists)
    try:
        fixationCross.autoDraw = False
    except:
        print('fixation cross does not exist.')
    
    df=pd.DataFrame(listlist,columns=['Absolute Time','Block','Trial','Color','Trial Time', 'Phase', 'Phase Time', 'Rating'])
    df.to_csv('avgFile%s.csv'%expInfo['subject'])


    # display cool-down message
    message1.setText("That's the end! ")
    message2.setText("Press 'q' or 'escape' to end the session.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    message1.draw()
    message2.draw()
    win.flip()
    thisKey = event.waitKeys(keyList=['q','escape'])
    
    # exit
    core.quit()

#handle transition between blocks
def BetweenBlock():
    while (globalClock.getTime()<tNextFlip[0]):
        win.flip() # to update ratingScale
    # stop autoDraw
    anxSlider.autoDraw = False
    AddToFlipTime(300)
    message1.setText("This concludes the current block. Please wait for further instruction before continuing.")
    message2.setText("Press SPACE to continue.")
    win.logOnFlip(level=logging.EXP, msg='BetweenBlock')
    message1.draw()
    message2.draw()
    win.flip()
    thisKey = event.waitKeys(keyList=['space']) # use space bar to avoid accidental advancing
    if thisKey :
        tNextFlip[0] = globalClock.getTime() + 2.0


def integrateData(ratingScale, arrayLength, iStim, avgArray, block):
    thisHistory = ratingScale.getHistory()[arrayLength - 1:]
    logging.log(level=logging.DATA,msg='RatingScale %s: history=%s'%(finalImages[iStim],thisHistory))
    if len(avgArray) == 0:
        avgFile.write('%s,' %(block + 1))
        avgFile.write(finalImages[iStim][9:-6] + ',')
    x = [a[1] for a in thisHistory]
    y = [a[0] for a in thisHistory]
    if len(thisHistory) == 1:
        avgRate = y[0]
    else :
        avgRate = trapz(y,x)/(x[-1] - x[0])
    avgArray.append(avgRate)
    logging.log(level=logging.DATA,msg='RatingScale %s: avgRate=%s'%(finalImages[iStim],avgRate))
    avgFile.write('%.3f,' % (avgRate))
    if len(avgArray) == 5 :
        avgFile.write(str(sum(avgArray) / float(len(avgArray))) + '\n')
        avgArray *= 0
    arrayLength = len(ratingScale.getHistory())
    return arrayLength

def EveryHalf(ratingScale):
    x = [a[1] for a in ratingScale.getHistory()]
    y = [a[0] for a in ratingScale.getHistory()]
    countTime = round(x[-1])
    for b in np.arange(0, countTime, 0.5):
        avgFile.write(str(b) + ',')
    avgFile.write('\n')
    i = 0
    for a in range(len(x)):
        if x[a] == i:
            avgFile.write(str(y[a]) + ',')
            i = i + 0.5
        elif x[a] > i:
            missed = math.ceil((x[a] - i)/0.5)
            avgFile.write((str(y[a-1]) + ',') * missed)
            i = i + 0.5 * missed
    avgFile.write('\n\n')

def BehavFile(absTime, block, trial, color, trialTime, phase, phaseTime, rating):
    list = [absTime, block, trial, color, trialTime, phase, phaseTime, rating]
    listlist.append(list)



def MakePersistentVAS(question, options, win, name='Question', textColor='black',pos=(0.,-0.70),stepSize=1., scaleTextPos=[0.,-0.50], 
                  labelYPos=-0.75, markerSize=0.1, tickHeight=0.0, tickLabelWidth=0.0, downKey=params['questionDownKey'],upKey=params['questionUpKey'],selectKey=[],hideMouse=True):
    # Make triangle
    markerStim = visual.ShapeStim(win,lineColor=textColor,fillColor=textColor,vertices=((-markerSize/2.,markerSize*np.sqrt(5./4.)),(markerSize/2.,markerSize*np.sqrt(5./4.)),(0,0)),units='norm',closeShape=True,name='triangle');
    
    tickMarks = np.linspace(0,50,len(options)).tolist()
    if tickLabelWidth==0.0: # if default value, determine automatically to fit all tick mark labels
      tickWrapWidth = (tickMarks[1]-tickMarks[0])*0.9/100 # *.9 for extra space, /100 for norm units
    else: # use user-specified value
      tickWrapWidth = tickLabelWidth;
    
    # Create ratingScale
    ratingScale = visual.RatingScale(win, scale=question, \
      low=0., high=50., markerStart=25., precision=1., labels=options, tickMarks=tickMarks, tickHeight=tickHeight, \
      marker=markerStim, markerColor=textColor, markerExpansion=1, singleClick=False, disappear=False, \
      textSize=0.8, textColor=textColor, textFont='Helvetica Bold', showValue=False, \
      showAccept=False, acceptKeys=selectKey, acceptPreText='key, click', acceptText='accept?', acceptSize=1.0, \
      leftKeys=downKey, rightKeys=upKey, respKeys=(), lineColor=textColor, skipKeys=[], \
      mouseOnly=False, noMouse=hideMouse, size=1.0, stretch=1.5, pos=pos, minTime=0.4, maxTime=np.inf, \
      flipVert=False, depth=0, name=name, autoLog=True)
    # Fix text wrapWidth
    for iLabel in range(len(ratingScale.labels)):
      ratingScale.labels[iLabel].wrapWidth = tickWrapWidth
      ratingScale.labels[iLabel].pos = (ratingScale.labels[iLabel].pos[0],labelYPos)
      ratingScale.labels[iLabel].alignHoriz = 'center'
    # Move main text
    ratingScale.scaleDescription.pos = scaleTextPos
    
    # Make it persistent by setting autoDraw to True
    ratingScale.autoDraw = True;
    
    # Display until time runs out (or key is pressed, if specified)
    win.logOnFlip(level=logging.EXP, msg='Display %s'%name)
    win.flip()
    
    return ratingScale

# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #
def RunPrompts():
    BasicPromptTools.RunPrompts(["Let's practice with the rating scale you'll be using today."],["Press the space bar to continue."],win,message1,message2)

    pracScale = PersistentScale(questions_prac, options_prac, win,name='pracScale',pos=(0.,-0.70),scaleTextPos=[0.,-0.50], 
                                    textColor=params['textColor'],stepSize=params['vasStepSize'],
                                    labelYPos=-0.75, markerSize=0.1, tickHeight=0.0, tickLabelWidth=0.0, 
                                    downKey=params['questionDownKey'],upKey=params['questionUpKey'],selectKey=params['questionSelectKey'],
                                    hideMouse=True)
    
        # display prompts
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts(["You are about to see a set of growing squares of a certain color. When the color fills up the screen you will feel the heat pain on your arm."],["Press any button to continue and see an example."],win,message1,message2)
        
        tNextFlip[0] = globalClock.getTime() + 10
        fixation.autoDraw = True
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        while (globalClock.getTime()<tNextFlip[0]):
            win.flip() # to update ratingScale
        fixation.autoDraw = False # stop  drawing fixation cross
        tNextFlip[0] = globalClock.getTime() + 5
        fixationReady.autodraw = True
        win.logOnFlip(level=logging.EXP, msg='Display Get Ready')
        while (globalClock.getTime()<tNextFlip[0]):
            fixationReady.draw()
            win.flip() # to update ratingScale
        fixationReady.autoDraw = False # stop  drawing fixation cross
        trialStart = GrowingSquare(5,0,0,pracScale)
        event.waitKeys()
        
        WaitForFlipTime()   
        AddToFlipTime(180)
        stimImage.setImage(promptImage)
        stimImage.autoDraw = True; 
        win.flip()
        
        key = event.waitKeys()
        stimImage.autoDraw = False;
        
        tNextFlip[0] = globalClock.getTime()
        WaitForFlipTime()
        
        BasicPromptTools.RunPrompts(topPrompts,bottomPrompts,win,message1,message2)
        thisKey = event.waitKeys() # use if need to repeat instructions
        if thisKey[0] == 'r':
            RunPrompts()
    tNextFlip[0] = globalClock.getTime() + 5.0



# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #
#SetPortData(params['codeVAS'])
#RunMoodVas(questions_vas1,options_vas1,name='PreVAS')
#
#WaitForFlipTime()
#
#RunPrompts()


# log experiment start and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')
tStimVec = np.zeros(params['nTrials'])


avgArray = []

for block in range(0, params['nBlocks']):
    if block == 3:
        anxSlider.autoDraw = False
        fixation.autoDraw = False
        RunMoodVas(questions_vas2,options_vas2,name='MidRun')
        WaitForFlipTime()
        BasicPromptTools.RunPrompts(["Thank you for your responses."],["Press the space bar to continue."],win,message1,message2)
        thisKey = event.waitKeys(keyList=['space']) # use space bar to avoid accidental advancing
        if thisKey :
            tNextFlip[0] = globalClock.getTime() + 5.0
    logging.log(level=logging.EXP,msg='==== START BLOCK %d/%d ===='%(block+1,params['nBlocks']))
    # wait before first stimulus
    fixation.autoDraw = True # Start drawing fixation cross
    win.callOnFlip(SetPortData,data=params['codeBaseline'])
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    anxSlider = MakePersistentVAS(win=win, question = '',name='anxSlider', pos=(0, -0.7), options=("Not Anxious","Very Anxious"), textColor=params['textColor'])
# Wait until it's time to display first stimulus
    while (globalClock.getTime()<tNextFlip[0]):
        win.flip() # to update ratingScale
    fixation.autoDraw = False # stop  drawing fixation cross
    fixationReady.autoDraw = True
    tNextFlip[0] = globalClock.getTime() + 5
    win.logOnFlip(level=logging.EXP, msg='Display Get Ready')
    while (globalClock.getTime()<tNextFlip[0]):
        win.flip() # to update ratingScale
    fixationReady.autoDraw = False
    arrayLength = 1
    painITI = 0
    ############################################
    ############################################
    for trial in range(params['nTrials']):
        trialStart, phaseStart = GrowingSquare(color_list[trial], block, trial, anxSlider)
        tNextFlip[0] = globalClock.getTime() + (painISI[painITI])
        painITI += 1
        fixationCross.autodraw = False
        SetPortData(params['codeFixation'])
        fixation.autoDraw = True
        win.logOnFlip(level=logging.EXP, msg='Display Fixation')
        phaseStart = globalClock.getTime()
        while (globalClock.getTime()<tNextFlip[0]):
            win.flip() # to update ratingScale
            BehavFile(globalClock.getTime(),block+1,trial+1,color_list[trial],globalClock.getTime()-trialStart,"safe",globalClock.getTime()-phaseStart,anxSlider.getRating())
        fixation.autoDraw = False # stop  drawing fixation cross
        fixationReady.autodraw = True
        tNextFlip[0] = globalClock.getTime() + 5
        win.logOnFlip(level=logging.EXP, msg='Display Get Ready')
        phaseStart = globalClock.getTime()
        while (globalClock.getTime()<tNextFlip[0]):
            fixationReady.draw()
            win.flip() # to update ratingScale
            BehavFile(globalClock.getTime(),block+1,trial+1,color_list[trial],globalClock.getTime()-trialStart,"ready",globalClock.getTime()-phaseStart,anxSlider.getRating())
        fixationReady.autoDraw = False # stop  drawing fixation cross
    ############################################
    ############################################
    
    # Log anxiety responses manually
    logging.log(level=logging.DATA,msg='RatingScale %s: history=%s'%(anxSlider.name,anxSlider.getHistory()))
    
    # Randomize order of colors for next block
    if block < (params['nBlocks']-1):
        BetweenBlock()
        random.shuffle(color_list)
        random.shuffle(painISI)
    logging.log(level=logging.EXP,msg='==== END BLOCK %d/%d ===='%(block+1,params['nBlocks']))
    #EveryHalf(anxSlider)

anxSlider.autoDraw = False
WaitForFlipTime()
RunMoodVas(questions_vas3,options_vas3,name='PostRun')
WaitForFlipTime()


# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# exit experiment
CoolDown()
