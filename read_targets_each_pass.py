import os
from astropy.io import fits
from astropy.table import Table, vstack, unique
from astropy.table import Column, join
import numpy as np

tile_info_file = '/project/projectdirs/desi/software/edison/desimodel/master/data/footprint/desi-tiles.fits'
pass_data = fits.open(tile_info_file)[1].data
mask_desi = pass_data['IN_DESI']==1
pass_desi =pass_data[mask_desi]
mask_dark = pass_desi['PROGRAM']=='DARK'
pass_desi_dark = pass_desi[mask_dark]
len_pass_file = pass_desi_dark.shape[0]

arr = np.arange(40200).reshape(10050, 4)
t = Table(arr, names=('TILEID', 'ELG', 'LRG', 'QSO'))
for filename in os.listdir(os.getcwd()):
    start = filename.find('tile_') + 5
    end = filename.find('.fits', start)
    tile_id =filename[start:end].lstrip("0")
    tile_data = fits.open(filename)[1].data
    mask_ELG = tile_data['DESI_TARGET']==2
    no_ELG=sum(mask_ELG)
    mask_LRG = tile_data['DESI_TARGET']==1
    no_LRG=sum(mask_LRG)
    mask_QSO = tile_data['DESI_TARGET']==4
    no_QSO=sum(mask_QSO)
    t.add_row([tile_id ,no_ELG,no_LRG, no_QSO])
nt = unique(t, keys=['TILEID'], keep='last')
joined_table = join(nt, pass_desi, keys='TILEID')
new_table = joined_table.group_by('PASS')
ink =new_table.groups.indices

new_tab_survey_dark=new_table[ink[0]:ink[1]].group_by('PROGRAM')
sumvals = new_tab_survey_dark.groups.aggregate(np.sum)
avvals = new_tab_survey_dark.groups.aggregate(np.mean)
output_tab_D = Table([sumvals['ELG'], sumvals['LRG'], sumvals['QSO'], sumvals['PASS'],sumvals['PROGRAM']], names=('ELG', 'LRG', 'QSO', 'PASS', 'PROGRAM'))
for i in range(1,len(ink)-1):
    new_tab_survey_dark=new_table[ink[i]:ink[i+1]].group_by('PROGRAM')
    sumvals = new_tab_survey_dark.groups.aggregate(np.sum)
    avvals = new_tab_survey_dark.groups.aggregate(np.mean)
    output_tab_D.add_row([sumvals['ELG'], sumvals['LRG'], sumvals['QSO'], avvals['PASS'], sumvals['PROGRAM']])
print(output_tab_D)

         

