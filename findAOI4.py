# poss = [[-300,40],[300,40],[300,-40],[-300,-40]] # Get Ready
# poss = [[-300,-300],[300,-210],[300,-300],[-300,-210]] # VAS
# poss = [[-130,40],[130,40],[130,-40],[-130,-40]] # SAFE
# poss = [[-40,40],[40,40],[40,-40],[-40,-40]] # Fixation Cross
# poss = [[-10,-260],[-10,-270],[10,-260],[10,-270]] # VAS center
import sys
sys.path.insert(1, './src')
import time
from EyeTrackerCalibration import EyeTrackerCalibration,eyeLinkFinishRecording
from psychopy import visual,core
import numpy as np

params = {

'questionDownKey': '1',   # move slider left
    'questionUpKey':'2',      # move slider right
}

## Setup Psychopy Window.
screenRes = [1024,768]
# win = visual.Window((1024,768), monitor="testMonitor",color="white",winType='pyglet')
win = visual.Window(screenRes, allowGUI=False, monitor='testMonitor', units='deg', name='win',color=(217,217,217),colorSpace='rgb255')
img = visual.ImageStim(win=win, image="img/10.jpg", units="pix", opacity=1)
                        # size=screenRes)

fixation = visual.TextStim(win, pos = [0,0], text = 'SAFE', font = 'Helvetica Bold', color = 'skyblue', alignHoriz = 'center', bold = True, height = 3)

# Create ratingScale
name='Question'
textColor='black'
pos=(0.,-0.70)
stepSize=1.
scaleTextPos=[0.,-0.50]
labelYPos=-0.75
markerSize=0.1
tickHeight=0.0
tickLabelWidth=0.0
downKey=params['questionDownKey']
upKey=params['questionUpKey']
selectKey=[]
hideMouse=True
options = ["Not Anxious","Very Anxious"]
question = ''
markerStim = visual.ShapeStim(win, lineColor=textColor, fillColor=textColor, vertices=(
(-markerSize / 2., markerSize * np.sqrt(5. / 4.)), (markerSize / 2., markerSize * np.sqrt(5. / 4.)), (0, 0)),
                              units='norm', closeShape=True, name='triangle');
# tickMarks = np.linspace(0,100,len(options[iQ])).tolist()
tickMarks = np.linspace(0,100,len(options[0])).tolist()

ratingScale = visual.RatingScale(win, scale=question, \
                                 low=0., high=50., markerStart=25., precision=1., labels=options,
                                 tickHeight=tickHeight, \
                                 marker=markerStim, markerColor=textColor, markerExpansion=1, singleClick=False,
                                 disappear=False, \
                                 textSize=0.8, textColor=textColor, textFont='Helvetica Bold', showValue=False, \
                                 showAccept=False, acceptKeys=selectKey, acceptPreText='key, click',
                                 acceptText='accept?', acceptSize=1.0, \
                                 leftKeys=downKey, rightKeys=upKey, respKeys=(), lineColor=textColor, skipKeys=[], \
                                 mouseOnly=False, noMouse=hideMouse, size=1.0, stretch=1.5, pos=pos, minTime=0.4,
                                 maxTime=np.inf, \
                                 flipVert=False, depth=0, name=name, autoLog=True)
# fixationReady = visual.TextStim(win, pos = [0,0], text = 'GET READY', font = 'Helvetica Bold', color = 'gray', alignHoriz = 'center', bold = True, height = 3,wrapWidth=500)
# fixationCross = visual.ShapeStim(win,lineColor='#000000',lineWidth=5.0,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');

# fixationReady.draw()
# img.draw()
# rect = visual.Rect(win=win, units='norm', size=0.1, fillColor='red', lineColor='red', lineWidth=20)
# poss = [[240,-260],[240,-270],[220,-260],[220,-270]] # VAS (right)
# poss = [[-240,-260],[-240,-270],[-220,-260],[-220,-270]] # VAS (left)



ratingScale.draw()
win.flip()

while ratingScale .noResponse:
    ratingScale.draw()
    R = ratingScale.getRating()
    print(R)

    poss = [[9.2 * R - 230 + 25, -225], [9.2 * R - 230 + 25, -270], [9.2 * R - 230 - 25, -225], [9.2 * R - 230 - 25, -270]]  # VAS (right)
    for pos in poss:
        # img.draw()

        circle2 = visual.Circle(win=win, units="pix", fillColor='black', lineColor='white', edges=1000, pos=pos,
                                radius=3)
        circle2.draw()

    win.flip()


sizeDiff2 = circle2.pos * 0.216

# for i in range(180):
#     # timer = core.Clock()
#     # timer.add(0.0665)
#     rect.size += 0.0216
#
#     # print(rect.size)
#     rect.draw()
#     circle2.pos += sizeDiff2
#     circle2.draw()
#
#     win.flip()
#     core.wait(0.06)

win.close()
