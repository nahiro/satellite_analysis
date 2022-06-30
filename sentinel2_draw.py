#!/usr/bin/env python
import os
import sys
import gdal
from glob import glob
import numpy as np
import matplotlib as mpl
import matplotlib.pyplot as plt
import matplotlib.cm as cm
from matplotlib.backends.backend_pdf import PdfPages

datdir = '.'
band = 'B4'

band_list = []
with open('band_names.txt','r') as fp:
    for line in fp:
        item = line.split()
        if len(item) != 2:
            continue
        band_list.append(item[1])

plt.interactive(True)
fig = plt.figure(1,facecolor='w',figsize=(6,7))
plt.subplots_adjust(left=0.1,right=0.95,bottom=0.05,top=0.95,hspace=0.05)

pdf = PdfPages('L2A_{}.pdf'.format(band))
fs = sorted(glob(os.path.join(datdir,'*_resample.tif')))
for fnam in fs:
    f = os.path.splitext(os.path.basename(fnam))[0].split('_')[0]

    ds = gdal.Open(fnam)
    indx = band_list.index('quality_scene_classification')
    flag = ds.GetRasterBand(indx+1).ReadAsArray()
    indx = band_list.index(band)
    data = ds.GetRasterBand(indx+1).ReadAsArray()*1.0e-4
    ds = None

    fig.clear()
    #ax1 = plt.subplot(211,frameon=False)
    ax1 = plt.subplot(211)
    ax1.set_xticks([])
    ax1.set_yticks([])
    im = ax1.imshow(data,vmin=0.0,vmax=0.4,cmap=cm.jet)
    ax12 = plt.colorbar(im,ticks=np.arange(0.0,1.0,0.1)).ax
    ax12.set_ylabel('Reflectance')
    ax12.yaxis.set_label_coords(4.0,0.5)
    ax1.set_title('L2A '+f+' '+band,y=1.005)

    #ax2 = plt.subplot(212,frameon=False)
    ax2 = plt.subplot(212)
    ax2.set_xticks([])
    ax2.set_yticks([])
    flag[flag >= 7.5] = np.nan
    bounds = np.arange(0.5,7.6,1.0)
    cmap = mpl.colors.ListedColormap(['red','#666666','brown','g','y','b','m'])
    cmap.set_over('w')
    cmap.set_under('k')
    norm = mpl.colors.BoundaryNorm(bounds,cmap.N)
    #ax2.imshow(flag,vmin=0.0,vmax=25.0,cmap=cm.gray) # cloud_confidence
    #ax2.imshow(flag,vmin=0.0,vmax=0.3,cmap=cm.gray) # aot
    #im = ax2.imshow(flag,vmin=0.0,vmax=7.5,cmap=cmap,norm=norm) # scene_classification
    im = ax2.imshow(flag,cmap=cmap,norm=norm) # scene_classification
    ax22 = plt.colorbar(im,extend='both',boundaries=[-10]+list(bounds)+[10],extendfrac='auto',ticks=bounds+0.5).ax
    ax22.set_ylabel('Label')
    ax22.yaxis.set_label_coords(4.0,0.5)

    #gnam = os.path.splitext(os.path.basename(fnam))[0]+'.png'
    plt.draw()
    plt.pause(0.1)
    #plt.savefig(gnam)
    plt.savefig(pdf,format='pdf')
    sys.stderr.write('{} {:5d} {:5d} {:8d}\n'.format(f,data.shape[1],data.shape[0],data.size))
    #break
pdf.close()
