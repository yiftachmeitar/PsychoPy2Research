#!/usr/bin/env python2

# ====================================== #
# ===Import all the relevant packages=== #
# ====================================== #

from psychopy import core, gui, data, event, sound, logging
import pandas as pd
from psychopy.tools.filetools import fromFile, toFile  # saving and loading parameter files
import time as ts, numpy as np  # for timing and array operations
from numpy import trapz
import os
import BasicPromptTools  # for loading/presenting prompts and questions
import RatingScales
import random  # for randomization of trials
import math
from devices import Pathway
from HelperFunctions import reverse_string
# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?
saveParams = False;
newParamsFilename = 'GalbraithHeatParams.psydat'

# Global Exit (Jimmy)
# event.globalKeys.add(key='q', func=os._exit, func_args=[1], func_kwargs=None)

# Declare primary task parameters.
params = {
    # Declare stimulus and response parameters
    'screenIdx': 0,
    'nTrials': 1,  # number of squares in each block
    'nBlocks': 1,  # number of blocks (aka runs) - need time to move electrode in between
    'painDur': 4,  # time of heat sensation (in seconds)
    'tStartup': 5,  # pause time before starting first stimulus
    # declare prompt and question files
    'skipPrompts': True,  # go right to the task after vas and baseline
    'promptDir': 'Text/',  # directory containing prompts and questions files
    'promptFile': 'HeatAnticipationPrompts.txt',  # Name of text file containing prompts
    'initialpromptFile': 'InitialSafePrompts.txt',  # explain "safe" and "get ready" before the practice
    'questionFile': 'Text/AnxietyScale.txt',  # Name of text file containing Q&As
    'questionDownKey': '1',  # move slider left
    'questionUpKey': '2',  # move slider right
    'questionDur': 5.0,
    'vasStepSize': 0.5,  # how far the slider moves with a keypress (increase to move faster)
    'textColor': 'dimgray',  # black in rgb255 space or gray in rgb space
    'PreVasMsg': reverse_string("כעת נבצע דירוג"),  # Text shown BEFORE each VAS except the final one
    'introPractice': 'Questions/PracticeRating.txt',  # Name of text file containing practice rating scales
    'moodQuestionFile1': 'Questions/ERVas1RatingScales.txt',
    # Name of text file containing mood Q&As presented before run
    'moodQuestionFile2': 'Questions/ERVasRatingScales.txt',
    # Name of text file containing mood Q&As presented after 3rd block
    'moodQuestionFile3': 'Questions/ERVas4RatingScales.txt',
    # Name of text file containing mood Q&As presented after run
    'questionSelectKey': '3',  # select answer for VAS
    'questionSelectAdvances': True,  # will locking in an answer advance past an image rating?
    'vasTextColor': 'dimgray',  # color of text in both VAS types (-1,-1,-1) = black
    'vasMarkerSize': 0.1,  # in norm units (2 = whole screen)
    'vasLabelYDist': 0.1,  # distance below line that VAS label/option text should be, in norm units
    # declare display parameters
    'fullScreen': False,  # run in full screen mode?
    'screenToShow': 0,  # display on primary screen (0) or secondary (1)?
    'fixCrossSize': 50,  # size of cross, in pixels
    'fixCrossPos': [0, 0],  # (x,y) pos of fixation cross displayed before each stimulus (for gaze drift correction)
    'screenColor': (217, 217, 217),  # in rgb255 space: (r,g,b) all between 0 and 255 - light grey
    # parallel port parameters
    'sendPortEvents': False,  # send event markers to biopac computer via parallel port
    'portAddress': 0xE050,  # 0xE050,  0x0378,  address of parallel port
    'codeBaseline': 144,  # parallel port code for baseline period
    'codeFixation': 143,  # parallel port code for fixation period - safe
    'codeReady': 145,  # parallel port code for Get ready stimulus
    'codeVAS': 142,  # parallel port code for 3 VASs
    'convExcel': 'tempConv.xlsx',  # excel file with temp to binary code mappings
}

# save parameters
if saveParams:
    dlgResult = gui.fileSaveDlg(prompt='Save Params...', initFilePath=os.getcwd() + '/Params',
                                initFileName=newParamsFilename,
                                allowed="PICKLE files (.psydat)|.psydat|All files (.*)|")
    newParamsFilename = dlgResult
    if newParamsFilename is None:  # keep going, but don't save
        saveParams = False
    else:
        toFile(newParamsFilename, params)  # save it!

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #

scriptName = 'Main.py'
try:  # try to get a previous parameters file
    expInfo = fromFile('%s-lastExpInfo.psydat' % scriptName)
    expInfo['session'] += 1  # automatically increment session number
    expInfo['paramsFile'] = [expInfo['paramsFile'], 'Load...']
    expInfo['LHeat'] = 36.0
    expInfo['MHeat'] = 41.0
    expInfo['HHeat'] = 46.0
    expInfo['painSupport'] = False

