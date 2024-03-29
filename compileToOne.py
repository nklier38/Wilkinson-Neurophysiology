import os
import csv
import re
import numpy as np
from scipy import stats
import matplotlib.pyplot as plt 


import matplotlib.patches as mpatches
                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                 import sys





ear = 12
date = 13
muscle = 14

genotype = 1
sex = 2
completeID = 0

counts = [0, 0, 0]

genotypes = ['WT', 'Het', 'Hom']

header1 = ['Stretch length', 'Stretch speed', 'Resting Discharge FPS', 'RD SD', 'Dynamic Peak', 'Dynamic Index', 'IST', 'IST SD', 'IST inst freq', 'FST', 'FST SD', 'FST inst freq', 'seconds into ramp of last firing action potential', 'Eartag number', 'Muscle number', 'date', 'Genotype number', 'Genotype', 'sex']
header2 = ['Vibration amplitude', 'Vibration frequency', 'BL FPS', 'BL FPS SD', 'BL av. inst. freq.', 'vibration FPS', 'vibration FPS SD', 'vibration av inst. freq', 'Entrainment: length of cycle in seconds', 'Entrainment: mean firing time from cycle start', 'entrainment: position 0 to 1', 'cycle position standard deviation', 'number of cycles with spikes', 'total cycles in vibration', 'percent of cycles with spikes', 'Eartag number', 'Muscle number', 'date']

def openCSV(path, fileName):
   data_f = open(path + os.sep + fileName)
   data_table = []
   data = []
   for r in data_f:
         for row in r.split('\n'):
            currentRow = row.split(',')
            fixedRow = []
            for item in currentRow:
               try:
                  fixedRow.append(item) 
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
      
def writeToOne(folder, fileName, header):
    count = 0
    allData = []
    filesList = os.listdir(folder)
    #key = openCSV('compilations', 'key.csv')
    key = []
    for item in filesList:
        count += 1
        thisFile = openCSV(folder, str(item))
        thisFile = addData(thisFile, key)
        print(str(item))
        del(thisFile[0])
        allData.extend(thisFile)
    allData.sort(key=lambda x: int(x[15])) #15 is index of genotype number
    allData = [header] + allData
    formatWrite(allData, 'compilations', fileName)
#    try:
#        formatWrite(allData, 'compilations' + folder, fileName)
#    except:
#        pass
    #print(allData)
    return allData
def getAvs(allData, label):
    stretchCount = 0.0
    prevSex = ''
    prevMusc = ''
    prevDate = ''
    prevEartag = ''
    prevStretch = '2.50%'
    prevGenNum = ''
    prevGen = ''
    thisDate = 14
    thisGen = 16 
    thisGenNum = 15
    thisSex = 17
    thisMusc = 13
    thisStretchInd = 0
    thisEartag = 12
    RDFPSTot = 0.0
    RDSDTot = 0.0
    DPTot = 0.0
    DITot = 0.0
    ISTFPSTot = 0.0
    ISTSDTot = 0.0
    ISTFreqTot = 0.0
    FSTFPSTot = 0.0
    FSTSDTot = 0.0
    FSTFreqTot = 0.0
    avData = [header1]
    for rowInd in range(1, len(allData)):
        row = allData[rowInd]
        #print(row)
        thisStretch = row[0]
        if (thisStretch != prevStretch):
            newRow = []
            newRow.append(prevStretch)
            newRow.append('40%')
            newRow.append(RDFPSTot/stretchCount)
            RDFPSTot = 0.0
            newRow.append(RDSDTot/stretchCount)
            RDSDTot = 0.0
            newRow.append(DPTot/stretchCount)
            DPTot = 0.0
            newRow.append(DITot/stretchCount)
            DITot = 0.0
            newRow.append(ISTFPSTot/stretchCount)
            ISTFPSTot = 0.0
            newRow.append(ISTSDTot/stretchCount)
            ISTSDTot = 0.0
            newRow.append(ISTFreqTot/stretchCount)
            ISTFreqTot = 0.0
            newRow.append(FSTFPSTot/stretchCount)
            FSTFPSTot = 0.0
            newRow.append(FSTSDTot/stretchCount)
            FSTSDTot = 0.0
            newRow.append(FSTFreqTot/stretchCount)
            FSTFreqTot = 0.0
            stretchCount = 0.0
            newRow.append(prevEartag)
            newRow.append(prevMusc)
            newRow.append(prevDate)
            newRow.append(prevGenNum)
            newRow.append(prevGen)
            newRow.append(prevSex)
            #print(newRow)
            avData.append(newRow)
            
        
        prevStretch = row[int(thisStretchInd)]
        prevEartag = row[thisEartag]
        prevMusc = row[thisMusc]
        prevDate = row[thisDate]
        prevGenNum = row[thisGenNum]
        prevGen = row[thisGen]
        prevSex = row[thisSex]
        RDFPSTot += float(row[2])
        RDSDTot += float(row[3])
        DPTot += float(row[4])
        DITot += float(row[5])
        ISTFPSTot += float(row[6])
        ISTSDTot += float(row[7])
        ISTFreqTot += float(row[8])
        FSTFPSTot += float(row[9])
        FSTSDTot += float(row[10])
        FSTFreqTot += float(row[11])
        stretchCount += 1
    newRow = []
    newRow.append(prevStretch)
    newRow.append('40%')
    newRow.append(RDFPSTot/stretchCount)
    RDFPSTot = 0.0
    newRow.append(RDSDTot/stretchCount)
    RDSDTot = 0.0
    newRow.append(DPTot/stretchCount)
    DPTot = 0.0
    newRow.append(DITot/stretchCount)
    DITot = 0.0
    newRow.append(ISTFPSTot/stretchCount)
    ISTFPSTot = 0.0
    newRow.append(ISTSDTot/stretchCount)
    ISTSDTot = 0.0
    newRow.append(ISTFreqTot/stretchCount)
    ISTFreqTot = 0.0
    newRow.append(FSTFPSTot/stretchCount)
    FSTFPSTot = 0.0
    newRow.append(FSTSDTot/stretchCount)
    FSTSDTot = 0.0
    newRow.append(FSTFreqTot/stretchCount)
    FSTFreqTot = 0.0
    stretchCount = 0.0
    newRow.append(prevEartag)
    newRow.append(prevMusc)
    newRow.append(prevDate)
    newRow.append(prevGenNum)
    newRow.append(prevGen)
    newRow.append(prevSex)
    #print(newRow)
    avData.append(newRow)
    formatWrite(avData, 'compilations', 'averages' + label + '.csv')
    return avData
    
