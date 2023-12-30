#!/usr/bin/env python3

import sys
from os import listdir

import os
from os.path import isfile, join
import argparse
from PIL import Image

files=None

shrink=260

def reorder_staple(scan_list):
    scan_list=sorted(scan_list)
    crop_list=[]
    print ("Reordering based on having been stapled")

    # Pages ordered (n=scan_count*2):
    # n   :   0
    # 1   : n-1
    # n-2 :   2
    # 3   : m-3

    scan_last_width = Image.open(scan_list[-1]).width - shrink
    scan_last_height = Image.open(scan_list[-1]).height

    shrink_step_size = shrink / (len(scan_list) /2)
    shrink_step=0
    shrink_change=0

    # Step 5
    # Reorder pages now that they are split
    page_count=len(scan_list)*2
    page_pos=1
    page_order=[]
    while page_pos < page_count:
        page_order.append(page_count)
        page_order.append(page_pos)
        page_pos += 1
        page_count -= 1
        page_order.append(page_pos)
        page_order.append(page_count)
        page_pos += 1
        page_count -= 1
    print (page_order)

    page_pos=0


    for filename in scan_list:

        with Image.open(filename) as scan:
            print("Working on: "+str(scan.filename))
            # Step 1
            # Cut left side of page linearly based on maximum page shrink every page change
            im_crop = scan.crop((shrink_step, 0, scan.width, scan_last_height))

            scan_diff = (im_crop.width - scan_last_width)/2
            print("Diff: [" + str(scan_diff) + "] page W [" + str(scan.width)  + "] last [" + str(scan_last_width) + "]")

            # Step 2
            # Hommoginize page size to minimum page size to make PDF cleaner
            im_crop = im_crop.crop((scan_diff, 0, im_crop.width-scan_diff,im_crop.height ))

            # Step 3
            # Cut pages in middle now that they are more correcter sizes
            im_crop_l = im_crop.crop((0, 0, im_crop.width/2, scan.height))
            im_crop_r = im_crop.crop((im_crop.width/2, 0, im_crop.width,scan.height))

            # Step 4
            # Write split scan files
            im_crop_l.save(os.path.dirname(filename)+"/page-"+str(page_order[page_pos]).zfill(4)+".jpg")
            page_pos+=1
            im_crop_r.save(os.path.dirname(filename)+"/page-"+str(page_order[page_pos]).zfill(4)+".jpg")
            page_pos+=1

            if not shrink_change:
                shrink_change=1
            else:
                shrink_change=0
                shrink_step += shrink_step_size





def get_files(path):
    return [join(path, f) for f in listdir(path) if isfile(join(path, f))]


def getargs():
    parser = argparse.ArgumentParser(conflict_handler='resolve')

    # Add main action modes
    parser.add_argument('-t', '--type',choices=["staple"], nargs='?', default='staple', help='The way the pages were bound and need to be sorted')
    parser.add_argument('-f', '--folder', action='store', default=None, help='The directory where all the scans are')
    # Override help to allow for a dynamic help screen.
    parser.add_argument('--help','-h', action='store_true',  help='Print this help screen')

    # early exit for help parsing
    args_mode,other=parser.parse_known_args()

    # If help run print that and exit with all args
    if args_mode.help:
        parser.print_help()
        sys.exit()

    return parser.parse_args()


def parse_args(args):


    if args.type=="staple":
        if args.folder is not None:
            reorder_staple(get_files(args.folder))


if __name__ == '__main__':
    parse_args(getargs())
