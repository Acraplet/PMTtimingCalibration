import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

file_path = "/home/ac4317/Laptops/Year1/WCTE/DataSets/geofile_NuPRISMBeamTest_16cShort_mPMT_topcapcentralpmtremoved.txt"

def convert_3d_to_2d_cylinder(x,y,z):
    x = np.array(x)
    y = np.array(y)
    z = np.array(z)

    out_x = 396/2 * np.arctan(x/z) #+ (np.sign(x) - np.sign(z))/2 * 2 *  np.pi*396

    #z + np.sqrt(1+x**2)

    #
    #396 - radius in cm
    out_x_plus = np.where(out_x>0, out_x, 0)
    out_x_minus = np.where(out_x<0, out_x, 0)
    out_x_plusx_plusz = np.where(z>0, out_x_plus, 0)
    out_x_minusx_plusz = np.where(z>0, out_x_minus, 0)
    out_x_plusx_minusz = np.where(z<0, ( out_x_plus - np.pi/2 * 396) , 0)
    out_x_minusx_minusz = np.where(z<0, (out_x_minus + np.pi/2 * 396), 0)

    out_x = out_x_plusx_plusz + out_x_minusx_plusz + np.where(out_x>0, out_x_plusx_minusz, out_x_minusx_minusz)


    #end caps
    out_x = np.where((y>=y.max()-5.5), x, out_x)
    out_y = np.where((y>=y.max()-5.5), z + 250, y)


    out_x = np.where((y<=y.min()+5.5), x, out_x)
    out_y = np.where((y<=y.min()+5.5), z - 250 , out_y)

    return out_x, out_y

df = pd.DataFrame()
i=0

with open(file_path) as file:
    for line in file:
        c=[]
        a = line.rstrip().split()
        for b in a:
            c.append(float(b))
        new_row = pd.Series(data=c, index=['i', 'mPMT_id', 'PMT_id', 'x','y', 'z', 'x_dir', 'y_dir', 'z_dir', 'dense'], dtype=np.float64)
        df = df.append(new_row, ignore_index=True)
file.close()

print(df)



df["2d_x"], df["2d_y"] = convert_3d_to_2d_cylinder(df["x"], df['y'], df['z'])

print(df)

df['mPMT_id'] = df['mPMT_id'] - 10995

fig = plt.figure(figsize=(20,10))
ax = plt.axes()
#ax.set_title("binned Poisson likelihood (per bin)\n%s"%(name_short), fontsize="xx-large")
ax.scatter(df["2d_x"],  df["2d_y"], s = 10)
i = 8
while i<len(df):
    ax.text(df["2d_x"][i],  df["2d_y"][i], "%i"%df['mPMT_id'][i], weight = 'bold')
    i = i+19
plt.title("WCSim 16cShort mPMT_id", weight = 'bold')
plt.xlabel("x")
plt.ylabel("y")
plt.show()