except:  # if not there then use a default set
    expInfo = {
        'subject': '1',
        'session': 1,
        'LHeat': '36.0',
        'MHeat': '41.0',
        'HHeat': '46.0',
        'skipPrompts': False,
        'painSupport': True,
        'paramsFile': ['DEFAULT', 'Load...'],
    }

# overwrite params struct if you just saved a new parameter set
if saveParams:
    expInfo['paramsFile'] = [newParamsFilename, 'Load...']

# present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','session','LHeat','MHeat','HHeat','skipPrompts','painSupport','paramsFile'])
if not dlg.OK:
    core.quit()  # the user hit cancel, so exit

# find parameter file
if expInfo['paramsFile'] == 'Load...':
    dlgResult = gui.fileOpenDlg(prompt='Select parameters file', tryFilePath=os.getcwd(),
                                allowed="PICKLE files (.psydat)|.psydat|All files (.*)|")
    expInfo['paramsFile'] = dlgResult[0]
# load parameter file
if expInfo['paramsFile'] not in ['DEFAULT', None]:  # otherwise, just use defaults.
    # load params file
    params = fromFile(expInfo['paramsFile'])

# transfer skipPrompts from expInfo (gui input) to params (logged parameters)
params['painSupport'] = expInfo['painSupport']
params['skipPrompts'] = expInfo['skipPrompts']

# save experimental info
toFile('%s-lastExpInfo.psydat' % scriptName, expInfo)  # save params to file for next time

# make a log file to save parameter/event  data
dateStr = ts.strftime("%b_%d_%H%M", ts.localtime())  # add the current time
filename = '%s-%s-%d-%s' % (scriptName, expInfo['subject'], expInfo['session'], dateStr)  # log filename
logging.LogFile((filename + '.log'), level=logging.INFO)  # , mode='w') # w=overwrite
logging.log(level=logging.INFO, msg='---START PARAMETERS---')
logging.log(level=logging.INFO, msg='filename: %s' % filename)
logging.log(level=logging.INFO, msg='subject: %s' % expInfo['subject'])
logging.log(level=logging.INFO, msg='session: %s' % expInfo['session'])
logging.log(level=logging.INFO, msg='LHeat: %s' % expInfo['LHeat'])
logging.log(level=logging.INFO, msg='MHeat: %s' % expInfo['MHeat'])
logging.log(level=logging.INFO, msg='HHeat: %s' % expInfo['HHeat'])
logging.log(level=logging.INFO, msg='date: %s' % dateStr)
# log everything in the params struct
for key in sorted(params.keys()):  # in alphabetical order
    logging.log(level=logging.INFO, msg='%s: %s' % (key, params[key]))  # log each parameter

logging.log(level=logging.INFO, msg='---END PARAMETERS---')


# ==================================== #
# == SET UP PARALLEL PORT AND MEDOC == #
# ==================================== #
#
if params['painSupport']:
    if params['sendPortEvents']:
        from psychopy import parallel

        port = parallel.ParallelPort(address=params['portAddress'])
        port.setData(0)  # initialize to all zeros
    else:
        print("Parallel port not used.")

if params['painSupport']:
    # ip and port number from medoc application
    my_pathway = Pathway(ip='10.150.254.8', port_number=20121)

    # Check status of medoc connection
    response = my_pathway.status()
    print(response)

# ========================== #
# ===== SET UP STIMULI ===== #
# ========================== #
from psychopy import visual

#Initializing screen Resolution
screenRes = [1024,768]

# Initialize deadline for displaying next frame
tNextFlip = [0.0]  # put in a list to make it mutable (weird quirk of python variables)

# create clocks and window
globalClock = core.Clock()  # to keep track of time
win = visual.Window(screenRes, fullscr=params['fullScreen'], allowGUI=False, monitor='testMonitor',
                    screen=params['screenToShow'], units='deg', name='win', color=params['screenColor'],
                    colorSpace='rgb255')
win.setMouseVisible(False)
# create fixation cross
fCS = params['fixCrossSize']  # size (for brevity)
fCP = params['fixCrossPos']  # position (for brevity)
fixation = visual.TextStim(win, pos=[0, 5], text='SAFE', font='Helvetica Bold', color='skyblue', alignHoriz='center',
                           bold=True, height=3.5)

fixationReady = visual.TextStim(win, pos=[0, 5], text='GET READY', font='Helvetica Bold', color='gray',
                                alignHoriz='center', bold=True, height=3.5, wrapWidth=500)
