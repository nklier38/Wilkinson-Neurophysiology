import sys
import os
import csv
import numpy as np

columns = ['vibration frequency', 'vibration standard time', 'Resting Discharge FPS', 'RD SD', 'resting discharge av. inst. freq', 'Resting discharge % of baseline', 'Vibe standard time', 'Vibe FPS', 'Vibe SD', 'Vibe av. inst. freq', 'Vibe % of baseline', 'time silence', 'ramp number', 'macro number', 'max resting discharge in macro', 'max Vibe in macro', 'max Time silence in macro']
ranges = [[0,0],[0,0],[0, 10], [10, 19]]
stretchLengthInd = 0 #constant indeces in the ranges and column arrays, allows for their use without magic numbers
stretchSpeedInd = stretchLengthInd + 1
RDind = stretchLengthInd +2
vibeind = stretchLengthInd +3
dataKey = ["50hz", "100hz"]

timeBetweenRamps = 205.5588379

def statsOverRange(lowerBound, upperBound, data): #highly inefficient, but small data set means this is not a huge concern. Takes the lowerbound and upperbound times, and loops through data and returns a length 2 list with the maximum frequency and FPS average over range
    maxFreq = 0.0
    timeInd = 0
    freqInd = 1
    spikeCount = 0.0
    totalFreq = 0.0
    dpset = False
    interval = upperBound-lowerBound #time of the interval
    differSet = [] #a list of the time differences between spikes within the interval range
    for index, spike in enumerate(data):#loops through the entire dataset
#        print(index)
#        print(spike)
        time = spike[timeInd]
        freq = spike[freqInd]
        #print(time)
        if (time >= lowerBound) & (time < upperBound): #when it reaches the proper range, stats are calculated
            spikeCount += 1 #counts spikes in interval range
            totalFreq += freq
            if(freq > maxFreq):
                maxFreq = freq
                dpset = True
#            print(len(data))
#            print(index)
            if not (index == (len(data) - 1)):
                differSet.append(data[index + 1][timeInd] - spike[freqInd])
    #differSet)
    #del differSet[-1] #removes the last element of differ set, which is the time difference between a spike out of range and a spike in range
    stanDev = np.std(differSet)
    FPS = spikeCount/interval #FPS calulation is done as the spikes per time
    if(spikeCount == 0.0):
        avFreq = 0
    else:
        avFreq = totalFreq/spikeCount
    if not dpset:
        maxFreq = 0
    return [FPS, maxFreq, stanDev, avFreq] #can add any additional calculations to this list and then pass it to analyze

def process(dataFolder): #"manager" method. Takes all relevant data files, pairs them with their length files, and runs analyze on every pair of files with the appropriate inputs.
    files_list = os.listdir(dataFolder)
    nameMusc = [] #intended to be a collection of unique trials when sections are a thing
    trials = []
    for item in files_list:
        fileName = str(item)
        if fileName[:9] not in nameMusc:
            nameMusc.append(item[:9])
    for item in nameMusc:
        nameSet = False
        name = "unidentifiedName"
        lengthFiles = []
        outputFiles = []
        thisID = item[:9]
        for inputFile in files_list:
            if(str(inputFile)[:9] == thisID and ("output" in str(inputFile))):
                outputFiles.append(inputFile)
            elif(str(inputFile)[:9] == thisID and ("lengths" in str(inputFile))):
                lengthFiles.append(inputFile)
                if not nameSet:
                    nameSet = True
                    name = str(inputFile)
        trial = [name]
        print(name)
        if('continuous' in name):
            trial.extend(unifyContinuousFiles(lengthFiles, outputFiles))
        else:
            trial.extend(unifyFiles(lengthFiles, outputFiles))
        trials.append(trial)
        unanalyzed = []
        success = []
        #print(trials)
    for item in trials:
        #print(len(item))
        name = item[0]
        freqData = getFreqs(item[2])
        identifier = name.split("_")[0] + "_" + name.split("_")[1] #I know there's probably a better way to do this
        print(item)
        analyzedData = analyze(freqData, item[1])
            
        analyzedName = name + "_vibrations.csv"
        formatWrite(analyzedData, 'vibrations', analyzedName)
        print('analyzed file: ' +  str(item[0]))
        
#        try:
#            analyzedData = analyze(freqData, item[1])
#            analyzedName = name + "_analyzed.csv"
#            formatWrite(analyzedData, 'analyzed', analyzedName)
#            success.append([name])
#            print('analyzed file: ' +  str(item[0]))
#        except Exception as e:
#            print("problem file: " + str(item[0]))
#            exc_type, exc_obj, exc_tb = sys.exc_info()
#            fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
#            unanalyzed.append([name])
#            print(exc_type, fname, exc_tb.tb_lineno)
#    formatWrite(success, "log", "successful.csv")
#    formatWrite(unanalyzed, "log", "errors.csv")
    if(len(unanalyzed) is not 0):
        print("Files not analyzed due to error: ")
        print(unanalyzed)
    else:
        print("No errors detected")
        
