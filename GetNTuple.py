#!/usr/bin/python

#a program to select the entries of the root files that are or interest for the follwoing part

import sys
import uproot
import numpy as np

import pandas as pd
import matplotlib.pyplot as plt
import tensorflow as tf
import awkward as ak

import sys

#Select which branch you are intersted to
#branch = "CherenkovHits"
branch = "CherenkovDigiHits"

name = "%s"%sys.argv[1]

# loading the tree
tree = uproot.open("%s"%name)["%s"%branch]
#tree = uproot.open("wcsim_output_10kphot_1kev_originalgeom_flat.root")["CherenkovHits"]


# define what variables are to be read into the dataframe
if branch == "CherenkovHits":
  target = [ "mPMT", "mPMT_pmt", "PMT_QTot", "PMT_x", "PMT_y", "PMT_z",  "Time"]

if branch == "CherenkovDigiHits":
  target = [ "mPMT", "mPMT_pmt", "Q", "PMT_x", "PMT_y", "PMT_z",  "T"]


subtree = tree.arrays(target, library="ak")



photonID = np.array([])
mPMT =  np.array([])
mPMT_pmt =  np.array([])
PMT_QTot =  np.array([])
PMT_x = np.array([])
PMT_y = np.array([])
PMT_z = np.array([])
Time =  np.array([])


nb_photons = len(subtree['mPMT'])

#create numpy arrays with the informations including one with the photon number 
for i in range(nb_photons):
  photon_index = np.array(subtree['mPMT'][i])*0+i
  photonID = np.append(photonID, photon_index, axis = 0)
  mPMT = np.append(mPMT, np.array(subtree['mPMT'][i]), axis = 0)
  mPMT_pmt = np.append(mPMT_pmt, np.array(subtree['mPMT_pmt'][i]), axis = 0)
  PMT_x = np.append(PMT_x, np.array(subtree['PMT_x'][i]), axis = 0)
  PMT_y = np.append(PMT_y, np.array(subtree['PMT_y'][i]), axis = 0)
  PMT_z = np.append(PMT_z, np.array(subtree['PMT_z'][i]), axis = 0)
  if branch == "CherenkovHits":
    Time = np.append(Time, np.array(subtree['Time'][i]), axis = 0)
    PMT_QTot = np.append(PMT_QTot, np.array(subtree['PMT_QTot'][i]), axis = 0)
  if branch == "CherenkovDigiHits":
    Time = np.append(Time, np.array(subtree['T'][i]), axis = 0)
    PMT_QTot = np.append(PMT_QTot, np.array(subtree['Q'][i]), axis = 0)


#Currently usign the same naming system for CherenkovDigiHits and CherenkovHits
#maybe not ideal cause the only information about whether it is Digi or not is now
#in the file name...
branchDict = {'photonID': photonID,
              'mPMT': mPMT,
              'mPMT_pmt': mPMT_pmt,
              'PMT_QTot': PMT_QTot,
              'PMT_x': PMT_x,
              'PMT_y': PMT_y,
              'PMT_z': PMT_z,
              'Time':Time
              }

makeup = uproot.recreate("%s_%s.root"%(name[:-10],branch))
makeup['ntuple']= branchDict
makeup.close()