def addData(data, key): #adds genotype and sex data
    #print(key)
    #print(data)
    thisMusc = data[1][muscle]
    thisDate = data[1][date]
    thisTag = data[1][ear]
    print(thisTag)
    gen = '?'
    thisSex = '?'
#    completeName = "-".join([oneRow[date], oneRow[muscle], oneRow[ear]])
    trialInfo = []   
    for x in range(1, len(key)):
        trial = key[x]
        if((re.search(thisTag, trial[completeID], re.IGNORECASE)) or ((re.search(thisDate, trial[completeID], re.IGNORECASE)) and (re.search(thisMusc, trial[completeID], re.IGNORECASE)))): 
            print(trial)
            gen = int(trial[genotype])
            thisSex = trial[sex]
    for row in data:
        try:
            row.extend([gen, genotypes[int(gen)], thisSex])
        except:
            row.extend([gen, '?', thisSex])
        
    return data
def graphAvs(avData):
    homs = []
    hets = []
    WTs = []
    for row in avData:
        if (row[15] == 0):
            WTs.append(row)
        elif(row[15] == 1):
            hets.append(row)
        elif(row[15] == 2):
            homs.append(row)
    homSets = getSets(homs)
    print(homSets[1])
    hetSets = getSets(hets)
    WTSets = getSets(WTs)
    
    
    plt.xlabel('Stretch magnitude- % of resting length')
    plt.ylabel('Mean firing frequency during IST')
    plt.plot([2.5, 5.0, 7.5], [np.average(homSets[1][0]), np.average(homSets[1][1]), np.average(homSets[1][2])], 'bo-', label= 'homozygotes')
    plt.plot([2.5, 5.0, 7.5], [np.average(hetSets[1][0]), np.average(hetSets[1][1]), np.average(hetSets[1][2])], 'go-', label= 'heterozygotes')
    plt.plot([2.5, 5.0, 7.5], [np.average(WTSets[1][0]), np.average(WTSets[1][1]), np.average(WTSets[1][2])], 'ro-', label= 'wild type')
    plt.errorbar([2.5, 5.0, 7.5], [np.average(homSets[1][0]), np.average(homSets[1][1]), np.average(homSets[1][2])], yerr = [stats.sem(homSets[1][0]), stats.sem(homSets[1][1]), stats.sem(homSets[1][2])], capsize = 10)
    plt.errorbar([2.5, 5.0, 7.5], [np.average(WTSets[1][0]), np.average(WTSets[1][1]), np.average(WTSets[1][2])], yerr = [stats.sem(WTSets[1][0]), stats.sem(WTSets[1][1]), stats.sem(WTSets[1][2])], capsize = 10)
    plt.errorbar([2.5, 5.0, 7.5], [np.average(hetSets[1][0]), np.average(hetSets[1][1]), np.average(hetSets[1][2])], yerr = [stats.sem(hetSets[1][0]), stats.sem(hetSets[1][1]), stats.sem(hetSets[1][2])], capsize = 10)
