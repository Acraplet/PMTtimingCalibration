
import numpy as np
import pandas as pd
import uproot
import TOFCorrection
import Smearing
import matplotlib.pyplot as plt
import iminuit as im

name = "../DataSets/wcsim_output_10kphot_1kev_originalgeom_CherenkovDigiHits_cal300.root"

tree = uproot.open("%s"%name)["ntuple"]
dfTOF_calibrated = tree.arrays(library="pd")

source = [0,0,0]
#Here check the std of each pmt as a function of the distance to the source
distance = (dfTOF_calibrated['PMT_x']-source[0])**2 + (dfTOF_calibrated['PMT_y']-source[1])**2 + (dfTOF_calibrated['PMT_z']-source[2])**2
distance = np.sqrt(distance)

plt.plot(distance, abs(dfTOF_calibrated['calibration_std']), 'x', label = 'source at %s'%source)
plt.xlabel('Carthesian distance to the source (cm)', fontsize = 'x-large')
plt.ylabel('Std of the gaussian fitted to each PMT (ns)', fontsize = 'x-large')
plt.title("Standard deviation of the PMT's hit time distribution \n as a function of the distance to the source", fontsize = 'x-large')
plt.legend()
plt.grid()
plt.show()


#plt.xlabel('Carthesian distance to the source (cm)', fontsize = 'xx-large')
