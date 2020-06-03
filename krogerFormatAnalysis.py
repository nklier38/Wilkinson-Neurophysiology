
import os
import csv
import numpy as np
import traceback
import re

columns = ['ramp number', 'stretch marker time', 'Stretch length', 'Stretch speed', 'Resting Discharge FPS', 'RD SD', 'Dynamic Peak', 'Dynamic Index', 'IST FPS', 'IST FPS SD', 'IST inst freq', 'FST FPS', 'FST SD', 'FST inst freq']
ranges = [[0,0],[0,0],[0, 9.9], [9.9, 10.25], [0,0], [10.25, 10.75], [13.25, 13.75], [0,0],[0,0]]
stretchLengthInd = 0 #constant indeces in the ranges and column arrays, allows for their use without magic numbers
stretchSpeedInd = stretchLengthInd + 1
RDind = stretchLengthInd +2
DPind = stretchLengthInd +3
DIind = stretchLengthInd +4
ISTind = stretchLengthInd +5
FSTind = stretchLengthInd +6
EartagIndInName = 2 #in the split name file
MuscleIndInName = 1
stretchLengths = ['2.50%', '2.50%','2.50%', '2.50%', '2.50%','2.50%','2.50%', '2.50%','2.50%','5.00%','5.00%','5.00%','5.00%','5.00%','5.00%','5.00%','5.00%','5.00%','7.50%','7.50%','7.50%', '7.50%','7.50%','7.50%','7.50%','7.50%','7.50%']
stretchSpeeds = ['20%', '20%','20%','40%','40%','40%','60%','60%','60%','20%', '20%','20%','40%','40%','40%','60%','60%','60%','20%', '20%','20%','40%','40%','40%','60%','60%','60%']



def statsOverRange(lowerBound, upperBound, data): #highly inefficient, but small data set means this is not a huge concern. Takes the lowerbound and upperbound times, and loops through data and returns a length 2 list with the maximum frequency and FPS average over range
    maxFreq = -1.0
    timeInd = 0
    freqInd = 1
    spikeCount = 0.0
    dpset = False
    interval = upperBound-lowerBound #time of the interval
    differSet = [] #a list of the time differences between spikes within the interval range
    totalFreq = 0.0
    for index, spike in enumerate(data):#loops through the entire dataset
      #  #index)
        time = spike[timeInd]
        freq = spike[freqInd]
        if (time >= lowerBound) & (time < upperBound): #when it reaches the proper range, stats are calculated
            spikeCount += 1 #counts spikes in interval range
            totalFreq += freq
            if(freq > maxFreq):
                maxFreq = freq
                dpset = True
            if(index < (len(data) - 1)):
                #print(data[index + 1]) 
                differSet.append(data[index + 1][timeInd] - spike[freqInd]) #PROBLEMS OCCUR HERE WITH SOME FILES
    #differSet)
    #del differSet[-1] #removes the last element of differ set, which is the time difference between a spike out of range and a spike in range
    with np.errstate(all = 'ignore'):
        stanDev = np.std(differSet)
    FPS = spikeCount/interval #FPS calulation is done as the spikes per time
    try:
        instFreq = totalFreq/spikeCount
    except:
        instFreq = 0
    if not dpset:
        maxFreq = 0
    return [FPS, maxFreq, stanDev, instFreq] #can add any additional calculations to this list and then pass it to analyze

def process(dataFolder): #"manager" method. Takes all relevant data files, pairs them with their length files, and runs analyze on every pair of files with the appropriate inputs.
    pairedFiles = []
    badFiles = []
    analyzedCount = 0
    #pairedFiles)
    files_list = os.listdir(dataFolder)
    for item in files_list:   #pairing length files to output files
        file_name = str(item)
        if file_name[-11:] == 'lengths.csv' and file_name[:-11]+'output.csv' in files_list: #pairing taken from old code
            pairedFiles.append([file_name, file_name[:-11]+'output.csv'])
        elif file_name[-11:] == 'lengths.csv' and file_name[:-11]+'outputs.csv' in files_list: 
            pairedFiles.append([file_name, file_name[:-11]+'outputs.csv'])
        elif file_name[-11:] == 'lengths.csv' and file_name[:-11]+'output.csv' not in files_list:
            print('ERROR! There is no corresponding spike output file for length file with name '+ file_name)
    #pairedFiles)
    for item in pairedFiles:
       # brokenName = str(item[0]).split("_") # splits name into each seperate bit of information, allowing them to be retrieved easily
        brokenName = re.split('_|-| ', str(item[0]))
        fixedBrokenName = brokenName[:-1]
        #brokenName)
        try:
            import europeanReader as eu
            lengths = eu.openCSV(dataFolder, str(item[0]))
            #print(lengths)
            data = eu.openCSV(dataFolder, str(item[1]))
        except ImportError:
            lengths = openCSV(dataFolder, str(item[0]))
            data = openCSV(dataFolder, str(item[1]))
        dataByTime = getFreqs(data)
        
