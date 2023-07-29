# -*- coding: utf-8 -*-
"""
Created on Mon Aug  1 17:09:40 2022

@author: Luke Brown
"""

#import required modules
import glob, rawpy
import numpy as np
from skimage import filters, measure
import imageio as iio
from uncertainties import ufloat, unumpy

def process(img_dir,
            k = ufloat(0.5, 0.2), direction = 'up', down_factor = 3,
            pre_process_raw = True, save_bin_img = False):
    '''
    Returns a dictionary containing:
        Effective plant area index (PAIe), plant area index (PAI), and the clumping index (Ω)
        The fraction of vegetation cover (FCOVER)
        The fraction of crown cover (CC)
        The fraction of crown porosity (CP)

        Required parameters:
            img_dir: A directory containing images to be processed (string)

        Optional parameters:
            k: The extinction coefficient used to compute PAIe and PAI - an uncertainties ufloat may be specified to allow uncertainties in the extinction coefficient to be propagated through to the derived PAIe and PAI values (default is 0.5, corresponding to a spherical leaf angle distribution, with a standard uncertainty of 0.2)
            direction: The direction the images were acquired in ('up' or' down', default is 'up')
            down_factor: Specifies a downsampling factor to speed up the computation (default is 3)
            pre_process_raw: Specifies whether to pre-process RAW images (e.g. as recommended by Macfarlane et al. (2014)) (default is True)
            save_bin_img: Specifies whether to save the binarised image to the same directory as the input image as an 8-bit PNG (canopy = 0, gaps = 255), which may be useful for quality control purposes (default is False)  
    '''
# =============================================================================
# INPUT VALIDATION CHECKS
# =============================================================================
    
    #check img_dir is a string and raise error if not
    if not isinstance(img_dir, str):
        raise ValueError('Variable \'img_dir\' must be a string')
    
    #check img_dir, k, direction, down_factor, pre_process_raw and save_bin_img have a single value and raise error if not
    if not (np.size(img_dir) == 1 & 
            np.size(k) == 1 & 
            np.size(direction) == 1 & 
            np.size(down_factor) == 1 & 
            np.size(pre_process_raw == 1) & 
            np.size(save_bin_img) == 1):
        raise ValueError('Variables \'img_dir\', \'k\', \'direction\', \'mask\', \'down_factor\', \'pre_process_raw\' and \'save_bin_img\' must have a single value only') 
    #check direction is either 'up' or 'down' and raise error if not
    if not (direction == 'up' or direction == 'down'):
        raise ValueError('Variable \'direction\' must be either \'up\' or \'down\'')
    #check down_factor is an integer and raise error if not
    if not isinstance(down_factor, int):
        raise ValueError('Variable \'down_factor\' must be an integer')
    #check pre_process_raw and save_classifed are boolean and raise error if not:
    if not (isinstance(pre_process_raw, bool) & 
            isinstance(save_bin_img, bool)):
        raise ValueError('Variables \'pre_process_raw\' and \'save_bin_img\' must be boolean')
        
# =============================================================================
# LOCATION OF IMAGES
# =============================================================================
        
    #locate images
    images = glob.glob(img_dir + '/*.NEF')
    images.extend(glob.glob(img_dir + '/*.CR2'))
    images.extend(glob.glob(img_dir + '/*.CR3'))
    images.extend(glob.glob(img_dir + '/*.PEF'))
    images.extend(glob.glob(img_dir + '/*.RAW'))
    images.extend(glob.glob(img_dir + '/*.JPG'))
    images.extend(glob.glob(img_dir + '/*.JPEG'))
    images.extend(glob.glob(img_dir + '/*.PNG'))
    images.extend(glob.glob(img_dir + '/*.GIF'))
    images.extend(glob.glob(img_dir + '/*.BMP'))
    images.extend(glob.glob(img_dir + '/*.TIF'))
    images.extend(glob.glob(img_dir + '/*.TIFF'))
    n_images = len(images)
    #check images have been found
    if n_images < 1:
        raise ValueError('No images could be located in \'img_dir\'')
                
# =============================================================================
# CREATION OF ARRAYS TO STORE INTERMEDIATE RESULTS
# =============================================================================
    
    #create arrays to store gap fraction, crown cover, and crown porosity for each image
    gf = np.zeros(n_images)
    cc = np.zeros(n_images)
    cp = np.zeros(n_images)
        
