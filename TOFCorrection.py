#!/usr/bin/python
#this is part a of the timing calibration software: apply the TOF correction to
#recorded as a function of the chosen origin. To be used with a caller code:
#TimingCalibration.py

'''How is the TOF made?

waterVelocity set at 22.34 cm ns^-1.

Caluclate the longest travel time within the detector with (DistFullColumn(dfTOF, origin)/waterVelocity).max() and add the input offset to it. This is based on the largest distance between a PMT that has been hit and the position of the source - origin.

Create a reference dataframe: dfTOFPos that has no reflections (hit time after the longest possible straight travel time) and no dark noise (hit time before offset).

TOF correct by calculating the distance to the source and divide by velocity of sound in water both the reference dataframe dfTOFPos and the full dataframe.

Substract the mean of the TOFTime of the reference dataframe to the full dataset to shift the whole distribution so that the direct hits distribution has a mean of 0.

Highlight the initial hits that were either before the offset (DN) or after the longest straight travel time possible (reflections) in the tank and set their TOFTime to the flag value of -9999.

'''
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

  #if we want to make cuts on our dataframe
  dfTOF = df#'[df['photonID'] <= 500].copy()
  print('a', len(dfTOF['Time']))
  #And have the longest time that a photon can take to travel directly to one of the hit pmts
  longestTravelTime = (DistFullColumn(dfTOF, origin)/waterVelocity).max() + offset
  print('\n Longest straight line travel time possible in the detector', longestTravelTime, 'ns')

  #Grab the direct hit times
  dfTOFPos = dfTOF[dfTOF['Time'] >= offset]
  dfTOFPos = dfTOFPos[dfTOFPos['Time'] <= longestTravelTime].copy()

  #TOF correct both dataFrames
  dfTOFPos['TOFTime'] = dfTOFPos['Time'] - DistFullColumn(dfTOFPos, origin)/waterVelocity
  dfTOF['TOFTime'] = dfTOF['Time'] - DistFullColumn(dfTOF, origin)/waterVelocity


   #shift: mean time is now 0
  dfTOF['TOFTime'] = dfTOF['TOFTime'] - dfTOFPos['TOFTime'].mean()

  #The dark noise hit and reflections have TOFTime set to a flag value
  dfTOF.loc[dfTOF['Time'] >= longestTravelTime, ['TOFTime']] = +9999
  dfTOF.loc[dfTOF['Time'] <= offset, ['TOFTime']] = -9999

  #dataframe where we will add the TOF corrected times
  dfFinal= pd.DataFrame()
  dfFinal = dfFinal.append(dfTOF)

  print('\nRemoved negative input times and added the TOF correction to the dataframe\n')

  return dfFinal


