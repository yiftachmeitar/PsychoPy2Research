#!/usr/bin/env python2

# ====================================== #
# ===Import all the relevant packages=== #
# ====================================== #

from psychopy import core, gui, data, event, sound, logging
import pandas as pd
from psychopy.tools.filetools import fromFile, toFile  # saving and loading parameter files
import time as ts, numpy as np  # for timing and array operations
import BasicPromptTools  # for loading/presenting prompts and questions
import RatingScales
import random  # for randomization of trials
from devices import Pathway
from HelperFunctions import reverse_string
# from psychopy import visual # visual causes a bug in the guis, so it's declared after all GUIs run.

# ====================== #
# ===== PARAMETERS ===== #
# ====================== #
# Save the parameters declared below?

# Declare primary task parameters.
params = {
    # Declare stimulus and response parameters
    'screenIdx': 0,
    'nTrials': 2,  # number of squares in each block
    'nBlocks': 2,  # number of blocks (aka runs) - need time to move electrode in between
    'painDur': 4,  # time of heat sensation (in seconds)
    'tStartup': 5,  # pause time before starting first stimulus
    # declare prompt and question files
    'skipPrompts': True,  # go right to the task after vas and baseline
    'promptDir': 'Text/',  # directory containing prompts and questions files
    'promptFile': 'HeatAnticipationPrompts.txt',  # Name of text file containing prompts
     # 'initialpromptFile': 'InitialSafePrompts.txt',  # explain "safe" and "get ready" before the practice - NOT USING THESE SCREENS RIGHT NOW
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
    # Name of text file containing pain Rating Scale presented after each trial
    'MoodRatingPainFile': 'Questions/MoodRatingPainFile.txt',
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
    'image1' : 'img/image1.png',
    'image2' : 'img/image2.png',
    'image3' : 'img/image3.png',
    'techInstructionImage1': 'img/techInstructionImage1.png',
    'techInstructionImage2': 'img/techInstructionImage2.png',
}

# ========================== #
# ===== SET UP LOGGING ===== #
# ========================== #

scriptName = 'Main.py'
try:  # try to get a previous parameters file
    expInfo = fromFile('%s-lastExpInfo.psydat' % scriptName)
    expInfo['session'] += 1  # automatically increment session number
    expInfo['T2'] = 36.0
    expInfo['T4'] = 41.0
    expInfo['T6'] = 46.0
    expInfo['T8'] = 48.0
    expInfo['painSupport'] = False

except:  # if not there then use a default set
    expInfo = {
        'subject': '1',
        'session': 1,
        'T2': '36.0',
        'T4': '41.0',
        'T6': '46.0',
        'T8': '50.0',
        'painSupport': True,
    }


# present a dialogue to change select params
dlg = gui.DlgFromDict(expInfo, title=scriptName, order=['subject','session','T2','T4','T6','T8','painSupport'])
if not dlg.OK:
    core.quit()  # the user hit cancel, so exit

params['painSupport'] = expInfo['painSupport']

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
logging.log(level=logging.INFO, msg='T2: %s' % expInfo['T2'])
logging.log(level=logging.INFO, msg='T4: %s' % expInfo['T4'])
logging.log(level=logging.INFO, msg='T6: %s' % expInfo['T6'])
logging.log(level=logging.INFO, msg='T8: %s' % expInfo['T8'])
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
fixation = visual.TextStim(win, pos=[0, 5], text='SAFE', font='Arial Hebrew', color='skyblue', alignHoriz='center',
                           bold=True, height=3.5)