#    plt.errorbar([2.5, 5.0, 7.5], [np.average(hetSets[1][0]), np.average(hetSets[1][1]), np.average(hetSets[1][2])], 'g-')
#    plt.errorbar([2.5, 5.0, 7.5], [np.average(WTSets[1][0]), np.average(WTSets[1][1]), np.average(WTSets[1][2])], 'r-')\
    WTleg = mpatches.Patch(color='red', label='Wild type')
    hetleg = mpatches.Patch(color = 'green', label = 'heterozygotes')
    homleg = mpatches.Patch(color = 'blue', label = 'homozygotes')
    plt.legend(handles=[WTleg, hetleg, homleg])
    plt.savefig('IST.png')
    plt.figure(2)
    plt.xlabel('Stretch magnitude- % of resting length')
    plt.ylabel('Mean firing frequency during FST')
    plt.plot([2.5, 5.0, 7.5], [np.average(homSets[2][0]), np.average(homSets[2][1]), np.average(homSets[2][2])], 'bo-', label= 'homozygotes')
    plt.plot([2.5, 5.0, 7.5], [np.average(hetSets[2][0]), np.average(hetSets[2][1]), np.average(hetSets[2][2])], 'go-', label= 'heterozygotes')
    plt.plot([2.5, 5.0, 7.5], [np.average(WTSets[2][0]), np.average(WTSets[2][1]), np.average(WTSets[2][2])], 'ro-', label= 'wild type')
    plt.errorbar([2.5, 5.0, 7.5], [np.average(homSets[2][0]), np.average(homSets[2][1]), np.average(homSets[2][2])], yerr = [stats.sem(homSets[2][0]), stats.sem(homSets[2][1]), stats.sem(homSets[2][2])], capsize = 10)
    plt.errorbar([2.5, 5.0, 7.5], [np.average(WTSets[2][0]), np.average(WTSets[2][1]), np.average(WTSets[2][2])], yerr = [stats.sem(WTSets[2][0]), stats.sem(WTSets[2][1]), stats.sem(WTSets[2][2])], capsize = 10)
    plt.errorbar([2.5, 5.0, 7.5], [np.average(hetSets[2][0]), np.average(hetSets[2][1]), np.average(hetSets[2][2])], yerr = [stats.sem(hetSets[2][0]), stats.sem(hetSets[2][1]), stats.sem(hetSets[2][2])], capsize = 10)
    WTleg = mpatches.Patch(color='red', label='Wild type')
    hetleg = mpatches.Patch(color='green', label='heterozygotes')
    homleg = mpatches.Patch(color='blue', label='homozygotes')
    plt.legend(handles=[WTleg, hetleg, homleg])
    plt.savefig('FST.png')
    plt.show()
    
def getSets(data):
    
    lowDPset = []
    lowISTset = []
    lowFSTset = []
    medDPset = []
    medISTset = []
    medFSTset =[]
    highDPset = []
    highISTset = []
    highFSTset = []
    for row in data:
        if ('2.50' in row[0]):
            lowDPset.append(row[4])
            lowISTset.append(row[8])
            lowFSTset.append(row[11])
        elif ('5.00' in row[0]):
            medDPset.append(row[4])
            medISTset.append(row[8])
            medFSTset.append(row[11])
        elif ('7.50' in row[0]):
            highDPset.append(row[4])
            highISTset.append(row[8])
            highFSTset.append(row[11])
    DPsets = [lowDPset, medDPset, highDPset]
    ISTsets = [lowISTset, medISTset, highISTset]
    FSTsets = [lowFSTset, medFSTset, highFSTset]
    return[DPsets, ISTsets, FSTsets]
    
def simpleCollection(header, targetFolder, dataFolder, name):
    count = 0
    allData = [header]
    filesList = os.listdir(dataFolder)
    for item in filesList:
        count += 1
        thisFile = openCSV(dataFolder, str(item))
        print(str(item))
        del(thisFile[0])
        allData.extend(thisFile)
    try:
        formatWrite(allData, targetFolder, name)
    except:
        pass
    #print(allData)
    return allData
    
    
if __name__ == '__main__':
   #graphAvs(getAvs(writeToOne('analyzed', 'ramps.csv', header1)))
   #dataFolder = 'analyzed' + input()
   getAvs(writeToOne('analyzedWT', 'rampsWT.csv', header1), 'WT')
   getAvs(writeToOne('analyzedHet', 'rampsHet.csv', header1), 'Het')
   #getAvs(writeToOne('vibrations', 'vibes.csv', header2))
   simpleCollection(header2, 'compilations', 'HetVibrations', 'HetVibes.csv')
   simpleCollection(header2, 'compilations', 'WTVibrations', 'WTvibes.csv')