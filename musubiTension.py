import sys
import os
import csv
import re

##comments marked with exclamation marks already existed in the file beforehand, the rest were added by me to understand stuff

defaultFileName = 'tension.csv'
results_folder_name = 'Results'
output_file_append_text = 'results.csv'
columns = ['time', 'mean within range', 'time at maximum', 'maximum value in range', 'min value in range', 'tension value at selection', 'length maximum', 'time at length maximum']

def getData(data_folder, fileName):
   data_f = open(data_folder + os.sep + fileName)
   data_table = []
   data = []
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
               #print(fixedRow)
   data_table = [x for x in data_table if x != ['']]
   return data_table

def findMarkers(data):
   thresholdA = float(float(data[0][6]) + 2.4)
   thresholdB = float(float(data[0][6]) + 2.4)
   thresholdSet = False
   markers = []
   currentIndex = 0
   for r in data:
      if currentIndex != 0:
         try:
            thresholdA = (float(float(data[int(currentIndex - 1)][6])) + 2.4)
            thresholdB = (float(float(data[int(currentIndex + 1)][6])) + 2.4)
         except Exception as error:
            pass      
      isfloat = True
      try:
         x = float(r[6])
      except Exception:
         pass
      if (x > thresholdA) & (x > thresholdB) & isfloat:
         markers.append(float(r[7]))
      currentIndex = currentIndex + 1
   finalMarkers = filterMarkers(markers)
   return finalMarkers
def filterMarkers(markers):
   finalMarkers = []
   index = 1
   finalMarkers.append(markers[0])
   while index < len(markers) - 1:
      differenceNext = (markers[index + 1]) -(markers[index])
      differencePrevious = (markers[index]) - (markers[index - 1])
      if (differenceNext > 60) & (differencePrevious > 60):
         finalMarkers.append(markers[index])
      index = index + 1
   finalMarkers.append(markers[len(markers) - 1])
   return(finalMarkers)
def pointsOfInterest(markers):
   #print(markers)
   ramps = []
   allPoints = []
   key = ['marker', 'stretch start/baseline end', 'peak end', 'hold start', 'hold end', 'stretch end']
   numRamps = round(((len(markers)/3) + 0.5), 0)
   print('number of ramps in this file: ' + str(numRamps))
   x = 1
   while x <= numRamps:
      rampStartIndex = (x-1)*3
      print(x)
      print('ramp starting Index: ' + str(rampStartIndex))
      ramps.append(markers[rampStartIndex])
      x = x+1
   for ramp in ramps:
      points = []
      points.append(ramp)
      points.append(ramp + 9.75)
      points.append(ramp + 13)  
      points.append(ramp + 13.25)
      points.append(ramp + 13.75)
      points.append(ramp + 14.5)
      allPoints.append(points)
   return allPoints
def process(ramps, data):
   key = ['Ramp #', 'BL tension', 'BL tension start point', 'peak tension', 'value 3.25 seconds in', 'time 3.25 seconds into ramp', 'value 3.75 seconds into ramp', 'time 3.75 seconds into ramp', 'average of 3.25 and 3.75', 'average of all interval points', 'placeholder for time at min', 'Min value'] #need to add two more here that you don't know exactly what they are
   processedRamps = []
   processedRamps.append(key)
   rampNum = 0
   for ramp in ramps:
      processed = []
      if rampNum%6 == 0:
         processedRamps.append(["", "", "", "", "", "", "", "", "", "", ""])
         macroNumstr = "for macro #:", str((rampNum/6) + 1)
         processedRamps.append(macroNumstr)
      rampNum = rampNum + 1
      #columns = ['time', 'mean within range', 'time at maximum', 'maximum value in range', 'min value in range', 'tension value at selection', 'length maximum', 'time at length maximum']
      baselineData = simplifyRange(ramp[0], ramp[1], data)
      peakData = simplifyRange(ramp[1], ramp[2], data) #should return a set of the same values, except cut out the lengths and add a end of selection tension value as last value
      #problem: the times for the peak are not sufficient to cover for the peak
      holdData = simplifyRange(ramp[3], ramp[4], data)
      minData = simplifyRange(ramp[4], ramp[5], data)
      processed.append(rampNum%6)
      processed.append(baselineData[1]) #BL tension
      processed.append(baselineData[0]) #BL tension select time
      processed.append(peakData[3]) #Peak TEnsion THIS IS GIVING YOU ISSUES
      processed.append(float(holdData[5]))#tension value at 3.25 hold point
      processed.append(ramp[3])#selection actual start for 3.25 seconds in
      processed.append(holdData[6])#value at 3.75 time
      processed.append(ramp[4])#time for 3.75
      processed.append((float(processed[4])+float(processed[6]))/2)#average of 3.25 and 3.75 values
      processed.append(holdData[1])#mean of all values
      processed.append("") #placeholder for time at minimum, to do this it would require a differnet setup
      processed.append(minData[4])#minimum value
      processedRamps.append(processed)
   #print "processedRamps"
   #print processedRamps
   return processedRamps