fixationCross = visual.ShapeStim(win, lineColor='#000000', lineWidth=5.0, vertices=(
(fCP[0] - fCS / 2, fCP[1]), (fCP[0] + fCS / 2, fCP[1]), (fCP[0], fCP[1]), (fCP[0], fCP[1] + fCS / 2),
(fCP[0], fCP[1] - fCS / 2)), units='pix', closeShape=False, name='fixCross');
# create text stimuli
message1 = visual.TextStim(win, pos=[0, +.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='topMsg',
                           text="aaa", units='norm')
message2 = visual.TextStim(win, pos=[0, -.5], wrapWidth=1.5, color='#000000', alignHoriz='center', name='bottomMsg',
                           text="bbb", units='norm')

# load VAS Qs & options
[questions, options, answers] = BasicPromptTools.ParseQuestionFile(params['questionFile'])
print('%d questions loaded from %s' % (len(questions), params['questionFile']))

# get stimulus files

# image slide in instructions to explain color of square
promptImage = 'TIMprompt2.jpg'
stimImage = visual.ImageStim(win, pos=[0, 0], name='ImageStimulus', image=promptImage, units='pix')

color_list = [1, 2, 3, 4, 1, 2, 3,4]  # 1-green, 2-yellow, 3-red, 4-black, ensure each color is presented twice at random per block
random.shuffle(color_list)

# for "random" black heat - want 4 each of l,m,h
randBlack = [0, 0, 0, 0, 1, 1, 1, 1, 2, 2, 2, 2]
random.shuffle(randBlack)
randBlackCount = 0  # keep track of which black square we are in during task
sleepRand = [0, 0.5, 1, 1.5, 2]  # slightly vary onset of heat pain

# for "random" ITI avg 15 sec
painITI = 0
painISI = [13, 14, 16, 17, 13, 14, 16, 17]
random.shuffle(painISI)

# read questions and answers from text files for instructions text, 3 Vass, and practice scale questions
[topPrompts, bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptDir'] + params['promptFile'])
print('%d prompts loaded from %s' % (len(topPrompts), params['promptFile']))

[topPrompts1, bottomPrompts1] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts1.txt")
print('%d prompts loaded from %s' % (len(topPrompts1), "InitialSafePrompts1.txt"))

[topPrompts2, bottomPrompts2] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts2.txt")
print('%d prompts loaded from %s' % (len(topPrompts2), "InitialSafePrompts2.txt"))

[topPrompts3, bottomPrompts3] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts3.txt")
print('%d prompts loaded from %s' % (len(topPrompts3), "InitialSafePrompts3.txt"))

[questions_vas1, options_vas1, answers_vas1] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile1'])
print('%d questions loaded from %s' % (len(questions_vas1), params['moodQuestionFile1']))

[questions_vas2, options_vas2, answers_vas2] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile2'])
print('%d questions loaded from %s' % (len(questions_vas2), params['moodQuestionFile2']))

[questions_vas3, options_vas3, answers_vas3] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile3'])
print('%d questions loaded from %s' % (len(questions_vas3), params['moodQuestionFile3']))

[questions_prac, options_prac, answers_prac] = BasicPromptTools.ParseQuestionFile(params['introPractice'])
print('%d questions loaded from %s' % (len(questions_prac), params['introPractice']))

listlist = []

# excel in the folder to convert from Celsius temp to binary code for the medoc machine
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


# pause everything until stimuli are ready to move on
def WaitForFlipTime():
    while (globalClock.getTime() < tNextFlip[0]):
        keyList = event.getKeys()
        # Check for escape characters
        for key in keyList:
            if key in ['q', 'escape']:
                CoolDown()


# main function that takes information to run through each trial
def GrowingSquare(color, block, trial, ratings, params, tracker):
    import time
    global painITI

    # set color of square
    if color == 1:
        col = 'darkseagreen'
        colCode = int('8fbc8f', 16)
    elif color == 2:
        col = 'khaki'
        colCode = int('F0E68C', 16)
    elif color == 3:
        col = 'lightcoral'
        colCode = int('F08080', 16)
    elif color == 4:
        col = 'black'
        colCode = int('000000', 16)
    else:
        col = 'gray'
        colCode = int('808080', 16)

    trialStart = globalClock.getTime()
    phaseStart = globalClock.getTime()
    rect = visual.Rect(win=win, units='norm', size=0.1, fillColor=col, lineColor=col, lineWidth=20)
    rect.draw()
    fixationCross.lineColor = 'lightgrey'
    fixationCross.draw()
    WaitForFlipTime()
    # gray color = during the instructions
    if col != 'gray':
        SetPort(color, 1, block)
    fixation.autoDraw = False
    win.flip()

    Rbefore = ratings.getRating()
    # loop to continuously grow the square (180 * .0665 = ~12 sec to grow to total size)
    for i in range(180):
        timer = core.Clock()
        timer.add(0.0665)

        while timer.getTime() < 0:
            rect.draw()
            fixationCross.draw()
            win.flip()
            # get new keys
            newKeys = event.getKeys(keyList=['q', 'escape'], timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys) > 0:
                for thisKey in newKeys:
                    if thisKey[0] in ['q', 'escape']:  # escape keys
                        CoolDown()  # exit gracefully

        R = ratings.getRating()

        rect.size = rect.size + 0.0216
        rect.draw()
        fixationCross.draw()
        win.flip()

        Rbefore = R

        if col != 'gray':
            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "square",
                      globalClock.getTime() - phaseStart, ratings.getRating())
        ++i

    if col != 'gray':
        # print(time.time())
        SetPort(color, 2, block)
        phaseStart = globalClock.getTime()
        tNextFlip[0] = globalClock.getTime() + (params['painDur'])
        if params['painSupport']:
            my_pathway.start()
        # make sure can update rating scale while delaying onset of heat pain
        timer = core.Clock()
        timer.add(3 + random.sample(sleepRand, 1)[0])
        while timer.getTime() < 0:
            rect.draw()
            fixationCross.draw()

            R = ratings.getRating()

            rect.size = rect.size + 0.0216
            rect.draw()
            fixationCross.draw()
            win.flip()
            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "full",
                      globalClock.getTime() - phaseStart, ratings.getRating())
            # get new keys
            newKeys = event.getKeys(keyList=['q', 'escape'], timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys) > 0:
                for thisKey in newKeys:
                    if thisKey[0] in ['q', 'escape']:  # escape keys
                        CoolDown()  # exit gracefully
        if params['painSupport']:
            my_pathway.trigger()
        # give medoc time to give heat before signalling to stop
        timer = core.Clock()
        timer.add(5)
        while timer.getTime() < 0:
            rect.draw()
            fixationCross.draw()

            # R = anxSlider.getRating()
            R = ratings.getRating()

            rect.size = rect.size + 0.0216
            rect.draw()
            fixationCross.draw()
            win.flip()

            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "full",
                      globalClock.getTime() - phaseStart, ratings.getRating())
            # get new keys
            newKeys = event.getKeys(keyList=['q', 'escape'], timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys) > 0:
                for thisKey in newKeys:
                    if thisKey[0] in ['q', 'escape']:  # escape keys
                        CoolDown()  # exit gracefully
        if params['painSupport']:
            response = my_pathway.stop()
        # Flush the key buffer and mouse movements
        event.clearEvents()
        # Wait for relevant key press or 'painDur' seconds
        while (globalClock.getTime() < tNextFlip[0]):  # until it's time for the next frame
            rect.draw()
            fixationCross.draw()

            # R = anxSlider.getRating()
            R = ratings.getRating()

            rect.size = rect.size + 0.0216
            rect.draw()
            fixationCross.draw()
            win.flip()

            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "full",
                      globalClock.getTime() - phaseStart, ratings.getRating())
            # get new keys
            newKeys = event.getKeys(keyList=['q', 'escape'], timeStamped=globalClock)
            # check each keypress for escape keys
            if len(newKeys) > 0:
                for thisKey in newKeys:
                    if thisKey[0] in ['q', 'escape']:  # escape keys
                        CoolDown()  # exit gracefully
        # print(time.time())
    return trialStart, phaseStart