fixationReady = visual.TextStim(win, pos=[0, 5], text='GET READY', font='Arial Hebrew', color='gray',
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

# load technical instruction images
techInstructionImage1 = visual.ImageStim(win, image=params['techInstructionImage1'], pos=(0, 0));
techInstructionImage2 = visual.ImageStim(win, image=params['techInstructionImage2'], pos=(0, 0));
technicalInstructionsSlides = [techInstructionImage1, techInstructionImage2]


# load Instructions images
image1 = visual.ImageStim(win, image=params['image1'], pos=(0, 0))
image2 = visual.ImageStim(win, image=params['image2'], pos=(0, 0))
image3 = visual.ImageStim(win, image=params['image3'], pos=(0, 0))
instructionsSlides = [image1, image2, image3]


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
painISI = [1, 1, 1, 1, 1, 1, 1, 1]
random.shuffle(painISI)

# read questions and answers from text files for instructions text, 3 Vass, and practice scale questions
[topPrompts, bottomPrompts] = BasicPromptTools.ParsePromptFile(params['promptDir'] + params['promptFile'])
print('%d prompts loaded from %s' % (len(topPrompts), params['promptFile']))

# PROMPTS FOR EXPLANATION - NOT USING
# [topPrompts1, bottomPrompts1] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts1.txt")
# print('%d prompts loaded from %s' % (len(topPrompts1), "InitialSafePrompts1.txt"))
#
# [topPrompts2, bottomPrompts2] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts2.txt")
# print('%d prompts loaded from %s' % (len(topPrompts2), "InitialSafePrompts2.txt"))
#
# [topPrompts3, bottomPrompts3] = BasicPromptTools.ParsePromptFile(params['promptDir'] + "InitialSafePrompts3.txt")
# print('%d prompts loaded from %s' % (len(topPrompts3), "InitialSafePrompts3.txt"))

[questions_vas1, options_vas1, answers_vas1] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile1'])
print('%d questions loaded from %s' % (len(questions_vas1), params['moodQuestionFile1']))

[questions_vas2, options_vas2, answers_vas2] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile2'])
print('%d questions loaded from %s' % (len(questions_vas2), params['moodQuestionFile2']))

[questions_vas3, options_vas3, answers_vas3] = BasicPromptTools.ParseQuestionFile(params['moodQuestionFile3'])
print('%d questions loaded from %s' % (len(questions_vas3), params['moodQuestionFile3']))

[questions_RatingPain, options_RatingPain, answers_RatingPain] = BasicPromptTools.ParseQuestionFile(params['MoodRatingPainFile'])
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
def GrowingSquare(color, block, trial, params):
    import time
    global painITI

    # set color of square
    if color == 1:
        col = 'darkseagreen'
        colCode = int('8fbc8f', 16)
        colorName='Green'
    elif color == 2:
        col = 'khaki'
        colCode = int('F0E68C', 16)
        colorName='Yellow'
    elif color == 3:
        col = 'lightcoral'
        colCode = int('F08080', 16)
        colorName='Red'
    elif color == 4:
        col = 'black'
        colCode = int('000000', 16)
        colorName = 'Black'
    else:
        col = 'gray'
        colCode = int('808080', 16)
        colorName='Black'

    trialStart = globalClock.getTime()
    phaseStart = globalClock.getTime()

    # Load pre-defined images of square at different sizes
    squareImages = []
    for i in range(1, 6):
        squareImages.append(visual.ImageStim(win, image=f"Circles2/{color}{colorName}_{i}.JPG", pos=(0, 0)))

    WaitForFlipTime()
    # gray color = during the instructions
    if col != 'gray':
        SetPort(color, 1, block)
    win.flip()

    for i in range(5):
        # Set size of rating scale marker based on current square size
        sizeRatio = squareImages[i].size[0] / squareImages[0].size[0]

        squareImages[i].draw()
        win.flip()

        # Wait for specified duration
        core.wait(2)

        # get new keys
        newKeys = event.getKeys(keyList=['q', 'escape'], timeStamped=globalClock)
        # check each keypress for escape keys
        if len(newKeys) > 0:
            for thisKey in newKeys:
                if thisKey[0] in ['q', 'escape']:  # escape keys
                    CoolDown()  # exit gracefully


        if col != 'gray':
            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "square",
                      globalClock.getTime() - phaseStart)

    if col != 'gray':
        print(time.time())
        SetPort(color, 2, block)
        phaseStart = globalClock.getTime()
        tNextFlip[0] = globalClock.getTime() + (params['painDur'])
        if params['painSupport']:
            my_pathway.start()
        # make sure can update rating scale while delaying onset of heat pain
        timer = core.Clock()
        timer.add(3 + random.sample(sleepRand, 1)[0])
        while timer.getTime() < 0:
            # rect.draw()
            squareImages[-1].draw()

            win.flip()
            BehavFile(globalClock.getTime(), block + 1, trial + 1, color, globalClock.getTime() - trialStart, "full",
                      globalClock.getTime() - phaseStart,)
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

        if params['painSupport']:
            response = my_pathway.stop()
        # Flush the key buffer and mouse movements
        event.clearEvents()

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
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T2']))]
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 2:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T4']))]
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 3:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T6']))]
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        elif color == 4:
            code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T8']))]
            logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))

        # FOR BLACK RANDOM - COMMENTED
        # elif color == 4:
        #     if randBlack[randBlackCount] == 2:
        #         code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T6']))]
        #         logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        #         randBlackCount += 1
        #     elif randBlack[randBlackCount] == 1:
        #         code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T4']))]
        #         logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        #         randBlackCount += 1
        #     elif randBlack[randBlackCount] == 0:
        #         code = excelTemps[excelTemps['Temp'].astype(str).str.contains(str(expInfo['T2']))]
        #         logging.log(level=logging.EXP, msg='set medoc %s' % (code.iat[0, 1]))
        #         randBlackCount += 1

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

