from astropy.table import Table, join
from astropy.io import fits
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
from scipy import stats

z_data = fits.open('/project/projectdirs/desi/datachallenge/quicksurvey2017/output/dark/4/zcat.fits')[1].data          
mask = z_data['SPECTYPE']=='GALAXY'
zgal= z_data[mask] 

bins = np.linspace(-20, 80, 20)                                                                                          
bin_size = bins[1]-bins[0]

mtl_data = fits.open('/project/projectdirs/desi/datachallenge/quicksurvey2017/output/dark/4/mtl.fits')[1].data         
mask = mtl_data['DESI_TARGET']!=4  
gal_data = mtl_data[mask]
joined_table = join(zgal, gal_data, keys='TARGETID')  
mask_join = joined_table['DESI_TARGET']==2 
masked_table = joined_table[mask_join]

#points = np.array([masked_table['DEC'], masked_table['RA'],masked_table['Z']])
#hist, binedges = np.histogramdd(points, normed=False)

#Setup a 3D figure and plot points as well as a series of slices
#fig = plt.figure()
#ax1 = fig.add_subplot(111, projection='3d')
#ax1.plot(points[:,0],points[:,1],points[:,2],'k.',alpha=0.3)

#Use one less than bin edges to give rough bin location
#X, Y = np.meshgrid(binedges[0][:-1],binedges[1][:-1])

#Loop over range of slice locations (default histogram uses 10 bins)
#for ct in [0,2,5,7,9]: 
 #   cs = ax1.contourf(X,Y,hist[:,:,ct], 
  #                    zdir='z', 
   #                   offset=binedges[2][ct], 
    #                  level=100, 
     #                 cmap=plt.cm.RdYlBu_r, 
      #                alpha=0.5)

#ax1.set_xlim(-3, 3)
#ax1.set_ylim(-3, 3)
#ax1.set_zlim(-3, 3)
#plt.colorbar(cs)
#savefig('radecz.png')
#plt.show()


 
digitized = np.digitize(masked_table['DEC'], bins)
masked_table['dec bin'] = digitized
grouped_table = masked_table.group_by('dec bin')
placeindex = grouped_table.groups.indices
xedges = [np.arange(-180,200,20)]
yedges=[ 0. ,  0.2,  0.4,  0.6,  0.8,  1. ,  1.2,  1.4,  1.6,  1.8,  2. ,2.2,  2.4]
for ival in range(0,len(grouped_table['RA'])):
    if grouped_table['RA'][ival] > 180:
        grouped_table['RA'][ival] = grouped_table['RA'][ival]-360.
for indexval in range(0,(len(placeindex)-1)):
    val1 = placeindex[indexval]
    val2 = placeindex[indexval +1]
    points = np.array([grouped_table['RA'][val1:val2],grouped_table['Z'][val1:val2]]) 
    pointsT = points.T
    hist, binedges = np.histogramdd(pointsT, normed=False, bins=(xedges, yedges)) 
    file_hist = 'hist%d.txt' % indexval 
    np.savetxt(file_hist, hist)
    if indexval ==0:
        np.savetxt('binedges.txt', binedges)

#obs_mean = grouped_table.groups.aggregate(np.mean)
#dec_data = Table([obs_mean['DEC'],obs_mean[''],obs_mean['ZWARN']])
#obs_data.write('Z_zwarn_zerror_mtl4.csv', format='csv')   