# Send parallel port event
def SetPortData(data):
    if params['painSupport'] and params['sendPortEvents']:
        logging.log(level=logging.EXP, msg='set port %s to %d' % (format(params['portAddress'], '#04x'), data))
        port.setData(data)
        print(data)
    else:
        if params['painSupport']:
            print('Port event: %d' % data)


# use color, size, and block to calculate data for SetPortData
def SetPort(color, size, block):
    global randBlackCount
    SetPortData((color - 1) * 6 ** 2 + (size - 1) * 6 + (block))
    if size == 1:
        if color == 1:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['LHeat']))]
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 2:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['MHeat']))]
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 3:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['HHeat']))]
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 4:
            if randBlack[randBlackCount] == 2:
                code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['HHeat']))]
                logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
                randBlackCount += 1
            elif randBlack[randBlackCount] == 1:
                code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['MHeat']))]
                logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
                randBlackCount += 1
            elif randBlack[randBlackCount] == 0:
                code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['LHeat']))]
                logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
                randBlackCount += 1
        if params['painSupport']:
            response = my_pathway.program(code.iat[0, 1])
            my_pathway.start()
            my_pathway.trigger()


# Handle end of a session

def RunVas(questions, options, pos=(0., -0.25), scaleTextPos=[0., 0.25], questionDur=params['questionDur'],
           isEndedByKeypress=params['questionSelectAdvances'], name='Vas'):
    # wait until it's time
    WaitForFlipTime()

    # Show questions and options
    [rating, decisionTime, choiceHistory] = RatingScales.ShowVAS(questions, options, win, questionDur=questionDur, \
                                                                 upKey=params['questionUpKey'],
                                                                 downKey=params['questionDownKey'],
                                                                 selectKey=params['questionSelectKey'], \
                                                                 isEndedByKeypress=isEndedByKeypress,
                                                                 textColor=params['vasTextColor'], name=name, pos=pos, \
                                                                 scaleTextPos=scaleTextPos,
                                                                 labelYPos=pos[1] - params['vasLabelYDist'],
                                                                 markerSize=params['vasMarkerSize'], \
                                                                 tickHeight=1, tickLabelWidth=0.9)

    # Update next stim time
    if isEndedByKeypress:
        SetFlipTimeToNow()  # no duration specified, so timing creep isn't an issue
    else:
        AddToFlipTime(1) # I changes that from: AddToFlipTime(questionDur * len(questions))  # add question duration * # of questions


