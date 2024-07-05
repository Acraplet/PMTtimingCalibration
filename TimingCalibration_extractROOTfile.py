#!/usr/bin/python
#Caller code to perform timing calibrations for any Water Cherenkov detector geometry
import sys
import numpy as np
import pandas as pd
import uproot
import TOFCorrection#_extractRootfile as TOFCorrection
import Smearing
import matplotlib.pyplot as plt

#step 1: import the dataset
name = "wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits.root"
#"wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits.root"
#
#
tree = uproot.open("%s"%name)["ntuple"]
df = tree.arrays(library="pd")

#step 2: TOF corrected time('TOFTime') to the dataset
diffuserPosition = [0,0,0]
offset = 950
dfTOF = TOFCorrection.AddTOFCorrection(df, diffuserPosition, offset)

#Ignore Dark noises and reflections
dfTOF = dfTOF[dfTOF['TOFTime'] != -9999]

#Step 3.1.1: Order the datasets and keep only 1 hit time to compare with True dataset:
#checking event by event by changing line 43 in TOFCorrection.py
check = False

if check == True:
  #Step 3.0: Check agreement with true dataset
  nameTrue = "wcsim_output_10kphot_1kev_originalgeom_CherenkovHits.root"
  treeTrue = uproot.open("%s"%nameTrue)["ntuple"]
  dfTrue = treeTrue.arrays(library="pd")

  #Need to TOF correct the true data too
  offset = 0
  dfTOFTrue = TOFCorrection.AddTOFCorrection(dfTrue, diffuserPosition, offset)

  #Ignore Dark noises and reflections
  dfTOFTrue = dfTOFTrue[dfTOFTrue['TOFTime'] != -9999]

  dfTOF_sorted, dfTOFTrue_sorted = Smearing.FilterAlign(dfTOF, dfTOFTrue)

  if abs(len(dfTOF_sorted)-len(dfTOFTrue_sorted)) <= 1:
    print('Mapping sucessful! We have one more entry only')
    if len(dfTOF_sorted) == len(dfTOFTrue_sorted)+1:
      difference = dfTOF_sorted[:-1] - dfTOFTrue_sorted
      heck = dfTOF_sorted['Time'][:-1] - dfTOFTrue_sorted['TOFTime']
    if len(dfTOF_sorted)+1 == len(dfTOFTrue_sorted):
      difference = dfTOF_sorted - dfTOFTrue_sorted[:-1]
      check = dfTOF_sorted['Time'] - dfTOFTrue_sorted['TOFTime'][:-1]
    if len(dfTOF_sorted) == len(dfTOFTrue_sorted):
      difference = dfTOF_sorted - dfTOFTrue_sorted
      check = dfTOF_sorted['Time'] - dfTOFTrue_sorted['TOFTime']
    print(difference)


#step3: Smear the dataset:
mu = 0
sigma = 25
fraction = 1
dfTOF_smeared = Smearing.AddSmearing(dfTOF, mu = mu, sigma = sigma, fraction = fraction)


#Step 4: Calibrate the offset out:
nb_hits = 300
dfTOF_calibrated = Smearing.Calibrate(dfTOF_smeared, nb_hits= nb_hits)

#dfTOF_calibrated = dfTOF_calibrated[abs(dfTOF_calibrated['smearingTime']) <= 40]

#ignore the pmts without enough hits
dfTOF_calibrated = dfTOF_calibrated[abs(dfTOF_calibrated['calibration_mean']) <= 9998]
#can also check removing the non-smeared PMTs -> good to check but doesn't affect the output
#dfTOF_calibrated = dfTOF_calibrated[abs(dfTOF_calibrated['smearingTime']) != 0]


print('Standard devition droped from: ', dfTOF_smeared['smearedTime'].std(), 'to: ', (dfTOF_smeared['smearedTime']-dfTOF_calibrated['calibration_mean']).std())


#extract the root file with all the python-computed data to compare with ROOT likelihood tests
#print(type(dfTOF_calibrated))
#dfTOF_calibrated.to_csv('example3.csv', index_label='index')

df_eval = dfTOF_calibrated
treeBranches = {column : str(df_eval[column].dtypes) for column in df_eval}
branchDict = {column : np.array(df_eval[column]) for column in df_eval}
#tree = uproot.WritableTree(treeBranches)



#sys.path.append("/home/acraplet/Alie/Masters/")
with uproot.recreate("%s_cal300.root"%name[:-5]) as f:
    f.mktree("ntuple", treeBranches)
    #f["ntuple"] = tree
    f["ntuple"].extend(branchDict)



raise BelowPlotting