def getFreqs(data):
    newData = []
    data = sorted(data)
    for x in range(0, len(data) - 1):
        #print(data[x + 1][0])
        #print((data[x][0]))
        if(data[x+1][0] != data[x][0]):
            newData.append([data[x][0], (1/((data[x + 1][0]) - (data[x][0])))])
    return newData       

def unifyContinuousFiles(lengths, output):
    dataFolder = "data"
    unifiedLengths = []
    unifiedOutput = []
    sortedLengths = sorted(lengths)
    sortedOutput = sorted(output)
#    print("sorted lengths, then outputs:")
#    print(sortedLengths)
#    print(sortedOutput)
    for x in range(0, len(sortedOutput)):
#        try:
#            import  as eu
#            lengthData = eu.openCSV(dataFolder, str(sortedLengths[x]))
#            data = eu.openCSV(dataFolder, str(sortedOutput[x]))
#        except ImportError:
#            lengthData = openCSV(dataFolder, str(sortedLengths[x]))
#            data = openCSV(dataFolder, str(sortedOutput[x]))
        lengthData = openCSV(dataFolder, str(sortedLengths[x]))
        data = openCSV(dataFolder, str(sortedOutput[x]))
        for row in data:
            try:
                newRow = []
                newRow.append(float(row[0]))
                newRow.extend(row[1:])
                unifiedOutput.append(newRow)
            except:
                pass
        for row in lengthData:
            try:
                newRow = []
                newRow.append(float(row[0]))
                newRow.extend(row[1:])
                unifiedLengths.append(newRow)
            except:
                pass
    return [unifiedLengths, unifiedOutput]
        
def unifyFiles(lengths, output):
    dataFolder = "data"
    prevTime = 0
    unifiedLengths = []
    unifiedOutput = []
    sortedLengths = sorted(lengths)
    sortedOutput = sorted(output)
#    print("sorted lengths, then outputs:")
#    print(sortedLengths)
#    print(sortedOutput)
    for x in range(0, len(sortedOutput)):
#        try:
#            import europeanReader as eu
#            lengthData = eu.openCSV(dataFolder, str(sortedLengths[x]))
#            data = eu.openCSV(dataFolder, str(sortedOutput[x]))
#        except ImportError:
#            lengthData = openCSV(dataFolder, str(sortedLengths[x]))
#            data = openCSV(dataFolder, str(sortedOutput[x]))
        print(sortedLengths)
        lengthData = openCSV(dataFolder, str(sortedLengths[x]))
        data = openCSV(dataFolder, str(sortedOutput[x]))
        for row in data:
            try:
                newRow = []
                newRow.append(float(row[0]) + prevTime)
                newRow.extend(row[1:])
                unifiedOutput.append(newRow)
            except:
                pass
        for row in lengthData:
            try:
                newRow = []
                newRow.append(float(row[0]) + prevTime)
                newRow.extend(row[1:])
                unifiedLengths.append(newRow)
            except:
                pass
        prevTime = unifiedLengths[-1][0]
                
    return [unifiedLengths, unifiedOutput]
#            
def getFirstMacroStats(data, markers):
    totBL = 0.0
    totVibe = 0.0
    FPS = 0
    instFreq = 3
    for m in markers:
        marker = m[0]

        vibe = statsOverRange(marker + ranges[vibeind][0], marker + ranges[vibeind][1], data)
        totBL += statsOverRange(marker, marker + ranges[RDind][1], data)[instFreq] #statsOverRange returns a length 2 list, index 0 being the average FPS in the range and index 2 being the peak frequecy in the range
        totVibe += vibe[instFreq]
        #totSilence += float(getTimeSilence(marker, data))
    #return [(totBL/len(markers)), (totDP/len(markers)), (totDI/len(markers)), (totIST/len(markers)), (totFST/len(markers))]
    #return [(totBL/6), (totDP/6), (totDI/6), (totIST/6), (totFST/6), (totSilence/6)]
    if(totBL == 0):
        totBL = 1
    return [(totBL/6), (totVibe/6)]

def analyze(data, lengths): #data is a 2 dimensional array representation of the output CSV. Length is the same for the lengths file. Broken name is an array with each element of the name, used to get muscle number and date
    final = [columns] #list final will be a two dimensional array that will be written into a CSV. top row is the header, each subsequent row is data from a ramp
    #print(lengths)
    allMarkers = getMarkers(lengths) # will return a two dimensional list. each sub list is length three and represents the timestamp, length value, and tension value at the lengths channel markers
    rampCounters = 0 #probably redundant with x below but I'm scared to touch it because it works 
    print(len(allMarkers))
    FPS = 0
    maxFreq = 1
    stanDev = 2
    instFreq = 3
    macroNum = 0
    macroOne = [getFirstMacroStats(data, allMarkers[1:19:3]), getFirstMacroStats(data, allMarkers[2:20:3])]
    maxRD = 0.0
    maxSilence = 0.0
