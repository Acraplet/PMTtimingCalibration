#!/usr/bin/python
#Caller code to perform timing calibrations for any Water Cherenkov detector geometry

import numpy as np
import pandas as pd
import uproot
import TOFCorrection
import Smearing
import matplotlib.pyplot as plt
import iminuit as im
import os
import sys
import matplotlib.colors as colors

#step 1: import the dataset
#os.chdir("../WCSim/")
name = "%s"%sys.argv[1]#"wcsim_1kphot_3eV_16c_pos0_CherenkovDigiHits.root"


if name[0] == ".":
  print("Please give the name of the file, not the path to it, if it is not in ../WCSim check the code")
  raise wrongFile


saveFile = False

if sys.argv[2] == "1":
  saveFile = True



#"wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits.root"
#"wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits.root"
#
os.chdir("/home/ac4317/Laptops/Year1/WCTE/WCSim")
tree = uproot.open("../WCSim/%s"%name)["ntuple"]
df = tree.arrays(library="pd")

#step 2: TOF corrected time('TOFTime') to the dataset
pos = int(sys.argv[3])
if pos == 27:
  diffuserPosition = [75,75,-100]
if pos == 1:
  diffuserPosition = [-75,-75,100]
if pos == 0 or pos == 14:
  diffuserPosition = [0,0,0]
if pos == 13:
  diffuserPosition = [0,0,-100]


offset = 950
dfTOF = TOFCorrection.AddTOFCorrection(df, diffuserPosition, offset)

#save a copy of the file with the flagged values
dfTOFwithFlag = dfTOF

#Ignore Dark noises and reflections
dfTOF = dfTOF[abs(dfTOF['TOFTime']) != 9999]

print(len(dfTOF['TOFTime']))
#step 2.5: check the TOF correction for reco dataset


#now some fitting:
def fit_func_gauss(xx,A,mean,std):
    #function to fit
        return A*np.exp(-(xx-mean)**2/(2*std**2))

def least_squares_np(params):
    #least square function that will be optimised by iminuit
    global hist, mean_beans, sig
    return sum((hist-fit_func_gauss(mean_beans, *params))**2/sig)

t = dfTOF['Time']-930
sig = 1

hist, bin_edges = np.histogram(t, density=False, bins = 100)
#plt.plot(hist, bin_edges[:-1])
mean_beans = np.array([(bin_edges[i]+bin_edges[i+1])/2 for i in range(len(bin_edges)-1)])
po = [len(t),t.mean(),t.std()]

for i in range(10):
    m=im.Minuit(least_squares_np, (po[0], po[1], po[2]))
    m.errordef = 1
    m.migrad()
    po=m.values
po_time = po
print(po)


#plt.show()
#plt.show()





plt.figure(figsize=(20,15))
plt.plot(np.linspace(-50, 50, 1000), fit_func_gauss(np.linspace(-50, 50, 1000), *po), 'k--')
plt.hist(dfTOF['Time']-930, bins = 99, label = 'Initial \nMean: %.2fns, Std: %.2fns'%(po_time[1]+930, abs(po_time[2])))

t = dfTOF['TOFTime']
sig = 1

hist, bin_edges = np.histogram(t, density=False, bins = 100)
#plt.plot(hist, bin_edges[:-1])
mean_beans = np.array([(bin_edges[i]+bin_edges[i+1])/2 for i in range(len(bin_edges)-1)])
po = [len(t),t.mean(),t.std()]

for i in range(10):
    m=im.Minuit(least_squares_np, (po[0], po[1], po[2]))
    m.errordef = 1
    m.migrad()
    po=m.values
print(po)
po_TOFTime = po




plt.plot(np.linspace(-50, 50, 1000), fit_func_gauss(np.linspace(-50, 50, 1000), *po), 'k--')
#plt.show()


plt.hist(dfTOF['TOFTime'], bins = 99, label = 'TOF Corrected \nMean: %.2fns, Std: %.2fns'%(po_TOFTime[1], abs(po_TOFTime[2])))
plt.title('Time of flight correction \n %s'%(name), fontsize = 'xx-large')
plt.xlabel('Hit Time (ns)', fontsize = 'x-large')
plt.ylabel('Occurences, Total nb of hits:%i'%(len(dfTOF['TOFTime'])), fontsize = 'x-large')
plt.grid()
plt.xlim(-5, 35)
plt.legend(fontsize='x-large')

path = "/home/ac4317/Laptops/Year1/WCTE/New_codes/Pictures/%s"%name[:-5]
if (not os.path.isdir(path)):
  print("\nCreating a new forlder %s"%path)
  os.makedirs(path)
os.chdir(path)
plt.savefig("%s_TOF_correction.png"%name[:-5])
plt.show()



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
nb_hits = 500
dfTOF_calibrated = Smearing.Calibrate(dfTOF_smeared, nb_hits= nb_hits)

#dfTOF_calibrated = dfTOF_calibrated[abs(dfTOF_calibrated['smearingTime']) <= 40]

#ignore the pmts without enough hits
dfTOF_calibrated = dfTOF_calibrated[abs(dfTOF_calibrated['calibration_mean']) <= 9997]
#can also check removing the non-smeared PMTs -> good to check but doesn't affect the output
dfTOF_calibrated = dfTOF_calibrated[abs(dfTOF_calibrated['smearingTime']) != 0]