def PersistentScale(question, options, win, name='Question', textColor='black', pos=(0., 0.), stepSize=1.,
                    scaleTextPos=[0., 0.45],
                    labelYPos=-0.27648, markerSize=0.1, tickHeight=0.0, tickLabelWidth=0.0, questionDur=float('inf'),
                    isEndedByKeypress=True,
                    downKey='down', upKey='up', selectKey='enter', hideMouse=True, repeatDelay=0.5, params=params):
    # import packages
    from psychopy import visual  # for ratingScale
    import numpy as np  # for tick locations
    from pyglet.window import key  # for press-and-hold functionality

    # set up
    nQuestions = len(question)
    rating = [None] * nQuestions
    decisionTime = [None] * nQuestions
    choiceHistory = [[0]] * nQuestions
    # Set up pyglet key handler
    keyState = key.KeyStateHandler()
    win.winHandle.push_handlers(keyState)
    # Get attributes for key handler (put _ in front of numbers)
    if downKey[0].isdigit():
        downKey_attr = '_%s' % downKey
    else:
        downKey_attr = downKey
    if upKey[0].isdigit():
        upKey_attr = '_%s' % upKey
    else:
        upKey_attr = upKey

    for iQ in range(nQuestions):
        # Make triangle
        markerStim = visual.ShapeStim(win, lineColor=textColor, fillColor=textColor, vertices=(
        (-markerSize / 2., markerSize * np.sqrt(5. / 4.)), (markerSize / 2., markerSize * np.sqrt(5. / 4.)), (0, 0)),
                                      units='norm', closeShape=True, name='triangle');

        tickMarks = np.linspace(0, 36, len(options[iQ])).tolist()
        if tickLabelWidth == 0.0:  # if default value, determine automatically to fit all tick mark labels
            tickWrapWidth = (tickMarks[1] - tickMarks[0]) * 0.9 / 36  # *.9 for extra space, /100 for norm units
        else:  # use user-specified value
            tickWrapWidth = tickLabelWidth;

        # Create ratingScale
        ratingScale = visual.RatingScale(win, scale=question[iQ], \
                                         low=0., high=36., markerStart=18., precision=1., labels=options[iQ],
                                         tickMarks=tickMarks, tickHeight=tickHeight, \
                                         marker=markerStim, markerColor=textColor, markerExpansion=1, singleClick=False,
                                         disappear=False, \
                                         textSize=0.8, textColor=textColor, textFont='Helvetica Bold', showValue=False, \
                                         showAccept=False, acceptKeys=selectKey, acceptPreText='key, click',
                                         acceptText='accept?', acceptSize=1.0, \
                                         leftKeys=downKey, rightKeys=upKey, respKeys=(), lineColor=textColor,
                                         skipKeys=[], \
                                         mouseOnly=False, noMouse=hideMouse, size=1.0, stretch=1.75, pos=pos,
                                         minTime=1.5, maxTime=np.inf, \
                                         flipVert=False, depth=0, name=name, autoLog=True)
        # Fix text wrapWidth
        for iLabel in range(len(ratingScale.labels)):
            ratingScale.labels[iLabel].wrapWidth = tickWrapWidth
            ratingScale.labels[iLabel].pos = (ratingScale.labels[iLabel].pos[0], labelYPos)
            ratingScale.labels[iLabel].alignHoriz = 'center'
        # Move main text
        ratingScale.scaleDescription.pos = scaleTextPos

        # Display until time runs out (or key is pressed, if specified)
        win.logOnFlip(level=logging.EXP, msg='Display %s%d' % (name, iQ))

        tStart = ts.time()
        while (ts.time() - tStart) < questionDur:
            # Look for keypresses
            if keyState[getattr(key, downKey_attr)]:  # returns True if left key is pressed
                tPress = ts.time()
                valPress = ratingScale.markerPlacedAt
                keyPressed = downKey_attr
                step = -stepSize
            elif keyState[getattr(key, upKey_attr)]:  # returns True if the right key is pressed
                tPress = ts.time()
                valPress = ratingScale.markerPlacedAt
                keyPressed = upKey_attr
                step = stepSize
            else:
                keyPressed = None

            # Handle sliding for held keys
            while (keyPressed is not None) and ((ts.time() - tStart) < questionDur):
                # update time
                durPress = ts.time() - tPress
                # update display
                ratingScale.draw()
                win.flip()

                # check for key release
                if keyState[getattr(key, keyPressed)] == False:
                    break
                # Update marker
                if durPress > repeatDelay:
                    ratingScale.markerPlacedAt = valPress + (durPress - repeatDelay) * step * 60  # *60 for refresh rate
                    ratingScale.markerPlacedAt = max(ratingScale.markerPlacedAt, ratingScale.low)
                    ratingScale.markerPlacedAt = min(ratingScale.markerPlacedAt, ratingScale.high)
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
            logging.log(level=logging.DATA,
                        msg='RatingScale %s: (no response) rating=%g' % (ratingScale.name, rating[iQ]))
            logging.log(level=logging.DATA, msg='RatingScale %s: rating RT=%g' % (ratingScale.name, decisionTime[iQ]))
            logging.log(level=logging.DATA, msg='RatingScale %s: history=%s' % (ratingScale.name, choiceHistory[iQ]))

    return ratingScale


