#!/usr/bin/python
#this is part a of the timing calibration software: apply the smearing correction to
#recorded as a function of the chosen origin. To be used with a caller code:
#TimingCalibration.py
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import numpy.random as rd
import random
from scipy.optimize import curve_fit
import iminuit as im


def Gauss(x, a, mean, sigma):
    return a*np.exp(-(x-mean)**2/(2*sigma**2))

def fit_func_gauss(xx,A,mean,std):
    #function to fit
        return A*np.exp(-(xx-mean)**2/(2*std**2))

def least_squares_np(params):
    #least square function that will be optimised by iminuit
    global hist, mean_beans, sig

    return sum((hist-fit_func_gauss(mean_beans,params[0], params[1], params[2]))**2/sig)


least_squares_np.errordef = im.Minuit.LEAST_SQUARES

def fit_Gaussian(times, nb_hits = 100):
  t = np.array(times)
  global hist, mean_beans, sig

  po_init = [1, 0, 1]
  if len(t)>nb_hits:
    sig = 1e-5
    hist, bin_edges = np.histogram(t, density=True, bins = int(len(t)/10))
    mean_beans = np.array([(bin_edges[i]+bin_edges[i+1])/2 for i in range(len(bin_edges)-1)])
    po = [1, t.mean(), t.std()]
    for i in range(10):
      m=im.Minuit(least_squares_np, (po[0],po[1],po[2]))
      m.migrad()
      po=m.values
    #print(po)
  #if m.valid==True:
    #plt.plot(mean_beans, hist, 'x', label = f'{m.valid}')
    #plt.plot(mean_beans, Gauss(mean_beans, po[0], po[1], po[2]), 'r-')
    #plt.legend()
    #plt.show()

    if abs(po[2])>=1000 or abs(po[0])>=1000 or po == po_init or po == [1, 1, 1]:
      sig = 1
      hist, bin_edges = np.histogram(t, density=True, bins = int(len(t)/20))
      mean_beans = np.array([(bin_edges[i]+bin_edges[i+1])/2 for i in range(len(bin_edges)-1)])
      print('fit failed with iminuit, try with scipy')
      po = [1, t.mean(), t.std()]
      #print(po)
      #po, _ = curve_fit(Gauss, mean_beans, hist)
      for i in range(10):
        m=im.Minuit(least_squares_np, (po[0],po[1],po[2]))
        m.migrad()
        po=m.values
      print(po)
      #plt.plot(mean_beans, hist, 'x', label = 'second try')
      #plt.plot(mean_beans, Gauss(mean_beans, po[0], po[1], po[2]), '-')
      #plt.legend()
      #plt.show()
    return po[1], po[2]

#if only a few hits -> need to lower the quality of the fit -> lower number of bins
#for now a hard cut, can arrange later
  else :
    #sig = 1e-7
    #hist, bin_edges = np.histogram(t, density=True, bins = int(len(t)/6))
    #mean_beans = np.array([(bin_edges[i]+bin_edges[i+1])/2 for i in range(len(bin_edges)-1)])
    #po = [1, t.mean(), t.std()]
    #for i in range(10):
      #m=im.Minuit(least_squares_np, (po[0],po[1],po[2]))
      #m.migrad()
      #po=m.values


    #print(po)
    #if m.valid==True:
    #plt.plot(mean_beans, hist, 'x', label = f'{m.valid}')
    #plt.plot(mean_beans, Gauss(mean_beans, po[0], po[1], po[2]), 'r-')
    #plt.legend()
    #plt.show()

    #if abs(po[2])>=1000 or abs(po[0])>=1000 or po == po_init:
      #sig = 1e-3
      #po = [1, t.mean(), t.std()]
      #hist, bin_edges = np.histogram(t, density=True, bins = int(len(t)/4))
      #mean_beans = np.array([(bin_edges[i]+bin_edges[i+1])/2 for i in range(len(bin_edges)-1)])
      #print('fit failed with iminuit, try with scipy low number of edge')
      #for i in range(10):
        #m=im.Minuit(least_squares_np, (po[0],po[1],po[2]))
        #m.migrad()
        #po=m.values
      #print(po)


      #plt.plot(mean_beans, hist, 'x', label = 'second try low nub')
      #plt.plot(mean_beans, Gauss(mean_beans, po[0], po[1], po[2]), 'r-')
      #plt.legend()
      #plt.show()
    po = [1, -9999, -9999]
    return po[1], po[2]