def RunMoodVas(questions, options, name='MoodVas'):

    # Wait until it's time
    WaitForFlipTime()

    SetPortData(params['codeBaseline'])
    # display pre-VAS prompt
    if not params['skipPrompts']:
        BasicPromptTools.RunPrompts([params['PreVasMsg']], [reverse_string("לחץ על כל דבר כדי להמשיך")], win, message1, message2)

    # Display this VAS
    for i in range(len(questions)):
        question = [questions[i]]
        option = [options[i]]
        imgName = question[0].replace(' ', '_')
        imgName = imgName.replace('?', '')
        imgName = imgName.replace('\n', '')

        RunVas(question, option, questionDur=float("inf"), isEndedByKeypress=True, name=name)

    BasicPromptTools.RunPrompts([], [reverse_string("מנוחה קצרה")], win, message1, message2)
    tNextFlip[0] = globalClock.getTime()

    # wait until it's time to show screen
    WaitForFlipTime()
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(1)


def CoolDown():
    # Stop drawing ratingScale (if it exists)
    try:
        fixationCross.autoDraw = False
    except:
        print('fixation cross does not exist.')

    df = pd.DataFrame(listlist,
                      columns=['Absolute Time', 'Block', 'Trial', 'Color', 'Trial Time', 'Phase', 'Phase Time'])
    df.to_csv('avgFile%s.csv' % expInfo['subject'])

    message1.setText(reverse_string("הגענו לסוף הניסוי"))
    message2.setText(reverse_string("לחץ על אסקייפ כדי לסיים"))
    win.logOnFlip(level=logging.EXP, msg='Display TheEnd')

    message1.setFont('Arial Hebrew')
    message2.setFont('Arial Hebrew')
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
    AddToFlipTime(1)
    tNextFlip[0] = globalClock.getTime() + 1.0

    # COMMENTED OUT NEED TO PRESS SPACE BEFORE PROCEEDING TO NEXT SLIDE
    # message1.setText(reverse_string("הסתיים הבלוק הנוכחי"))
    # message2.setText(reverse_string("לחץ על מקש הרווח כדי להתקדם"))
    # win.logOnFlip(level=logging.EXP, msg='BetweenBlock')
    #
    # message1.setFont('Arial Hebrew')
    # message2.setFont('Arial Hebrew')
    # message1.draw()
    # message2.draw()
    # win.flip()
    #
    # thisKey = event.waitKeys(keyList=['space'])  # use space bar to avoid accidental advancing
    # if thisKey:
    #     tNextFlip[0] = globalClock.getTime() + 2.0

