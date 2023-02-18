# poss = [[-350,140],[-350,50],[350,50],[350,140]] # question
# poss = [[-400,-160],[-400,-40],[400,-160],[400,-40]] # VAS
import sys
sys.path.insert(1, './src')
import time
from EyeTrackerCalibration import EyeTrackerCalibration,eyeLinkFinishRecording
from psychopy import visual,core
import numpy as np

## Setup Psychopy Window.
screenRes = [1024,768]
# win = visual.Window((1024,768), monitor="testMonitor",color="white",winType='pyglet')
win = visual.Window(screenRes, allowGUI=False, monitor='testMonitor', units='deg', name='win',color=(217,217,217),colorSpace='rgb255')
img = visual.ImageStim(win=win, image="img/How_is_your_mood_right_now", units="pix", opacity=1)
                        # size=screenRes)

fixation = visual.TextStim(win, pos = [0,5], text = 'SAFE', font = 'Helvetica Bold', color = 'skyblue', alignHoriz = 'center', bold = True, height = 3.5)
# fixationReady = visual.TextStim(win, pos = [0,0], text = 'GET READY', font = 'Helvetica Bold', color = 'gray', alignHoriz = 'center', bold = True, height = 3,wrapWidth=500)
# fixationCross = visual.ShapeStim(win,lineColor='#000000',lineWidth=5.0,vertices=((fCP[0]-fCS/2,fCP[1]),(fCP[0]+fCS/2,fCP[1]),(fCP[0],fCP[1]),(fCP[0],fCP[1]+fCS/2),(fCP[0],fCP[1]-fCS/2)),units='pix',closeShape=False,name='fixCross');

# fixationReady.draw()
img.draw()
# rect = visual.Rect(win=win, units='norm', size=0.1, fillColor='red', lineColor='red', lineWidth=20)
poss = [[-400,-160],[-400,-40],[400,-160],[400,-40]] # VAS
for pos in poss:
    circle2 = visual.Circle(win=win, units="pix", fillColor='black', lineColor='white', edges=1000,pos=pos,radius=3)
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

# win.close()