def Calibrate(df, nb_hits):
  #want to extract the offseting times and the calibrated times
  print('Calibration has started, please wait')
  df['calibration_std'] = np.zeros(len(df))
  df['calibration_mean'] = np.zeros(len(df))
  u=0
  for i in df['PMT_ID'].unique():

    PMT_Time = df['smearedTime'][df['PMT_ID']==i]
    #u += len(PMT_Time)
    #print(u)
    mean, std = fit_Gaussian(PMT_Time, nb_hits)
    df['calibration_mean'][df['PMT_ID']==i] = mean

    #this should save std in all the correct positions of the column
    df['calibration_std'][df['PMT_ID']==i] = std


  print(u)

  return df


def AddSmearing(df, mu = 0, sigma = 1, fraction = 1):
  if 'TOFTime' not in df.columns:
   print("TOFTime doesn't exist:\nYou might need to run the AddTOFCorrection function\npart of the TOFCOrrection.py module")
   raise MissingTOFTime

  #This is needed otherwise we have a painful warning message
  df=df.copy()

  #This is a unique number allocated to a given pmt correcponding
  df['PMT_ID'] = df['mPMT_pmt'] + df['mPMT']*20
  nb = df['PMT_ID'].astype(int).to_numpy()

  #a list of random numbers useful for making selections later
  #this is a uniform distibution between 0 and 1
  rand2 = pd.DataFrame(rd.rand(int(df['PMT_ID'].max())))

  #make a dataframe with the random number of each PMT
  r = rand2.iloc[nb-1][0].reset_index()
  smearing_list = pd.DataFrame([random.gauss(mu, sigma) for i in range(len(rand2))])[0]

  #get the right smearing for each PMT
  sm = smearing_list.iloc[nb-1]

  #draw from a given distribution offset times for a given fraction of pmts
  df['smearingTime'] = np.where(r[0] <= fraction, sm, 0)
  df['smearedTime'] = df['TOFTime']+df['smearingTime']

  return df