#plotting hor succesful the calibration is
plt.figure(figsize=(20,12))
plt.subplot(2, 1, 1)
plt.title('Comparision calibrated time and smearedTime mu = %.2f, sigma = %.2f \n fraction of times smeared = %.2f for pmts with at least %i hits: %s'%(mu, sigma, fraction, nb_hits, name), fontsize = 'xx-large', weight = 'bold')
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
#path = "/home/ac4317/Laptops/Year1/WCTE/New_codes/Pictures/%s"%name
if (not os.path.isdir(path)):
  print("\n Making new directory %s \n"%path)
  os.makedirs(path)
os.chdir(path)
plt.savefig("%s_calibration%i.png"%(name[:-5], nb_hits))
#plt.show()


source = diffuserPosition
plt.figure(figsize=(20,12))
#Here check the std of each pmt as a function of the distance to the source
distance = (dfTOF_calibrated['PMT_x']-source[0])**2 + (dfTOF_calibrated['PMT_y']-source[1])**2 + (dfTOF_calibrated['PMT_z']-source[2])**2
distance = np.sqrt(distance)

plt.plot(distance, abs(dfTOF_calibrated['calibration_std']), 'x', label = 'source at %s'%source)
plt.xlabel('Carthesian distance to the source (cm)', fontsize = 'xx-large')
plt.ylabel('Std of the gaussian fitted to each PMT (ns)', fontsize = 'xx-large')
plt.title("Standard deviation of the PMT's hit time distribution as a function of the distance to the source with at least %i hits \n  %s"%(nb_hits, name), fontsize = 'xx-large', weight = 'bold')
plt.legend()
plt.grid()

if (not os.path.isdir(path)):
  print("\n Making new directory %s \n"%path)
  os.makedirs(path)
os.chdir(path)
plt.savefig("%s_std_vs_dist_cal%i.png"%(name[:-5],nb_hits))
#plt.show()

#adding the very useful PMT_ID index
dfTOFwithFlag['PMT_ID'] = dfTOFwithFlag['mPMT_pmt'] + dfTOFwithFlag['mPMT']*20


source = diffuserPosition
plt.figure(figsize=(20,12))
#fig, ax = plt.subplots(1, 1)
#Here check the std of each pmt as a function of the distance to the source

list_nb_hits = []
list_ratio = []
list_dist = []

for i in dfTOFwithFlag['PMT_ID'].unique():
  buf = dfTOFwithFlag[dfTOFwithFlag['PMT_ID']==i]
  #print("PMT_ID", i, len(buf["TOFTime"]), len(buf[buf["TOFTime"]==9999]["TOFTime"]))

  #print(buf['PMT_x'].mean(), buf['PMT_y'].mean(), buf['PMT_z'].mean())
  #the distance is the same for all points here, we use mean bacause it is easier
  distance = (buf['PMT_x'].mean()-source[0])**2 + (buf['PMT_y'].mean()-source[1])**2 + (buf['PMT_z'].mean()-source[2])**2

  distance = np.sqrt(distance)

  #print(distance, len(buf[buf["TOFTime"]==9999])/len(buf["TOFTime"]))
  #plt.plot(distance, len(buf[buf["TOFTime"]==9999])/len(buf["TOFTime"]), 'bx')
  list_nb_hits.append(len(buf[buf["TOFTime"]!=9999]["TOFTime"]))
  list_ratio.append(len(buf[buf["TOFTime"]==9999])/len(buf["TOFTime"]))#
  list_dist.append(distance)


list_nb_hits = np.array(list_nb_hits)
#plt.plot(distance, len(buf[buf["TOFTime"]==9999]["TOFTime"])/len(buf["TOFTime"]), 'bx', label = 'source at %s'%source)

#plt.pcolor(list_dist, list_ratio, list_nb_hits, cmap='PuBu_r', shading='auto')
#plt.colorbar(pcm, ax=ax[1], extend='max')

plt.scatter(list_dist, list_ratio, c=list_nb_hits, cmap='rainbow', norm=colors.LogNorm(vmin=2, vmax=list_nb_hits.max()))
cbar = plt.colorbar()
cbar.set_label('# of direct hits per PMT', rotation=270, fontsize = 'x-large')

plt.xlabel('Carthesian distance to the source (cm)', fontsize = 'xx-large')
plt.ylabel('Ratio nb_refelctions/total_nb_hits', fontsize = 'xx-large')
plt.title("nb_refelctions/total_nb_hits of the PMT's hit time distribution as a function of the distance to the source \n source at %s %s"%(diffuserPosition, name), fontsize = 'xx-large', weight = 'bold')
#plt.legend()
plt.grid()

if (not os.path.isdir(path)):
  print("\n Making new directory %s \n"%path)
  os.makedirs(path)
os.chdir(path)
plt.savefig("%s_ratio_refelctions_vs_dist_cal.png"%(name[:-5]))
#plt.show()




if saveFile == True:
  os.chdir("/home/ac4317/Laptops/Year1/WCTE/DataSets")
  df_eval = dfTOF_calibrated
  treeBranches = {column : str(df_eval[column].dtypes) for column in df_eval}
  branchDict = {column : np.array(df_eval[column]) for column in df_eval}
  #tree = uproot.WritableTree(treeBranches)


  #sys.path.append("/home/acraplet/Alie/Masters/")
  with uproot.recreate("%s_cal%i.root"%(name[:-5], nb_hits)) as f:
      print("\n Saving file as  %s_cal%i.root \n"%(name[:-5], nb_hits))
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