# =============================================================================
# IMAGE BINARISATION AND MASKING
# =============================================================================
    
    #loop through images
    for i in range(n_images):
        #read in image
        if ('.NEF' in images[i]) | ('.CR2' in images[i]) | ('.CR3' in images[i]) | ('.PEF' in images[i]) | ('.RAW' in images[i]):
            if pre_process_raw:
                data = rawpy.imread(images[i]).postprocess(user_flip = 0)
            else:
                data = rawpy.imread(images[i]).postprocess(gamma = (1, 1), no_auto_bright = True, output_bps = 16, user_flip = 0) 
        else:
            data = iio.imread(images[i])
        
        #resize according to the downsampling factor
        if down_factor != 1:
            data = measure.block_reduce(data, (down_factor, down_factor, 1), np.mean)
       
        if direction == 'up':
            #threshold blue band
            b = data[:,:,2]
            bin_img = b > filters.threshold_isodata(b)
                
        elif direction == 'down':         
            #split red, green and blue bands into individual arrays, casting as float
            r = data[:,:,0].astype(float)  
            g = data[:,:,1].astype(float)  
            b = data[:,:,2].astype(float)  
			
            #calculate excess green and red indices
            ex_green = 2 * g - r - b
            ex_red = 1.4 * r - g
            #binarise image
            bin_img = ex_green - ex_red < 0
                    
        if save_bin_img:
            #save bin_img as PNG to same directory as input image
            iio.imwrite(images[i].split('.')[0] + '_bin.png', bin_img.astype(np.uint8) * 255)
                            
# =============================================================================
# COMPUTATION OF GAP FRACTION, CROWN COVER, and CROWN POROSITY   
# =============================================================================

        #label gaps in binarised image
        labelled_gaps = measure.label(bin_img)
        #determine unique gap IDs
        gaps = np.unique(labelled_gaps)
        
        #calculate image size
        img_size = np.size(bin_img)

        #create array to store gap sizes
        gap_size = np.zeros(len(gaps))

        #loop through unique gaps and determine size
        for j in range(len(gaps)):
            gap_size[j] = np.sum(labelled_gaps==j)
            
        #drop first gap (actually corresponds to canopy)
        gap_size = gap_size[1:]

        #calculate gap fraction, crown cover, and crown porosity
        gf[i] = np.sum(bin_img) / img_size
        cc[i] = 1 - np.sum(gap_size[gap_size / img_size > 0.013]) / img_size
        cp[i] = 1 - (1 - gf[i]) / cc[i]
    
# =============================================================================
# COMPUTATION OF PAIe/GAIe
# =============================================================================
    
    #create dictionary to store final results
    results = {}
    
    #determine the mean and standard error of gap fraction values over all images
    mean_gf = np.nanmean(gf)
    se_gf = np.nanstd(gf) / np.sqrt(np.sum(np.isfinite(gf)))
    #pack into uncertainties array
    mean_gf = ufloat(mean_gf, se_gf)
    
    #calculate PAIe
    results['paie'] = -unumpy.log(mean_gf) / k
                
# =============================================================================
# COMPUTATION OF PAI/GAI
# =============================================================================
    
    #determine the mean and standard error of crown cover values over all images
    mean_cc = np.nanmean(cc)
    se_cc = np.nanstd(cc) / np.sqrt(np.sum(np.isfinite(cc)))
    #pack into uncertainties float
    results['cc'] = ufloat(mean_cc, se_cc)
    
    #determine the mean and standard error of crown porosity values over all images
    mean_cp = np.nanmean(cp)
    se_cp = np.nanstd(cp) / np.sqrt(np.sum(np.isfinite(cp)))
    #pack into uncertainties ufloat
    results['cp'] = ufloat(mean_cp, se_cp)
    
    #calculate PAI
    results['pai'] = -results['cc'] * unumpy.log(results['cp']) / k
    
# =============================================================================
# COMPUTATION OF CLUMPING INDEX
# =============================================================================
    
    #calculate clumping index as ratio of PAIe to PAI
    results['clumping'] = results['paie'] / results['pai']

# =============================================================================
# COMPUTATION OF FCOVER
# =============================================================================
        
    #calculate FCOVER
    results['fcover'] = 1 - np.nanmean(mean_gf)
        
    #return results dictionary
    return results