def FilterAlign(dfTOF_sorted, dfTOFTrue_sorted):
  #A function to compare true and reco dataset ignoring pmts hit in one of the file but not the other
  #careful, this code updates the index. It is also very slow with large dataset
  #it also only saves the earliest hit time. We need to cut 3 entries at the end to make this work
  dfTOF_sorted = dfTOF_sorted.sort_values(by=['photonID', 'mPMT', 'mPMT_pmt', 'TOFTime'], ascending=True, ignore_index=True)
  #earliest hit time is saved only
  dfTOF_sorted = dfTOF_sorted.drop_duplicates(subset=['photonID','mPMT', 'mPMT_pmt'], keep='first', ignore_index=True)

  dfTOFTrue_sorted = dfTOFTrue_sorted.sort_values(by=['photonID', 'mPMT', 'mPMT_pmt', 'TOFTime'], ascending=True, ignore_index=True)
  dfTOFTrue_sorted = dfTOFTrue_sorted.drop_duplicates(subset=['photonID', 'mPMT', 'mPMT_pmt'], keep='first', ignore_index=True)
  i = 0
  lenghtMax = min(len(dfTOF_sorted), len(dfTOFTrue_sorted))

  while i <= lenghtMax-4:
    #print(i, dfTOF_sorted['mPMT_pmt'][i])
    shift = 0
    if (dfTOF_sorted['mPMT_pmt'][i] != dfTOFTrue_sorted['mPMT_pmt'][i] and dfTOF_sorted['mPMT'][i] == dfTOFTrue_sorted['mPMT'][i]) or (dfTOF_sorted['mPMT'][i] != dfTOFTrue_sorted['mPMT'][i]):
      #print(dfTOF_sorted['mPMT_pmt'][i], dfTOFTrue_sorted['mPMT_pmt'][i])

      #did have an extra entry?
      if dfTOF_sorted['mPMT_pmt'][i+1] == dfTOFTrue_sorted['mPMT_pmt'][i] and dfTOF_sorted['mPMT'][i+1] == dfTOFTrue_sorted['mPMT'][i]:
        dfTOF_sorted.drop([i], inplace = True)
        dfTOF_sorted.reset_index(drop = True, inplace = True)
        #print('\nRemoved #%i in the Reco dataset'%i)
        #print(dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :])
        ##print(dfTOF_sorted.iloc[i-10:i+10, :])
        shift = 1

      if dfTOF_sorted['mPMT_pmt'][i+2] == dfTOFTrue_sorted['mPMT_pmt'][i] and dfTOF_sorted['mPMT'][i+2] == dfTOFTrue_sorted['mPMT'][i]:
        dfTOF_sorted.drop([i, i+1], inplace = True)
        dfTOF_sorted.reset_index(drop = True, inplace = True)
        #print('\nRemoved #%i and #%i in the Reco dataset'%(i, i+1))
        #print(dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :])
        #print(dfTOF_sorted.iloc[i-10:i+10, :])
        shift = 1
        i = i-1

      if dfTOF_sorted['mPMT_pmt'][i+3] == dfTOFTrue_sorted['mPMT_pmt'][i] and dfTOF_sorted['mPMT'][i+3] == dfTOFTrue_sorted['mPMT'][i]:
        dfTOF_sorted.drop([i, i+1, i+2], inplace = True)
        dfTOF_sorted.reset_index(drop = True, inplace = True)
        #print('\nRemoved #%i and #%i and #%i in the Reco dataset'%(i, i+1, i+2))
        #print(dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :])
        #print(dfTOF_sorted.iloc[i-10:i+10, :])
        shift = 1
        i = i-2

      #or was it dfTOFTrue_sorted?
      if dfTOF_sorted['mPMT_pmt'][i] == dfTOFTrue_sorted['mPMT_pmt'][i+1] and dfTOF_sorted['mPMT'][i] == dfTOFTrue_sorted['mPMT'][i+1]:
        dfTOFTrue_sorted.drop([i], inplace = True)
        dfTOFTrue_sorted.reset_index(drop = True, inplace = True)
        #print('\nRemoved #%i in the True dataset'%i)
        #print(dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :])
        #print(dfTOF_sorted.iloc[i-10:i+10, :])
        shift = 1

      if dfTOF_sorted['mPMT_pmt'][i] == dfTOFTrue_sorted['mPMT_pmt'][i+2] and dfTOF_sorted['mPMT'][i] == dfTOFTrue_sorted['mPMT'][i+2]:
        dfTOFTrue_sorted.drop([i, i+1], inplace = True)
        dfTOFTrue_sorted.reset_index(drop = True, inplace = True)
        #print('\nRemoved #%i and #%i in the True dataset'%(i, i+1))
        #print(dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :])
        ##print(dfTOF_sorted.iloc[i-10:i+10, :])
        i = i-1
        shift = 1

      if dfTOF_sorted['mPMT_pmt'][i] == dfTOFTrue_sorted['mPMT_pmt'][i+3] and dfTOF_sorted['mPMT'][i] == dfTOFTrue_sorted['mPMT'][i+3]:
        dfTOFTrue_sorted.drop([i, i+1, i+2], inplace = True)
        dfTOFTrue_sorted.reset_index(drop = True, inplace = True)
        #print('\nRemoved #%i and #%i and #%i in the True dataset'%(i, i+1, i+2))
        #print(dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :])
        ##print(dfTOF_sorted.iloc[i-10:i+10, :])
        i = i-2
        shift = 1

      if shift == 0:
        #print('Issue at', i)
        #print(dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :])
        zoom = dfTOFTrue_sorted.iloc[i-10:i+10, :]-dfTOF_sorted.iloc[i-10:i+10, :]
        if zoom['mPMT'][i+1] == 0 and zoom['mPMT_pmt'][i+1] == 0:
          dfTOFTrue_sorted.drop([i], inplace = True)
          dfTOFTrue_sorted.reset_index(drop = True, inplace = True)
          dfTOF_sorted.drop([i], inplace = True)
          dfTOF_sorted.reset_index(drop = True, inplace = True)
        if zoom['mPMT'][i+2] == 0 and zoom['mPMT_pmt'][i+2] == 0:
          dfTOFTrue_sorted.drop([i, 1+1], inplace = True)
          dfTOFTrue_sorted.reset_index(drop = True, inplace = True)
          dfTOF_sorted.drop([i, 1+1], inplace = True)
          dfTOF_sorted.reset_index(drop = True, inplace = True)
          #print('Yes at 2')
          i = i-1

    if shift != 1:
      i = i+1
    lenghtMax = min(len(dfTOF_sorted), len(dfTOFTrue_sorted))
    #print(lenghtMax)

  return dfTOF_sorted[:-3], dfTOFTrue_sorted[:-3]

