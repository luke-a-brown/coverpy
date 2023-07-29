# CoverPy: Automated estimates of plant area index, vegetation cover, crown cover, crown porosity, and uncertainties from digital cover photography in Python

## Introduction

`coverpy` is an open-source Python module for automated derivation of canopy biophysical variables and uncertainties from digital cover photography (i.e. images acquired using a standard lens with a 30° to 60° field-of-view). `coverpy` is well-suited to batch processing and supports a wide range of image formats. Much of the `coverpy` code is based on <a href='https://github.com/luke-a-brown/hemipy'>the related `hemipy` module</a>, which is designed for processing digital hemispherical photography (i.e. images acquired with a fisheye lens).

From estimates of gap fraction determined by an automated binary image classification<sup>[1]</sup>, the following canopy biophysical variables (and their uncertainties) are computed by `coverpy`:

* Effective plant area index (PAI<sub>e</sub>), plant area index (PAI), and the clumping index (Ω)<sup>[2,3]</sup>;
* The fraction of vegetation cover (FCOVER);
* The fraction of crown cover (CC);
* The fraction of crown porosity (CP).

<sup>[1]</sup>For upwards-facing images, Ridler and Calvard's (1978) clustering algorithm is used to separate sky and canopy pixels, as it was shown to be the most robust of 35 algorithms tested by Jonckheere et al. (2005). In this case, only the blue band is used to maximise contrast and minimise the confounding effects of chromatic aberration and within-canopy multiple scattering (Leblanc et al., 2005; Macfarlane et al., 2014, 2007; Zhang et al., 2005). For downwards- facing images, the approach proposed by Meyer and Neto (2008) is adopted, which separates green vegetation from the underlying soil background on the basis of two colour indices.

<sup>[2]</sup>Ω is computed as the ratio of PAI<sub>e</sub> to PAI.

<sup>[3]</sup>For downwards-facing images, effective green area index (GAI<sub>e</sub>) and green area index (GAI) are provided as opposed to PAI<sub>e</sub> and PAI. 

## Installation

The latest release of `coverpy` can easily be installed using `pip`:

`pip install https://github.com/luke-a-brown/coverpy/archive/refs/tags/v0.1.0.zip`

## Dependencies

`coverpy` makes use of the `imageio`, `numpy`, `rawpy`, `scikit-image` and `uncertainties` modules, in addition to the `glob` module included in the Python Standard Library.

## Overview

`coverpy` consists of a single main function. The typical workflow for processing a set of digital cover photographs from a single measurement plot is as follows:

1.	Pass the directory of images to be processed to `coverpy`, along with the direction (i.e. upwards- or downwards-facing) of these images.

All images within a directory are processed together to provide a single value (and uncertainty) for each canopy biophysical variable. Therefore, each directory should correspond to a single measurement plot, which typically contains between 5 and 15 images.

## Processing options

The `coverpy.process()` function is configurable, and includes the ability to:
* Specify the extinction coefficient used to compute PAI<sub>e</sub> and PAI. An `uncertainties` `ufloat` may be specified to allow uncertainties in the extinction coefficient to be propagated through to the derived PAI<sub>e</sub> and PAI values (default is 0.5, corresponding to a spherical leaf angle distribution, with a standard uncertainty of 0.2);
* Specify a downsampling factor to speed up the computation (`down_factor`, default is 3);
* Specify whether to pre-process RAW images (e.g. as recommended by Macfarlane et al. (2014)) (`pre_process_raw`, default is True);
* Specify whether to save the binarised image to the same directory as the input image as an 8-bit PNG (canopy = 0, gaps = 255), which may be useful for quality control purposes (`save_bin_img`, default is False).

## Processing example

The example below demonstrates how `coverpy` can be used to process a set of upwards-facing images with the following directory structure:

* example_data
  - plot_a
      - image_1, image_2, ..., image_8, image_9

```
#import required modules
import coverpy, glob

#define input directory (sub-directories correspond to measurement plots and contain images from that plot)
input_dir = 'example_data/'

#open output file and write header
output_file = open('example_output.csv', 'w')
output_file.write('Plot,PAIe,PAI,Clumping,FCOVER,CC,CP\n')

#locate and loop through measurement plots
plots = glob.glob(input_dir + '/*')
for i in range(len(plots)):
	#run the main function and write results to output file
	results = coverpy.process(plots[i], direction = 'up')     
	output_file.write(plots[i].split('\\')[-1] + ',' +\
					  str(results['paie']) + ',' +\
					  str(results['pai']) + ',' +\
					  str(results['clumping']) + ',' +\
					  str(results['fcover']) + ',' +\
					  str(results['cc']) + ',' +\
					  str(results['cp']) + '\n')

#close output file
output_file.close()
```

## References

Jonckheere, I., Fleck, S., Nackaerts, K., Muys, B., Coppin, P., Weiss, M., Baret, F., 2004. Review of methods for in situ leaf area index determination. Agric. For. Meteorol. 121, 19–35. https://doi.org/10.1016/j.agrformet.2003.08.027

Leblanc, S.G., Chen, J.M., Fernandes, R., Deering, D.W., Conley, A., 2005. Methodology comparison for canopy structure parameters extraction from digital hemispherical photography in boreal forests. Agric. For. Meteorol. 129, 187–207. https://doi.org/10.1016/j.agrformet.2004.09.006

Macfarlane, C., Grigg, A., Evangelista, C., 2007. Estimating forest leaf area using cover and fullframe fisheye photography: Thinking inside the circle. Agric. For. Meteorol. 146, 1–12. https://doi.org/10.1016/j.agrformet.2007.05.001

Macfarlane, C., Ryu, Y., Ogden, G.N., Sonnentag, O., 2014. Digital canopy photography: Exposed and in the raw. Agric. For. Meteorol. 197, 244–253. https://doi.org/10.1016/j.agrformet.2014.05.014

Zhang, Y., Chen, J.M., Miller, J.R., 2005. Determining digital hemispherical photograph exposure for leaf area index estimation. Agric. For. Meteorol. 133, 166–181. https://doi.org/10.1016/j.agrformet.2005.09.009