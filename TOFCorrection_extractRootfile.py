#!/usr/bin/python
#this is part a of the timing calibration software: apply the TOF correction to
#recorded as a function of the chosen origin. To be used with a caller code:
#TimingCalibration.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

def Dist(df, ID, p):
  D = np.sqrt((df['PMT_x'][ID]-p[0])**2+(df['PMT_y'][ID]-p[1])**2+(df['PMT_z'][ID]-p[2])**2)
  return D

def DistFullColumn(df, p):
  D = np.sqrt((df['PMT_x']-p[0])**2+(df['PMT_y']-p[1])**2+(df['PMT_z']-p[2])**2)
  return D

def AddTOFCorrection(df, origin, offset = 950):
  #the main function takes as input the dataframe and the xyz origin
  #returns a dataframe filtered of its begative times and TOF corrected
  #w.r.t. the given origin
  waterVelocity = 22.34 #in cm ns^-1 , 2.234*10**8 ms^-1
  #offset = 0 #ns

  if 'TOFTime' in df.columns:
   if str(input("TOFTime exists, do you want to overwrite it? Y/N: ")) == 'N':
     raise TOFTimeAlreadyExists

  for i in ['mPMT', 'mPMT_pmt', 'PMT_QTot', 'PMT_x', 'PMT_y', 'PMT_z', 'Time']:
    if i not in df.columns:
      print('\nRequired dataframe missing %s column'%i)

  #dataframe where we will add the TOF corrected times
  dfFinal= pd.DataFrame()

  #go one photon at a time -> can loop afterwards, if we want

  dfTOF = df#'[df['photonID'] <= 500].copy()
  print('a', len(dfTOF['Time']))
  #And have the longest time that a photon can take to travel directly to one of the hit pmts
  longestTravelTime = (DistFullColumn(dfTOF, origin)/waterVelocity).max() + offset

  #These lower the number of entries by discarding DN and reflection hits -> they could be useful
  # Technically this line is not needed but makes plotting more intuitive
  #dfTOF = dfTOF[dfTOF['Time'] <= longestTravelTime].copy()
  
  #Need to remove negative Times that is Dark Noise:
  #dfTOF = dfTOF[dfTOF['Time'] >=offset].copy()

  print('\n Longest straight line travel time possible in the detector', longestTravelTime, 'ns')

  #Grab the earliest hit time that is larger than the offset (earliest true hit)
  
  dfTOFPos = dfTOF#[dfTOF['Time'] >= offset]
  idMinTime = dfTOFPos['Time'].idxmin()
  earliestTOFTime = Dist(dfTOFPos, idMinTime, origin)/waterVelocity

  print('\nEarliset hit: %.2fns EarliestTOF: %.2fns\n'%(dfTOFPos['Time'].min(), earliestTOFTime))

  #TOF correct the relevant dataFrame
  dfTOF['TOFTime'] = dfTOF['Time'] - DistFullColumn(dfTOF, origin)/waterVelocity + earliestTOFTime

   #shift: earliest time is now 0
  dfTOF['TOFTime'] = dfTOF['TOFTime'] - dfTOF[dfTOF['Time'] >= offset]['TOFTime'].min()

  #The dark noise hit and reflections have TOFTime set to a flag value
  dfTOF.loc[dfTOF['Time'] >= longestTravelTime, ['TOFTime']] = -9999
  dfTOF.loc[dfTOF['Time'] <= offset, ['TOFTime']] = -9999

  #will repeat that for each photon
  dfFinal = dfFinal.append(dfTOF)

  print('\nRemoved negative input times and added the TOF correction to the dataframe\n')

  return dfFinal


  #Some plotting
  #plt.hist(dfTOF['Time'], bins = 100, label = 'Mean:%.2fns, Std:%.2fns'%(dfTOF['Time'].mean(), dfTOF['Time'].std()))
  #plt.title('TOF corrected time photon #1 new method\n%s'%('originalgeom'), fontsize = 'x-large')
  #plt.xlabel('Hit Time (ns)', fontsize = 'x-large')
  #plt.ylabel('Occurences, Total nb of hits:%i'%(len(dfTOF['Time'])), fontsize = 'x-large')
  #plt.grid()
  #plt.legend()
  #plt.show()
