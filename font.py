from math import cos, sin, radians
import os
import re
import sys
from graphics import Character, Line
from subprocess import Popen, PIPE

VERSION = sys.version_info[0]

test_cmd = ["ttf2cxf_stream", "TEST", "STDOUT"]
try:
    p = Popen(test_cmd, stdout=PIPE, stderr=PIPE)
    stdout, stderr = p.communicate()
    if VERSION == 3:
        stdout = bytes.decode(stdout)
    ttf_is_supported = str.find(stdout.upper(), 'TTF2CXF') != -1
except:
    ttf_is_supported = False


def TTF_is_supported():
    return ttf_is_supported


def available_font_files(font_directory):
    try:
        candidates = os.listdir(font_directory)
        candidates.sort()
    except FileNotFoundError:
        candidates = list()

    for name in candidates:
        if str.find(name.upper(), '.CXF') != -1 \
                or (str.find(name.upper(), '.TTF') != -1
                    and TTF_is_supported()):
            yield name


###############################################################################
# This routine parses the .cxf font file and builds a font dictionary of      #
# line segment strokes required to cut each character.                        #
# Arcs (only used in some fonts) are converted to a number of line            #
# segments based on the angular length of the arc. Since the idea of          #
# this font description is to make it support independent x and y scaling,    #
# we do not use native arcs in the g-code.                                    #
###############################################################################
def parse_cxf_font_file(file, segarc):
    segarc = float(segarc)
    font = {}
    key = None
    stroke_list = []
    xmax, ymax = 0, 0
    for text_in in file:
        text = text_in+" "
        # format for a typical letter (lower-case r):
        # #comment, with a blank line after it
        #
        # [r] 3  (or "[0072] r" where 0072 is the HEX value of the character)
        # L 0,0,0,6
        # L 0,6,2,6
        # A 2,5,1,0,90
        #
        end_char = len(text)
        if end_char and key:  # save the character to our dictionary
            font[key] = Character(key)
            font[key].stroke_list = stroke_list
            font[key].xmax = xmax

        new_cmd = re.match('^\[(.*)\]\s', text)
        if new_cmd:  # new character
            key_tmp = new_cmd.group(1)
            if len(new_cmd.group(1)) == 1:
                key = ord(key_tmp)
            else:
                if len(key_tmp) == 5:
                    key_tmp = key_tmp[1:]
                if len(key_tmp) == 4:
                    try:
                        key = int(key_tmp, 16)
                    except:
                        key = None
                        stroke_list = []
                        xmax, ymax = 0, 0
                        continue
                else:
                    key = None
                    stroke_list = []
                    xmax, ymax = 0, 0
                    continue
            stroke_list = []
            xmax, ymax = 0, 0

        line_cmd = re.match('^L (.*)', text)
        if line_cmd:
            coords = line_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            stroke_list += [Line(coords)]
            xmax = max(xmax, coords[0], coords[2])

        arc_cmd = re.match('^A (.*)', text)
        if arc_cmd:
            coords = arc_cmd.group(1)
            coords = [float(n) for n in coords.split(',')]
            xcenter, ycenter, radius, start_angle, end_angle = coords

            # since font defn has arcs as ccw, we need some font foo
            if end_angle < start_angle:
                start_angle -= 360.0

            # approximate arc with line seg every "segarc" degrees
            segs = int((end_angle - start_angle) / segarc)+1
            angleincr = (end_angle - start_angle)/segs
            xstart = cos(radians(start_angle)) * radius + xcenter
            ystart = sin(radians(start_angle)) * radius + ycenter
            angle = start_angle
            for i in range(segs):
                angle += angleincr
                xend = cos(radians(angle)) * radius + xcenter
                yend = sin(radians(angle)) * radius + ycenter
                coords = [xstart, ystart, xend, yend]
                stroke_list += [Line(coords)]
                xmax = max(xmax, coords[0], coords[2])
                ymax = max(ymax, coords[1], coords[3])
                xstart = xend
                ystart = yend
    return font


def parse_cxf_font(filename, segarc):
    try:
        with open(filename) as f:
            font = parse_cxf_font_file(f, segarc)
    except:
        font = dict()

    return font


def parse_ttf_font(filename, SegArc, supports_extended_chars):
    option = ""
    if supports_extended_chars:
        option = "-e"

    cmd = ["ttf2cxf_stream",
           option,
           "-s",
           SegArc,
           filename, "STDOUT"]
    try:
        p = Popen(cmd, stdout=PIPE, stderr=PIPE)
        stdout, stderr = p.communicate()
        if VERSION == 3:
            file = bytes.decode(stdout).split("\n")
        else:
            file = stdout.split("\n")

        # build stroke lists from font file
        font = parse_cxf_font_file(file, SegArc)
    except:
        raise
        font = dict()

    return font


def parse_font_file(filename, segarc, supports_extended_chars):
    _, fileExtension = os.path.splitext(filename)
    TYPE = fileExtension.upper()

    if TYPE == '.CXF':
        font = parse_cxf_font(filename, segarc)
    elif TYPE == '.TTF' and TTF_is_supported():
        font = parse_ttf_font(filename, segarc, supports_extended_chars)
    else:
        font = {}

    return font