def BehavFile(absTime, block, trial, color, trialTime, phase, phaseTime):
    list = [absTime, block, trial, color, trialTime, phase, phaseTime]
    listlist.append(list)

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
        for slide in technicalInstructionsSlides:
            slide.draw()
            win.flip()
            event.waitKeys(keyList=['space'])
        WaitForFlipTime()
        SetPortData(params['codeVAS'])
        RunMoodVas(questions_vas1, options_vas1, name='PreVAS')
        # RunPrompts() We don't use "Run Prompts", but give instructions as text
        # Present each slide and wait for spacebar input to advance to the next slide
        for slide in instructionsSlides:
            slide.draw()
            win.flip()
            event.waitKeys(keyList=['space'])
        WaitForFlipTime()



    if block == 2: # If it's the second block, stops drawing the anxiety slider and fixation cross, runs a mood VAS rating task, displays some prompts, and sets the next stimulus presentation time to 4-6 seconds in the future.
        print("got to block 2 if statement")
        fixation.autoDraw = False

        # Run VAS after 2nd block
        RunMoodVas(questions_vas2, options_vas2, name='MidRun')

        # Rest slide
        message1.setText(reverse_string("מנוחה קצרה"))
        message1.setFont('Arial Hebrew')
        message1.draw()
        win.flip()

        timer = core.Clock()
        timer.add(random.randint(1, 2))
        while timer.getTime() < 0:
            win.flip()

        tNextFlip[0] = globalClock.getTime() + random.randint(1, 2)

        # BasicPromptTools.RunPrompts(["Thank you for your responses."], ["Press the space bar to continue."], win,message1, message2)
        # thisKey = event.waitKeys(keyList=['space'])  # use space bar to avoid accidental advancing
        # if thisKey:
        #     tNextFlip[0] = globalClock.getTime() + random.randint(4, 6)

    # wait before first stimulus
    fixationCross.draw()
    win.logOnFlip(level=logging.EXP, msg='Display Fixation')
    win.flip() # Flip the window to display the fixation cross
    core.wait(1) # Change to that: random.randint(4, 6)

    # wait until it's time to show screen
    WaitForFlipTime()
    # show screen and update next flip time
    win.flip()
    AddToFlipTime(1)

    win.callOnFlip(SetPortData, data=params['codeBaseline']) # Calls a function to set the port data to the baseline code.

    # Waits for 2 seconds before displaying the first stimulus.
    while (globalClock.getTime() < tNextFlip[0] + 2):

        win.flip()  # to update ratingScale

    arrayLength = 1
    painITI = 0

    ############################################

    # Starts a loop to present each trial.
    for trial in range(params['nTrials']):

        color = color_list[trial] # Selects the color for this trial.

        # Calls the GrowingSquare function to present the stimulus, and records the start time and phase start time.
        trialStart, phaseStart = GrowingSquare(color_list[trial], block, trial, params)
        win.flip() # Flips the screen and waits for 2 seconds.
        core.wait(1)

        # Sets the next stimulus presentation time.
        tNextFlip[0] = globalClock.getTime() + (painISI[painITI])
        painITI += 1
        RunMoodVas(questions_RatingPain, options_RatingPain, name='PainRatingScale')
        WaitForFlipTime()
        tNextFlip[0] = globalClock.getTime() + random.randint(2, 4)

    ### THE FIXATION "SAFE" AND "GET READY" WAS DELETED FROM HERE ###

    ############################################

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


WaitForFlipTime() #  This waits for the next screen refresh.

RunMoodVas(questions_vas3, options_vas3, name='PostRun') # This displays a mood VAS after the experiment is completed.

WaitForFlipTime() # This waits for the next screen refresh.

# Log end of experiment
logging.log(level=logging.EXP, msg='--- END EXPERIMENT ---')

# clean-up & exit experiment
CoolDown()


