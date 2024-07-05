
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

#name = "%s"%sys.argv[1]
name0 = "../wcsim_hybrid_attenuation_fit_files/out_2k_pos0.root"
name0 = "../wcsim_hybrid_attenuation_fit_files/Output_checks/out_wcsim_2kphot_3eV_16cShort_pos0_v2.root"
name13 = "../wcsim_hybrid_attenuation_fit_files/Output_checks/out_wcsim_2kphot_3eV_16cShort_pos13_v2.root"
name1 = "../wcsim_hybrid_attenuation_fit_files/Output_checks/out_wcsim_2kphot_3eV_16cShort_pos1_v2.root"

tree0 = uproot.open("%s"%name0)["hitRate_pmtType0"]
tree1 = uproot.open("%s"%name1)["hitRate_pmtType0"]
tree13 = uproot.open("%s"%name13)["hitRate_pmtType0"]

df0 = tree0.arrays(library="pd")
df1 = tree1.arrays(library="pd")
df13 = tree13.arrays(library="pd")


lim_low = 947
lim_high = 952.5

list_df = [df1, df13, df0]
list_labels = [

    "wcsim_2kphot_3eV_16cShort_pos1.root \n source at [-75, -75, 100]",
    "wcsim_2kphot_3eV_16cShort_pos13.root \n source at [0, 0, 100]",
    "wcsim_2kphot_3eV_16cShort_pos0.root +5.5ns \n source at [0, 0, 0]",
               ]

for i in range(3):
    df = list_df[i]
    if i != 2:
        df = df[df["timetof"]>lim_low]
        df = df[df["timetof"]<lim_high]
    else:
        df = df[df["timetof"]>941.5]
        df = df[df["timetof"]<947]
        df["timetof"] = df["timetof"]+5.5


    plt.hist(df["timetof"], bins=20, histtype='step', label = "%s"%(list_labels[i]) )


plt.xlim(lim_low-2, lim_high+2)
plt.ylabel("Hits", fontsize='x-large')
plt.xlabel("timetof (ns)", fontsize='x-large')
plt.title("timetof with cuts [947-952.5] ", fontsize='x-large', weight='bold')
plt.grid()
plt.legend(fontsize='large')
plt.show()