#        print("now analyzing: " + "_".join(fixedBrokenName)) #uncomment this section and comment out the below if you want the code to terminate on an error
#        analyzedData = analyze(dataByTime, lengths, brokenName)
#        analyzedName = "_".join(fixedBrokenName) + "_analyzed.csv"
#        formatWrite(analyzedData, 'analyzedTimeOnly', analyzedName)
#        analyzedCount += 1
        
        try:
            print("now analyzing: " + "_".join(fixedBrokenName))
            analyzedData = analyze(dataByTime, lengths, brokenName)
            analyzedName = "_".join(fixedBrokenName) + "_analyzed.csv"
            formatWrite(analyzedData, 'analyzed', analyzedName)
            analyzedCount += 1
        except Exception as e:
            traceback.print_exc()
            print("problem file: " + str(item[0]) + '. problem shown above.')
            badFiles.append(str(item[0]))
    if not (len(badFiles) == 0):
        print("analyzed " + str(analyzedCount) + " out of " + str(len(pairedFiles)) + " files successfully. Files not analyzed: ")
        for name in badFiles:
            print(name)
        print("double check that inputs have been set up correctly. If they have and the error is still occuring, double check the labchart file. If that doesn't work, contact Nikola.")
    print("done")
def getFreqs(data):
    newData = []
    data = sorted(data)
    for x in range(0, len(data) - 1):
        #print(data[x + 1][0])
        #print((data[x][0]))
        if(data[x+1][0] != data[x][0]):
            newData.append([data[x][0], (1/((data[x + 1][0]) - (data[x][0])))])
    return newData


def detectAdjust(markers, lengths):
    print("deciding between a marker to stretch interval of 10 seconds or 14 seconds...")
    #sample first 10 seconds for the baseline length
    #set arbitrary threshold for detcting a stretch 12 seconds out: call it like +0.2
    #if detect stretch, you're good. If don't detect stretch, try detecting ~16 seconds out.
    #if neither pass, deafault to 10- it could be a vibration or something
    #if 14 passes, then use that
    #if both pass, what kind of weird macro format are you using? 
    #will only test the first event, as it SHOULD be consistent throughout the macro
    #but, if there are errors, this would be something to double check for the file that messes things up
    thresh = 0.2
    baselineTot = 0.0
    baselinePoints = 0.0
    timePoint = lengths[0][0]
    ind = 0
    print(markers)
    while(timePoint < markers[0][0] + 5):
        if(timePoint > markers[0][0]):
            baselineTot += lengths[ind][1]
            baselinePoints += 1
        timePoint = lengths[ind][0]
        ind +=1
    avBL = baselineTot/baselinePoints
    rampThreshold = avBL + thresh
    
    #sample 10 seconds
    
    tenSecCheck = markers[0][0] + 12
    frtnSecCheck = markers[0][0] + 16
    tenSecPass = False
    frtnSecPass = False
    tenSecChecked = False
    
    for point in lengths:
        if(point[0] > tenSecCheck and not tenSecChecked):
            tenSecChecked = True
            if(point[1] > rampThreshold):
                tenSecPass = True
        if(point[0] > frtnSecCheck):
            if(point[1] > rampThreshold):
                frtnSecPass = True
            break
    
    if(tenSecPass and not frtnSecPass):
        print("Normal macro format. Interval set to 10 seconds.")
    if(frtnSecPass and not tenSecPass):
        print("14 second interval detected. Adjusting time ranges.")
        adjustRanges(4)
    if(not tenSecPass and not frtnSecPass):
        print("no ramp detected. Vibration is possible. Using standard 10 second interval.")
    if(tenSecPass and frtnSecPass):
        print("unrecognized macro format. Interval may be something other than 10 or 14 seconds. Adjust code or contact Nikola accordingly. Defaulting to 10 second interval")
    

def getOldMarkers(data): #time index 0, length index 1, tension index 2
   markers = []
   for index in range(0, 18):
       if (index%2 == 0):
           markers.append(data[index])
   return markers
