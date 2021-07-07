# std_candle
Code to illustrate the behaviour of standard candles

## Introduction
This code has two steps
1. Convert RAW images (.NEF or .CR2) to fits files. For example the code 
  `python raw_to_fits.py examples/DSC_0042.NEF`
  will produce the file `examples/DSC_0042.fits`

2. Extract the magnitude from a specified region of the image. This is done by following the instruction on `reduce_standard_candles.ipynb`
