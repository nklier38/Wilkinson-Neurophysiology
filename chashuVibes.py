
import os
import csv
import numpy as np
import traceback
import re
import matplotlib.pyplot as plt

columns = columns = ['Vibration amplitude', 'Vibration frequency', 'BL FPS', 'BL FPS SD', 'BL av. inst. freq.', 'vibration FPS', 'vibration FPS SD', 'vibration av inst. freq', 'Entrainment: length of cycle in seconds', 'Entrainment: mean firing time from cycle start', 'entrainment: position 0 to 1', 'cycle position standard deviation', 'number of cycles with spikes', 'total cycles in vibration', 'percent of cycles with spikes', 'Eartag number', 'Muscle number', 'date']

EartagIndInName = 2 #in the split name file
MuscleIndInName = 1
stretchAmps = [5 , 5 , 5 , 5 , 25 , 25 , 25 , 25 , 50 , 50 , 50 , 50 , 75 , 75 , 75 , 75, 1, 1, 1, 1, 1, 1, 1, 1] #in micrometers
stretchFreqs = [10, 25, 50, 100, 10, 25, 50, 100, 10, 25, 50, 100, 10, 25, 50, 100, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1] # in hz



def statsOverRange(lowerBound, upperBound, data):
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
            data = eu.openCSV(dataFolder, str(item[1]))
        except ImportError:
            lengths = openCSV(dataFolder, str(item[0]))
            data = openCSV(dataFolder, str(item[1]))
        dataByTime = getFreqs(data)
        
#        print("now analyzing: " + "_".join(fixedBrokenName)) #uncomment this section and comment out the below if you want the code to terminate on an error
#        analyzedData = analyze(dataByTime, lengths, brokenName)
#        analyzedName = "_".join(fixedBrokenName) + "_analyzed.csv"
#        formatWrite(analyzedData, 'vibrations', analyzedName)
#        analyzedCount += 1
        
        try:
            print("now analyzing: " + "_".join(fixedBrokenName))
            analyzedData = analyze(dataByTime, lengths, brokenName)
            analyzedName = "_".join(fixedBrokenName) + "_vibrations.csv"
            formatWrite(analyzedData, dataFolder + 'Vibrations', analyzedName)
            analyzedCount += 1
        except Exception as e:
            traceback.print_exc()
            print("problem file: " + str(item[0]) + '. problem shown above.')
            badFiles.append(str(item[0]))
    print("analyzed " + str(analyzedCount) + " out of " + str(len(pairedFiles)) + " files successfully. Files not analyzed: ")
    for name in badFiles:
        print(name)
    print("double check that inputs have been set up correctly. If they have and the error is still occuring, double check the labchart file. If that doesn't work, contact Nikola.")
    
def getFreqs(data):
    newData = []
    data = sorted(data)
    for x in range(0, len(data) - 1):
        #print(data[x + 1][0])
        #print((data[x][0]))
        if(data[x+1][0] != data[x][0]):
            newData.append([data[x][0], (1/((data[x + 1][0]) - (data[x][0])))])
    return newData

def getOldMarkers(data): #time index 0, length index 1, tension index 2
   markers = []
   for index in range(0, 18):
       if (index%2 == 0):
           markers.append(data[index])
   markers.extend(data[18:])
   return markers

def analyze(data, lengths, brokenName): #data is a 2 dimensional array representation of the output CSV. Length is the same for the lengths file. Broken name is an array with each element of the name, used to get muscle number and date
    final = [columns] #list final will be a two dimensional array that will be written into a CSV. top row is the header, each subsequent row is data from a ramp
    if(len(lengths) > 40):
        allMarkers = getMarkers(lengths) 
    else:
        allMarkers = getOldMarkers(lengths)# will return a two dimensional list. each sub list is length three and represents the timestamp, length value, and tension value at the lengths channel markers
    eartag = brokenName[EartagIndInName]
    date = brokenName[0]
    #len(allMarkers))
    muscle = brokenName[MuscleIndInName]
    vibeCounters = 0 #probably redundant with x below but I'm scared to touch it because it works 
    FPS = 0
    maxFreq = 1
    stanDev = 2
    instFreqInd = 3
    allHistogramData = []
    percentages = []
    print(allMarkers)
    if(len(allMarkers) is not 25):
        print("marker warning on file. Total marker number should be 25, is actually " + str(len(allMarkers)))
        print(allMarkers)
    for x in range(9, len(allMarkers)): #9 ramps in this format, the vibrations start
        markerRow = allMarkers[x]
        marker = markerRow[0]
        row = []
        #print(vibeCounters)
        thisVibeFreq = stretchFreqs[vibeCounters]
        row.append(str(stretchAmps[vibeCounters]) + "um")
        row.append(str(thisVibeFreq) + "hz")
        vibeCounters += 1 #allows for iteration over set lists
        RD = statsOverRange(marker, marker + 10, data) #statsOverRange returns a length 2 list, index 0 being the average FPS in the range and index 2 being the peak frequecy in the range
        vibeStats = statsOverRange(marker + 10, marker + 19, data)
        row.append(RD[FPS])
        row.append(RD[stanDev])
        row.append(RD[instFreqInd])
        row.append(vibeStats[FPS])
        row.append(vibeStats[stanDev])
        row.append(vibeStats[instFreqInd])
        entrainStats = entrainmentStats(data, marker + 10, thisVibeFreq)
        row.extend(entrainStats[0]) #'Entrainment: length of cycle in seconds', 'Entrainment: mean firing time from cycle start', 'entrainment: position 0 to 1', 'cycle position standard deviation', 'number of cycles with spikes', 'total cycles in vibration', 'percent of cycles with spikes'
        row.append(eartag)
        row.append(muscle)
        row.append(date)
        allHistogramData.append(entrainStats[1])
        percentages.append(row[14])
        final.append(row)
    #genUnifiedGraph(allHistogramData, brokenName, percentages)
    return final