def RunMoodVas(questions, options, name='MoodVas'):

    # Wait until it's time
    WaitForFlipTime()

    SetPortData(params['codeBaseline'])
    # display pre-VAS prompt
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts([params['PreVasMsg']], [reverse_string("לחץ על כל דבר כדי להמשיך.")], win, message1, message2)

    # Display this VAS
    for i in range(len(questions)):
        question = [questions[i]]
        option = [options[i]]
        imgName = question[0].replace(' ', '_')
        imgName = imgName.replace('?', '')
        imgName = imgName.replace('\n', '')

        RunVas(question, option, questionDur=float("inf"), isEndedByKeypress=True, name=name)

        # win.getMovieFrame()  # Defaults to front buffer, I.e. what's on screen now.
        # win.saveMovieFrames('img/' + imgName + '.jpg')
    # RunVas(questions,options,questionDur=float("inf"), isEndedByKeypress=True,name=name)

    BasicPromptTools.RunPrompts([], [reverse_string("מנוחה קצרה")], win, message1, message2)
    tNextFlip[0] = globalClock.getTime()

    fixationCross.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')

    # wait until it's time to show screen
    WaitForFlipTime()
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(1)


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

    df = pd.DataFrame(listlist,
                      columns=['Absolute Time', 'Block', 'Trial', 'Color', 'Trial Time', 'Phase', 'Phase Time',
                               'Rating'])
    df.to_csv('avgFile%s.csv' % expInfo['subject'])

    # # display cool-down message
    # tracker.sendMessage('TRIAL_RESULT 0')
    # tracker.sendMessage('TRIALID %d' % 0)
    # tracker.sendMessage('!V IMGLOAD CENTER %s %d %d %d %d' % ('img/end.jpg', 1024 / 2, 768 / 2, 1024, 768))

    message1.setText("That's the end! ")
    message2.setText("Press 'q' or 'escape' to end the session.")
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')
    # Save Screenshot
    # win.getMovieFrame()  # Defaults to front buffer, I.e. what's on screen now.
    # win.saveMovieFrames('img/end.jpg')

    message1.draw()
    message2.draw()
    win.flip()

    thisKey = event.waitKeys(keyList=['q', 'escape'])

    # exit
    core.quit()


# handle transition between blocks
def BetweenBlock(params):
    while (globalClock.getTime() < tNextFlip[0]):
        win.flip()  # to update ratingScale
    # stop autoDraw
    anxSlider.autoDraw = False
    AddToFlipTime(1)
    message1.setText("This concludes the current block. Please wait for further instruction before continuing.")
    message2.setText("Press SPACE to continue.")
    win.logOnFlip(level=logging.EXP, msg='BetweenBlock')

    message1.draw()
    message2.draw()
    win.flip()

    thisKey = event.waitKeys(keyList=['space'])  # use space bar to avoid accidental advancing
    if thisKey:
        tNextFlip[0] = globalClock.getTime() + 2.0


def integrateData(ratingScale, arrayLength, iStim, avgArray, block):
    thisHistory = ratingScale.getHistory()[arrayLength - 1:]
    logging.log(level=logging.DATA, msg='RatingScale %s: history=%s' % (finalImages[iStim], thisHistory))
    if len(avgArray) == 0:
        avgFile.write('%s,' % (block + 1))
        avgFile.write(finalImages[iStim][9:-6] + ',')
    x = [a[1] for a in thisHistory]
    y = [a[0] for a in thisHistory]
    if len(thisHistory) == 1:
        avgRate = y[0]
    else:
        avgRate = trapz(y, x) / (x[-1] - x[0])
    avgArray.append(avgRate)
    logging.log(level=logging.DATA, msg='RatingScale %s: avgRate=%s' % (finalImages[iStim], avgRate))
    avgFile.write('%.3f,' % (avgRate))
    if len(avgArray) == 5:
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
            missed = math.ceil((x[a] - i) / 0.5)
            avgFile.write((str(y[a - 1]) + ',') * missed)
            i = i + 0.5 * missed
    avgFile.write('\n\n')


