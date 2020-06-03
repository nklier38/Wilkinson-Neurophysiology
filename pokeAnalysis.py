# -*- coding: utf-8 -*-
"""
Created on Mon Oct  7 13:46:32 2019

@author: Nikola Klier
"""

import os
import csv
import numpy as np
import traceback
import re

columns = ['Stretch length', 'Stretch speed', 'Resting Discharge FPS', 'RD SD', 'Dynamic Peak', 'Dynamic Index', 'IST FPS', 'IST FPS SD', 'IST inst freq', 'FST FPS', 'FST SD', 'FST inst freq', 'seconds into ramp of last firing action potential', 'Eartag number', 'Muscle number', 'date']
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
stretchLengths = ['2.50%', '2.50%','2.50%', '5.00%','5.00%','5.00%','7.50%','7.50%','7.50%']
stretchSpeeds = ['40%','40%','40%','40%','40%','40%','40%','40%','40%']



def statsOverRange(lowerBound, upperBound, data): #highly inefficient, but small data set means this is not a huge concern. Takes the lowerbound and upperbound times, and loops through data and returns a length 2 list with the maximum frequency and FPS average over range
    maxFreq = -1.0
    timeInd = 0
    freqInd = 1
    spikeCount = 0.0
    finalSpike = 0.0
    dpset = False
    interval = upperBound-lowerBound #time of the interval
    differSet = [] #a list of the time differences between spikes within the interval range
    totalFreq = 0.0
    prevSpike = 0.0
    setFinalSpike = True
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
                differSet.append(data[index + 1][timeInd] - spike[freqInd]) 
        if(time >= upperBound) & setFinalSpike:
            finalSpike = prevSpike
            setFinalSpike = False
        prevSpike = time
    with np.errstate(all = 'ignore'):
        stanDev = np.std(differSet)
    FPS = spikeCount/interval #FPS calulation is done as the spikes per time
    try:
        instFreq = totalFreq/spikeCount
    except:
        instFreq = 0
    if not dpset:
        maxFreq = 0
    finalRampFire = finalSpike - lowerBound
    return [FPS, maxFreq, stanDev, instFreq, finalRampFire] #can add any additional calculations to this list and then pass it to analyze

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
#        formatWrite(analyzedData, 'analyzedTimeOnly', analyzedName)
#        analyzedCount += 1
        
        try:
            print("now analyzing: " + "_".join(fixedBrokenName))
            #analyzedData = analyze(dataByTime, lengths, brokenName) just doing poke here
            analyzedPokeData = pokeAnalyze(dataByTime, lengths, brokenName)
            analyzedName = "_".join(fixedBrokenName) + "_chashuAnalyzed.csv"
            analyzedPokeName = "_".join(fixedBrokenName) + "_pokeAnalyzed.csv"
            #formatWrite(analyzedData, 'analyzed', analyzedName)
            formatWrite(analyzedPokeData, 'analyzed', analyzedPokeName)
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
   return markers


def pokeAnalyze(data, lengths, brokenName):
    final = [columns] #list final will be a two dimensional array that will be written into a CSV. top row is the header, each subsequent row is data from a ramp
    if(len(lengths) > 40):
        allMarkers = getMarkers(lengths) 
    else:
        allMarkers = getOldMarkers(lengths)# will return a two dimensional list. each sub list is length three and represents the timestamp, length value, and tension value at the lengths channel markers
    eartag = brokenName[EartagIndInName]
    date = brokenName[0]
    #len(allMarkers))
    muscle = brokenName[MuscleIndInName]
    rampCounters = 0 #probably redundant with x below but I'm scared to touch it because it works 
    FPS = 0
    maxFreq = 1
    stanDev = 2
    instFreqInd = 3
    for x in range(0, 29): #9 ramps in this format
        markerRow = allMarkers[x]
        marker = markerRow[0]
        #marker)
        #x)
        row = []
        row.append('5%') #stretch length from set list
        row.append('40%') #stretch speed from set list
        rampCounters += 1 #allows for iteration over set lists
        RD = statsOverRange(marker, marker + ranges[RDind][1], data) #statsOverRange returns a length 2 list, index 0 being the average FPS in the range and index 2 being the peak frequecy in the range
        DP = statsOverRange(marker + ranges[DPind][0], marker + ranges[DPind][1], data)
        IST = statsOverRange(marker + ranges[ISTind][0], marker + ranges[ISTind][1], data)
        DI = DP[maxFreq] - IST[instFreqInd]
        FST = statsOverRange(marker + ranges[FSTind][0], marker + ranges[FSTind][1], data)
        wholeRamp = statsOverRange(marker + 10, marker + 14, data)
        finalAP = wholeRamp[4]
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
        row.append(finalAP)
        print(eartag)
        row.append(eartag)
        row.append(muscle)
        row.append(date)
        final.append(row)
    return final
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
    rampCounters = 0 #probably redundant with x below but I'm scared to touch it because it works 
    FPS = 0
    maxFreq = 1
    stanDev = 2
    instFreqInd = 3
    for x in range(0,9): #9 ramps in this format
        markerRow = allMarkers[x]
        marker = markerRow[0]
        #marker)
        #x)
        row = []
        row.append(stretchLengths[rampCounters]) #stretch length from set list
        row.append(stretchSpeeds[rampCounters]) #stretch speed from set list
        rampCounters += 1 #allows for iteration over set lists
        RD = statsOverRange(marker, marker + ranges[RDind][1], data) #statsOverRange returns a length 2 list, index 0 being the average FPS in the range and index 2 being the peak frequecy in the range
        DP = statsOverRange(marker + ranges[DPind][0], marker + ranges[DPind][1], data)
        IST = statsOverRange(marker + ranges[ISTind][0], marker + ranges[ISTind][1], data)
        DI = DP[maxFreq] - IST[instFreqInd]
        FST = statsOverRange(marker + ranges[FSTind][0], marker + ranges[FSTind][1], data)
        wholeRamp = statsOverRange(marker + 10, marker + 14, data)
        finalAP = wholeRamp[4]
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
        row.append(finalAP)
        print(eartag)
        row.append(eartag)
        row.append(muscle)
        row.append(date)
        final.append(row)
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

if __name__ == '__main__':
    process('pokeData')