#step 2.5: check the TOF correction for reco dataset
plt.hist(dfTOF['TOFTime'], bins = 100, label = 'Mean:%.2fns, Std:%.2fns'%(dfTOF['TOFTime'].mean(), dfTOF['TOFTime'].std()))
plt.title('TOF corrected time new method\n%s'%name, fontsize = 'x-large')
plt.xlabel('Hit Time (ns)', fontsize = 'x-large')
plt.ylabel('Occurences, Total nb of hits:%i'%(len(dfTOF['TOFTime'])), fontsize = 'x-large')
plt.grid()
#plt.xlim(-10, 30)
plt.legend()
plt.show()

#step 2.5: check the TOF correction for true dataset
plt.hist(dfTOFTrue['TOFTime'], bins = 100, label = 'Mean:%.2fns, Std:%.2fns'%(dfTOFTrue['TOFTime'].mean(), dfTOFTrue['TOFTime'].std()))
plt.title('True time TOF shifted new method\n%s'%nameTrue, fontsize = 'x-large')
plt.xlabel('Hit Time (ns)', fontsize = 'x-large')
plt.ylabel('Occurences, Total nb of hits:%i'%(len(dfTOFTrue['TOFTime'])), fontsize = 'x-large')
plt.grid()
#plt.xlim(-10, 30)
plt.legend()
plt.show()


#check the compatibility between True and Reco datasets
plt.title('TOF corrected time new method\n%s'%name, fontsize = 'x-large')
plt.subplot(1,2,2)
plt.hist(check, bins = 100, label = 'Mean:%.2fns, Std:%.2fns'%(check.mean(), check.std()))
plt.xlabel('Hit Time difference RecoTOF-True (ns)', fontsize = 'x-large')
plt.ylabel('Occurences, Total nb of hits:%i'%(len(check)), fontsize = 'x-large')
plt.grid()
plt.legend()

plt.subplot(1,2,1)
plt.hist(difference['TOFTime'], bins = 100, label = 'Mean:%.2fns, Std:%.2fns'%(difference['TOFTime'].mean(), difference['TOFTime'].std()))
plt.xlabel('Hit Time difference RecoTOF-TrueTOF(ns)', fontsize = 'x-large')
plt.ylabel('Occurences, Total nb of hits:%i'%(len(difference['TOFTime'])), fontsize = 'x-large')
plt.grid()
plt.legend()
plt.show()

#compare the TOF time and the smeared time
plt.subplot(2,1,1)
plt.title(f'Comparision TOFTime and smearedTime \n mu = {mu}, sigma = {sigma} fraction of times smeared = {fraction}', fontsize = 'xx-large', weight = 'bold')
plt.ylabel(f'TOF Time', fontsize = 'x-large')
plt.xlim(-10, 20+mu)
plt.hist(dfTOF_smeared['TOFTime'], bins = 100)
plt.grid()

plt.subplot(2,1,2)
plt.grid()
#plt.xlim(-10, 20+mu)
plt.ylabel(f'Smeared Time', fontsize = 'x-large')
plt.hist(dfTOF_smeared['smearedTime'], bins = 100)
plt.xlabel('Time (ns)', fontsize = 'x-large')
print('Standard devition droped from: ', dfTOF_smeared['smearedTime'].std(), 'to: ', (dfTOF_smeared['smearedTime']-dfTOF_calibrated['calibration_mean']).std())
plt.show()

#plotting hor succesful the calibration is
plt.subplot(2, 1, 1)
plt.title('Comparision calibrated time and smearedTime \n mu = %.2f, sigma = %.2f fraction of times smeared = %.2f \n for pmts with at least %i hits'%(mu, sigma, fraction, nb_hits), fontsize = 'xx-large', weight = 'bold')
plt.plot(dfTOF_calibrated['smearingTime'], dfTOF_calibrated['calibration_mean'], 'x', label = 'Output of the calibration')
plt.xlabel('Smearing Time (ns)', fontsize = 'xx-large')
plt.ylabel('Calibration output (ns)', fontsize = 'xx-large')
ref = [dfTOF_calibrated['smearingTime'].min(), dfTOF_calibrated['smearingTime'].max()]
plt.plot(ref, ref, 'k--')
plt.grid()
plt.legend(fontsize='x-large')
plt.subplot(2, 1, 2)


diff = (dfTOF_calibrated['smearingTime']-dfTOF_calibrated['calibration_mean'])
diff = np.array(diff[diff<=30])
print(diff.max())
plt.hist(diff, bins = 50, label = 'Mean:%.3fns, std:%.3fns'%(diff.mean(), diff.std()))
plt.xlim(diff.mean()-5*diff.std(), diff.mean()+5*diff.std())
plt.xlabel('Difference between smearing time and calibrated times (ns)', fontsize = 'xx-large')
plt.ylabel("Number of hits", fontsize = 'xx-large')
plt.grid()
plt.legend(fontsize='x-large')
plt.show()



