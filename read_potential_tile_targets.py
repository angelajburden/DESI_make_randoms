import os
from astropy.io import fits
from astropy.table import Table, vstack, join
from astropy.table import Column, unique
import matplotlib.pyplot as plt
from mpl_toolkits.basemap import Basemap
import matplotlib.cm as cm
import numpy as np

#some useful functions
def save_potential_target_data(total_unique_targs, output_filename):    
    hdu = fits.table_to_hdu(total_unique_targs)
    hdu.writeto(outfile_filename)

def get_target_density(data, xmax, xmin, ymax, ymin, no_ra, no_dec, targ_flag, obs_flag, pass_flag):
    #Specify limits of binned data                                                                                                        
    ymin = -90.
    ymax = 90.
    xmin = 0.
    xmax = 360.
    bin_size_x = (xmax-xmin)/no_ra
    bin_size_y = (ymax-ymin)/no_dec
    if targ_flag ==1:
        targ_type = 'LRG'
    if targ_flag==2:
        targ_type = 'ELG'
    if targ_flag==4:
        targ_type = 'QSO'

    if obs_flag == 1:
        mask = data['SOURCETYPE']==targ_type
        masked_data = data[mask]
    if obs_flag ==2:
        mask = data['TRUETYPE']==targ_type
        masked_data = data[mask]
    if obs_flag ==3:
        masked_data = data
    del data
    if pass_flag<100:
        mask_pass=masked_data['PASS']==pass_flag
        masked_pass_data =masked_data[mask_pass]
    if pass_flag ==100:
        masked_pass_data =masked_data
    del masked_data

    H, xedges, yedges = np.histogram2d(masked_pass_data['RA'],masked_pass_data['DEC'], bins=(no_ra,no_dec),range=[[xmin, xmax], [ymin, ymax]])
    y = ymin:bin_size_y:(ymax-bin_size_y)
    x = xmin:bin_size_x:(xmax-bin_size_x)
    [X,Y] = np.meshgrid(x,y);
    X=np.transpose(X)
    Y=np.transpose(Y)
    middecrad = (Y)*np.pi/180;
    area =  bin_size_x*bin_size_y*np.cos(middecrad);
    density_in_bins = H/area;
    return density_in_bins

def hammer_plot_density(density, xmax, xmin, ymax, ymin, no_ra, no_dec, targ_flag, obs_flag, pass_flag):
    if targ_flag ==1:
        targ_type = 'LRG'
    if targ_flag==2:
        targ_type = 'ELG'
    if targ_flag==4:
        targ_type = 'QSO'
    if obs_flag==1:
        name_obs = 'source'
    if obs_flag==2:
        name_obs = 'true'
    
    outfile = "target_density_%s_%s_pass%d.pdf" %(targ_type, name_obs, pass_flag)
    bin_size_x = (xmax-xmin)/no_ra
    bin_size_y = (ymax-ymin)/no_dec
    y = ymin:bin_size_y:(ymax-bin_size_y)
    x = xmin:bin_size_x:(xmax-bin_size_x)
    [X,Y] = np.meshgrid(x,y);
    X=np.transpose(X)
    Y=np.transpose(Y)
    f = plt.figure()
    m = Basemap(projection='moll',lon_0=180,resolution='c')
    cs = m.pcolor(X, Y, density,  cmap=plt.cm.jet,latlon=True)
    cbar = m.colorbar(cs,location='bottom',pad="5%")
    f.savefig(outfile, bbox_inches='tight')

#---------------------------------------------MAIN-------------------------------------------------------   
#This first part of the code reads  all potential targets (within reach if a fiber), all actual targets 
#selected by the fiber and filters the info. so only the unique tarets are recorded, joins the tile number to the pass number
#and joins the target id to the truth table to see what the targets were thought to be, what they actually are and their ra, dec, and z.
i=0
j=0
tile_info_file = '/project/projectdirs/desi/software/edison/desimodel/master/data/footprint/desi-tiles.fits'
pass_data = fits.open(tile_info_file)[1].data
truth = fits.open('/global/project/projectdirs/desi/datachallenge/quicksurvey2017/input/dark/truth.fits')[1].data
truth_table = Table( [ truth['TARGETID'],truth['RA'], truth['DEC'], truth['TRUEZ'], truth['TRUETYPE'], truth['SOURCETYPE']], 
              names = ('TARGETID', 'RA', 'DEC', 'TRUEZ','TRUETYPE','SOURCETYPE'))

for filename in os.listdir(os.getcwd()):
    start = filename.find('tile_') + 5
    end = filename.find('.fits', start)
    tile_id =filename[start:end].lstrip("0")

    tile_data1 = fits.open(filename)[1].data
    tile_data2 = fits.open(filename)[2].data

    add_rows_all1 = Table(tile_data1['TARGETID'])
    add_rows_all2 = Table(tile_data2['POTENTIALTARGETID'])
    del tile_data1, tile_data2

    add_rows1 = unique(add_rows_all1,keys='TARGETID')
    add_rows1['OBS'] = np.ones(len(add_rows1))
    add_rows2 = unique(add_rows_all2,keys='POTENTIALTARGETID')
    add_rows2['OBS'] = np.zeros(len(add_rows2))
    add_rows2['POTENTIALTARGETID'].name = 'TARGETID'

    add_rows1['TILEID']= np.ones(len(add_rows1))*int(tile_id)
    add_rows2['TILEID']= np.ones(len(add_rows2))*int(tile_id)

    tot_targs = (vstack([add_rows1,add_rows2]))
    del add_rows1, add_rows2

    uni_targs = unique(tot_targs, keys = 'TARGETID')
    pass_targs = join(uni_targs, pass_data, keys='TILEID')
    del uni_targs

    unique_targs = join(pass_targs, truth_table, keys='TARGETID')

    if i==0:
        tot_unique_targsL100 = unique_targs
    else:
        tot_unique_targsL100 =(vstack([tot_unique_targsL100, unique_targs]))
    i+=1
    #this next part is for efficiency, it is slow to vstack everything at once, please change this if you know of a better method.    
    if i %100 ==0:
        print(i)
        if i==100:
            total_unique_targs = tot_unique_targsL100
        else:
            total_unique_targs = vstack(total_unique_targs, total_unique_targsL100)
        i=0
        del total_unique_targsL100


#the data ['TARGETID', 'RA', 'DEC', 'TRUEZ','TRUETYPE','SOURCETYPE', 'OBS, 'PASS', 'TILEID'] where OBS is if the object was assigned a fiber
#from all tiles in the directory is now in the table total_unique_targs.

#Edit out the following functions depending on your objectives.
#to save all this data 
save_potential_target_data(total_unique_targs, outall_filename)
get_target_density(data, xmax, xmin, ymax, ymin, no_ra, no_dec, targ_flag, obs_flag, pass_flag)
hammer_plot_density(density, xmax, xmin, ymax, ymin, no_ra, no_dec, targ_flag, obs_flag, pass_flag)