def genUnifiedGraph(histograms, brokenName, percentages):                                    
    brokenName.append("figures.pdf")
    plt.figure(figsize=[20, 20])                                       
    for x in range(0, 16):
        print(percentages)
        percent = round(percentages[x], 2)
        plt.subplot(4, 4, x +1)
        plt.title(str(stretchAmps[x]) +" um stretch at " + str(stretchFreqs[x]) + "hz")      
        plt.xlabel("position in cycle")
        plt.ylabel("spike count")
        yScale = 50
        plt.ylim(top = yScale)
        plt.text(150, yScale * 0.9, str(percent) + "%", fontsize = 'large')
        #plt.xlim(right = 2000)
        plt.plot(histograms[x])   
    plt.savefig("vibrations" + os.sep + "histograms" + os.sep + "_".join(brokenName))

def entrainmentStats(data, vibeStart, vibefreq):
    cycleData = getOneCycleRepresentation(data, vibeStart, vibefreq)
    singleCycleRep = cycleData[0]
    histogramData = getHistogramRepresentation(singleCycleRep, vibefreq)
    stats = []
    cycleTime = 9/vibefreq
    meanTimeStamp = np.mean(singleCycleRep)
    stats.append(cycleTime)
    stats.append(meanTimeStamp)
    stats.append(meanTimeStamp/cycleTime)
    stats.append(np.std(singleCycleRep))
    numSpikes = len(singleCycleRep)
    numCycles = vibefreq * 9
    stats.append(numSpikes)
    stats.append(numCycles)
    stats.append(cycleData[1]*100/numCycles)
    return [stats, histogramData]

def getHistogramRepresentation(differences, vibefreq):
    differences.sort()
    indeces = [int(i * 20000) for i in differences]
#    plt.plot(indeces)
#    plt.show()
    pointsPerCycle = int((1/vibefreq)*20000)
    counts = [0] * pointsPerCycle
    for x in range(0, pointsPerCycle):
        for spike in indeces:
            if spike == x:
                #print("if statement triggered")
                counts[x] += 1
    return adjustHistData(counts,vibefreq)
def adjustHistData(counts, freq):
    adjustedData = []
    numInStep = 100/freq
    subCount = 0
    for x in range(0, len(counts)):
        subCount += counts[x]
        if (x%numInStep == 0):
            adjustedData.append(subCount)
            subCount = 0
    return adjustedData
    
def generateCycleStarts(vibeStart, vibeFreq):
    cycleStarts = []
    cycleStep = 1/vibeFreq
    currentVibeMark = vibeStart
    while(currentVibeMark < (vibeStart +9)):
        cycleStarts.append(currentVibeMark)
        currentVibeMark += cycleStep
    return cycleStarts

def getOneCycleRepresentation(data, vibeStart, vibefreq):
    vibeEnd = vibeStart + 9
    vibeTimes = []
    cycleStep = 1/vibefreq
    cycleStarts = generateCycleStarts(vibeStart, vibefreq) #returns a list of marks at the timestamp of each cycle start. Basically the vibeStart, and then vibeStart + certain number of cycle seconds
    cycleCounted = False
    uniqueCycleSpikes = 0
    for item in data: #basic loop adding timestamps in the vibration range of times to one single array where they can be manipulated on their own
        spikeTime = item[0]
        #print(spikeTime)
        if( vibeStart < spikeTime and spikeTime < vibeEnd):
            vibeTimes.append(item)  
    singleCycleTimes = []
    for cycle in cycleStarts:
        cycleEnd = cycle + cycleStep
        cycleCounted = False
        for spikeDuo in vibeTimes:
            spike = spikeDuo[0]
            #print(spike)
            if (spike < cycleEnd and spike > cycle):
                singleCycleTimes.append(spike - cycle)
                if not cycleCounted:
                    uniqueCycleSpikes += 1
                    cycleCounted = True
    return [singleCycleTimes, uniqueCycleSpikes]
def getMarkers(data): #time index 0, length index 1, tension index 2   

   thresholdA = float(float(data[0][1]) + 2.4)
   thresholdB = float(float(data[0][1]) + 2.4)
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
       x = float(r[1])
#       try:
#         x = float(r[1])
#       except Exception:
#         pass
       #print(thresholdA)
       #print(thresholdB)
       if (x > thresholdA) & (x > thresholdB) & isfloat:
         markers.append(r)
       currentIndex = currentIndex + 1
   return markers#=-    
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

if __name__ == '__main__':
    process('Het')
    process('WT')