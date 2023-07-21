# PsychoPy2Research
A repository for building a psychology experiment for stress and anxiety

## Instructions

### Changes Needed in Main.py in Order to Connect to External Devices

1. Change 'sendPortEvents' param from 'False' to 'True' in 'params' dictionary
2. change 'portAddress' to the correct port address
3. Change 'painSupport' param from 'False' to 'True' in 'expInfo' dictionary
4. Set proper IP in that line: my_pathway = 'Pathway(ip='10.150.254.8', port_number=20121)'
5. Set 'convExcel'


### Relevant Constants

1. 'nTrials' - number of trials
2. 'nBlocks' - number of blocks
3. 'questionDur' - Duration of a question