def BehavFile(absTime, block, trial, color, trialTime, phase, phaseTime, rating):
    list = [absTime, block, trial, color, trialTime, phase, phaseTime, rating]
    listlist.append(list)


def MakePersistentVAS(question, options, win, name='Question', textColor='black', pos=(0., -0.70), stepSize=1.,
                      scaleTextPos=[0., -0.50],
                      labelYPos=-0.75, markerSize=0.1, tickHeight=0.0, tickLabelWidth=0.0,
                      downKey=params['questionDownKey'], upKey=params['questionUpKey'], selectKey=[], hideMouse=True):
    # Make triangle
    markerStim = visual.ShapeStim(win, lineColor=textColor, fillColor=textColor, vertices=(
    (-markerSize / 2., markerSize * np.sqrt(5. / 4.)), (markerSize / 2., markerSize * np.sqrt(5. / 4.)), (0, 0)),
                                  units='norm', closeShape=True, name='triangle');

    tickMarks = np.linspace(0, 36, len(options)).tolist()
    if tickLabelWidth == 0.0:  # if default value, determine automatically to fit all tick mark labels
        tickWrapWidth = (tickMarks[1] - tickMarks[0]) * 0.9 / 36  # *.9 for extra space, /100 for norm units
    else:  # use user-specified value
        tickWrapWidth = tickLabelWidth;

    # Create ratingScale
    ratingScale = visual.RatingScale(win, scale=question, \
                                     low=0., high=36., markerStart=18., precision=1, labels=options,
                                     tickMarks=tickMarks, tickHeight=tickHeight, \
                                     marker=markerStim, markerColor=textColor, markerExpansion=1, singleClick=False,
                                     disappear=False, \
                                     textSize=0.8, textColor=textColor, textFont='Helvetica Bold', showValue=False, \
                                     showAccept=False, acceptKeys=selectKey, acceptPreText='key, click',
                                     acceptText='accept?', acceptSize=1.0, \
                                     leftKeys=downKey, rightKeys=upKey, respKeys=(), lineColor=textColor, skipKeys=[], \
                                     mouseOnly=False, noMouse=hideMouse, size=1.0, stretch=1.75, pos=pos, minTime=0.4,
                                     maxTime=np.inf, \
                                     flipVert=False, depth=0, name=name, autoLog=True)
    # Fix text wrapWidth
    for iLabel in range(len(ratingScale.labels)):
        ratingScale.labels[iLabel].wrapWidth = tickWrapWidth
        ratingScale.labels[iLabel].pos = (ratingScale.labels[iLabel].pos[0], labelYPos)
        ratingScale.labels[iLabel].alignHoriz = 'center'
    # Move main text
    ratingScale.scaleDescription.pos = scaleTextPos

    # Make it persistent by setting autoDraw to True
    ratingScale.autoDraw = True;

    # Display until time runs out (or key is pressed, if specified)
    win.logOnFlip(level=logging.EXP, msg='Display %s' % name)
    win.flip()

    return ratingScale


# =========================== #
# ======= RUN PROMPTS ======= #
# =========================== #
def RunPrompts():

    # display prompts
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts(["Let's practice with the rating scale you'll be using today."],
                                    ["Press the space bar to continue."], win, message1, message2)

        pracScale = PersistentScale(questions_prac, options_prac, win, name='pracScale', pos=(0., -0.70),
                                    scaleTextPos=[0., -0.50],
                                    textColor=params['textColor'], stepSize=params['vasStepSize'],
                                    labelYPos=-0.8, markerSize=0.1, tickHeight=0.0, tickLabelWidth=0.0,
                                    downKey=params['questionDownKey'], upKey=params['questionUpKey'],
                                    selectKey=params['questionSelectKey'],
                                    hideMouse=True, params=params)

        BasicPromptTools.RunPrompts(topPrompts1, bottomPrompts1, win, message1, message2)
        BasicPromptTools.RunPrompts(topPrompts2, bottomPrompts2, win, message1, message2)

        # BasicPromptTools.RunPrompts(["You are about to see a set of growing squares of a certain color. When the color fills up the screen you will feel the heat pain on your arm."],["Press any button to continue and see an example."],win,message1,message2)

        trialStart = GrowingSquare(5, 0, 0, pracScale, params, "")
        event.waitKeys()

        WaitForFlipTime()
        AddToFlipTime(1)
        stimImage.setImage(promptImage)
        stimImage.autoDraw = True;
        win.flip()

        key = event.waitKeys()
        stimImage.autoDraw = False;

        tNextFlip[0] = globalClock.getTime()
        WaitForFlipTime()

        BasicPromptTools.RunPrompts(topPrompts, bottomPrompts, win, message1, message2)
        thisKey = event.waitKeys()  # use if need to repeat instructions
        if thisKey[0] == 'r':
            RunPrompts()

        BasicPromptTools.RunPrompts(["We are about to start !"], ["Press any button to continue"], win, message1,
                                    message2)

    tNextFlip[0] = globalClock.getTime() + 5.0