def simplifyRange(startTime, endTime, data):
   simpleData = []
   length = len(data)
   isMinIndex = False
   isMaxIndex = False
   searchIndex=length/2
   maxIndex = length - 1
   minIndex = 0
   while not isMinIndex:
      searchTime = data[int(searchIndex)][0]
      #print 'startTime: ' + str(startTime) + 'searchTime: ' + str(searchTime)
      startTime = float(startTime)
      searchTime = float(searchTime)
      if (startTime <= searchTime) & (searchTime <= (startTime + 0.05)):
         isMinIndex = True        
         startTimeIndex = int(searchIndex)
      elif searchTime < startTime:
         minIndex = searchIndex
         searchIndex = ((maxIndex - searchIndex)/2) + searchIndex
      elif searchTime > startTime:
         #print('loop finding starting index')
         maxIndex = searchIndex
         searchIndex = searchIndex - ((searchIndex - minIndex)/2)  
   searchIndex = int(length/2)
   maxIndex = length - 1
   minIndex = 0
   #print('now finding max index')
   while not isMaxIndex:
      searchTime = data[int(searchIndex)][0]
      #print('endTime: ' + str(endTime) + ' searchTime: ' + str(searchTime))
      startTime = float(endTime)
      searchTime = float(searchTime)
      if (endTime <= searchTime) & (searchTime <= (endTime + 0.05)):
         isMaxIndex = True        
         endTimeIndex = int(searchIndex - 1)
      elif searchTime < endTime:
         minIndex = searchIndex
         searchIndex = ((maxIndex - minIndex)/2) + minIndex
      elif searchTime > endTime:
         maxIndex = searchIndex
         searchIndex = maxIndex - ((maxIndex - minIndex)/2)  
   maxTension = -float('inf')
   minTension = float('inf')
   total = 0
   x = startTimeIndex
   while x <= endTimeIndex:
      if float(data[x][3]) > maxTension:
         #print 'altering max tension:'
         maxTension = float(data[x][3])
         #print maxTension
         maxTensionTime = data[x][2]
      #print 'data[x][4]: '
      #print data[x][4]
      if float(data[x][4]) < minTension:
        # print 'new min tension: '
         #print data[x][4]
         minTension = float(data[x][4])
      total += float(data[x][1])
      x = x + 1
   simpleData.append(data[startTimeIndex][0])
   simpleData.append(total/(endTimeIndex - startTimeIndex + 1))
   simpleData.append(maxTensionTime)
   simpleData.append(maxTension)
   simpleData.append(minTension)
   simpleData.append(data[startTimeIndex][5])
   simpleData.append(data[endTimeIndex][5])
   #print simpleData
   return simpleData
   
def formatWrite(analyzed, foldername, filename):
   with open(foldername+os.sep+filename, "w", newline='') as analyzedFile:
      writer = csv.writer(analyzedFile)
      writer.writerows(analyzed)
      
if __name__ == '__main__':
  data_folder = 'data'
  results = []
  for item in os.listdir(data_folder):
     data = getData(data_folder, str(item))
     final = process(pointsOfInterest(findMarkers(data)), data)
     #formatWrite(final, data_folder, ("analyzed" + str(item) + ".csv"))
     formatWrite(final, data_folder, ("analyzed" + str(item)))
     print('analyzed ' + str(item))
  print('All done, check your files!')
  #print final