def analyze(data, lengths, brokenName): #data is a 2 dimensional array representation of the output CSV. Length is the same for the lengths file. Broken name is an array with each element of the name, used to get muscle number and date
    final = [columns] #list final will be a two dimensional array that will be written into a CSV. top row is the header, each subsequent row is data from a ramp
    #print(lengths)
    if(len(lengths) > 40):
        allMarkers = getMarkers(lengths) 
    else:
        allMarkers = getOldMarkers(lengths)# will return a two dimensional list. each sub list is length three and represents the timestamp, length value, and tension value at the lengths channel markers
    detectAdjust(allMarkers, lengths)
    eartag = brokenName[EartagIndInName]
    date = brokenName[0]
    #print(allMarkers)
    #len(allMarkers))
    muscle = brokenName[MuscleIndInName]
    rampCounters = 0 #probably redundant with x below but I'm scared to touch it because it works 
    FPS = 0
    maxFreq = 1
    stanDev = 2
    instFreqInd = 3
    x = 0
    totRamps = 0
    vibeSkipCounter = 0 #tallies the number of ramps that have been analyzed so that it can skip the vibrations in between seqeunces of stretch
    while x < len(allMarkers): #27 ramps in this format
        totRamps += 1
        
        markerRow = allMarkers[x]
        marker = markerRow[0]
        #marker)
        #x)
        row = [totRamps]
        row.append(marker)
#        print(len(stretchLengths))
#        print(rampCounters)
        row.append(stretchLengths[rampCounters]) #stretch length from set list
        row.append(stretchSpeeds[rampCounters]) #stretch speed from set list
        rampCounters += 1 #allows for iteration over set lists
        RD = statsOverRange(marker, marker + ranges[RDind][1], data) #statsOverRange returns a length 2 list, index 0 being the average FPS in the range and index 2 being the peak frequecy in the range
        DP = statsOverRange(marker + ranges[DPind][0], marker + ranges[DPind][1], data)
        IST = statsOverRange(marker + ranges[ISTind][0], marker + ranges[ISTind][1], data)
        DI = DP[maxFreq] - IST[instFreqInd]
        FST = statsOverRange(marker + ranges[FSTind][0], marker + ranges[FSTind][1], data)
        row.append(RD[FPS])
        row.append(RD[stanDev])
        row.append(DP[maxFreq])
        row.append(DI)
        row.append(IST[FPS])
        row.append(IST[stanDev])
        row.append(IST[instFreqInd])
        row.append(FST[FPS])
        row.append(FST[stanDev])
        row.append(FST[instFreqInd])
        final.append(row)
        x += 1
        vibeSkipCounter += 1
        if(vibeSkipCounter%27 == 0) and (vibeSkipCounter is not 0):
            rampCounters = 0
            vibeSkipCounter = 0
            x += 16
    return final
def getMarkers(data): #time index 0, length index 1, tension index 2
   thresholdA = float(float(data[0][1]) + 2.0)
   thresholdB = float(float(data[0][1]) + 2.0)
   markers = []
   currentIndex = 0
   for index in range(0, len(data)):
       r = data[index]
       if currentIndex != 0:
         try:
            thresholdA = (float(float(data[int(currentIndex - 1)][1])) + 2.0)
            thresholdB = (float(float(data[int(currentIndex + 1)][1])) + 2.0)

         except Exception as error:
            pass      
       isfloat = True
       try:
         x = float(r[1])
       except Exception:
         pass
       if (x > thresholdA) & (x > thresholdB) & isfloat:
         markers.append(r)
       currentIndex = currentIndex + 1
   return markers
    
def openCSV(path, fileName):
   data_f = open(path + os.sep + fileName)
   data_table = []
   for r in data_f:
         for row in r.split('\n'):
            currentRow = row.split(',')
            fixedRow = []
            for item in currentRow:
               try:
                  fixedRow.append(float(item)) 
               except:
                  pass
            if fixedRow != []:
               data_table.append(fixedRow)
   data_table = [x for x in data_table if x != ['']]
   return data_table
    
def formatWrite(analyzed, foldername, filename):
   with open(foldername+os.sep+filename, "w", newline='') as analyzedFile:
      writer = csv.writer(analyzedFile)
      writer.writerows(analyzed)      

def adjustRanges(adjVal):
    for x in range(0, len(ranges)): 
        for y in range(0, 2):
            ranges[x][y] = ranges [x][y] + adjVal



if __name__ == '__main__':
    #adjustRanges(4)  #Delete this line when using a normal 10 second range

    process('data')