# =========================== #
# ===== MAIN EXPERIMENT ===== #
# =========================== #


# log the start of the and set up
logging.log(level=logging.EXP, msg='---START EXPERIMENT---')

# Creates an empty numpy array for the number of trials specified in the experiment parameters.
tStimVec = np.zeros(params['nTrials'])

# Creates an empty list for storing average ratings across trials
avgArray = []

# Starts a for loop that iterates over each block of the experiment.
for block in range(0, params['nBlocks']):

    if block == 0: #  If it's the first block, runs a mood VAS rating task and displays some prompts to the participant.
        SetPortData(params['codeVAS'])
        RunMoodVas(questions_vas1, options_vas1, name='PreVAS')
        WaitForFlipTime()
        RunPrompts()

    if block == 2: # If it's the second block, stops drawing the anxiety slider and fixation cross, runs a mood VAS rating task, displays some prompts, and sets the next stimulus presentation time to 4-6 seconds in the future.
        print("got to block 2 if statement")
        anxSlider.autoDraw = False
        fixation.autoDraw = False
        RunMoodVas(questions_vas2, options_vas2, name='MidRun')
        WaitForFlipTime()

        BasicPromptTools.RunPrompts(["Thank you for your responses."], ["Press the space bar to continue."], win,message1, message2)
        thisKey = event.waitKeys(keyList=['space'])  # use space bar to avoid accidental advancing
        if thisKey:
            tNextFlip[0] = globalClock.getTime() + random.randint(4, 6)

    # wait before first stimulus

    fixation.autoDraw = True  # Start drawing fixation cross

    win.callOnFlip(SetPortData, data=params['codeBaseline']) # Calls a function to set the port data to the baseline code.

    tracker = ""

    # Creates a new persistent visual analog scale (VAS) to measure anxiety.
    anxSlider = MakePersistentVAS(win=win, question='', name='anxSlider', pos=(0, -0.7),
                                  options=("Not Anxious", "Very Anxious"), textColor=params['textColor'])

    # Waits for 2 seconds before displaying the first stimulus.
    while (globalClock.getTime() < tNextFlip[0] + 2):
        R = anxSlider.getRating()

        win.flip()  # to update ratingScale

    arrayLength = 1
    painITI = 0

    ############################################

    # Starts a loop to present each trial.
    for trial in range(params['nTrials']):

        color = color_list[trial] # Selects the color for this trial.
        ratings = anxSlider
        # GrowingSquare(color, block, trial, ratings, params)

        # Calls the GrowingSquare function to present the stimulus, and records the start time and phase start time.
        trialStart, phaseStart = GrowingSquare(color_list[trial], block, trial, anxSlider, params, tracker)
        win.flip() # Flips the screen and waits for 2 seconds.
        core.wait(2)

        # Safe screen showed up (issue exists)

        # Sets the next stimulus presentation time.
        tNextFlip[0] = globalClock.getTime() + (painISI[painITI])
        painITI += 1


    ### THE FIXATION "SAFE" AND "GET READY" WAS DELETED FROM HERE ###

    ############################################

    # Logs the history of the anxiety VAS ratings for this block.
    logging.log(level=logging.DATA, msg='RatingScale %s: history=%s' % (anxSlider.name, anxSlider.getHistory()))

    # Randomize order of colors for next block (if there is a next block, meaning we are not in the end)
    if block < (params['nBlocks'] - 1):
        BetweenBlock(params)  # betweenblock message
        random.shuffle(color_list)
        random.shuffle(painISI)
    logging.log(level=logging.EXP, msg='==== END BLOCK %d/%d ====' % (block + 1, params['nBlocks'])) #  Logs the end of the block.

    # finish recording
    # if block == 2 or block == 5:
    if block == 2 or block == (params['nBlocks'] - 1):
        print ("I got to the last if statement")


anxSlider.autoDraw = False # This stops drawing the persistent VAS.
WaitForFlipTime() #  This waits for the next screen refresh.

RunMoodVas(questions_vas3, options_vas3, name='PostRun') # This displays a mood VAS after the experiment is completed.

WaitForFlipTime() # This waits for the next screen refresh.

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# clean-up & exit experiment
CoolDown()