#    print("macro 1 stats:")
#    print(macroOne)
    #print(data)
    #print(allMarkers)
    for shift in range(0,2):
        macroNum = 0.0
        maxRD = 0.0
        maxVibe = 0.0
        maxSilence = 0.0
        for x in range (0, len(allMarkers)):
            if(x%18 == 0):
                macroNum += 1
#                maxRD = 0.0
#                maxVibe = 0.0
#                maxSilence = 0.0
                #final[-1].extend([maxRD, maxVibe, maxSilence])
            if(x%3 == (1 + shift)):
                markerRow = allMarkers[x]
                marker = markerRow[0]
                row = []
                row.append(dataKey[shift])
                rampCounters += 1 #allows for iteration over set lists
                rampNum = int((x)/3)  + 1 #- shift
                rampSTDstart = round((rampNum - 1)*timeBetweenRamps, 1)
                vibestdStart = round(rampSTDstart + 10, 1)
                vibestdEnd = round(rampSTDstart + 19, 1)
                RD = statsOverRange(marker, marker + ranges[RDind][1], data) #statsOverRange returns a length 2 list, index 0 being the average FPS in the range and index 2 being the peak frequecy in the range
                vibe = statsOverRange(marker + ranges[vibeind][0], marker + ranges[vibeind][1], data)
                timeSilence = getTimeSilence(marker, data)
                if(RD[instFreq] > float(maxRD)):
                    maxRD = RD[instFreq]
                if(vibe[instFreq] > float(maxVibe)):
                    maxVibe = vibe[instFreq]
                try:
                    if(float(timeSilence) > float(maxSilence)):
                        maxSilence = timeSilence
                except:
                    pass
                row.append(rampSTDstart)
                row.append(RD[FPS])
                row.append(RD[stanDev])
                row.append(RD[instFreq])
                row.append(RD[instFreq]*100/macroOne[shift][0])
                row.append(str(vibestdStart) + "-" + str(vibestdEnd))
                row.append(vibe[FPS])
                row.append(vibe[stanDev])
                row.append(vibe[instFreq])
                row.append(vibe[instFreq]*100/macroOne[shift][1])
                row.append(timeSilence)
                #row.append("nothing here now")
                row.append(rampNum)
                row.append(macroNum)
                if(((x+(2 - shift))%18 == 0) or (x == len(allMarkers) - 1)):
                    row.extend([maxRD, maxVibe, maxSilence])
                    maxRD = 0.0
                    maxVibe = 0.0
                    maxSilence = 0.0
                final.append(row)
                #places them at the first row of the macro  
    return final

def getTimeSilence(marker, data):
    #print(data)
    startTime = marker + 14.2
    for x in range(0, len(data)):
        if data[x][0] > startTime:
#            print("action potential before and after time stamps")
#            print(data[x-1][0])
#            print(data[x][0])
            silence = data[x][0] - data[x-1][0]
            if(silence > 40):
                return "-" 
            return silence
            #return data[x][0] - startTime
#def getMarkers(data): #time index 0, length index 1, tension index 2
#   thresholdA = float(float(data[0][1]) + 2.4)
#   thresholdB = float(float(data[0][1]) + 2.4)
#   markers = []
#   currentIndex = 0
#   for index in range(0, len(data)):
#       r = data[index]
#       if currentIndex != 0:
#         try:
#            thresholdA = (float(float(data[int(currentIndex - 1)][1])) + 2.4)
#            thresholdB = (float(float(data[int(currentIndex + 1)][1])) + 2.4)
#
#         except Exception as error:
#            pass      
#       try:
#         x = float(r[1])
#       except Exception:
#         pass
#       if (x > thresholdA) & (x > thresholdB):
#           markers.append(r)
#       currentIndex = currentIndex + 1
#   return markers

def getMarkers(data): #time index 0, length index 1, tension index 2   

   thresholdA = float(float(data[0][1]) + 2.4)
   thresholdB = float(float(data[0][1]) + 2.4)
   markers = []
   currentIndex = 0
   for index in range(0, len(data)):
       r = data[index]
       if currentIndex != 0:
         try:
            thresholdA = (float(float(data[int(currentIndex - 1)][1])) + 2.4)
            thresholdB = (float(float(data[int(currentIndex + 1)][1])) + 2.4)

         except Exception as error:
            pass      
       isfloat = True
       x = float(r[1])
       #print(x)
#       try:
#         x = float(r[1])
#       except Exception:
#         pass
       if (x > thresholdA) & (x > thresholdB) & isfloat:
         markers.append(r)
       currentIndex = currentIndex + 1
   return markers    
    
def openCSV(path, fileName):
   data_f = open(path + os.sep + fileName)
   data_table = []
   data = []
   for r in data_f:
         for row in r.split('\n'):
            currentRow = row.split(',')
            fixedRow = []
            for item in currentRow:
               if(item == '#NUM!'):
                   item = 0
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
    process('data')