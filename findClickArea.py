import sys
sys.path.insert(1, './src')
import time
from EyeTrackerCalibration import EyeTrackerCalibration,eyeLinkFinishRecording
from psychopy import visual,core
import numpy as np

eyeLinkSupport = True
eyeLinkDebug = True
params = {
    'screenSize' : (1024,768),
}

# Eyelink Calibration
if eyeLinkSupport:
    tracker = EyeTrackerCalibration(params['screenSize'])

# Eyelink start recording
if eyeLinkSupport:
    tracker.setRecordingState(True)

## Setup Psychopy Window.
win = visual.Window((1024,768), monitor="testMonitor",color="black",winType='pyglet')
rect = visual.Rect(win=win, units='norm', size=0.1, fillColor='red', lineColor='red', lineWidth=20)
circle2 = visual.Circle(win=win, units="pix", fillColor='black', lineColor='white', edges=1000,pos=(26, 19.5),radius=2)

if eyeLinkDebug and eyeLinkSupport:
    circle = visual.Circle(win=win, units="pix", fillColor='black', lineColor='white', edges=1000, pos=(0, 0),
                           radius=10)
rect.draw()
circle2.draw()
win.flip()
# win.close()

sizeDiff2 = circle2.pos * 0.216

# Eyelink OI Initialization (initial value)
if eyeLinkSupport:
    aoiPoint = np.array([26,19.5])
    aoiDiff = aoiPoint * 0.216

# Start Eyelink Trial label
if eyeLinkSupport:
    tracker.sendMessage('TRIAL_RESULT 0')
    tracker.sendMessage('TRIALID %d' % 0)

for i in range(180):
    # timer = core.Clock()
    # timer.add(0.0665)
    rect.size += 0.0216

    # print(rect.size)
    rect.draw()
    circle2.pos += sizeDiff2
    circle2.draw()

    if eyeLinkDebug and eyeLinkSupport:
        position = tracker.getPosition()
        if position != None and type(position) != int:
            circle.pos = position
            circle.draw()

    win.flip()
    if eyeLinkSupport:
        aoiTimeStart = time.time() * 1000
    core.wait(0.06)

    if eyeLinkSupport:
        aoiTimeEnd = time.time() * 1000
        aoiPoint += aoiDiff
        tracker.sendMessage('!V IAREA %d %d RECTANGLE %d %d %d %d %d %s' % (int(aoiTimeEnd - aoiTimeStart), 0,
                                                                            1, 512 - aoiPoint[0],
                                                                            390 - aoiPoint[1],
                                                                            512 + aoiPoint[0],
                                                                            390 + aoiPoint[1],
                                                                            'growing rectangle(red)'))
win.close()


# Finish recording
outEDF = "test.EDF"
tracker = eyeLinkFinishRecording(tracker,outEDF)

# tracker.sendMessage('TRIAL_RESULT 0')
# tracker.setRecordingState(False)
# # open a connection to the tracker and download the result file.
# trackerIO = pylink.EyeLink('100.1.1.1')
# trackerIO.receiveDataFile("et_data.EDF", 'test.EDF')

# tracker.sendMessage('!V IAREA %d %d RECTANGLE %d %d %d %d %d %s' % (int(aoiTimeEnd - aoiTimeStart), 0,
#                                                                     1, 512 - circle2.pos[0],
#                                                                     390 - circle2.pos[1],
#                                                                     512 + circle2.pos[0],
#                                                                     390 + circle2.pos[1],
#                                                                     'growing rectangle(' + rect.fillColor) + ')')


# 3.988

# circle = visual.Circle(win=win, units="pix", fillColor='black', lineColor='white', edges=1000,
#                        pos=(110,-320),
#                        radius=5)
#
# circle.draw()
# rect.draw()
# win.flip()
#
# c = event.getKeys()

# Green: (-350,-320), (-350,290), (-110,290), (-110,-320)
# Red: (350,-320), (350,290), (110,290),(110,-320)

# rect = visual.Rect(win=win, units = 'norm', size = 0.1, fillColor = col, lineColor = col, lineWidth = 20)
#     rect.draw()