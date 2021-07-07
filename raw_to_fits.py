import argparse
import sys
import os

import rawpy
import astropy.io.fits as fits
import numpy as np
import matplotlib.pyplot as plt

def main():
    parser = argparse.ArgumentParser(formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="Transforms raw camera data to fits")
    parser.add_argument('image', type=str, default=None, help='image name, required')
    parser.add_argument('--xmin', type=int, default=1000, help='minimum pixel in x to be saved in the reduced fits file (requires --manual option)')
    parser.add_argument('--xmax', type=int, default=3000, help='maximum pixel in x to be saved in the reduced fits file (requires --manual option)')
    parser.add_argument('--ymin', type=int, default=1000, help='minimum pixel in y to be saved in the reduced fits file (requires --manual option)')
    parser.add_argument('--ymax', type=int, default=2200, help='maximum pixel in y to be saved in the reduced fits file (requires --manual option)')
    parser.add_argument('--manual', action='store_true', help='choose the interval (requires --crop option)')
    parser.add_argument('--plot', action='store_true', help='plots data instead of saving it')
    parser.add_argument('--crop', action='store_true', help='crops image and saves a reduced fits file')
    args = parser.parse_args()
    
    # load image, and obtain rgb matrix
    raw = rawpy.imread(args.image)
    rgb = raw.postprocess(rawpy.Params(output_color=rawpy.ColorSpace.raw, highlight_mode=rawpy.HighlightMode.Ignore)).astype(np.float32)
    red = 0
    green = 1
    blue = 2
    
    # combine colors and create fits HDU (full image)
    combined = rgb[:,:,red] + rgb[:,:,green] + rgb[:,:,blue]
    new_hdu = fits.PrimaryHDU(combined)

    # crop the image
    if args.crop:
        if args.manual:
            xmin = args.xmin
            xmax = args.xmax
            ymin = args.ymin
            ymax = args.ymax
        else:
            xmean = 0.0
            weight = 0.0
            for pixelx in range(0, combined.shape[1]):
                xmean += pixelx*np.mean(combined[:,pixelx])
                weight += np.mean(combined[:,pixelx])
            xmean /= weight
            xmean = int(xmean)
            xmin = max(xmean - 1250, 0)
            xmax = min(xmean + 1250, combined.shape[1]-1)

            ymean = 0.0
            weight = 0.0
            for pixely in range(0, combined.shape[0]):
                ymean += pixely*np.mean(combined[pixely,:])
                weight += np.mean(combined[pixely,:])
            ymean /= weight
            ymean = int(ymean)
            ymin = max(ymean - 1250, 0)
            ymax = min(ymean + 1250, combined.shape[0]-1)
        rgb_reduced = rgb[ymin:ymax,xmin:xmax]

        # combine colors and create fits HDU (cropped image)
        combined_reduced = rgb_reduced[:,:,red] + rgb_reduced[:,:,green] + rgb_reduced[:,:,blue]
        new_hdu_reduced = fits.PrimaryHDU(combined_reduced)

    # names of the fits files
    if args.image.lower().endswith("cr2") or args.image.lower().endswith("nef"):
        fits_name = '{}.fits'.format(args.image[:-4])
        if args.crop:
            fits_name_reduced = '{}_reduced.fits'.format(args.image[:-4])
    else:
        print ("could not detect format in image {}".format(args.image))

    # save data
    if not args.plot:
        try:
            print ("full fits file saved to {}".format(fits_name))
            new_hdu.writeto(fits_name)
        except IOError:
            os.remove(fits_name)
            new_hdu.writeto(fits_name)
        if args.crop:
            try:
                print ("reduced fits file saved to {}".format(fits_name_reduced))
                new_hdu_reduced.writeto(fits_name_reduced)
            except IOError:
                os.remove(fits_name_reduced)
                new_hdu_reduced.writeto(fits_name_reduced)

    # plot data
    else:
        plt.figure(figsize=(5, 5))
        plt.title('full image')
        plt.imshow(rgb)
        if args.crop:
            print ("--xmin {} --xmax {} --ymin {} --ymax {}".format(xmin, xmax, ymin, ymax))
            plt.figure(figsize=(5, 5))
            plt.title('cropped image')
            plt.imshow(rgb_reduced)
        plt.show()

if __name__ == "__main__":
    main()
