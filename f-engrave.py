#!/usr/bin/python
"""
    f-engrave G-Code Generator

    Copyright (C) <2011-2019>  <Scorch>
    Source was used from the following works:
              engrave-11.py G-Code Generator -- Lawrence Glaister --
              GUI framework from arcbuddy.py -- John Thornton  --
              cxf2cnc.py v0.5 font parsing code --- Ben Lipkowitz(fenn) --
              dxf.py DXF Viewer (http://code.google.com/p/dxf-reader/)
              DXF2GCODE (http://code.google.com/p/dfxf2gcode/)

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.

    To make it a menu item in Ubuntu use the Alacarte Menu Editor and add
    the command python YourPathToThisFile/ThisFilesName.py
    make sure you have made the file executable by right
    clicking and selecting properties then Permissions and Execute

    To use with LinuxCNC see the instructions at:
    http://wiki.linuxcnc.org/cgi-bin/emcinfo.pl?Simple_EMC_G-Code_Generators

    Version 0.1 Initial code

    Version 0.2 - Added V-Carve code
                - Fixed potential inf loop
                - Added pan and zoom
                - Moved Font file read out of calculation loop (increased
                  speed)

    Version 0.3 - Bug fix for flip normals and flip text
                - Moved depth scalar calc out of for loop

    Version 0.4 - Added importing for DXF files
                - Added import True Type fonts using the ttf2cxf_stream helper
                  program
                - Fixed line thickness display when zooming

    Version 0.5 - Added support for more DXF entity types POLYLINE and LEADER
                  (leaders won't have arrow heads)
                - Added global accuracy setting
                - Added straight line detection in v-carve output (reduces
                  number of G1 commands and output file size)
                - Improved handling of closed loops in v-carving
                - Added global variable named "Zero" for non-zero checks

    Version 0.6 - Added import Portable BitMap (PBM) images using Potrace as a
                  helper program
                - Default directory for opening PBM and DXF files is now set to
                  the current font directory
                - Default directory for and saving is now set to the users home
                  directory
                - Helper programs should now be found if they are in the global
                  search path or F-Engrave script folder (Previously the helper
                  programs needed to be in f-engrave script folder)

    Version 0.7 - Increased speed of v-carve calculation for large designs.
                  Approximately 20 times faster now.
                - Added window that displays status and contains a stop button
                  for v-carve calculations
                - Fixed display so that it no longer freezes during long
                  calculations
                - Fixed divide by zero error for certain fonts (Bug in Versions
                  0.5 and 0.6)

    Version 0.8 - Changed interface when working with image (DXF or PBM) files.
                - Added post processing logic to reduce number and distance of
                  rapid moves
                - Fixed bug in DXF code that caused failure to import some DXF
                  files.
                - Changed settings dialogs to allow recalculation and v-carving
                  from the dialog window to preview settings
                - Added some logic for determining default .ngc names and
                  directory when saving
                - Remove option for steps around corner (now internally
                  calculated based on step length and bit geometry)

    Version 0.9 - Added arc fitting to g-code output
                - Fixed extended characters up to 255 (now uses numbers for the
                  font index rather than the character)
                - Added option for a second operation g-code output file to
                  clean-up islands and adjacent areas of a v-carving
                - Cleaned up some GUI bugs introduced in Version 0.8
                - Remove flip border normals option
                - Default to check "all" instead of current character "chr"
                - Changed the percent complete calculation to use the % of the
                  total segment length rather than the segment count

    Version 0.91 - Fixed bug that caused Radius setting from text mode to
                   affect image mode
                 - Fixed bug that caused some DXF files to fail erroneously

    Version 0.92 - Fixed bug that caused some buttons on the v-carve setting to
                   not show up.

    Version 0.93 - Fixed bug that caused bad g-code in some cases.

    Version 1.00 - Added support for DXF polyline entity "bulges" (CamBam uses
                   polyline bulges in DXF exports)
                 - Modified code to be compatible with Python 3.  (F-Engrave
                   now works with Python 2.5 through 3.3)
                 - Removed stale references to grid the grid geometry manager
                 - Made minor user interface changes

    Version 1.01 - Fixed bug importing text information from g-code file in
                   Python 3
                 - Put additional restriction on arc fitting to prevent arcing
                   straight lines

    Version 1.02 - Put more restrictions on arc fitting to prevent huge
                   erroneous circles
                 - Added key binding for CTRL-g to copy g-code to clipboard

    Version 1.10 - Added Command line option to set the default directory
                 - Added setting option for disabling the use of variable in
                   the g-code output
                 - Added option for b-carving (using a ball end mill in v-carve
                   mode)
                 - Added the text to be engraved to the top of the ngc file
                 - Added max depth to the v-carve settings
                 - Eliminated failure to save g-code file when the image file
                   name contains extended characters.
                 - Changed the default .ngc/.svg file name when saving. Now it
                   always uses the base of the image file name.
                 - Changed the default behavior for v-carve step size. Now the
                   default in or mm value is always reset (0.010in or 0.25mm)
                   when switching between unit types.  This will ensure that
                   metric users will start with a good default step size
                   setting.

    Version 1.11 - Fixed error when saving clean up g-code.
                 - Removed Extra spaces from beginning of g-code preamble and
                   post-amble
                 - Added arc fitting to the variables that are saved to and
                   read from the g-code output file

    Version 1.12 - Added logic to add newline to g-code preamble and g-code
                   post-amble whenever a pipe character "|" is input

    Version 1.13 - Fixed bug preventing clean up tool-paths when the "Cut Depth
                   Limit" variable is used.

    Version 1.14 - Fixed bug preventing the use of the Cut Depth Limit when
                   b-carving
                 - Updated website info in help menu

    Version 1.20 - Added option to enable extended (Unicode) characters
                 - Also made a small change to the v-carve algorithm to fix a
                   special case.

    Version 1.21 - Added more command line options including a batch mode with
                   no GUI

    Version 1.22 - Fixed three bugs associated with importing dxf files
                 - Fixed bug associated with clean up calculations
                 - Changed minimum allowable line spacing from one to zero

    Version 1.30 - When importing DXF files F-Engrave no longer relies on the
                   direction of the loop (clockwise/counter-clockwise) to
                   determine which side to cut.  Now F-Engrave determines which
                   loops are inside of other loops and flips the directions
                   automatically.
                 - Added a new option for "V-Carve Loop Accuracy" in v-carve
                   settings.  This setting tells F-Engrave to ignore features
                   smaller than the set value.  This allows F-Engrave to ignore
                   small DXF imperfections that resulted in bad tool paths.

    Version 1.31 - Fixed bug that was preventing batch mode from working in
                   V1.30

    Version 1.32 - Added limit to the length of the engraved text included in
                   g-code file comment (to prevent error with long engraved
                   text)
                 - Changed number of decimal places output when in mm mode to 3
                   (still 4 places for inches)
                 - Changed g-code format for G2/G3 arcs to center format arcs
                   (generally preferred format)
                 - Hard coded G90 and G91.1 into g-code output to make sure the
                   output will be interpreted correctly by g-code interpreters.

    Version 1.33 - Added option to scale original input image size rather than
                   specify a image height

    Version 1.34 - Eliminated G91.1 code when arc fitting is disabled.  When
                   arc fitting is disabled the code (G91.1) is not needed and
                   it may cause problems for interpretors that do not support
                   that code (i.e. ShapeOko)

    Version 1.35 - Fixed importing of ellipse features from DXF files. Ellipse
                   end overlapped the beginning of the ellipse.
                 - Fixed saving long text to .ncg files.  Long text was
                   truncated when a .ngc file was opened.

    Version 1.36 - Fixed major bug preventing saving .ngc files when the text
                   was not a long string.

    Version 1.37 - Added logic to ignore very small line segments that caused
                   problems v-carving some graphic input files.

    Version 1.38 - Changed default origin to the DXF input file origin when
                   height is set by percentage of DXF image size.

    Version 1.39 - Fixed bug in v-carving routine resulting in failed v-carve
                   calculation. (Bug introduced in Version 1.37)

    Version 1.40 - Added code to increased v-carving speed (based on input from
                   geo01005)
                 - Windows executable file now generated from Python 2.5 with
                   Psyco support (significant speed increase)
                 - Changed Default Origin behavior (for DXF/Image files) to be
                   the origin of the DXF file or lower left corner of the input
                   image.
                 - Added automatic scaling of all linear dimensions values when
                   changing between units (in/mm)
                 - Fixed bug in clean up function in the v-carve menu.  (the
                   bug resulted in excessive Z motions in some cases)
                 - Fixed bug resulting in the last step of v-carving for any
                   given loop to be skipped/incorrect.

    Version 1.41 - Adjusted global Zero value (previous value resulted in
                   rounding errors in some cases)
                 - Removed use of accuracy (Acc) in the v-carve circle
                   calculation

    Version 1.42 - Changed default to disable variables in g-code output.

    Version 1.43 - Fixed bug in v-carve cleanup routing that caused some areas
                   to not be cleaned up.

    Version 1.44 - Fixed really bad bug in v-carve cleanup for bitmap images
                   introduced in V1.43

    Version 1.45 - Added multi-pass cutting for v-carving
                 - Removed "Inside Corner Angle" and "Outside Corner Angle"
                   options

    Version 1.46 - Fixed bug which cause double cutting of v-carve pattern when
                   multi-pass cutting was disabled

    Version 1.47 - Added ability to read more types of DXF files (files using
                   BLOCKS with the INSERT command)
                 - Fixed errors when running batch mode for v-carving.
                 - Added .tap to the drop down list of file extensions in the
                   file save dialog

    Version 1.48 - Fixed another bug in the multi-pass code resulting in
                   multi-pass cutting when multi-pass cutting was disabled.

    Version 1.49 - Added option to suppress option recovery comments in the
                   g-code output
                 - Added button in "General Settings" to automatically save a
                   configuration (config.ngc) file

    Version 1.50 - Modified helper program (ttf2cxf_stream) and F-Engrave
                   interaction with it to better control the line
                 - segment approximation of arcs.
                 - Added straight cutter support
                 - Added option to create prismatic cuts (inverse of v-carve).
                   This option opens the possibility of making v-carve inlays.
                 - Fixed minor bug in the v-bit cleanup tool-path generation
                 - Changed the behavior when using inverting normals for
                   v-carving.  Now a box is automatically generated to bound
                   the cutting on the outside of the design/lettering.  The
                   size of the box is controlled by the Box/Circle Gap setting
                   in the general settings.
                 - Removed v-carve accuracy setting
                 - Added option for radius format g-code arcs when arc fitting.
                   This will help compatibility with g-code interpreters that
                   are missing support for center format arcs.

    Version 1.51 - Added Plunge feed rate setting (if set to zero the normal
                   feed rate applies)
                 - Removed default coolant start/stop M codes for the header
                   and footer
                 - Changed default footer to include a newline character
                   between the M codes another Shapeoko/GRBL problem.
                 - Fixed some Python 3 incompatibilities with reading
                   configuration files

    Version 1.52 - Fixed potential divide by zero error in DXF reader
                 - Text mode now includes space for leading carriage returns
                   (i.e. Carriage returns before text characters)

    Version 1.53 - Changed space for leading carriage returns to only apply at
                   0,90,270 and 180 degree rotations.
                 - Added floating tool tips to the options on the main window
                   (hover over the option labels to see the tool tip text)

    Version 1.54 - Fixed bug that resulted in errors if the path to a file
                   contained the text of an F-Engrave setting variable
                 - Reduced time to open existing g-code files by eliminating
                   unnecessary recalculation calls.
                 - Added configuration variable to remember the last. Folder
                   location used when a configuration file is saved.
                 - Added support for most jpg, gif, tif and png files (it is
                   still best to use Bitmaps)
                 - After saving a new configuration file the settings menu will
                   now pop back to the top (sometimes it would get buried under
                   other windows)
                 - Now searches current folder and home folder for image files
                   when opening existing g-code files.
                   previously the image file needed to be in the exact path
                   location as when the file was saved

    Version 1.55 - Fixed error in line/curve fitting that resulted in bad
                   output with high Accuracy settings
                 - Fixed missing parentheses on file close commands (resulted
                   in problems when using PyPy
                 - Suppress comments in g-code should now suppress all full
                   line g-code comments
                 - Fixed error that resulted in cutting outside the lines with
                   large Accuracy settings

    Version 1.56 - Changed line/curve fitting to use Douglas-Peucker curve
                   fitting routine originally from LinuxCNC image2gcode
                 - Re-enabled the use of #2 variable when engraving with
                   variable enabled (was broken in previous version)
                 - Fixed SVG export (was broken in previous version)

    Version 1.57 - Fixed feed rate. Changes in 1.56 resulted in feed rate not
                   being written to g-code file.

    Version 1.58 - Fixed some special cases which resulted in errors being
                   thrown (v-carve single lines)
                 - Changed the default settings to be more compatible with
                   incomplete g-code interpretors like GRBL

    Version 1.59 - Fixed bug in arc fitting
                 - Rewrote Cleanup operation calculations (fixes a bug that
                   resulted in some areas not being cleaned up
                 - Changed flip normals behavior, There are now two options:
                   Flip Normals and Add Box (Flip Normals)
                 - Changed prismatic cut to allow the use of either of the two
                   Flip normals options (one of the two Flip normals options
                   must be selected for the inlay cuts to be performed properly
                 - Added DXF Export option (with and without auto closed loops)

    Version 1.60 - Fixed divide by zero error in some cleanup sceneries.

    Version 1.61 - Fixed a bug that prevented opening DXF files that contain no
                   features with positive Y coordinates

    Version 1.62 - Fixed a bug that resulted in bad cleanup tool paths in some
                   situations

    Version 1.63 - Removed code that loaded _imaging module.  The module is not
                   needed
                 - Changed "Open F-Engrave G-Code File" to
                   "Read Settings From File"
                 - Added "Save Setting to File" file option in File menu
                 - Fixed v-bit cleanup step over. Generated step was twice the
                   input cleanup step.
                 - Updated icon.
                 - Added console version of application to windows
                   distribution. For batch mode in Windows.
    Version 1.64 - Fixed bug that created erroneous lines in some circumstances
                   during v-carving.
                 - Mapped save function to Control-S for easier g-code saving

    Version 1.65 - Fixed bug in sort_for_v_carve that resulted in an error for
                   certain designs.

    Version 1.66 - Fixed a problem with the origin when wrapping text in some
                   cases.
                 - Decreased number of updates while doing computations which
                   increases overall calculation speed.
                 - Fixed problem that can cause the program to freeze if the
                   saved settings contain errors.


    Version 1.67 - Improved DXF import for DXF files with some incomplete data
                 - Fixed curve fitting upon g-code export.  Limited curve
                   fitting angle to avoid curve fitting sharp corners.

    Version 1.68 - Fixed typo in code introduced in v1.67 that broke curve
                   fitting.

    Version 1.69 - A couple of minor fixes to keep things working in Python 3.x
                 - Added ability to disable ploting of v-carve toolpath and
                   area
                 - Fixed problem causing v-carve path to go outside of design
                   bounds for very thin design sections.
    Version 1.70 - Fixed a bug introduced in V1.69 that caused v-carving
                   cleanup calculations to fail sometimes.

    Version 1.71 - Changed Potrace version that is distributed with F-Engrave
                   from 1.10 to 1.16
                 - Fixed problem with cleanup cutting wrong area for some cases

    Version 1.72 - Fixed a bug that resulted in bad cleanup tool paths in some
                   situations
                 - Explicitly set the font for the GUI

    Version 1.73 - Made importing png images with clear backgrounds work better
                 - Added PNG and TIF to the image file types that show up by
                   default

    """

version = "1.73"
# Setting QUIET to True will stop almost all console messages
QUIET = False
DEBUG = False

import sys

VERSION = sys.version_info[0]

if VERSION == 3:
    from tkinter import END, RIGHT, LEFT, CENTER, Tk, Button, Checkbutton
    from tkinter import Label, PhotoImage, X, Y, W, E, SW, BOTH, Entry, SUNKEN
    from tkinter import Radiobutton, Toplevel, BooleanVar, StringVar, Canvas
    from tkinter import Scrollbar, Listbox, Frame, Text, Menu, VERTICAL
    from tkinter import ALL, FLAT, Event, BOTTOM, OptionMenu
    from tkinter.filedialog import askdirectory, askopenfilename
    from tkinter.filedialog import asksaveasfilename
else:
    from Tkinter import END, RIGHT, LEFT, CENTER, Tk, Button, Checkbutton
    from Tkinter import Label, PhotoImage, X, Y, W, E, SW, BOTH, Entry, SUNKEN
    from Tkinter import Radiobutton, Toplevel, BooleanVar, StringVar, Canvas
    from Tkinter import Scrollbar, Listbox, Frame, Text, Menu, VERTICAL
    from Tkinter import ALL, FLAT, Event, BOTTOM, OptionMenu
    from tkFileDialog import askdirectory, askopenfilename
    from tkFileDialog import asksaveasfilename

if VERSION < 3 and sys.version_info[1] < 6:

    def next(item):
        return item.next()


try:
    import psyco

    psyco.full()
    sys.stdout.write("(Psyco loaded: You have the fastest F-Engrave.)\n")
except:
    pass

PIL = True
if PIL:
    try:
        from PIL import Image

        Image.MAX_IMAGE_PIXELS = None
    except:
        PIL = False
        sys.stdout.write("PIL Not loaded.\n")


from bit import bit_from_shape
from config import Config
from constants import Zero, IN_AXIS, Plane, NumberCheck
from constants import MIN_METRIC_STEP_LEN, MIN_IMP_STEP_LEN
from douglas import douglas
from dxf import parse_dxf, WriteDXF
from gcode import Gcode
import getopt
from graphics import Get_Angle, Transform, Rotn, CoordScale, DetectIntersect
from graphics import Clean_coords_to_Path_coords
from graphics import Find_Paths, record_v_carve_data, find_max_circle
from graphics import sort_for_v_carve, Sort_Paths
import font
from math import sqrt, radians, tan, acos, sin, cos, fabs, floor, ceil
from math import degrees
from messages import Message
import os
import re
import struct
from subprocess import Popen, PIPE
from svg import SVG
from time import time
from tkinter_config import FeStringVar, FeBooleanVar
from tkinter_extras import ToolTip
import webbrowser
from icon import temp_icon

try:
    unichr
except NameError:
    unichr = chr

message = Message(quiet=QUIET or IN_AXIS, debug=DEBUG)

def config_initialise():
    config = Config()

    config.batch = FeBooleanVar()
    config.show_axis = FeBooleanVar()
    config.show_box = FeBooleanVar()
    config.show_v_path = FeBooleanVar()
    config.show_v_area = FeBooleanVar()
    config.show_thick = FeBooleanVar()
    config.flip = FeBooleanVar()
    config.mirror = FeBooleanVar()
    config.outer = FeBooleanVar()
    config.upper = FeBooleanVar()
    config.fontdex = FeBooleanVar()
    config.v_flop = FeBooleanVar()
    config.v_pplot = FeBooleanVar()
    config.inlay = FeBooleanVar()
    config.no_comments = FeBooleanVar()
    config.ext_char = FeBooleanVar()
    config.var_dis = FeBooleanVar()
    config.useIMGsize = FeBooleanVar()
    config.plotbox = FeBooleanVar()

    config.clean_P = FeBooleanVar()
    config.clean_X = FeBooleanVar()
    config.clean_Y = FeBooleanVar()
    config.v_clean_P = FeBooleanVar()
    config.v_clean_X = FeBooleanVar()
    config.v_clean_Y = FeBooleanVar()

    config.arc_fit = FeStringVar()
    config.YSCALE = FeStringVar()
    config.XSCALE = FeStringVar()
    config.LSPACE = FeStringVar()
    config.CSPACE = FeStringVar()
    config.WSPACE = FeStringVar()
    config.TANGLE = FeStringVar()
    config.TRADIUS = FeStringVar()
    config.ZSAFE = FeStringVar()
    config.ZCUT = FeStringVar()
    config.STHICK = FeStringVar()
    config.origin = FeStringVar()
    config.justify = FeStringVar()
    config.units = FeStringVar()

    config.xorigin = FeStringVar()
    config.yorigin = FeStringVar()
    config.segarc = FeStringVar()
    config.accuracy = FeStringVar()

    config.funits = FeStringVar()
    config.FEED = FeStringVar()
    config.PLUNGE = FeStringVar()
    config.fontfile = FeStringVar()
    config.H_CALC = FeStringVar()
    # self.plotbox    = FeStringVar()
    config.boxgap = FeStringVar()
    config.fontdir = FeStringVar()
    config.cut_type = FeStringVar()
    config.input_type = FeStringVar()

    config.bit_shape = FeStringVar()
    config.v_bit_angle = FeStringVar()
    config.v_bit_dia = FeStringVar()
    config.v_depth_lim = FeStringVar()
    config.v_drv_crner = FeStringVar()
    config.v_stp_crner = FeStringVar()
    config.v_step_len = FeStringVar()
    config.allowance = FeStringVar()
    config.v_check_all = FeStringVar()
    config.v_max_cut = FeStringVar()
    config.v_rough_stk = FeStringVar()

    config.clean_dia = FeStringVar()
    config.clean_step = FeStringVar()
    config.clean_v = FeStringVar()
    config.clean_name = FeStringVar()

    config.gpre = FeStringVar()
    config.gpost = FeStringVar()

    config.bmp_turnpol = FeStringVar()
    config.bmp_turdsize = FeStringVar()
    config.bmp_alphamax = FeStringVar()
    config.bmp_opttolerance = FeStringVar()
    config.bmp_longcurve = BooleanVar()

    config.maxcut = FeStringVar()
    config.current_input_file = FeStringVar()
    config.bounding_box = FeStringVar()

    # INITILIZE VARIABLES
    # If you want to change a default setting this is the place to do it.
    config.batch.set(0)
    config.show_axis.set(1)
    config.show_box.set(1)
    config.show_v_path.set(1)
    config.show_v_area.set(1)
    config.show_thick.set(1)
    config.flip.set(0)
    config.mirror.set(0)
    config.outer.set(1)
    config.upper.set(1)
    config.fontdex.set(0)
    config.useIMGsize.set(0)
    config.plotbox.set(0)

    config.v_flop.set(0)
    config.v_pplot.set(0)
    config.inlay.set(0)
    config.no_comments.set(1)
    config.ext_char.set(0)
    config.var_dis.set(1)

    config.clean_P.set(1)
    config.clean_X.set(1)
    config.clean_Y.set(0)
    config.v_clean_P.set(0)
    config.v_clean_X.set(0)
    config.v_clean_Y.set(1)

    config.arc_fit.set("none")  # "none", "center", "radius"
    config.YSCALE.set("2.0")
    config.XSCALE.set("100")
    config.LSPACE.set("1.1")
    config.CSPACE.set("25")
    config.WSPACE.set("100")
    config.TANGLE.set("0.0")
    config.TRADIUS.set("0.0")
    config.ZSAFE.set("0.25")
    config.ZCUT.set("-0.005")
    config.STHICK.set("0.01")
    config.origin.set("Default")  # Options are "Default",
    #             "Top-Left", "Top-Center", "Top-Right",
    #             "Mid-Left", "Mid-Center", "Mid-Right",
    #             "Bot-Left", "Bot-Center", "Bot-Right"

    config.justify.set("Left")  # Options are "Left", "Right", "Center"
    config.units.set("in")  # Options are "in" and "mm"
    config.FEED.set("5.0")
    config.PLUNGE.set("0.0")
    config.fontfile.set(" ")
    config.H_CALC.set("max_use")
    # self.plotbox.set("no_box")
    config.boxgap.set("0.25")
    config.fontdir.set("fonts")
    config.cut_type.set("engrave")  # Options are "engrave" and "v-carve"
    config.input_type.set("text")  # Options are "text" and "image"

    config.bit_shape.set("VBIT")
    config.v_bit_angle.set("60")
    config.v_bit_dia.set("0.5")
    config.v_depth_lim.set("0.0")
    config.v_drv_crner.set("135")
    config.v_stp_crner.set("200")
    config.v_step_len.set("0.01")
    config.allowance.set("0.0")
    config.v_check_all.set("all")  # Options are "chr" and "all"
    config.v_rough_stk.set("0.0")
    config.v_max_cut.set("-1.0")

    # options: black, white, right, left, minority, majority, or random
    config.bmp_turnpol.set("minority")
    config.bmp_turdsize.set("2")  # default 2
    config.bmp_alphamax.set("1")  # default 1
    config.bmp_opttolerance.set("0.2")  # default 0.2
    config.bmp_longcurve.set(1)  # default 1 (True)

    config.xorigin.set("0.0")
    config.yorigin.set("0.0")
    config.segarc.set("5.0")
    config.accuracy.set("0.001")

    config.clean_v.set("0.05")
    config.clean_dia.set(".25")  # Diameter of clean-up bit
    # Clean-up step-over as percent of clean-up bit diameter
    config.clean_step.set("50")
    config.clean_name.set("_clean")

    config.current_input_file.set(" ")
    config.bounding_box.set(" ")

    if config.units.get() == "in":
       config.funits.set("in/min")
    else:
       config.units.set("mm")
       config.funits.set("mm/min")

    # G-Code Default Preamble
    # G17        ; sets XY plane
    # G64 P0.003 ; G64 P- (motion blending tolerance set to 0.003) This is
    #              the default in engrave.py
    # G64        ; G64 without P option keeps the best speed possible, no
    #              matter how far away from the programmed point you end
    #              up.
    # M3 S3000   ; Spindle start at 3000
    config.gpre.set("G17 G64 P0.001 M3 S3000")

    # G-Code Default Postamble
    # M5 ; Stop Spindle
    # M9 ; Turn all coolant off
    # M2 ; End Program
    config.gpost.set("M5|M2")

    return config


def calc_vbit_dia(config, bit):
    bit_dia = bit.diameter(
        config.v_depth_lim.get(), config.inlay.get(), config.allowance.get()
    )
    return bit_dia


def calc_depth_limit(config, bit):
    try:
        max_cut = bit.max_cut_depth(config.v_depth_lim.get())
        config.maxcut.set("%.3f" % (max_cut))
    except:
        config.maxcut.set("error")


def get_flop_status(config, CLEAN_FLAG=False):
    v_flop = bool(config.v_flop.get())

    if config.input_type.get() == "text" and not CLEAN_FLAG:
        if config.plotbox.get():
            v_flop = not (v_flop)
        if config.mirror.get():
            v_flop = not (v_flop)
        if config.flip.get():
            v_flop = not (v_flop)
    return v_flop


############################################################################
class Application(Frame):
    def __init__(self, master):
        Frame.__init__(self, master)
        self.w = 780
        self.h = 490
        Frame(master, width=self.w, height=self.h)
        self.master = master
        self.x = -1
        self.y = -1
        self.initComplete = 0
        self.delay_calc = 0
        self.STOP_CALC = False

        # if PIL == False:
        #    fmessage("Python Imaging Library (PIL) was not found...Bummer")
        #    fmessage("    PIL enables more image file formats.")

        if not font.TTF_is_supported():
            message.fmessage(
                "ttf2cxf_stream executable is not present/working...Bummer"
            )

        cmd = ["potrace", "-v"]
        try:
            p = Popen(cmd, stdout=PIPE, stderr=PIPE)
            stdout, stderr = p.communicate()
            if VERSION == 3:
                stdout = bytes.decode(stdout)
            if str.find(stdout.upper(), "POTRACE") != -1:
                self.POTRACE_AVAIL = True
                if str.find(stdout.upper(), "1.1") == -1:
                    message.fmessage(
                        "F-Engrave Requires Potrace Version 1.10 or Newer."
                    )
            else:
                self.POTRACE_AVAIL = False
                message.fmessage("potrace is not working...Bummer")
        except:
            message.fmessage(
                "potrace executable is not present/working...Bummer"
            )
            self.POTRACE_AVAIL = False

        self.createWidgets()

    def f_engrave_init(self):
        self.master.update()
        self.initComplete = 1
        self.delay_calc = 0
        self.menu_Mode_Change()

    def createWidgets(self):
        self.master.bind("<Configure>", self.Master_Configure)
        self.master.bind("<Escape>", self.KEY_ESC)
        self.master.bind("<F1>", self.KEY_F1)
        self.master.bind("<F2>", self.KEY_F2)
        self.master.bind("<F3>", self.KEY_F3)
        self.master.bind("<F4>", self.KEY_F4)
        self.master.bind("<F5>", self.KEY_F5)  # self.Recalculate_Click)
        self.master.bind("<Control-Up>", self.Listbox_Key_Up)
        self.master.bind("<Control-Down>", self.Listbox_Key_Down)
        self.master.bind("<Prior>", self.KEY_ZOOM_IN)  # Page Up
        self.master.bind("<Next>", self.KEY_ZOOM_OUT)  # Page Down
        self.master.bind("<Control-g>", self.KEY_CTRL_G)
        self.master.bind("<Control-s>", self.KEY_CTRL_S)

        config = self.config = config_initialise()

        bit = bit_from_shape(
            config.bit_shape.get(),
            config.v_bit_dia.get(),
            config.v_bit_angle.get()
        )

        # Derived variables
        calc_depth_limit(config, bit)


        self.segID = []
        self.coords = []
        self.vcoords = []
        self.clean_coords = []
        self.clean_segment = []
        self.clean_coords_sort = []
        self.v_clean_coords_sort = []

        self.font = {}
        self.RADIUS_PLOT = 0
        self.MAXX = 0
        self.MINX = 0
        self.MAXY = 0
        self.MINY = 0

        self.Xzero = float(0.0)
        self.Yzero = float(0.0)
        self.default_text = "F-Engrave"
        self.HOME_DIR = os.path.expanduser("~")
        self.NGC_FILE = self.HOME_DIR + "/None"
        self.IMAGE_FILE = self.HOME_DIR + "/None"

        self.pscale = 0
        # PAN and ZOOM STUFF
        self.panx = 0
        self.panx = 0
        self.lastx = 0
        self.lasty = 0

        # END INITIALIZING VARIABLES

        config_file = "config.ngc"
        home_config1 = self.HOME_DIR + "/" + config_file
        config_file2 = ".fengraverc"
        home_config2 = self.HOME_DIR + "/" + config_file2
        if os.path.isfile(config_file):
            self.Open_G_Code_File(config_file)
        elif os.path.isfile(home_config1):
            self.Open_G_Code_File(home_config1)
        elif os.path.isfile(home_config2):
            self.Open_G_Code_File(home_config2)

        opts, args = None, None
        try:
            opts, args = getopt.getopt(
                sys.argv[1:],
                "hbg:f:d:t:",
                [
                    "help",
                    "batch",
                    "gcode_file",
                    "fontdir=",
                    "defdir=",
                    "text=",
                ],
            )
        except:
            message.fmessage("Unable interpret command line options")
            sys.exit()
        for option, value in opts:
            if option in ("-h", "--help"):
                message.fmessage(" ")
                message.fmessage(
                    "Usage: python f-engrave.py [-g file | -f fontdir | "
                    "-d directory | -t text | -b ]"
                )
                message.fmessage(
                    "-g    : f-engrave gcode output file to read "
                    "(also --gcode_file)"
                )
                message.fmessage(
                    "-f    : path to font file, directory or image file "
                    "(also --fontdir)"
                )
                message.fmessage("-d    : default directory (also --defdir)")
                message.fmessage("-t    : engrave text (also --text)")
                message.fmessage("-b    : batch mode (also --batch)")
                message.fmessage("-h    : print this help (also --help)\n")
                sys.exit()
            if option in ("-g", "--gcode_file"):
                self.Open_G_Code_File(value)
                self.NGC_FILE = value
            if option in ("-f", "--fontdir"):
                if os.path.isdir(value):
                    config.fontdir.set(value)
                elif os.path.isfile(value):
                    dirname = os.path.dirname(value)
                    fileName, fileExtension = os.path.splitext(value)
                    TYPE = fileExtension.upper()
                    if TYPE == ".CXF" or TYPE == ".TTF":
                        config.input_type.set("text")
                        config.fontdir.set(dirname)
                        config.fontfile.set(
                            os.path.basename(fileName) + fileExtension
                        )
                    else:
                        config.input_type.set("image")
                        self.IMAGE_FILE = value
                else:
                    message.fmessage("File/Directory Not Found:\t%s" % (value))

            if option in ("-d", "--defdir"):
                self.HOME_DIR = value
                if str.find(self.NGC_FILE, "/None") != -1:
                    self.NGC_FILE = self.HOME_DIR + "/None"
                if str.find(self.IMAGE_FILE, "/None") != -1:
                    self.IMAGE_FILE = self.HOME_DIR + "/None"
            if option in ("-t", "--text"):
                value = value.replace("|", "\n")

                self.default_text = value
            if option in ("-b", "--batch"):
                config.batch.set(True)

        if config.batch.get():
            message.fmessage("(F-Engrave Batch Mode)")

            if config.input_type.get() == "text":
                self.Read_font_file()
            else:
                self.Read_image_file()

            self.DoIt()
            if config.cut_type.get() == "v-carve":
                self.V_Carve_It()

            gcode = self.WriteGCode()

            for line in gcode:
                try:
                    sys.stdout.write(line + "\n")
                except:
                    sys.stdout.write("(skipping line)\n")
            sys.exit()

        # make a Status Bar
        self.statusMessage = StringVar()
        self.statusMessage.set("")
        self.statusbar = Label(
            self.master,
            textvariable=self.statusMessage,
            bd=1,
            relief=SUNKEN,
            height=1,
        )
        self.statusbar.pack(anchor=SW, fill=X, side=BOTTOM)
        self.statusMessage.set("Welcome to F-Engrave")

        # Buttons
        self.Recalculate = Button(self.master, text="Recalculate")
        self.Recalculate.bind("<ButtonRelease-1>", self.Recalculate_Click)

        # Canvas
        lbframe = Frame(self.master)
        self.PreviewCanvas_frame = lbframe
        self.PreviewCanvas = Canvas(
            lbframe,
            width=self.w - 525,
            height=self.h - 200,
            background="grey75",
        )
        self.PreviewCanvas.pack(side=LEFT, fill=BOTH, expand=1)
        self.PreviewCanvas_frame.place(x=230, y=10)

        self.PreviewCanvas.bind("<Button-4>", self._mouseZoomIn)
        self.PreviewCanvas.bind("<Button-5>", self._mouseZoomOut)
        self.PreviewCanvas.bind("<2>", self.mousePanStart)
        self.PreviewCanvas.bind("<B2-Motion>", self.mousePan)
        self.PreviewCanvas.bind("<1>", self.mouseZoomStart)
        self.PreviewCanvas.bind("<B1-Motion>", self.mouseZoom)
        self.PreviewCanvas.bind("<3>", self.mousePanStart)
        self.PreviewCanvas.bind("<B3-Motion>", self.mousePan)

        # Left Column #
        self.Label_font_prop = Label(
            self.master, text="Text Font Properties:", anchor=W
        )

        self.Label_Yscale = Label(
            self.master, text="Text Height", anchor=CENTER
        )
        self.Label_Yscale_u = Label(
            self.master, textvariable=config.units.TK, anchor=W
        )
        self.Label_Yscale_pct = Label(self.master, text="%", anchor=W)
        self.Entry_Yscale = Entry(self.master, width="15")
        self.Entry_Yscale.configure(textvariable=config.YSCALE.TK)
        self.Entry_Yscale.bind("<Return>", self.Recalculate_Click)
        config.YSCALE.TK.trace_variable("w", self.Entry_Yscale_Callback)
        self.Label_Yscale_ToolTip = ToolTip(
            self.Label_Yscale,
            text="Character height of a single line of text.",
        )
        # or the height of an imported image. (DXF, BMP, etc.)')

        self.NormalColor = self.Entry_Yscale.cget("bg")

        self.Label_Sthick = Label(self.master, text="Line Thickness")
        self.Label_Sthick_u = Label(
            self.master, textvariable=config.units.TK, anchor=W
        )
        self.Entry_Sthick = Entry(self.master, width="15")
        self.Entry_Sthick.configure(textvariable=config.STHICK.TK)
        self.Entry_Sthick.bind("<Return>", self.Recalculate_Click)
        config.STHICK.TK.trace_variable("w", self.Entry_Sthick_Callback)
        self.Label_Sthick_ToolTip = ToolTip(
            self.Label_Sthick,
            text="Thickness or width of engraved lines. "
            "Set this to your engraving cutter diameter.  "
            "This setting only affects the displayed lines, not the g-code "
            "output.",
        )

        self.Label_Xscale = Label(
            self.master, text="Text Width", anchor=CENTER
        )
        self.Label_Xscale_u = Label(self.master, text="%", anchor=W)
        self.Entry_Xscale = Entry(self.master, width="15")
        self.Entry_Xscale.configure(textvariable=config.XSCALE.TK)
        self.Entry_Xscale.bind("<Return>", self.Recalculate_Click)
        config.XSCALE.TK.trace_variable("w", self.Entry_Xscale_Callback)
        self.Label_Xscale_ToolTip = ToolTip(
            self.Label_Xscale,
            text="Scaling factor for the width of characters.",
        )

        self.Label_useIMGsize = Label(self.master, text="Set Height as %")
        self.Checkbutton_useIMGsize = Checkbutton(
            self.master, text=" ", anchor=W
        )
        self.Checkbutton_useIMGsize.configure(
            variable=config.useIMGsize.TK, command=self.useIMGsize_var_Callback
        )

        self.Label_Cspace = Label(
            self.master, text="Char Spacing", anchor=CENTER
        )
        self.Label_Cspace_u = Label(self.master, text="%", anchor=W)
        self.Entry_Cspace = Entry(self.master, width="15")
        self.Entry_Cspace.configure(textvariable=config.CSPACE.TK)
        self.Entry_Cspace.bind("<Return>", self.Recalculate_Click)
        config.CSPACE.TK.trace_variable("w", self.Entry_Cspace_Callback)
        self.Label_Cspace_ToolTip = ToolTip(
            self.Label_Cspace,
            text="Character spacing as a percent of character width.",
        )

        self.Label_Wspace = Label(
            self.master, text="Word Spacing", anchor=CENTER
        )
        self.Label_Wspace_u = Label(self.master, text="%", anchor=W)
        self.Entry_Wspace = Entry(self.master, width="15")
        self.Entry_Wspace.configure(textvariable=config.WSPACE.TK)
        self.Entry_Wspace.bind("<Return>", self.Recalculate_Click)
        config.WSPACE.TK.trace_variable("w", self.Entry_Wspace_Callback)
        self.Label_Wspace_ToolTip = ToolTip(
            self.Label_Wspace,
            text="Width of the space character. This is determined as a "
            "percentage of the maximum width of the characters in the "
            "currently selected font.",
        )

        self.Label_Lspace = Label(
            self.master, text="Line Spacing", anchor=CENTER
        )
        self.Entry_Lspace = Entry(self.master, width="15")
        self.Entry_Lspace.configure(textvariable=config.LSPACE.TK)
        self.Entry_Lspace.bind("<Return>", self.Recalculate_Click)
        config.LSPACE.TK.trace_variable("w", self.Entry_Lspace_Callback)
        self.Label_Lspace_ToolTip = ToolTip(
            self.Label_Lspace,
            text="The vertical spacing between lines of text. This is a "
            "multiple of the text height previously input. A vertical "
            "spacing of 1.0 could result in consecutive lines of text "
            "touching each other if the maximum height character is directly "
            "below a character that extends the lowest (like a 'g').",
        )

        self.Label_pos_orient = Label(
            self.master, text="Text Position and Orientation:", anchor=W
        )

        self.Label_Tangle = Label(
            self.master, text="Text Angle", anchor=CENTER
        )
        self.Label_Tangle_u = Label(self.master, text="deg", anchor=W)
        self.Entry_Tangle = Entry(self.master, width="15")
        self.Entry_Tangle.configure(textvariable=config.TANGLE.TK)
        self.Entry_Tangle.bind("<Return>", self.Recalculate_Click)
        config.TANGLE.TK.trace_variable("w", self.Entry_Tangle_Callback)
        self.Label_Tangle_ToolTip = ToolTip(
            self.Label_Tangle,
            text="Rotation of the text or image from horizontal.",
        )

        self.Label_Justify = Label(self.master, text="Justify", anchor=CENTER)
        self.Justify_OptionMenu = OptionMenu(
            root,
            config.justify.TK,
            "Left",
            "Center",
            "Right",
            command=self.Recalculate_RQD_Click,
        )
        self.Label_Justify_ToolTip = ToolTip(
            self.Label_Justify,
            text="Justify determins how to align multiple lines of text. "
            "Left side, Right side or Centered.",
        )

        self.Label_Origin = Label(self.master, text="Origin", anchor=CENTER)
        self.Origin_OptionMenu = OptionMenu(
            root,
            config.origin.TK,
            "Top-Left",
            "Top-Center",
            "Top-Right",
            "Mid-Left",
            "Mid-Center",
            "Mid-Right",
            "Bot-Left",
            "Bot-Center",
            "Bot-Right",
            "Default",
            command=self.Recalculate_RQD_Click,
        )
        self.Label_Origin_ToolTip = ToolTip(
            self.Label_Origin,
            text="Origin determins where the X and Y zero position is located"
            " relative to the engraving.",
        )

        self.Label_flip = Label(self.master, text="Flip Text")
        self.Checkbutton_flip = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_flip.configure(variable=config.flip.TK)
        config.flip.TK.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_flip_ToolTip = ToolTip(
            self.Label_flip,
            text="Selecting Flip Text/Image mirrors the design about a "
            "horizontal line",
        )

        self.Label_mirror = Label(self.master, text="Mirror Text")
        self.Checkbutton_mirror = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_mirror.configure(variable=config.mirror.TK)
        config.mirror.TK.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_mirror_ToolTip = ToolTip(
            self.Label_mirror,
            text="Selecting Mirror Text/Image mirrors the design about a "
            "vertical line.",
        )

        self.Label_text_on_arc = Label(
            self.master, text="Text on Circle Properties:", anchor=W
        )

        self.Label_Tradius = Label(
            self.master, text="Circle Radius", anchor=CENTER
        )
        self.Label_Tradius_u = Label(
            self.master, textvariable=config.units.TK, anchor=W
        )
        self.Entry_Tradius = Entry(self.master, width="15")
        self.Entry_Tradius.configure(textvariable=config.TRADIUS.TK)
        self.Entry_Tradius.bind("<Return>", self.Recalculate_Click)
        config.TRADIUS.TK.trace_variable("w", self.Entry_Tradius_Callback)
        self.Label_Tradius_ToolTip = ToolTip(
            self.Label_Tradius,
            text="Circle radius is the radius of the circle that the text in "
            "the input box is placed on. If the circle radius is set to 0.0 "
            "the text is not placed on a circle.",
        )

        self.Label_outer = Label(self.master, text="Outside circle")
        self.Checkbutton_outer = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_outer.configure(variable=config.outer.TK)
        config.outer.TK.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_outer_ToolTip = ToolTip(
            self.Label_outer,
            text="Select whether the text is placed so that is falls on the "
            "inside of the circle radius or the outside of the circle radius.",
        )

        self.Label_upper = Label(self.master, text="Top of Circle")
        self.Checkbutton_upper = Checkbutton(self.master, text=" ", anchor=W)
        self.Checkbutton_upper.configure(variable=config.upper.TK)
        config.upper.TK.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Label_upper_ToolTip = ToolTip(
            self.Label_upper,
            text="Select whether the text is placed on the top of the circle "
            "of on the bottom of the circle (i.e. concave down or concave up).",
        )

        self.separator1 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator2 = Frame(height=2, bd=1, relief=SUNKEN)
        self.separator3 = Frame(height=2, bd=1, relief=SUNKEN)

        # End Left Column #

        # Right Column #
        self.Label_gcode_opt = Label(
            self.master, text="Gcode Properties:", anchor=W
        )

        self.Label_Feed = Label(self.master, text="Feed Rate")
        self.Label_Feed_u = Label(
            self.master, textvariable=config.funits.TK, anchor=W
        )
        self.Entry_Feed = Entry(self.master, width="15")
        self.Entry_Feed.configure(textvariable=config.FEED.TK)
        self.Entry_Feed.bind("<Return>", self.Recalculate_Click)
        config.FEED.TK.trace_variable("w", self.Entry_Feed_Callback)
        self.Label_Feed_ToolTip = ToolTip(
            self.Label_Feed,
            text="Specify the tool feed rate that is output in the g-code "
            "output file.",
        )

        self.Label_Plunge = Label(self.master, text="Plunge Rate")
        self.Label_Plunge_u = Label(
            self.master, textvariable=config.funits.TK, anchor=W
        )
        self.Entry_Plunge = Entry(self.master, width="15")
        self.Entry_Plunge.configure(textvariable=config.PLUNGE.TK)
        self.Entry_Plunge.bind("<Return>", self.Recalculate_Click)
        config.PLUNGE.TK.trace_variable("w", self.Entry_Plunge_Callback)
        self.Label_Plunge_ToolTip = ToolTip(
            self.Label_Plunge,
            text="Plunge Rate sets the feed rate for vertical moves into the "
            "material being cut.\n\nWhen Plunge Rate is set to zero plunge "
            "feeds are equal to Feed Rate.",
        )

        self.Label_Zsafe = Label(self.master, text="Z Safe")
        self.Label_Zsafe_u = Label(
            self.master, textvariable=config.units.TK, anchor=W
        )
        self.Entry_Zsafe = Entry(self.master, width="15")
        self.Entry_Zsafe.configure(textvariable=config.ZSAFE.TK)
        self.Entry_Zsafe.bind("<Return>", self.Recalculate_Click)
        config.ZSAFE.TK.trace_variable("w", self.Entry_Zsafe_Callback)
        self.Label_Zsafe_ToolTip = ToolTip(
            self.Label_Zsafe,
            text="Z location that the tool will be sent to prior to any rapid"
            " moves.",
        )

        self.Label_Zcut = Label(self.master, text="Engrave Depth")
        self.Label_Zcut_u = Label(
            self.master, textvariable=config.units.TK, anchor=W
        )
        self.Entry_Zcut = Entry(self.master, width="15")
        self.Entry_Zcut.configure(textvariable=config.ZCUT.TK)
        self.Entry_Zcut.bind("<Return>", self.Recalculate_Click)
        config.ZCUT.TK.trace_variable("w", self.Entry_Zcut_Callback)
        self.Label_Zcut_ToolTip = ToolTip(
            self.Label_Zcut,
            text="Depth of the engraving cut. This setting has no effect when "
            "the v-carve option is selected.",
        )

        self.Checkbutton_fontdex = Checkbutton(
            self.master, text="Show All Font Characters", anchor=W
        )
        config.fontdex.TK.trace_variable("w", self.Entry_recalc_var_Callback)
        self.Checkbutton_fontdex.configure(variable=config.fontdex.TK)
        self.Label_fontfile = Label(
            self.master,
            textvariable=config.current_input_file.TK,
            anchor=W,
            foreground="grey50",
        )
        self.Label_List_Box = Label(
            self.master, text="Font Files:", foreground="#101010", anchor=W
        )
        lbframe = Frame(self.master)
        self.Listbox_1_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Listbox_1 = Listbox(
            lbframe, selectmode="single", yscrollcommand=scrollbar.set
        )
        scrollbar.config(command=self.Listbox_1.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Listbox_1.pack(side=LEFT, fill=BOTH, expand=1)

        self.Listbox_1.bind("<ButtonRelease-1>", self.Listbox_1_Click)
        self.Listbox_1.bind("<Up>", self.Listbox_Key_Up)
        self.Listbox_1.bind("<Down>", self.Listbox_Key_Down)

        for name in font.available_font_files(config.fontdir.get()):
            self.Listbox_1.insert(END, name)

        if len(config.fontfile.get()) < 4:
            try:
                config.fontfile.set(self.Listbox_1.get(0))
            except:
                config.fontfile.set(" ")

        config.fontdir.TK.trace_variable("w", self.Entry_fontdir_Callback)

        self.V_Carve_Calc = Button(
            self.master, text="Calc V-Carve", command=self.V_Carve_Calc_Click
        )

        self.Radio_Cut_E = Radiobutton(
            self.master, text="Engrave", value="engrave", anchor=W
        )
        self.Radio_Cut_E.configure(variable=config.cut_type.TK)
        self.Radio_Cut_V = Radiobutton(
            self.master, text="V-Carve", value="v-carve", anchor=W
        )
        self.Radio_Cut_V.configure(variable=config.cut_type.TK)
        config.cut_type.TK.trace_variable("w", self.Entry_recalc_var_Callback)
        # End Right Column #

        # Text Box
        self.Input_Label = Label(self.master, text="Input Text:", anchor=W)

        lbframe = Frame(self.master)
        self.Input_frame = lbframe
        scrollbar = Scrollbar(lbframe, orient=VERTICAL)
        self.Input = Text(
            lbframe,
            width="40",
            height="12",
            yscrollcommand=scrollbar.set,
            bg="white",
        )
        self.Input.insert(END, self.default_text)
        scrollbar.config(command=self.Input.yview)
        scrollbar.pack(side=RIGHT, fill=Y)
        self.Input.pack(side=LEFT, fill=BOTH, expand=1)
        self.Input.bind("<Key>", self.Recalculate_RQD_Nocalc)

        # GEN Setting Window Entry initialization
        self.Entry_Xoffset = Entry()
        self.Entry_Yoffset = Entry()
        self.Entry_BoxGap = Entry()
        self.Entry_ArcAngle = Entry()
        self.Entry_Accuracy = Entry()
        # Bitmap Setting Window Entry initialization
        self.Entry_BMPturdsize = Entry()
        self.Entry_BMPalphamax = Entry()
        self.Entry_BMPoptTolerance = Entry()
        # V-Carve Setting Window Entry initialization
        self.Entry_Vbitangle = Entry()
        self.Entry_Vbitdia = Entry()
        self.Entry_VDepthLimit = Entry()
        self.Entry_InsideAngle = Entry()
        self.Entry_OutsideAngle = Entry()
        self.Entry_StepSize = Entry()
        self.Entry_Allowance = Entry()
        self.Entry_W_CLEAN = Entry()
        self.Entry_CLEAN_DIA = Entry()
        self.Entry_STEP_OVER = Entry()
        self.Entry_V_CLEAN = Entry()

        # Make Menu Bar
        self.menuBar = Menu(self.master, relief="raised", bd=2)

        top_File = Menu(self.menuBar, tearoff=0)
        top_File.add(
            "command",
            label="Save Settings to File",
            command=self.menu_File_Save_Settings_File,
        )
        top_File.add(
            "command",
            label="Read Settings from File",
            command=self.menu_File_Open_G_Code_File,
        )
        top_File.add_separator()
        if self.POTRACE_AVAIL:
            top_File.add(
                "command",
                label="Open DXF/Image",
                command=self.menu_File_Open_DXF_File,
            )
        else:
            top_File.add(
                "command",
                label="Open DXF",
                command=self.menu_File_Open_DXF_File,
            )
        top_File.add_separator()
        top_File.add(
            "command",
            label="Save G-Code",
            command=self.menu_File_Save_G_Code_File,
        )
        top_File.add_separator()
        top_File.add(
            "command", label="Export SVG", command=self.menu_File_Save_SVG_File
        )
        top_File.add(
            "command", label="Export DXF", command=self.menu_File_Save_DXF_File
        )
        top_File.add(
            "command",
            label="Export DXF (close loops)",
            command=self.menu_File_Save_DXF_File_close_loops,
        )
        if IN_AXIS:
            top_File.add(
                "command",
                label="Write To Axis and Exit",
                command=self.WriteToAxis,
            )
        else:
            top_File.add("command", label="Exit", command=self.menu_File_Quit)
        self.menuBar.add("cascade", label="File", menu=top_File)

        top_Edit = Menu(self.menuBar, tearoff=0)
        top_Edit.add(
            "command",
            label="Copy G-Code Data to Clipboard",
            command=self.CopyClipboard_GCode,
        )
        top_Edit.add(
            "command",
            label="Copy SVG Data to Clipboard",
            command=self.CopyClipboard_SVG,
        )
        self.menuBar.add("cascade", label="Edit", menu=top_Edit)

        top_View = Menu(self.menuBar, tearoff=0)
        top_View.add(
            "command", label="Recalculate", command=self.menu_View_Recalculate
        )
        top_View.add_separator()

        top_View.add(
            "command",
            label="Zoom In <Page Up>",
            command=self.menu_View_Zoom_in,
        )
        top_View.add(
            "command",
            label="Zoom Out <Page Down>",
            command=self.menu_View_Zoom_out,
        )
        top_View.add(
            "command", label="Zoom Fit <F5>", command=self.menu_View_Refresh
        )

        top_View.add_separator()

        top_View.add_checkbutton(
            label="Show Thickness",
            variable=config.show_thick.TK,
            command=self.menu_View_Refresh,
        )
        top_View.add_checkbutton(
            label="Show Origin Axis",
            variable=config.show_axis.TK,
            command=self.menu_View_Refresh,
        )
        top_View.add_checkbutton(
            label="Show Bounding Box",
            variable=config.show_box.TK,
            command=self.menu_View_Refresh,
        )
        top_View.add_checkbutton(
            label="Show V-Carve ToolPath",
            variable=config.show_v_path.TK,
            command=self.menu_View_Refresh,
        )
        top_View.add_checkbutton(
            label="Show V-Carve Area",
            variable=config.show_v_area.TK,
            command=self.menu_View_Refresh,
        )
        self.menuBar.add("cascade", label="View", menu=top_View)

        top_Settings = Menu(self.menuBar, tearoff=0)
        top_Settings.add(
            "command",
            label="General Settings",
            command=self.GEN_Settings_Window,
        )
        top_Settings.add(
            "command",
            label="V-Carve Settings",
            command=self.VCARVE_Settings_Window,
        )
        if self.POTRACE_AVAIL:
            top_Settings.add(
                "command",
                label="Bitmap Import Settings",
                command=self.PBM_Settings_Window,
            )

        top_Settings.add_separator()
        top_Settings.add_radiobutton(
            label="Engrave Mode", variable=config.cut_type.TK, value="engrave"
        )
        top_Settings.add_radiobutton(
            label="V-Carve Mode", variable=config.cut_type.TK, value="v-carve"
        )

        top_Settings.add_separator()
        top_Settings.add_radiobutton(
            label="Text Mode (CXF/TTF)",
            variable=config.input_type.TK,
            value="text",
            command=self.menu_Mode_Change,
        )
        top_Settings.add_radiobutton(
            label="Image Mode (DXF/Bitmap)",
            variable=config.input_type.TK,
            value="image",
            command=self.menu_Mode_Change,
        )

        self.menuBar.add("cascade", label="Settings", menu=top_Settings)

        top_Help = Menu(self.menuBar, tearoff=0)
        top_Help.add(
            "command", label="About (E-Mail)", command=self.menu_Help_About
        )
        top_Help.add(
            "command", label="Help (Web Page)", command=self.menu_Help_Web
        )
        self.menuBar.add("cascade", label="Help", menu=top_Help)

        self.master.config(menu=self.menuBar)

    def entry_set(self, val2, calc_flag=NumberCheck.is_valid, new=0):
        config = self.config
        if calc_flag == NumberCheck.is_valid and new == 0:
            try:
                self.statusbar.configure(bg="yellow")
                val2.configure(bg="yellow")
                self.statusMessage.set(" Recalculation required.")
            except:
                pass
        elif calc_flag == NumberCheck.is_not_a_number:
            try:
                val2.configure(bg="red")
                self.statusbar.configure(bg="red")
                self.statusMessage.set(" Value should be a number. ")
            except:
                pass
        elif calc_flag == NumberCheck.is_invalid:
            try:
                self.statusbar.configure(bg="red")
                val2.configure(bg="red")
            except:
                pass
        elif (
            calc_flag == NumberCheck.is_valid
            or calc_flag == NumberCheck.is_valid_no_recalc_required
        ) and new == 1:
            try:
                self.statusbar.configure(bg="white")
                self.statusMessage.set(config.bounding_box.get())
                val2.configure(bg="white")
            except:
                pass
        elif calc_flag == NumberCheck.is_valid_no_recalc_required and new == 0:
            try:
                self.statusbar.configure(bg="white")
                self.statusMessage.set(config.bounding_box.get())
                val2.configure(bg="white")
            except:
                pass

        elif (
            calc_flag == NumberCheck.is_valid
            or calc_flag == NumberCheck.is_valid_no_recalc_required
        ) and new == 2:
            return 0
        return 1

    def Write_Config_File(self, event):
        gcode = self.WriteGCode(config_file=True)
        config_file = "config.ngc"
        configname_full = self.HOME_DIR + "/" + config_file

        current_name = event.widget.winfo_parent()
        win_id = event.widget.nametowidget(current_name)

        if os.path.isfile(configname_full):
            try:
                win_id.withdraw()
            except:
                pass

            if not message.message_ask_ok_cancel(
                "Replace",
                "Replace Exiting Configuration File?\n" + configname_full,
            ):
                try:
                    win_id.deiconify()
                except:
                    pass
                return

        try:
            fout = open(configname_full, "w")
        except:
            self.statusMessage.set(
                "Unable to open file for writing: %s" % (configname_full)
            )
            self.statusbar.configure(bg="red")
            return

        for line in gcode:
            try:
                fout.write(line + "\n")
            except:
                fout.write("(skipping line)\n")
        fout.close()
        self.statusMessage.set(
            "Configuration File Saved: %s" % (configname_full)
        )
        self.statusbar.configure(bg="white")
        try:
            win_id.deiconify()
        except:
            pass

    def append_author_to_gcode(self, gcode):
        gcode.append_comment("Code generated by f-engrave-" + version + ".py")
        gcode.append_comment("by Scorch - 2021")

    def append_cleanup_comments_to_gcode(
        self, gcode, cleanup_bit_type, BitDia, bit_angle, Units
    ):
        gcode.append_comment(" This file is a secondary operation for ")
        gcode.append_comment(" cleaning up a V-carve. ")

        if cleanup_bit_type == "straight":
            gcode.append_comment(" The tool paths were calculated based ")
            gcode.append_comment(" on using a bit with a ")
            gcode.append_comment(" Diameter of %.4f %s)" % (BitDia, Units))
        else:
            gcode.append_comment(" The tool paths were calculated based ")
            gcode.append_comment(" on using a v-bit with a ")
            gcode.append_comment(" angle of %.4f Degrees " % (bit_angle))

        gcode.append_comment(
            "========================================================="
        )

    def append_settings_to_gcode(self, gcode, text):
        config = self.config
        gcode.append_comment(
            "Settings used in f-engrave when this file was created"
        )
        if config.input_type.get() == "text":
            String_short = text
            max_len = 40
            if len(text) > max_len:
                String_short = text[0:max_len] + "___"
            gcode.append_comment(
                "Engrave Text: " + re.sub(r"\W+", " ", String_short) + ""
            )
        gcode.append_comment(
            "========================================================="
        )

        # BOOL
        gcode.append_comment(
            "fengrave_set show_axis   %s " % (int(config.show_axis.get()))
        )
        gcode.append_comment(
            "fengrave_set show_box    %s " % (int(config.show_box.get()))
        )
        gcode.append_comment(
            "fengrave_set show_thick  %s " % (int(config.show_thick.get()))
        )
        gcode.append_comment(
            "fengrave_set flip        %s " % (int(config.flip.get()))
        )
        gcode.append_comment(
            "fengrave_set mirror      %s " % (int(config.mirror.get()))
        )
        gcode.append_comment(
            "fengrave_set outer       %s " % (int(config.outer.get()))
        )
        gcode.append_comment(
            "fengrave_set upper       %s " % (int(config.upper.get()))
        )
        gcode.append_comment(
            "fengrave_set v_flop      %s " % (int(config.v_flop.get()))
        )
        gcode.append_comment(
            "fengrave_set v_pplot     %s " % (int(config.v_pplot.get()))
        )
        gcode.append_comment(
            "fengrave_set inlay       %s " % (int(config.inlay.get()))
        )
        gcode.append_comment(
            "fengrave_set bmp_long    %s " % (int(config.bmp_longcurve.get()))
        )
        gcode.append_comment(
            "fengrave_set var_dis     %s " % (int(config.var_dis.get()))
        )
        gcode.append_comment(
            "fengrave_set ext_char    %s " % (int(config.ext_char.get()))
        )
        gcode.append_comment(
            "fengrave_set useIMGsize  %s " % (int(config.useIMGsize.get()))
        )
        gcode.append_comment(
            "fengrave_set no_comments %s " % (int(config.no_comments.get()))
        )
        gcode.append_comment(
            "fengrave_set plotbox     %s " % (int(config.plotbox.get()))
        )
        gcode.append_comment(
            "fengrave_set show_v_path %s " % (int(config.show_v_path.get()))
        )
        gcode.append_comment(
            "fengrave_set show_v_area %s " % (int(config.show_v_area.get()))
        )

        # STRING
        gcode.append_comment(
            "fengrave_set arc_fit    %s " % (config.arc_fit.get())
        )
        gcode.append_comment(
            "fengrave_set YSCALE     %s " % (config.YSCALE.get())
        )
        gcode.append_comment(
            "fengrave_set XSCALE     %s " % (config.XSCALE.get())
        )
        gcode.append_comment(
            "fengrave_set LSPACE     %s " % (config.LSPACE.get())
        )
        gcode.append_comment(
            "fengrave_set CSPACE     %s " % (config.CSPACE.get())
        )
        gcode.append_comment(
            "fengrave_set WSPACE     %s " % (config.WSPACE.get())
        )
        gcode.append_comment(
            "fengrave_set TANGLE     %s " % (config.TANGLE.get())
        )
        gcode.append_comment(
            "fengrave_set TRADIUS    %s " % (config.TRADIUS.get())
        )
        gcode.append_comment(
            "fengrave_set ZSAFE      %s " % (config.ZSAFE.get())
        )
        gcode.append_comment("fengrave_set ZCUT       %s " % (config.ZCUT.get()))
        gcode.append_comment(
            "fengrave_set STHICK     %s " % (config.STHICK.get())
        )
        gcode.append_comment(
            "fengrave_set origin     %s " % (config.origin.get())
        )
        gcode.append_comment(
            "fengrave_set justify    %s " % (config.justify.get())
        )
        gcode.append_comment(
            "fengrave_set units      %s " % (config.units.get())
        )

        gcode.append_comment(
            "fengrave_set xorigin    %s " % (config.xorigin.get())
        )
        gcode.append_comment(
            "fengrave_set yorigin    %s " % (config.yorigin.get())
        )
        gcode.append_comment(
            "fengrave_set segarc     %s " % (config.segarc.get())
        )
        gcode.append_comment(
            "fengrave_set accuracy   %s " % (config.accuracy.get())
        )

        gcode.append_comment("fengrave_set FEED       %s " % (config.FEED.get()))
        gcode.append_comment(
            "fengrave_set PLUNGE     %s " % (config.PLUNGE.get())
        )
        gcode.append_comment(
            "fengrave_set fontfile   \042%s\042 " % (config.fontfile.get())
        )
        gcode.append_comment(
            "fengrave_set H_CALC     %s " % (config.H_CALC.get())
        )
        gcode.append_comment(
            "fengrave_set boxgap     %s " % (config.boxgap.get())
        )
        gcode.append_comment(
            "fengrave_set cut_type    %s " % (config.cut_type.get())
        )
        gcode.append_comment(
            "fengrave_set bit_shape   %s " % (config.bit_shape.get())
        )
        gcode.append_comment(
            "fengrave_set v_bit_angle %s " % (config.v_bit_angle.get())
        )
        gcode.append_comment(
            "fengrave_set v_bit_dia   %s " % (config.v_bit_dia.get())
        )
        gcode.append_comment(
            "fengrave_set v_drv_crner %s " % (config.v_drv_crner.get())
        )
        gcode.append_comment(
            "fengrave_set v_stp_crner %s " % (config.v_stp_crner.get())
        )
        gcode.append_comment(
            "fengrave_set v_step_len  %s " % (config.v_step_len.get())
        )
        gcode.append_comment(
            "fengrave_set allowance   %s " % (config.allowance.get())
        )

        gcode.append_comment(
            "fengrave_set v_max_cut   %s " % (config.v_max_cut.get())
        )
        gcode.append_comment(
            "fengrave_set v_rough_stk %s " % (config.v_rough_stk.get())
        )

        gcode.append_comment(
            "fengrave_set v_depth_lim  %s " % (config.v_depth_lim.get())
        )

        gcode.append_comment(
            "fengrave_set v_check_all %s " % (config.v_check_all.get())
        )
        gcode.append_comment(
            "fengrave_set bmp_turnp   %s " % (config.bmp_turnpol.get())
        )
        gcode.append_comment(
            "fengrave_set bmp_turds   %s " % (config.bmp_turdsize.get())
        )
        gcode.append_comment(
            "fengrave_set bmp_alpha   %s " % (config.bmp_alphamax.get())
        )
        gcode.append_comment(
            "fengrave_set bmp_optto   %s " % (config.bmp_opttolerance.get())
        )

        gcode.append_comment(
            "fengrave_set fontdir    \042%s\042 " % (config.fontdir.get())
        )
        gcode.append_comment(
            "fengrave_set gpre        %s " % (config.gpre.get())
        )
        gcode.append_comment(
            "fengrave_set gpost       %s " % (config.gpost.get())
        )

        gcode.append_comment(
            "fengrave_set imagefile   \042%s\042 " % (self.IMAGE_FILE)
        )
        gcode.append_comment(
            "fengrave_set input_type  %s " % (config.input_type.get())
        )

        gcode.append_comment(
            "fengrave_set clean_dia   %s " % (config.clean_dia.get())
        )
        gcode.append_comment(
            "fengrave_set clean_step  %s " % (config.clean_step.get())
        )
        gcode.append_comment(
            "fengrave_set clean_v     %s " % (config.clean_v.get())
        )
        clean_out = "%d,%d,%d,%d,%d,%d" % (
            config.clean_P.get(),
            config.clean_X.get(),
            config.clean_Y.get(),
            config.v_clean_P.get(),
            config.v_clean_Y.get(),
            config.v_clean_X.get()
        )
        gcode.append_comment("fengrave_set clean_paths  %s " % (clean_out))

        str_data = ""
        cnt = 0
        for char in text:
            if cnt > 10:
                str_data = str_data
                gcode.append_comment("fengrave_set TCODE   %s" % (str_data))
                str_data = ""
                cnt = 0
            str_data = str_data + " %03d " % (ord(char))
            cnt = cnt + 1
        str_data = str_data
        gcode.append_comment("fengrave_set TCODE   %s" % (str_data))

        gcode.append_comment(
            "fengrave_set NGC_DIR  \042%s\042 "
            % (os.path.dirname(self.NGC_FILE))
        )
        gcode.append_comment("Fontfile: %s " % (config.fontfile.get()))

        gcode.append_comment(
            "#########################################################"
        )

    def WriteGCode(self, config_file=False):
        config = self.config
        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )

        SafeZ = float(config.ZSAFE.get())
        Acc = float(config.accuracy.get())
        Depth = float(config.ZCUT.get())

        if config.batch.get():
            String = self.default_text
        else:
            String = self.Input.get(1.0, END)

        g = Gcode(
            message,
            safetyheight=SafeZ,
            tolerance=Acc,
            arc_fit=config.arc_fit.get(),
            metric=config.units.get() != "in",
            enable_variables=not config.var_dis.get()
        )

        if config_file or not config.no_comments.get():
            self.append_author_to_gcode(g)
            self.append_settings_to_gcode(g, String)

        if config_file:
            return g

        g.set_plane(Plane.xy)
        g.set_depth(Depth)

        g.append_mode()
        g.append_units()

        # Output preamble
        g.append_preamble(config.gpre.get())

        # Set Feed rate
        g.set_feed(config.FEED.get(), write_it=True)
        g.set_z_feed(config.PLUNGE.get())

        oldx = oldy = -99990.0
        first_stroke = True
        # Set up variables for multipass cutting
        maxDZ = float(config.v_max_cut.get())
        rough_stock = float(config.v_rough_stk.get())
        zmin = 0.0
        roughing = True
        rough_again = False

        if config.cut_type.get() == "engrave" or config.bit_shape.get() == "FLAT":
            ecoords = []
            if (config.bit_shape.get() == "FLAT") and (
                config.cut_type.get() != "engrave"
            ):
                Acc = float(config.v_step_len.get()) * 1.5  # fudge factor
                ###################################
                ###   Create Flat Cut ECOORDS   ###
                ###################################
                if len(self.vcoords) > 0:
                    rbit = calc_vbit_dia(config, bit) / 2.0
                    loopa_old = self.vcoords[0][3]
                    loop = 0
                    for i in range(1, len(self.vcoords)):
                        xa = self.vcoords[i][0]
                        ya = self.vcoords[i][1]
                        ra = self.vcoords[i][2]
                        loopa = self.vcoords[i][3]

                        if loopa_old != loopa:
                            loop = loop + 1
                        if ra >= rbit:
                            ecoords.append([xa, ya, loop])
                            loopa_old = loopa
                        else:
                            loop = loop + 1
                try:
                    Depth = float(config.maxcut.get())
                except:
                    Depth = 0.0
                if rough_stock > 0:
                    rough_again = True
                if (rough_stock > 0) and (-maxDZ < rough_stock):
                    rough_stock = -maxDZ

            else:
                ##########################
                ###   Create ECOORDS   ###
                ##########################
                loop = 0
                for line in self.coords:
                    XY = line
                    x1 = XY[0]
                    y1 = XY[1]
                    x2 = XY[2]
                    y2 = XY[3]
                    dx = oldx - x1
                    dy = oldy - y1
                    dist = sqrt(dx * dx + dy * dy)
                    # check and see if we need to move to a new discontinuous
                    # start point
                    if (dist > Acc) or first_stroke:
                        loop = loop + 1
                        first_stroke = False
                        ecoords.append([x1, y1, loop])
                    ecoords.append([x2, y2, loop])
                    oldx, oldy = x2, y2

            order_out = Sort_Paths(ecoords)
            ###########################

            while rough_again or roughing:
                if not rough_again:
                    roughing = False
                    maxDZ = -99999
                rough_again = False
                zmin = zmin + maxDZ

                z1 = Depth
                if roughing:
                    z1 = z1 + rough_stock
                if z1 < zmin:
                    z1 = zmin
                    rough_again = True
                zmax = zmin - maxDZ

                if (
                    config.bit_shape.get() == "FLAT"
                    and config.cut_type.get() != "engrave"
                ):
                    g.set_depth(z1)

                dist = 999
                lastx = -999
                lasty = -999
                z1 = 0
                nextz = 0

                for line in order_out:
                    temp = line
                    if temp[0] > temp[1]:
                        step = -1
                    else:
                        step = 1

                    loop_old = -1

                    for i in range(temp[0], temp[1] + step, step):
                        x1 = ecoords[i][0]
                        y1 = ecoords[i][1]
                        loop = ecoords[i][2]

                        # check and see if we need to move to a new
                        # discontinuous start point
                        if loop != loop_old:
                            g.flush()
                            dx = x1 - lastx
                            dy = y1 - lasty
                            dist = sqrt(dx * dx + dy * dy)
                            if dist > Acc:
                                g.safety()
                                g.rapid(x=x1, y=y1)
                                g.plunge_z()
                                lastx = x1
                                lasty = y1
                                g.cut(x1, y1)
                        else:
                            g.cut(x1, y1)
                            lastx = x1
                            lasty = y1

                        loop_old = loop
                    g.flush()
                g.flush()
            g.flush()
        # END engraving
        else:
            # V-carve stuff
            g.set_z_feed(config.FEED.get())

            ##########################
            ###   find loop ends   ###
            ##########################
            Lbeg = []
            Lend = []
            Lbeg.append(0)
            if len(self.vcoords) > 0:
                loop_old = self.vcoords[0][3]
                for i in range(1, len(self.vcoords)):
                    loop = self.vcoords[i][3]
                    if loop != loop_old:
                        Lbeg.append(i)
                        Lend.append(i - 1)
                    loop_old = loop
                Lend.append(i)

                # Find new order based on distance to next beginning

                order_out = []
                order_out.append([Lbeg[0], Lend[0]])
                inext = 0
                total = len(Lbeg)
                for i in range(total - 1):
                    ii = Lend.pop(inext)
                    Lbeg.pop(inext)
                    Xcur = self.vcoords[ii][0]
                    Ycur = self.vcoords[ii][1]

                    dx = Xcur - self.vcoords[Lbeg[0]][0]
                    dy = Ycur - self.vcoords[Lbeg[0]][1]
                    min_dist = dx * dx + dy * dy

                    inext = 0
                    for j in range(1, len(Lbeg)):
                        dx = Xcur - self.vcoords[Lbeg[j]][0]
                        dy = Ycur - self.vcoords[Lbeg[j]][1]
                        dist = dx * dx + dy * dy
                        if dist < min_dist:
                            min_dist = dist
                            inext = j
                    order_out.append([Lbeg[inext], Lend[inext]])
                #####################################################
                new_coords = []
                for line in order_out:
                    temp = line
                    for i in range(temp[0], temp[1] + 1):
                        new_coords.append(self.vcoords[i])

                half_angle = bit.half_angle
                bit_radius = bit.radius

                ################################
                # V-carve stuff
                # maxDZ       =  float(self.v_max_cut.get())
                # rough_stock =  float(self.v_rough_stk.get())
                # zmin        =  0.0
                # roughing    = True
                # rough_again = False
                if rough_stock > 0:
                    rough_again = True
                ################################
                if (rough_stock > 0) and (-maxDZ < rough_stock):
                    rough_stock = -maxDZ
                while rough_again or roughing:
                    if not rough_again:
                        roughing = False
                        maxDZ = -99999
                    rough_again = False
                    zmin = zmin + maxDZ

                    loop_old = -1

                    v_index = -1

                    while v_index < len(new_coords) - 1:
                        v_index = v_index + 1
                        x1 = new_coords[v_index][0]
                        y1 = new_coords[v_index][1]
                        r1 = new_coords[v_index][2]
                        loop = new_coords[v_index][3]

                        if v_index + 1 < len(new_coords):
                            nextr = new_coords[v_index + 1][2]
                        else:
                            nextr = 0

                        if config.bit_shape.get() == "VBIT":
                            z1 = -r1 / tan(half_angle)
                            nextz = -nextr / tan(half_angle)
                            if config.inlay.get():
                                inlay_depth = self.calc_r_inlay_depth()
                                z1 = z1 + inlay_depth
                                nextz = nextz + inlay_depth

                        elif config.bit_shape.get() == "BALL":
                            theta = acos(r1 / bit_radius)
                            z1 = -bit_radius * (1 - sin(theta))

                            next_theta = acos(nextr / bit_radius)
                            nextz = -bit_radius * (1 - sin(next_theta))
                        elif config.bit_shape.get() == "FLAT":
                            # This case should have been caught in the
                            # engraving section above
                            pass
                        else:
                            pass

                        if roughing:
                            z1 = z1 + rough_stock
                            nextz = nextz + rough_stock
                        if z1 < zmin:
                            z1 = zmin
                            rough_again = True
                        if nextz < zmin:
                            nextz = zmin
                            rough_again = True

                        zmax = zmin - maxDZ  # + rough_stock
                        if ((z1 > zmax) and (nextz > zmax)) and (roughing):
                            loop_old = -1
                            continue
                        # check and see if we need to move to a new
                        # discontinuous start point
                        if loop != loop_old:
                            g.safety()
                            g.rapid(x=x1, y=y1)
                            g.plunge_z(z1)

                            lastx = x1
                            lasty = y1
                            g.cut(x1, y1, z1)
                        else:
                            g.cut(x1, y1, z1)
                            lastx = x1
                            lasty = y1
                        loop_old = loop
                    g.flush()
                g.flush()
            g.flush()
            # End V-carve stuff
        # Make Circle
        XOrigin = float(config.xorigin.get())
        YOrigin = float(config.yorigin.get())
        Radius_plot = float(self.RADIUS_PLOT)
        if Radius_plot != 0 and config.cut_type.get() == "engrave":
            g.safety()
            g.rapid(
                x=-Radius_plot - self.Xzero + XOrigin, y=YOrigin - self.Yzero
            )
            g.plunge_z()
            g.arc(cw=True, I_offset=Radius_plot, J_offset=0.0)
        # End Circle

        # Done, so move Z to safe position.
        g.safety()

        # Postamble
        g.append_postamble(config.gpost.get())

        return g

    #############################
    # Write Cleanup G-code File #
    #############################
    def WRITE_CLEAN_UP(self, bit_type="straight"):
        config = self.config
        SafeZ = float(config.ZSAFE.get())
        bit = bit_from_shape(
            config.bit_shape.get(),
            config.v_bit_dia.get(),
            config.v_bit_angle.get()
        )

        calc_depth_limit(config, bit)
        try:
            Depth = float(config.maxcut.get())
        except:
            Depth = 0.0
        if config.inlay.get():
            Depth = Depth + float(config.allowance.get())

        g = Gcode(
            message,
            safetyheight=SafeZ,
            tolerance=float(config.accuracy.get()),
            arc_fit=config.arc_fit.get(),
            metric=config.units.get() != "in",
            enable_variables=not config.var_dis.get()
        )

        if not config.no_comments.get():
            self.append_author_to_gcode(g)
            self.append_cleanup_comments_to_gcode(
                g,
                bit_type,
                float(config.clean_dia.get()),
                bit.angle,
                config.units.get(),
            )

        g.set_depth(Depth)
        g.append_mode()
        g.append_units()

        # Output preamble
        g.append_preamble(config.gpre.get())

        # Set Feed rate
        g.set_feed(config.FEED.get(), write_it=True)
        g.set_z_feed(config.PLUNGE.get())

        if bit_type == "straight":
            coords_out = self.clean_coords_sort
        else:
            coords_out = self.v_clean_coords_sort

        # Multipass stuff
        ################################
        # Cleanup
        maxDZ = float(config.v_max_cut.get())
        rough_stock = float(config.v_rough_stk.get())
        zmin = 0.0
        roughing = True
        rough_again = False
        if rough_stock > 0:
            rough_again = True
        ################################
        if (rough_stock > 0) and (-maxDZ < rough_stock):
            rough_stock = -maxDZ
        while rough_again or roughing:
            if not rough_again:
                roughing = False
                maxDZ = -99999
            rough_again = False
            zmin = zmin + maxDZ

            # The clean coords have already been sorted so we can just write
            # them

            order_out = Sort_Paths(coords_out, 3)
            new_coords = []
            for line in order_out:
                temp = line
                if temp[0] < temp[1]:
                    step = 1
                else:
                    step = -1
                for i in range(temp[0], temp[1] + step, step):
                    new_coords.append(coords_out[i])
            coords_out = new_coords

            if len(coords_out) > 0:
                loop_old = -1
                v_index = -1
                while v_index < len(coords_out) - 1:
                    v_index = v_index + 1
                    x1 = coords_out[v_index][0]
                    y1 = coords_out[v_index][1]
                    loop = coords_out[v_index][3]

                    # Check and see if we need to move to a new discontinuous
                    # start point.
                    if loop != loop_old:
                        z1 = Depth
                        if roughing:
                            z1 = Depth + rough_stock  # Depth
                        if z1 < zmin:
                            z1 = zmin
                            rough_again = True

                        g.safety()
                        g.rapid(x=x1, y=y1)
                        g.plunge_z(z1)

                    else:
                        g.cut(x1, y1)

                    loop_old = loop

        # End multipass loop

        # Done, so move Z to safe position.
        g.safety()

        # Postamble
        g.append_postamble(config.gpost.get())

        return g

        ###################################

    def WriteSVG(self):
        config = self.config
        if config.cut_type.get() == "v-carve":
            Thick = 0.001
        else:
            Thick = float(config.STHICK.get())

        dpi = 100

        maxx = -99919.0
        maxy = -99929.0
        miny = 99959.0
        minx = 99969.0
        for line in self.coords:
            XY = line
            maxx = max(maxx, XY[0], XY[2])
            minx = min(minx, XY[0], XY[2])
            miny = min(miny, XY[1], XY[3])
            maxy = max(maxy, XY[1], XY[3])

        XOrigin = float(config.xorigin.get())
        YOrigin = float(config.yorigin.get())
        Radius_plot = float(self.RADIUS_PLOT)
        if Radius_plot != 0:
            maxx = max(maxx, XOrigin + Radius_plot - self.Xzero)
            minx = min(minx, XOrigin - Radius_plot - self.Xzero)
            miny = min(miny, YOrigin - Radius_plot - self.Yzero)
            maxy = max(maxy, YOrigin + Radius_plot - self.Yzero)

        maxx = maxx + Thick / 2
        minx = minx - Thick / 2
        miny = miny - Thick / 2
        maxy = maxy + Thick / 2

        width_in = maxx - minx
        height_in = maxy - miny
        width = (maxx - minx) * dpi
        height = (maxy - miny) * dpi

        svg = SVG(config.units.get(), width_in, height_in, width, height, dpi)

        # Make Circle
        if Radius_plot != 0 and config.cut_type.get() == "engrave":
            svg.circle(
                XOrigin - self.Xzero - minx,
                -YOrigin + self.Yzero + maxy,
                Radius_plot,
                Thick,
            )
        # End Circle

        for line in self.coords:
            XY = line
            svg.line(
                XY[0] - minx, -XY[1] + maxy, XY[2] - minx, -XY[3] + maxy, Thick
            )

        svg.close()

        return svg

    def CopyClipboard_GCode(self):
        self.clipboard_clear()
        if self.Check_All_Variables() > 0:
            return
        gcode = self.WriteGCode()
        for line in gcode:
            self.clipboard_append(line + "\n")

    def CopyClipboard_SVG(self):
        self.clipboard_clear()
        svgcode = self.WriteSVG()
        for line in svgcode:
            self.clipboard_append(line + "\n")

    def WriteToAxis(self):
        if self.Check_All_Variables() > 0:
            return
        gcode = self.WriteGCode()
        for line in gcode:
            try:
                sys.stdout.write(line + "\n")
            except:
                pass
        self.Quit_Click(None)

    def Quit_Click(self, event):
        self.statusMessage.set("Exiting!")
        root.destroy()

    def ZOOM_ITEMS(self, x0, y0, z_factor):
        all = self.PreviewCanvas.find_all()
        for i in all:
            self.PreviewCanvas.scale(i, x0, y0, z_factor, z_factor)
            w = self.PreviewCanvas.itemcget(i, "width")
            self.PreviewCanvas.itemconfig(i, width=float(w) * z_factor)
        self.PreviewCanvas.update_idletasks()

    def ZOOM(self, z_inc):
        all = self.PreviewCanvas.find_all()
        x = int(self.PreviewCanvas.cget("width")) / 2.0
        y = int(self.PreviewCanvas.cget("height")) / 2.0
        for i in all:
            self.PreviewCanvas.scale(i, x, y, z_inc, z_inc)
            w = self.PreviewCanvas.itemcget(i, "width")
            self.PreviewCanvas.itemconfig(i, width=float(w) * z_inc)
        self.PreviewCanvas.update_idletasks()

    def menu_View_Zoom_in(self):
        x = int(self.PreviewCanvas.cget("width")) / 2.0
        y = int(self.PreviewCanvas.cget("height")) / 2.0
        self.ZOOM_ITEMS(x, y, 2.0)

    def menu_View_Zoom_out(self):
        x = int(self.PreviewCanvas.cget("width")) / 2.0
        y = int(self.PreviewCanvas.cget("height")) / 2.0
        self.ZOOM_ITEMS(x, y, 0.5)

    def _mouseZoomIn(self, event):
        self.ZOOM_ITEMS(event.x, event.y, 1.25)

    def _mouseZoomOut(self, event):
        self.ZOOM_ITEMS(event.x, event.y, 0.75)

    def mouseZoomStart(self, event):
        self.zoomx0 = event.x
        self.zoomy = event.y
        self.zoomy0 = event.y

    def mouseZoom(self, event):
        dy = event.y - self.zoomy
        if dy < 0.0:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 1.15)
        else:
            self.ZOOM_ITEMS(self.zoomx0, self.zoomy0, 0.85)
        self.lasty = self.lasty + dy
        self.zoomy = event.y

    def mousePanStart(self, event):
        self.panx = event.x
        self.pany = event.y

    def mousePan(self, event):
        all = self.PreviewCanvas.find_all()
        dx = event.x - self.panx
        dy = event.y - self.pany
        for i in all:
            self.PreviewCanvas.move(i, dx, dy)
        self.lastx = self.lastx + dx
        self.lasty = self.lasty + dy
        self.panx = event.x
        self.pany = event.y

    def Recalculate_Click(self, event):
        self.DoIt()

    def Settings_ReLoad_Click(self, event, arg1="", arg2=""):
        config = self.config
        win_id = self.grab_current()
        if config.input_type.get() == "text":
            self.Read_font_file()
        else:
            self.Read_image_file()
        self.DoIt()
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    def VCARVE_Recalculate_Click(self):
        win_id = self.grab_current()
        self.V_Carve_Calc_Click()
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def CLEAN_Recalculate_Click(self):
        win_id = self.grab_current()
        if self.clean_segment == []:
            mess = "Calculate V-Carve must be executed\n"
            mess = mess + "prior to Calculating Cleanup"
            message.message_box("Cleanup Info", mess)
        else:
            stop = self.Clean_Calc_Click("straight")
            if stop != 1:
                self.Clean_Calc_Click("v-bit")
            self.Plot_Data()

        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Write_Clean_Click(self):
        config = self.config
        win_id = self.grab_current()
        if (
            config.clean_P.get()
            + config.clean_X.get()
            + config.clean_Y.get()
            + config.v_clean_P.get()
            + config.v_clean_Y.get()
            + config.v_clean_X.get()
        ) != 0:
            if self.clean_coords_sort == []:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message.message_box("Cleanup Info", mess)
            else:
                self.menu_File_Save_clean_G_Code_File("straight")
        else:
            mess = "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no V Cleanup paths were found)"
            message.message_box("Cleanup Info", mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    def Write_V_Clean_Click(self):
        config = self.config
        win_id = self.grab_current()
        if (
            config.clean_P.get()
            + config.clean_X.get()
            + config.clean_Y.get()
            + config.v_clean_P.get()
            + config.v_clean_Y.get()
            + config.v_clean_X.get()
        ) != 0:
            if self.v_clean_coords_sort == []:
                mess = "Calculate Cleanup must be executed\n"
                mess = mess + "prior to saving V Cleanup G-Code\n"
                mess = mess + "(Or no Cleanup paths were found)"
                message.message_box("Cleanup Info", mess)
            else:
                self.menu_File_Save_clean_G_Code_File("v-bit")
        else:
            mess = "Cleanup Operation must be set and\n"
            mess = mess + "Calculate Cleanup must be executed\n"
            mess = mess + "prior to Saving Cleanup G-Code\n"
            mess = mess + "(Or no Cleanup paths were found)"
            message.message_box("Cleanup Info", mess)
        try:
            win_id.withdraw()
            win_id.deiconify()
            win_id.grab_set()
        except:
            pass

    ######################

    def Close_Current_Window_Click(self, event=None):
        current_name = event.widget.winfo_parent()
        win_id = event.widget.nametowidget(current_name)
        win_id.destroy()

    def Stop_Click(self, event):
        self.STOP_CALC = True

    def calc_r_inlay_top(self, bit):
        inlay_depth = self.calc_r_inlay_depth()
        r_inlay_top = tan(bit.half_angle) * inlay_depth
        return r_inlay_top

    def calc_r_inlay_depth(self):
        config = self.config
        try:
            inlay_depth = float(config.maxcut.get())
        except:
            inlay_depth = 0.0
        return inlay_depth

    # Left Column #
    #############################
    def Entry_Yscale_Check(self):
        config = self.config
        try:
            value = float(config.YSCALE.get())
            if value <= 0.0:
                self.statusMessage.set(" Height should be greater than 0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Yscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check())

    #############################
    def Entry_Xscale_Check(self):
        config = self.config
        try:
            value = float(config.XSCALE.get())
            if value <= 0.0:
                self.statusMessage.set(" Width should be greater than 0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Xscale_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check())

    #############################
    def Entry_Sthick_Check(self):
        config = self.config
        try:
            value = float(config.STHICK.get())
            if value < 0.0:
                self.statusMessage.set(" Thickness should be greater than 0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Sthick_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check())

    #############################
    def Entry_Lspace_Check(self):
        config = self.config
        try:
            value = float(config.LSPACE.get())
            if value < 0.0:
                self.statusMessage.set(
                    " Line space should be greater than or equal to 0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Lspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check())

    #############################
    def Entry_Cspace_Check(self):
        config = self.config
        try:
            value = float(config.CSPACE.get())
            if value < 0.0:
                self.statusMessage.set(
                    " Character space should be greater than or equal to 0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Cspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check())

    #############################
    def Entry_Wspace_Check(self):
        config = self.config
        try:
            value = float(config.WSPACE.get())
            if value < 0.0:
                self.statusMessage.set(
                    " Word space should be greater than or equal to 0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Wspace_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check())

    #############################
    def Entry_Tangle_Check(self):
        config = self.config
        try:
            value = float(config.TANGLE.get())
            if value <= -360.0 or value >= 360.0:
                self.statusMessage.set(
                    " Angle should be between -360 and 360 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Tangle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check())

    #############################
    def Entry_Tradius_Check(self):
        config = self.config
        try:
            value = float(config.TRADIUS.get())
            if value < 0.0:
                self.statusMessage.set(
                    " Radius should be greater than or equal to 0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Tradius_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check())

    # End Left Column #

    # Right Column #
    #############################
    def Entry_Feed_Check(self):
        config = self.config
        try:
            value = float(config.FEED.get())
            if value <= 0.0:
                self.statusMessage.set(" Feed should be greater than 0.0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_Feed_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Feed, self.Entry_Feed_Check())

    #############################
    def Entry_Plunge_Check(self):
        config = self.config
        try:
            value = float(config.PLUNGE.get())
            if value < 0.0:
                self.statusMessage.set(
                    " Plunge rate should be greater than or equal to 0.0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_Plunge_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check())

    #############################
    def Entry_Zsafe_Check(self):
        config = self.config
        try:
            float(config.ZSAFE.get())
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_Zsafe_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check())

    #############################
    def Entry_Zcut_Check(self):
        config = self.config
        try:
            float(config.ZCUT.get())
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_Zcut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check())

    #############################
    # End Right Column #

    ######################################
    #    Settings Window Callbacks      #
    ######################################
    def Entry_Xoffset_Check(self):
        config = self.config
        try:
            float(config.xorigin.get())
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_Xoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check())

    #############################
    def Entry_Yoffset_Check(self):
        config = self.config
        try:
            float(config.yorigin.get())
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_Yoffset_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check())

    #############################
    def Entry_ArcAngle_Check(self):
        config = self.config
        try:
            value = float(config.segarc.get())
            if value <= 0.0:
                self.statusMessage.set(
                    " Arc Angle should be greater than zero."
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_ArcAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check())

    #############################
    def Entry_Accuracy_Check(self):
        config = self.config
        try:
            float(config.accuracy.get())
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Accuracy_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check())

    #############################
    def Entry_BoxGap_Check(self):
        config = self.config
        try:
            value = float(config.boxgap.get())
            if value <= 0.0:
                self.statusMessage.set(" Gap should be greater than zero.")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_BoxGap_Callback(self, varName, index, mode):
        config = self.config
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check())
        try:
            if not bool(config.plotbox.get()):
                self.Label_BoxGap.configure(state="disabled")
                self.Entry_BoxGap.configure(state="disabled")
                self.Label_BoxGap_u.configure(state="disabled")
            else:
                self.Label_BoxGap.configure(state="normal")
                self.Entry_BoxGap.configure(state="normal")
                self.Label_BoxGap_u.configure(state="normal")
        except:
            pass

    def Entry_Box_Callback(self, varName, index, mode):
        try:
            self.Entry_BoxGap_Callback(varName, index, mode)
        except:
            pass
        self.Recalc_RQD()

    #############################
    def Fontdir_Click(self, event):
        config = self.config
        win_id = self.grab_current()
        newfontdir = askdirectory(mustexist=1, initialdir=config.fontdir.get())
        if newfontdir != "" and newfontdir != ():
            if type(newfontdir) is not str:
                newfontdir = newfontdir.encode("utf-8")
            config.fontdir.set(newfontdir)
        try:
            win_id.withdraw()
            win_id.deiconify()
        except:
            pass

    ######################################
    #    V-Carve Settings Callbacks     #
    ######################################
    def Entry_Vbitangle_Check(self):
        config = self.config
        try:
            value = float(config.v_bit_angle.get())
            if value < 0.0 or value > 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_Vbitangle_Callback(self, varName, index, mode):
        config = self.config
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check())
        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )
        calc_depth_limit(config, bit)

    #############################
    def Entry_Vbitdia_Check(self):
        config = self.config
        try:
            value = float(config.v_bit_dia.get())
            if value <= 0.0:
                self.statusMessage.set(" Diameter should be greater than 0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Vbitdia_Callback(self, varName, index, mode):
        config = self.config
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check())
        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )
        calc_depth_limit(config, bit)

    #############################
    def Entry_VDepthLimit_Check(self):
        config = self.config
        try:
            value = float(config.v_depth_lim.get())
            if value > 0.0:
                self.statusMessage.set(" Depth should be less than 0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_VDepthLimit_Callback(self, varName, index, mode):
        config = self.config
        self.entry_set(self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check())
        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )
        calc_depth_limit(config, bit)

    #############################
    def Entry_InsideAngle_Check(self):
        config = self.config
        try:
            value = float(config.v_drv_crner.get())
            if value <= 0.0 or value >= 180.0:
                self.statusMessage.set(" Angle should be between 0 and 180 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_InsideAngle_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_InsideAngle, self.Entry_InsideAngle_Check())

    #############################
    def Entry_OutsideAngle_Check(self):
        config = self.config
        try:
            value = float(config.v_stp_crner.get())
            if value <= 180.0 or value >= 360.0:
                self.statusMessage.set(" Angle should be between 180 and 360 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_OutsideAngle_Callback(self, varName, index, mode):
        self.entry_set(
            self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check()
        )

    #############################
    def Entry_StepSize_Check(self):
        config = self.config
        try:
            value = float(config.v_step_len.get())
            if value <= 0.0:
                self.statusMessage.set(" Step size should be greater than 0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_StepSize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check())

    #############################
    def Entry_Allowance_Check(self):
        config = self.config
        try:
            value = float(config.allowance.get())
            if value > 0.0:
                self.statusMessage.set(
                    " Allowance should be less than or equal to 0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_Allowance_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_Allowance, self.Entry_Allowance_Check())

    #############################
    def Entry_Prismatic_Callback(self, varName, index, mode):
        config = self.config
        try:
            if not bool(config.inlay.get()):
                self.Label_Allowance.configure(state="disabled")
                self.Entry_Allowance.configure(state="disabled")
                self.Label_Allowance_u.configure(state="disabled")
            else:
                self.Label_Allowance.configure(state="normal")
                self.Entry_Allowance.configure(state="normal")
                self.Label_Allowance_u.configure(state="normal")
        except:
            pass
        self.Recalc_RQD()

    #############################
    def Entry_v_max_cut_Check(self):
        config = self.config
        try:
            value = float(config.v_max_cut.get())
            if value >= 0.0:
                self.statusMessage.set(
                    " Max Depth per Pass should be less than 0.0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid_no_recalc_required

    def Entry_v_max_cut_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check())

    #############################
    def Entry_v_rough_stk_Check(self):
        config = self.config
        try:
            value = float(config.v_rough_stk.get())
            if value < 0.0:
                self.statusMessage.set(
                    " Finish Pass Stock should be positive or zero "
                    "(Zero disables multi-pass)"
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        try:
            if float(config.v_rough_stk.get()) == 0.0:
                self.Label_v_max_cut.configure(state="disabled")
                self.Label_v_max_cut_u.configure(state="disabled")
                self.Entry_v_max_cut.configure(state="disabled")
            else:
                self.Label_v_max_cut.configure(state="normal")
                self.Label_v_max_cut_u.configure(state="normal")
                self.Entry_v_max_cut.configure(state="normal")
        except:
            pass
        return NumberCheck.is_valid_no_recalc_required

    def Entry_v_rough_stk_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check())

    #############################
    def Entry_V_CLEAN_Check(self):
        config = self.config
        try:
            value = float(config.clean_v.get())
            if value < 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_V_CLEAN_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check())

    #############################
    def Entry_CLEAN_DIA_Check(self):
        config = self.config
        try:
            value = float(config.clean_dia.get())
            if value <= 0.0:
                self.statusMessage.set(" Angle should be greater than 0.0 ")
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_CLEAN_DIA_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check())
        self.clean_coords = []
        self.v_clean_coords = []

    #############################
    def Entry_STEP_OVER_Check(self):
        config = self.config
        try:
            value = float(config.clean_step.get())
            if value <= 0.0:
                self.statusMessage.set(
                    " Step Over should be between 0% and 100% "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_STEP_OVER_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check())

    #############################

    def Entry_Bit_Shape_Check(self):
        config = self.config
        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )
        calc_depth_limit(config, bit)

        try:
            if bit.shape == "VBIT":
                self.Label_Vbitangle.configure(state="normal")
                self.Label_Vbitangle_u.configure(state="normal")
                self.Entry_Vbitangle.configure(state="normal")
                self.Label_photo.configure(state="normal")
                self.Label_Vbitdia.configure(text="V-Bit Diameter")
            elif bit.shape == "BALL":
                self.Label_Vbitangle.configure(state="disabled")
                self.Label_Vbitangle_u.configure(state="disabled")
                self.Entry_Vbitangle.configure(state="disabled")
                self.Label_photo.configure(state="disabled")
                self.Label_Vbitdia.configure(text="Ball Nose Bit Diameter")
            elif bit.shape == "FLAT":
                self.Label_Vbitangle.configure(state="disabled")
                self.Label_Vbitangle_u.configure(state="disabled")
                self.Entry_Vbitangle.configure(state="disabled")
                self.Label_photo.configure(state="disabled")
                self.Label_Vbitdia.configure(text="Straight Bit Diameter")
            else:
                pass
        except:
            pass

    def Entry_Bit_Shape_var_Callback(self, varName, index, mode):
        self.Entry_Bit_Shape_Check()

    ######################################
    # Bitmap Settings Window Callbacks  #
    ######################################
    def Entry_BMPturdsize_Check(self):
        config = self.config
        try:
            value = float(config.bmp_turdsize.get())
            if value < 1.0:
                self.statusMessage.set(
                    " Step size should be greater or equal to 1.0 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_BMPturdsize_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check())

    #############################
    def Entry_BMPalphamax_Check(self):
        config = self.config
        try:
            value = float(config.bmp_alphamax.get())
            if value < 0.0 or value > 4.0 / 3.0:
                self.statusMessage.set(
                    " Alpha Max should be between 0.0 and 1.333 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_BMPalphamax_Callback(self, varName, index, mode):
        self.entry_set(self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check())

    #############################
    def Entry_BMPoptTolerance_Check(self):
        config = self.config
        try:
            value = float(config.bmp_opttolerance.get())
            if value < 0.0:
                self.statusMessage.set(
                    " Alpha Max should be between 0.0 and 1.333 "
                )
                return NumberCheck.is_invalid
        except:
            return NumberCheck.is_not_a_number
        return NumberCheck.is_valid

    def Entry_BMPoptTolerance_Callback(self, varName, index, mode):
        self.entry_set(
            self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check()
        )

    #############################

    ##########################################################################
    ##########################################################################
    def Check_All_Variables(self):
        config = self.config
        if config.batch.get():
            return 0
        MAIN_error_cnt = (
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), 2)
            + self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), 2)
            + self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), 2)
            + self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), 2)
            + self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), 2)
            + self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), 2)
            + self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), 2)
            + self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), 2)
            + self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), 2)
            + self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), 2)
            + self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), 2)
            + self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), 2)
        )

        GEN_error_cnt = (
            self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), 2)
            + self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), 2)
            + self.entry_set(
                self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2
            )
            + self.entry_set(
                self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2
            )
            + self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)
            + self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), 2)
            + self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), 2)
            + self.entry_set(
                self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2
            )
            + self.entry_set(
                self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2
            )
            + self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)
        )

        VCARVE_error_cnt = (
            self.entry_set(
                self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), 2
            )
            + self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), 2)
            + self.entry_set(
                self.Entry_InsideAngle, self.Entry_InsideAngle_Check(), 2
            )
            + self.entry_set(
                self.Entry_OutsideAngle, self.Entry_OutsideAngle_Check(), 2
            )
            + self.entry_set(
                self.Entry_StepSize, self.Entry_StepSize_Check(), 2
            )
            + self.entry_set(
                self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), 2
            )
            + self.entry_set(
                self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), 2
            )
            + self.entry_set(
                self.Entry_Allowance, self.Entry_Allowance_Check(), 2
            )
            + self.entry_set(
                self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), 2
            )
        )

        PBM_error_cnt = (
            self.entry_set(
                self.Entry_BMPoptTolerance,
                self.Entry_BMPoptTolerance_Check(),
                2,
            )
            + self.entry_set(
                self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), 2
            )
            + self.entry_set(
                self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), 2
            )
        )

        ERROR_cnt = (
            MAIN_error_cnt + GEN_error_cnt + VCARVE_error_cnt + PBM_error_cnt
        )

        if ERROR_cnt > 0:
            self.statusbar.configure(bg="red")
        if PBM_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in PBM "
                "Settings Window "
            )
        if VCARVE_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in V-Carve "
                "Settings Window "
            )
        if GEN_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in General "
                "Settings Window "
            )
        if MAIN_error_cnt > 0:
            self.statusMessage.set(
                " Entry Error Detected: Check Entry Values in Main Window "
            )

        return ERROR_cnt

    ##########################################################################
    ##########################################################################
    def V_Carve_Calc_Click(self):
        config = self.config
        if self.Check_All_Variables() > 0:
            return

        vcalc_status = Toplevel(width=525, height=60)
        # Use grab_set to prevent user input in the main window during
        # calculations
        vcalc_status.grab_set()

        self.statusbar2 = Label(
            vcalc_status,
            textvariable=self.statusMessage,
            bd=1,
            relief=FLAT,
            height=1,
            anchor=W,
        )
        self.statusbar2.place(x=130 + 12 + 12, y=6, width=350, height=30)
        self.statusMessage.set("Starting Calculation")
        self.statusbar.configure(bg="yellow")

        self.stop_button = Button(vcalc_status, text="Stop Calculation")
        self.stop_button.place(x=12, y=17, width=130, height=30)
        self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

        self.Checkbutton_v_pplot = Checkbutton(
            vcalc_status, text="Plot During V-Carve Calculation", anchor=W
        )
        self.Checkbutton_v_pplot.place(
            x=130 + 12 + 12, y=34, width=300, height=23
        )
        self.Checkbutton_v_pplot.configure(variable=config.v_pplot.TK)

        vcalc_status.resizable(0, 0)
        vcalc_status.title("Executing V-Carve")
        vcalc_status.iconname("F-Engrave")

        try:
            vcalc_status.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                vcalc_status.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

        self.V_Carve_It()
        self.menu_View_Refresh()
        vcalc_status.grab_release()
        try:
            vcalc_status.destroy()
        except:
            pass

    ##########################################################################
    ##########################################################################
    def Clean_Calc_Click(self, bit_type="straight"):
        config = self.config
        if self.Check_All_Variables() > 0:
            return 1

        if self.clean_coords == []:
            vcalc_status = Toplevel(width=525, height=50)
            # Use grab_set to prevent user input in the main window during
            # calculations
            vcalc_status.grab_set()

            self.statusbar2 = Label(
                vcalc_status,
                textvariable=self.statusMessage,
                bd=1,
                relief=FLAT,
                height=1,
            )
            self.statusbar2.place(x=130 + 12 + 12, y=12, width=350, height=30)
            self.statusMessage.set("Starting Clean Calculation")
            self.statusbar.configure(bg="yellow")

            self.stop_button = Button(vcalc_status, text="Stop Calculation")
            self.stop_button.place(x=12, y=12, width=130, height=30)
            self.stop_button.bind("<ButtonRelease-1>", self.Stop_Click)

            vcalc_status.resizable(0, 0)
            vcalc_status.title("Executing Clean Area Calculation")
            vcalc_status.iconname("F-Engrave")

            try:
                vcalc_status.iconbitmap(bitmap="@emblem64")
            except:
                try:  # Attempt to create temporary icon bitmap file
                    temp_icon("f_engrave_icon")
                    vcalc_status.iconbitmap("@f_engrave_icon")
                    os.remove("f_engrave_icon")
                except:
                    pass

            clean_cut = 1
            self.V_Carve_It(clean_cut)
            vcalc_status.grab_release()
            try:
                vcalc_status.destroy()
            except:
                pass

        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )
        bit_radius = calc_vbit_dia(config, bit) / 2.0

        self.Clean_Path_Calc(bit_radius, bit_type)

        if self.clean_coords == []:
            return 1
        else:
            return 0

    def Entry_recalc_var_Callback(self, varName, index, mode):
        self.Recalc_RQD()

    def Entry_units_var_Callback(self):
        config = self.config
        if (config.units.get() == "in") and (config.funits.get() == "mm/min"):
            self.Scale_Linear_Inputs(1 / 25.4)
            config.funits.set("in/min")
        elif (config.units.get() == "mm") and (config.funits.get() == "in/min"):
            self.Scale_Linear_Inputs(25.4)
            config.funits.set("mm/min")
        self.Recalc_RQD()

    def Scale_Linear_Inputs(self, factor=1.0):
        config = self.config
        try:
            config.YSCALE.set("%.3g" % (float(config.YSCALE.get()) * factor))
            config.TRADIUS.set("%.3g" % (float(config.TRADIUS.get()) * factor))
            config.ZSAFE.set("%.3g" % (float(config.ZSAFE.get()) * factor))
            config.ZCUT.set("%.3g" % (float(config.ZCUT.get()) * factor))
            config.STHICK.set("%.3g" % (float(config.STHICK.get()) * factor))
            config.FEED.set("%.3g" % (float(config.FEED.get()) * factor))
            config.PLUNGE.set("%.3g" % (float(config.PLUNGE.get()) * factor))
            config.boxgap.set("%.3g" % (float(config.boxgap.get()) * factor))
            config.v_bit_dia.set("%.3g" % (float(config.v_bit_dia.get()) * factor))
            config.v_depth_lim.set(
                "%.3g" % (float(config.v_depth_lim.get()) * factor)
            )
            config.v_step_len.set(
                "%.3g" % (float(config.v_step_len.get()) * factor)
            )
            config.allowance.set("%.3g" % (float(config.allowance.get()) * factor))
            config.v_max_cut.set("%.3g" % (float(config.v_max_cut.get()) * factor))
            config.v_rough_stk.set(
                "%.3g" % (float(config.v_rough_stk.get()) * factor)
            )
            config.xorigin.set("%.3g" % (float(config.xorigin.get()) * factor))
            config.yorigin.set("%.3g" % (float(config.yorigin.get()) * factor))
            config.accuracy.set("%.3g" % (float(config.accuracy.get()) * factor))
            config.clean_v.set("%.3g" % (float(config.clean_v.get()) * factor))
            config.clean_dia.set("%.3g" % (float(config.clean_dia.get()) * factor))
        except:
            pass

    def useIMGsize_var_Callback(self):
        config = self.config
        if config.input_type.get() != "text":
            self.Read_image_file()
        try:
            ymx = max(self.font[key].get_ymax() for key in self.font)
            ymn = min(self.font[key].get_ymin() for key in self.font)
            image_height = ymx - ymn
        except:
            if config.units.get() == "in":
                image_height = 2
            else:
                image_height = 50
        if config.useIMGsize.get():
            config.YSCALE.set(
                "%.3g" % (100 * float(config.YSCALE.get()) / image_height)
            )
        else:
            config.YSCALE.set(
                "%.3g" % (float(config.YSCALE.get()) / 100 * image_height)
            )

        self.menu_View_Refresh()
        self.Recalc_RQD()

    def Listbox_1_Click(self, event):
        config = self.config
        labelL = []
        for i in self.Listbox_1.curselection():
            labelL.append(self.Listbox_1.get(i))
        try:
            config.fontfile.set(labelL[0])
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Listbox_Key_Up(self, event):
        config = self.config
        try:
            select_new = int(self.Listbox_1.curselection()[0]) - 1
        except:
            select_new = self.Listbox_1.size() - 2
        self.Listbox_1.selection_clear(0, END)
        self.Listbox_1.select_set(select_new)
        try:
            config.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Listbox_Key_Down(self, event):
        config = self.config
        try:
            select_new = int(self.Listbox_1.curselection()[0]) + 1
        except:
            select_new = 1
        self.Listbox_1.selection_clear(0, END)
        self.Listbox_1.select_set(select_new)
        try:
            config.fontfile.set(self.Listbox_1.get(select_new))
        except:
            return
        self.Read_font_file()
        self.DoIt()

    def Entry_fontdir_Callback(self, varName, index, mode):
        config = self.config
        self.Listbox_1.delete(0, END)
        self.Listbox_1.configure(bg=self.NormalColor)
        for name in font.available_font_files(config.fontdir.get()):
            self.Listbox_1.insert(END, name)

        if len(config.fontfile.get()) < 4:
            try:
                config.fontfile.set(self.Listbox_1.get(0))
            except:
                config.fontfile.set(" ")
        self.Read_font_file()
        self.Recalc_RQD()

    # End General Settings Callbacks

    def menu_File_Open_G_Code_File(self):
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR
        fileselect = askopenfilename(
            filetypes=[
                ("F-Engrave G-code Files", "*.ngc"),
                ("All Files", "*"),
            ],
            initialdir=init_dir,
        )

        if fileselect != "" and fileselect != ():
            self.Open_G_Code_File(fileselect)

    def menu_File_Open_DXF_File(self):
        init_dir = os.path.dirname(self.IMAGE_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        if self.POTRACE_AVAIL:
            if PIL:
                fileselect = askopenfilename(
                    filetypes=[
                        (
                            "DXF/Image Files",
                            ("*.dxf", "*.png", "*.bmp", "*.tif"),
                        ),
                        ("DXF Files", "*.dxf"),
                        (
                            "Bitmap Files",
                            ("*.bmp", "*.pbm", "*.ppm", "*.pgm", "*.pnm"),
                        ),
                        (
                            "Slower Image Files",
                            ("*.jpg", "*.png", "*.gif", "*.tif"),
                        ),
                        ("All Files", "*"),
                    ],
                    initialdir=init_dir,
                )
            else:
                fileselect = askopenfilename(
                    filetypes=[
                        (
                            "DXF/Bitmap Files",
                            (
                                "*.dxf",
                                "*.bmp",
                                "*.pbm",
                                "*.ppm",
                                "*.pgm",
                                "*.pnm",
                            ),
                        ),
                        ("DXF Files", "*.dxf"),
                        (
                            "Bitmap Files",
                            ("*.bmp", "*.pbm", "*.ppm", "*.pgm", "*.pnm"),
                        ),
                        ("All Files", "*"),
                    ],
                    initialdir=init_dir,
                )

        else:
            fileselect = askopenfilename(
                filetypes=[("DXF Files", "*.dxf"), ("All Files", "*")],
                initialdir=init_dir,
            )

        if fileselect != "" and fileselect != ():
            self.IMAGE_FILE = fileselect
            self.Read_image_file()
            self.DoIt()

    def Open_G_Code_File(self, filename):
        config = self.config
        self.delay_calc = 1
        boxsize = "0"
        try:
            fin = open(filename, "r")
        except:
            message.fmessage("Unable to open file: %s" % (filename))
            return
        text_codes = []
        ident = "fengrave_set"
        for line in fin:
            if ident in line:

                input_code = line.split(ident)[1].split()[0]

                if "TCODE" in input_code:
                    code_list = line[line.find("TCODE") :].split()
                    for char in code_list:
                        try:
                            text_codes.append(int(char))
                        except:
                            pass
                # BOOL
                elif "show_axis" in input_code:
                    config.show_axis.set(
                        line[line.find("show_axis") :].split()[1]
                    )
                elif "show_box" in input_code:
                    config.show_box.set(
                        line[line.find("show_box") :].split()[1]
                    )
                elif "show_thick" in input_code:
                    config.show_thick.set(
                        line[line.find("show_thick") :].split()[1]
                    )
                elif "flip" in input_code:
                    config.flip.set(
                        line[line.find("flip") :].split()[1]
                    )
                elif "mirror" in input_code:
                    config.mirror.set(
                        line[line.find("mirror") :].split()[1]
                    )
                elif "outer" in input_code:
                    config.outer.set(
                        line[line.find("outer") :].split()[1]
                    )
                elif "upper" in input_code:
                    config.upper.set(
                        line[line.find("upper") :].split()[1]
                    )
                elif "v_flop" in input_code:
                    config.v_flop.set(
                        line[line.find("v_flop") :].split()[1]
                    )
                elif "v_pplot" in input_code:
                    config.v_pplot.set(
                        line[line.find("v_pplot") :].split()[1]
                    )
                elif "inlay" in input_code:
                    config.inlay.set(
                        line[line.find("inlay") :].split()[1]
                    )
                elif "bmp_long" in input_code:
                    config.bmp_longcurve.set(
                        line[line.find("bmp_long") :].split()[1]
                    )
                elif "ext_char" in input_code:
                    config.ext_char.set(
                        line[line.find("ext_char") :].split()[1]
                    )
                elif "useIMGsize" in input_code:
                    config.useIMGsize.set(
                        line[line.find("useIMGsize") :].split()[1]
                    )
                elif "no_comments" in input_code:
                    config.no_comments.set(
                        line[line.find("no_comments") :].split()[1]
                    )
                elif "show_v_path" in input_code:
                    config.show_v_path.set(
                        line[line.find("show_v_path") :].split()[1]
                    )
                elif "show_v_area" in input_code:
                    config.show_v_area.set(
                        line[line.find("show_v_area") :].split()[1]
                    )

                elif "plotbox" in input_code:
                    if line[line.find("plotbox") :].split()[1] == "box":
                        config.plotbox.set(True)
                    elif line[line.find("plotbox") :].split()[1] == "no_box":
                        config.plotbox.set(False)
                    else:
                        config.plotbox.set(
                            line[line.find("plotbox") :].split()[1]
                        )

                # STRING
                elif "fontdir" in input_code:
                    config.fontdir.set(
                        line[line.find("fontdir") :].split("\042")[1]
                    )
                elif "gpre" in input_code:
                    gpre_tmp = ""
                    for word in line[line.find("gpre") :].split():
                        if word != ")" and word != "gpre":
                            gpre_tmp = gpre_tmp + word + " "
                    config.gpre.set(gpre_tmp)
                elif "gpost" in input_code:
                    gpost_tmp = ""
                    for word in line[line.find("gpost") :].split():
                        if word != ")" and word != "gpost":
                            gpost_tmp = gpost_tmp + word + " "
                    config.gpost.set(gpost_tmp)

                # STRING.set()
                elif "arc_fit" in input_code:
                    config.arc_fit.set(line[line.find("arc_fit") :].split()[1])
                elif "YSCALE" in input_code:
                    config.YSCALE.set(line[line.find("YSCALE") :].split()[1])
                elif "XSCALE" in input_code:
                    config.XSCALE.set(line[line.find("XSCALE") :].split()[1])
                elif "LSPACE" in input_code:
                    config.LSPACE.set(line[line.find("LSPACE") :].split()[1])
                elif "CSPACE" in input_code:
                    config.CSPACE.set(line[line.find("CSPACE") :].split()[1])
                elif "WSPACE" in input_code:
                    config.WSPACE.set(line[line.find("WSPACE") :].split()[1])
                elif "TANGLE" in input_code:
                    config.TANGLE.set(line[line.find("TANGLE") :].split()[1])
                elif "TRADIUS" in input_code:
                    config.TRADIUS.set(line[line.find("TRADIUS") :].split()[1])
                elif "ZSAFE" in input_code:
                    config.ZSAFE.set(line[line.find("ZSAFE") :].split()[1])
                elif "ZCUT" in input_code:
                    config.ZCUT.set(line[line.find("ZCUT") :].split()[1])
                elif "STHICK" in input_code:
                    config.STHICK.set(line[line.find("STHICK") :].split()[1])

                elif "xorigin" in input_code:
                    config.xorigin.set(line[line.find("xorigin") :].split()[1])
                elif "yorigin" in input_code:
                    config.yorigin.set(line[line.find("yorigin") :].split()[1])
                elif "segarc" in input_code:
                    config.segarc.set(line[line.find("segarc") :].split()[1])
                elif "accuracy" in input_code:
                    config.accuracy.set(line[line.find("accuracy") :].split()[1])

                elif "origin" in input_code:
                    config.origin.set(line[line.find("origin") :].split()[1])
                elif "justify" in input_code:
                    config.justify.set(line[line.find("justify") :].split()[1])
                elif "units" in input_code:
                    config.units.set(line[line.find("units") :].split()[1])
                elif "FEED" in input_code:
                    config.FEED.set(line[line.find("FEED") :].split()[1])
                elif "PLUNGE" in input_code:
                    config.PLUNGE.set(line[line.find("PLUNGE") :].split()[1])
                elif "fontfile" in input_code:
                    config.fontfile.set(
                        line[line.find("fontfile") :].split("\042")[1]
                    )
                elif "H_CALC" in input_code:
                    config.H_CALC.set(line[line.find("H_CALC") :].split()[1])
                elif "boxgap" in input_code:
                    config.boxgap.set(line[line.find("boxgap") :].split()[1])
                elif "boxsize" in input_code:
                    boxsize = line[line.find("boxsize") :].split()[1]
                elif "cut_type" in input_code:
                    config.cut_type.set(line[line.find("cut_type") :].split()[1])
                elif "bit_shape" in input_code:
                    config.bit_shape.set(
                        line[line.find("bit_shape") :].split()[1]
                    )
                elif "v_bit_angle" in input_code:
                    config.v_bit_angle.set(
                        line[line.find("v_bit_angle") :].split()[1]
                    )
                elif "v_bit_dia" in input_code:
                    config.v_bit_dia.set(
                        line[line.find("v_bit_dia") :].split()[1]
                    )
                elif "v_drv_crner" in input_code:
                    config.v_drv_crner.set(
                        line[line.find("v_drv_crner") :].split()[1]
                    )
                elif "v_stp_crner" in input_code:
                    config.v_stp_crner.set(
                        line[line.find("v_stp_crner") :].split()[1]
                    )
                elif "v_step_len" in input_code:
                    config.v_step_len.set(
                        line[line.find("v_step_len") :].split()[1]
                    )
                elif "allowance" in input_code:
                    config.allowance.set(
                        line[line.find("allowance") :].split()[1]
                    )
                elif "v_max_cut" in input_code:
                    config.v_max_cut.set(
                        line[line.find("v_max_cut") :].split()[1]
                    )
                elif "v_rough_stk" in input_code:
                    config.v_rough_stk.set(
                        line[line.find("v_rough_stk") :].split()[1]
                    )
                elif "var_dis" in input_code:
                    config.var_dis.set(
                        line[line.find("var_dis") :].split()[1]
                    )
                elif "v_depth_lim" in input_code:
                    config.v_depth_lim.set(
                        line[line.find("v_depth_lim") :].split()[1]
                    )
                elif "v_check_all" in input_code:
                    config.v_check_all.set(
                        line[line.find("v_check_all") :].split()[1]
                    )
                elif "bmp_turnp" in input_code:
                    config.bmp_turnpol.set(
                        line[line.find("bmp_turnp") :].split()[1]
                    )
                elif "bmp_turds" in input_code:
                    config.bmp_turdsize.set(
                        line[line.find("bmp_turds") :].split()[1]
                    )
                elif "bmp_alpha" in input_code:
                    config.bmp_alphamax.set(
                        line[line.find("bmp_alpha") :].split()[1]
                    )
                elif "bmp_optto" in input_code:
                    config.bmp_opttolerance.set(
                        line[line.find("bmp_optto") :].split()[1]
                    )
                elif "imagefile" in input_code:
                    self.IMAGE_FILE = line[line.find("imagefile") :].split(
                        "\042"
                    )[1]
                elif "input_type" in input_code:
                    config.input_type.set(
                        line[line.find("input_type") :].split()[1]
                    )
                elif "clean_dia" in input_code:
                    config.clean_dia.set(
                        line[line.find("clean_dia") :].split()[1]
                    )
                elif "clean_step" in input_code:
                    config.clean_step.set(
                        line[line.find("clean_step") :].split()[1]
                    )
                elif "clean_v" in input_code:
                    config.clean_v.set(line[line.find("clean_v") :].split()[1])
                elif "clean_paths" in input_code:
                    clean_paths = line[line.find("clean_paths") :].split()[1]
                    clean_split = [float(n) for n in clean_paths.split(",")]
                    if len(clean_split) > 5:
                        config.clean_P.set(bool(clean_split[0]))
                        config.clean_X.set(bool(clean_split[1]))
                        config.clean_Y.set(bool(clean_split[2]))
                        config.v_clean_P.set(bool(clean_split[3]))
                        config.v_clean_Y.set(bool(clean_split[4]))
                        config.v_clean_X.set(bool(clean_split[5]))
                elif "NGC_DIR" in input_code:
                    NGC_DIR = line[line.find("NGC_DIR") :].split("\042")[1]
                    self.NGC_FILE = NGC_DIR + "/None"

        fin.close()

        file_full = config.fontdir.get() + "/" + config.fontfile.get()
        fileName, fileExtension = os.path.splitext(file_full)
        TYPE = fileExtension.upper()

        if TYPE != ".CXF" and TYPE != ".TTF" and TYPE != "":
            if os.path.isfile(file_full):
                config.input_type.set("image")

        if boxsize != "0":
            config.boxgap.set(float(boxsize) * float(config.STHICK.get()))

        if config.arc_fit.get() == "0":
            config.arc_fit.set("none")
        elif config.arc_fit.get() == "1":
            config.arc_fit.set("center")

        if (
            config.arc_fit.get() != "none"
            and config.arc_fit.get() != "center"
            and config.arc_fit.get() != "radius"
        ):
            config.arc_fit.set("center")

        if text_codes != []:
            try:
                self.Input.delete(1.0, END)
                for Ch in text_codes:
                    try:
                        self.Input.insert(END, "%c" % (unichr(int(Ch))))
                    except:
                        self.Input.insert(END, "%c" % (chr(int(Ch))))
            except:
                self.default_text = ""
                for Ch in text_codes:
                    try:
                        self.default_text = self.default_text + "%c" % (
                            unichr(int(Ch))
                        )
                    except:
                        self.default_text = self.default_text + "%c" % (
                            chr(int(Ch))
                        )

        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )

        if config.units.get() == "in":
            config.funits.set("in/min")
        else:
            config.units.set("mm")
            config.funits.set("mm/min")

        calc_depth_limit(config, bit)

        self.delay_calc = 0
        if self.initComplete == 1:
            self.NGC_FILE = filename
            self.menu_Mode_Change()

    def menu_File_Save_Settings_File(self):
        config = self.config
        gcode = self.WriteGCode(config_file=True)
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)

        if config.input_type.get() == "image":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(
            defaultextension=".txt",
            filetypes=[("Settings File", "*.txt"), ("All Files", "*")],
            initialdir=init_dir,
            initialfile=init_file,
        )

        if filename != "" and filename != ():
            try:
                fout = open(filename, "w")
            except:
                self.statusMessage.set(
                    "Unable to open file for writing: %s" % (filename)
                )
                self.statusbar.configure(bg="red")
                return
            for line in gcode:
                try:
                    fout.write(line + "\n")
                except:
                    fout.write("(skipping line)\n")
            fout.close()
            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg="white")

    def menu_File_Save_G_Code_File(self):
        config = self.config
        if self.Check_All_Variables() > 0:
            return

        if self.vcoords == [] and config.cut_type.get() == "v-carve":
            mess = "V-carve path data does not exist.  "
            mess = mess + "Only settings will be saved.\n\n"
            mess = mess + "To generate V-Carve path data Click on the"
            mess = mess + '"Calculate V-Carve" button on the main window.'
            if not message.message_ask_ok_cancel("Continue", mess):
                return

        gcode = self.WriteGCode()
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)

        if config.input_type.get() == "image":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(
            defaultextension=".ngc",
            filetypes=[
                ("G-Code File", "*.ngc"),
                ("TAP File", "*.tap"),
                ("All Files", "*"),
            ],
            initialdir=init_dir,
            initialfile=init_file,
        )

        if filename != "" and filename != ():
            self.NGC_FILE = filename
            try:
                fout = open(filename, "w")
            except:
                self.statusMessage.set(
                    "Unable to open file for writing: %s" % (filename)
                )
                self.statusbar.configure(bg="red")
                return
            for line in gcode:
                try:
                    fout.write(line + "\n")
                except:
                    fout.write("(skipping line)\n")
            fout.close()
            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg="white")

    def menu_File_Save_clean_G_Code_File(self, bit_type="straight"):
        config = self.config
        if self.Check_All_Variables() > 0:
            return

        gcode = self.WRITE_CLEAN_UP(bit_type)

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)

        if config.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
            fileName_tmp, fileExtension = os.path.splitext(init_file)
            init_file = fileName_tmp
        else:
            init_file = "text"

        if bit_type == "v-bit":
            init_file = init_file + "_v" + config.clean_name.get()
        else:
            init_file = init_file + config.clean_name.get()

        filename = asksaveasfilename(
            defaultextension=".ngc",
            filetypes=[
                ("G-Code File", "*.ngc"),
                ("TAP File", "*.tap"),
                ("All Files", "*"),
            ],
            initialdir=init_dir,
            initialfile=init_file,
        )

        if filename != "" and filename != ():
            try:
                fout = open(filename, "w")
            except:
                self.statusMessage.set(
                    "Unable to open file for writing: %s" % (filename)
                )
                self.statusbar.configure(bg="red")
                return
            for line in gcode:
                try:
                    fout.write(line + "\n")
                except:
                    fout.write("(skipping line)\n")
            fout.close()
            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg="white")

    def menu_File_Save_SVG_File(self):
        config = self.config
        svgcode = self.WriteSVG()

        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)
        if config.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(
            defaultextension=".svg",
            filetypes=[("SVG File", "*.svg"), ("All Files", "*")],
            initialdir=init_dir,
            initialfile=init_file,
        )

        if filename != "" and filename != ():
            try:
                fout = open(filename, "w")
            except:
                self.statusMessage.set(
                    "Unable to open file for writing: %s" % (filename)
                )
                self.statusbar.configure(bg="red")
                return
            for line in svgcode:
                try:
                    fout.write(line + "\n")
                except:
                    pass
            fout.close()

            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg="white")

    def menu_File_Save_DXF_File_close_loops(self):
        self.menu_File_Save_DXF_File(close_loops=True)

    def menu_File_Save_DXF_File(self, close_loops=False):
        config = self.config
        if close_loops:
            self.V_Carve_It(clean_flag=0, DXF_FLAG=close_loops)

        DXF_CODE = WriteDXF(self.coords)
        init_dir = os.path.dirname(self.NGC_FILE)
        if not os.path.isdir(init_dir):
            init_dir = self.HOME_DIR

        fileName, fileExtension = os.path.splitext(self.NGC_FILE)
        init_file = os.path.basename(fileName)
        if config.input_type.get() != "text":
            fileName, fileExtension = os.path.splitext(self.IMAGE_FILE)
            init_file = os.path.basename(fileName)
        else:
            init_file = "text"

        filename = asksaveasfilename(
            defaultextension=".dxf",
            filetypes=[("DXF File", "*.dxf"), ("All Files", "*")],
            initialdir=init_dir,
            initialfile=init_file,
        )

        if filename != "" and filename != ():
            try:
                fout = open(filename, "w")
            except:
                self.statusMessage.set(
                    "Unable to open file for writing: %s" % (filename)
                )
                self.statusbar.configure(bg="red")
                return
            for line in DXF_CODE:
                try:
                    fout.write(line + "\n")
                except:
                    pass
            fout.close()

            self.statusMessage.set("File Saved: %s" % (filename))
            self.statusbar.configure(bg="white")

    def menu_File_Quit(self):
        if message.message_ask_ok_cancel("Exit", "Exiting F-Engrave...."):
            self.Quit_Click(None)

    def menu_View_Refresh_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_View_Refresh(self):
        config = self.config
        if (
            (not config.batch.get())
            and (self.initComplete == 1)
            and (self.delay_calc != 1)
        ):
            dummy_event = Event()
            dummy_event.widget = self.master
            self.Master_Configure(dummy_event, 1)

    def menu_Mode_Change_Callback(self, varName, index, mode):
        self.menu_View_Refresh()

    def menu_Mode_Change(self):
        config = self.config
        self.delay_calc = 1
        dummy_event = Event()
        dummy_event.widget = self.master
        self.Master_Configure(dummy_event, 1)
        self.delay_calc = 0
        if config.input_type.get() == "text":
            self.Read_font_file()
        else:
            self.Read_image_file()

        self.DoIt()

    def menu_View_Recalculate(self):
        self.DoIt()

    def menu_Help_About(self):
        about = "F-Engrave Version %s\n\n" % (version)
        about = about + "By Scorch.\n"
        about = about + "\163\143\157\162\143\150\100\163\143\157\162"
        about = about + "\143\150\167\157\162\153\163\056\143\157\155\n"
        about = about + "https://www.scorchworks.com/\n\n"
        try:
            python_version = "%d.%d.%d" % (
                sys.version_info.major,
                sys.version_info.minor,
                sys.version_info.micro,
            )
        except:
            python_version = ""
        about = (
            about
            + "Python "
            + python_version
            + " (%d bit)" % (struct.calcsize("P") * 8)
        )
        message.message_box("About F-Engrave", about)

    def menu_Help_Web(self):
        webbrowser.open_new(
            r"http://www.scorchworks.com/Fengrave/fengrave_doc.html"
        )

    def KEY_ESC(self, event):
        pass  # A stop calculation command may go here

    def KEY_F1(self, event):
        self.menu_Help_About()

    def KEY_F2(self, event):
        self.GEN_Settings_Window()

    def KEY_F3(self, event):
        self.VCARVE_Settings_Window()

    def KEY_F4(self, event):
        self.PBM_Settings_Window()

    def KEY_F5(self, event):
        self.menu_View_Refresh()

    def KEY_ZOOM_IN(self, event):
        self.menu_View_Zoom_in()

    def KEY_ZOOM_OUT(self, event):
        self.menu_View_Zoom_out()

    def KEY_CTRL_G(self, event):
        self.CopyClipboard_GCode()

    def KEY_CTRL_S(self, event):
        self.menu_File_Save_G_Code_File()

    def Master_Configure(self, event, update=0):
        config = self.config
        if event.widget != self.master:
            return
        if config.batch.get():
            return

        x = int(self.master.winfo_x())
        y = int(self.master.winfo_y())
        w = int(self.master.winfo_width())
        h = int(self.master.winfo_height())
        if (self.x, self.y) == (-1, -1):
            self.x, self.y = x, y
        if abs(self.w - w) > 10 or abs(self.h - h) > 10 or update == 1:
            #  Form changed size (resized) - adjust as required.
            self.w = w
            self.h = h
            # canvas
            if config.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)

            if config.input_type.get() == "text":
                self.Label_font_prop.configure(text="Text Font Properties:")
                self.Label_Yscale.configure(text="Text Height")
                self.Label_Xscale.configure(text="Text Width")
                self.Label_pos_orient.configure(
                    text="Text Position and Orientation:"
                )
                self.Label_Tangle.configure(text="Text Angle")
                self.Label_flip.configure(text="Flip Text")
                self.Label_mirror.configure(text="Mirror Text")

                self.Label_useIMGsize.place_forget()
                self.Checkbutton_useIMGsize.place_forget()

                # Left Column #
                w_label = 90
                w_entry = 60
                w_units = 35

                x_label_L = 10
                x_entry_L = x_label_L + w_label + 10
                x_units_L = x_entry_L + w_entry + 5

                Yloc = 6
                self.Label_font_prop.place(
                    x=x_label_L, y=Yloc, width=w_label * 2, height=21
                )
                Yloc = Yloc + 24
                self.Label_Yscale.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Yscale_pct.place_forget()
                self.Label_Yscale_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Yscale.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24
                self.Label_Sthick.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Sthick_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Sthick.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                if config.cut_type.get() != "engrave":
                    self.Entry_Sthick.configure(state="disabled")
                    self.Label_Sthick.configure(state="disabled")
                    self.Label_Sthick_u.configure(state="disabled")
                else:
                    self.Entry_Sthick.configure(state="normal")
                    self.Label_Sthick.configure(state="normal")
                    self.Label_Sthick_u.configure(state="normal")

                Yloc = Yloc + 24
                self.Label_Xscale.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Xscale_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Xscale.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24
                self.Label_Cspace.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Cspace_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Cspace.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24
                self.Label_Wspace.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Wspace_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Wspace.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24
                self.Label_Lspace.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Entry_Lspace.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24 + 12
                self.separator1.place(
                    x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2
                )
                Yloc = Yloc + 6
                self.Label_pos_orient.place(
                    x=x_label_L, y=Yloc, width=w_label * 2, height=21
                )

                Yloc = Yloc + 24
                self.Label_Tangle.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Tangle_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Tangle.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24
                self.Label_Justify.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Justify_OptionMenu.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24
                self.Label_Origin.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Origin_OptionMenu.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24
                self.Label_flip.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Checkbutton_flip.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24
                self.Label_mirror.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Checkbutton_mirror.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24 + 12
                self.separator2.place(
                    x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2
                )
                Yloc = Yloc + 6
                self.Label_text_on_arc.place(
                    x=x_label_L, y=Yloc, width=w_label * 2, height=21
                )

                Yloc = Yloc + 24
                self.Label_Tradius.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Tradius_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Tradius.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24
                self.Label_outer.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Checkbutton_outer.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24
                self.Label_upper.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Checkbutton_upper.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24 + 12
                self.separator3.place(
                    x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2
                )

                # End Left Column #

                # Start Right Column
                w_label = 90
                w_entry = 60
                w_units = 35

                x_label_R = self.w - 220
                x_entry_R = x_label_R + w_label + 10
                x_units_R = x_entry_R + w_entry + 5

                Yloc = 6
                self.Label_gcode_opt.place(
                    x=x_label_R, y=Yloc, width=w_label * 2, height=21
                )

                Yloc = Yloc + 24
                self.Entry_Feed.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )
                self.Label_Feed.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Feed_u.place(
                    x=x_units_R, y=Yloc, width=w_units + 15, height=21
                )

                Yloc = Yloc + 24
                self.Entry_Plunge.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )
                self.Label_Plunge.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Plunge_u.place(
                    x=x_units_R, y=Yloc, width=w_units + 15, height=21
                )

                Yloc = Yloc + 24
                self.Entry_Zsafe.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )
                self.Label_Zsafe.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Zsafe_u.place(
                    x=x_units_R, y=Yloc, width=w_units, height=21
                )

                Yloc = Yloc + 24
                self.Label_Zcut.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Zcut_u.place(
                    x=x_units_R, y=Yloc, width=w_units, height=21
                )
                self.Entry_Zcut.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )

                if config.cut_type.get() != "engrave":
                    self.Entry_Zcut.configure(state="disabled")
                    self.Label_Zcut.configure(state="disabled")
                    self.Label_Zcut_u.configure(state="disabled")
                else:
                    self.Entry_Zcut.configure(state="normal")
                    self.Label_Zcut.configure(state="normal")
                    self.Label_Zcut_u.configure(state="normal")

                Yloc = Yloc + 24 + 6
                self.Label_List_Box.place(
                    x=x_label_R + 0, y=Yloc, width=113, height=22
                )

                Yloc = Yloc + 24
                self.Listbox_1_frame.place(
                    x=x_label_R + 0,
                    y=Yloc,
                    width=160 + 25,
                    height=self.h - 324,
                )
                self.Label_fontfile.place(
                    x=x_label_R, y=self.h - 165, width=w_label + 75, height=21
                )
                self.Checkbutton_fontdex.place(
                    x=x_label_R, y=self.h - 145, width=185, height=23
                )

                # Buttons etc.

                Ybut = self.h - 60
                self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

                Ybut = self.h - 60
                self.V_Carve_Calc.place(
                    x=x_label_R, y=Ybut, width=100, height=30
                )

                Ybut = self.h - 105
                self.Radio_Cut_E.place(
                    x=x_label_R, y=Ybut, width=185, height=23
                )
                Ybut = self.h - 85
                self.Radio_Cut_V.place(
                    x=x_label_R, y=Ybut, width=185, height=23
                )

                self.PreviewCanvas.configure(
                    width=self.w - 455, height=self.h - 160
                )
                self.PreviewCanvas_frame.place(x=220, y=10)
                self.Input_Label.place(
                    x=222, y=self.h - 130, width=112, height=21, anchor=W
                )
                self.Input_frame.place(
                    x=222, y=self.h - 110, width=self.w - 455, height=75
                )

            else:
                self.Label_font_prop.configure(text="Image Properties:")
                self.Label_Yscale.configure(text="Image Height")
                self.Label_Xscale.configure(text="Image Width")
                self.Label_pos_orient.configure(
                    text="Image Position and Orientation:"
                )
                self.Label_Tangle.configure(text="Image Angle")
                self.Label_flip.configure(text="Flip Image")
                self.Label_mirror.configure(text="Mirror Image")
                # Left Column #
                w_label = 90
                w_entry = 60
                w_units = 35

                x_label_L = 10
                x_entry_L = x_label_L + w_label + 10
                x_units_L = x_entry_L + w_entry + 5

                Yloc = 6
                self.Label_font_prop.place(
                    x=x_label_L, y=Yloc, width=w_label * 2, height=21
                )
                Yloc = Yloc + 24
                self.Label_Yscale.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                if config.useIMGsize.get():
                    self.Label_Yscale_u.place_forget()
                    self.Label_Yscale_pct.place(
                        x=x_units_L, y=Yloc, width=w_units, height=21
                    )
                else:
                    self.Label_Yscale_pct.place_forget()
                    self.Label_Yscale_u.place(
                        x=x_units_L, y=Yloc, width=w_units, height=21
                    )

                self.Entry_Yscale.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                Yloc = Yloc + 24
                self.Label_useIMGsize.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Checkbutton_useIMGsize.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24
                self.Label_Sthick.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Sthick_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Sthick.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )
                if config.cut_type.get() != "engrave":
                    self.Entry_Sthick.configure(state="disabled")
                    self.Label_Sthick.configure(state="disabled")
                    self.Label_Sthick_u.configure(state="disabled")
                else:
                    self.Entry_Sthick.configure(state="normal")
                    self.Label_Sthick.configure(state="normal")
                    self.Label_Sthick_u.configure(state="normal")

                Yloc = Yloc + 24
                self.Label_Xscale.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Xscale_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Xscale.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                self.Label_Cspace.place_forget()
                self.Label_Cspace_u.place_forget()
                self.Entry_Cspace.place_forget()

                self.Label_Wspace.place_forget()
                self.Label_Wspace_u.place_forget()
                self.Entry_Wspace.place_forget()

                self.Label_Lspace.place_forget()
                self.Entry_Lspace.place_forget()

                Yloc = Yloc + 24 + 12
                self.separator1.place(
                    x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2
                )
                Yloc = Yloc + 6
                self.Label_pos_orient.place(
                    x=x_label_L, y=Yloc, width=w_label * 2, height=21
                )

                Yloc = Yloc + 24
                self.Label_Tangle.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Label_Tangle_u.place(
                    x=x_units_L, y=Yloc, width=w_units, height=21
                )
                self.Entry_Tangle.place(
                    x=x_entry_L, y=Yloc, width=w_entry, height=23
                )

                self.Label_Justify.place_forget()
                self.Justify_OptionMenu.place_forget()

                Yloc = Yloc + 24
                self.Label_Origin.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Origin_OptionMenu.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24
                self.Label_flip.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Checkbutton_flip.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                Yloc = Yloc + 24
                self.Label_mirror.place(
                    x=x_label_L, y=Yloc, width=w_label, height=21
                )
                self.Checkbutton_mirror.place(
                    x=x_entry_L, y=Yloc, width=w_entry + 40, height=23
                )

                self.Label_text_on_arc.place_forget()
                self.Label_Tradius.place_forget()
                self.Label_Tradius_u.place_forget()
                self.Entry_Tradius.place_forget()
                self.Label_outer.place_forget()
                self.Checkbutton_outer.place_forget()
                self.Label_upper.place_forget()
                self.Checkbutton_upper.place_forget()

                # End Left Column #
                # Start Right Column Items
                x_label_R = x_label_L
                x_entry_R = x_entry_L
                x_units_R = x_units_L

                Yloc = Yloc + 24 + 12
                self.separator2.place(
                    x=x_label_R, y=Yloc, width=w_label + 75 + 40, height=2
                )

                Yloc = Yloc + 6
                self.Label_gcode_opt.place(
                    x=x_label_R, y=Yloc, width=w_label * 2, height=21
                )

                Yloc = Yloc + 24
                self.Entry_Feed.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )
                self.Label_Feed.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Feed_u.place(
                    x=x_units_R, y=Yloc, width=w_units + 15, height=21
                )

                Yloc = Yloc + 24
                self.Entry_Plunge.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )
                self.Label_Plunge.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Plunge_u.place(
                    x=x_units_R, y=Yloc, width=w_units + 15, height=21
                )

                Yloc = Yloc + 24
                self.Entry_Zsafe.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )
                self.Label_Zsafe.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Zsafe_u.place(
                    x=x_units_R, y=Yloc, width=w_units, height=21
                )

                Yloc = Yloc + 24
                self.Label_Zcut.place(
                    x=x_label_R, y=Yloc, width=w_label, height=21
                )
                self.Label_Zcut_u.place(
                    x=x_units_R, y=Yloc, width=w_units, height=21
                )
                self.Entry_Zcut.place(
                    x=x_entry_R, y=Yloc, width=w_entry, height=23
                )

                if config.cut_type.get() != "engrave":
                    self.Entry_Zcut.configure(state="disabled")
                    self.Label_Zcut.configure(state="disabled")
                    self.Label_Zcut_u.configure(state="disabled")
                else:
                    self.Entry_Zcut.configure(state="normal")
                    self.Label_Zcut.configure(state="normal")
                    self.Label_Zcut_u.configure(state="normal")

                self.Label_List_Box.place_forget()
                self.Listbox_1_frame.place_forget()
                self.Checkbutton_fontdex.place_forget()

                Yloc = Yloc + 24 + 12
                self.separator3.place(
                    x=x_label_L, y=Yloc, width=w_label + 75 + 40, height=2
                )
                Yloc = Yloc + 6
                self.Label_fontfile.place(
                    x=x_label_R, y=Yloc, width=w_label + 75, height=21
                )

                # Buttons etc.
                offset_R = 100
                Ybut = self.h - 60
                self.Recalculate.place(x=12, y=Ybut, width=95, height=30)

                Ybut = self.h - 60
                self.V_Carve_Calc.place(
                    x=x_label_R + offset_R, y=Ybut, width=100, height=30
                )

                Ybut = self.h - 105
                self.Radio_Cut_E.place(
                    x=x_label_R + offset_R, y=Ybut, width=w_label, height=23
                )
                Ybut = self.h - 85
                self.Radio_Cut_V.place(
                    x=x_label_R + offset_R, y=Ybut, width=w_label, height=23
                )

                self.PreviewCanvas.configure(
                    width=self.w - 240, height=self.h - 45
                )
                self.PreviewCanvas_frame.place(x=230, y=10)
                self.Input_Label.place_forget()
                self.Input_frame.place_forget()

            ###########################################################
            if config.cut_type.get() == "v-carve":
                pass
            else:
                pass
            ###########################################################
            self.Plot_Data()

    def Plot_Line(
        self,
        XX1,
        YY1,
        XX2,
        YY2,
        midx,
        midy,
        cszw,
        cszh,
        PlotScale,
        col,
        radius=0,
    ):
        x1 = cszw / 2 + (XX1 - midx) / PlotScale
        x2 = cszw / 2 + (XX2 - midx) / PlotScale
        y1 = cszh / 2 - (YY1 - midy) / PlotScale
        y2 = cszh / 2 - (YY2 - midy) / PlotScale
        if radius == 0:
            thick = 0
        else:
            thick = radius * 2 / PlotScale
        self.segID.append(
            self.PreviewCanvas.create_line(
                x1, y1, x2, y2, fill=col, capstyle="round", width=thick
            )
        )

    def Plot_Circ(
        self, XX1, YY1, midx, midy, cszw, cszh, PlotScale, color, Rad, fill
    ):
        dd = Rad
        x1 = cszw / 2 + (XX1 - dd - midx) / PlotScale
        x2 = cszw / 2 + (XX1 + dd - midx) / PlotScale
        y1 = cszh / 2 - (YY1 - dd - midy) / PlotScale
        y2 = cszh / 2 - (YY1 + dd - midy) / PlotScale
        if fill == 0:
            self.segID.append(
                self.PreviewCanvas.create_oval(
                    x1, y1, x2, y2, outline=color, fill=None, width=1
                )
            )
        else:
            self.segID.append(
                self.PreviewCanvas.create_oval(
                    x1, y1, x2, y2, outline=color, fill=color, width=0
                )
            )

    def Recalculate_RQD_Nocalc(self, event):
        self.statusbar.configure(bg="yellow")
        self.Input.configure(bg="yellow")
        self.statusMessage.set(" Recalculation required.")

    def Recalculate_RQD_Click(self, event):
        self.statusbar.configure(bg="yellow")
        self.statusMessage.set(" Recalculation required.")
        self.DoIt()

    def Recalc_RQD(self):
        self.statusbar.configure(bg="yellow")
        self.statusMessage.set(" Recalculation required.")
        self.DoIt()

    ##########################################
    #          Read Font File                #
    ##########################################
    def Read_font_file(self):
        config = self.config
        if self.delay_calc == 1:
            return

        self.font = {}
        file_full = config.fontdir.get() + "/" + config.fontfile.get()
        if not os.path.isfile(file_full):
            return
        if not config.batch.get():
            self.statusbar.configure(bg="yellow")
            self.statusMessage.set("Reading Font File.........")
            self.master.update_idletasks()

        config.current_input_file.set(os.path.basename(file_full))

        self.font = font.parse_font_file(
            file_full, config.segarc.get(), config.ext_char.get()
        )

        if self.font:
            config.input_type.set("text")
        else:
            self.statusMessage.set(
                "Unable to open font file: %s" % (file_full)
            )
            self.statusbar.configure(bg="red")

        if not config.batch.get():
            self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 1)
            self.menu_View_Refresh()

    ##########################################
    #          Read Font File                #
    ##########################################
    def Read_image_file(self):
        config = self.config
        if self.delay_calc == 1:
            return

        self.font = {}
        file_full = self.IMAGE_FILE
        file_name = os.path.basename(file_full)
        if not os.path.isfile(file_full):
            file_full = file_name
            if not os.path.isfile(file_full):
                file_full = self.HOME_DIR + "/" + file_name
                if not os.path.isfile(file_full):
                    file_full = (
                        os.path.dirname(self.NGC_FILE) + "/" + file_name
                    )
                    if not os.path.isfile(file_full):
                        return
        self.IMAGE_FILE = file_full

        if not config.batch.get():
            self.statusbar.configure(bg="yellow")
            self.statusMessage.set(" Reading Image File.........")
            self.master.update_idletasks()

        fileName, fileExtension = os.path.splitext(file_full)
        config.current_input_file.set(os.path.basename(file_full))

        new_origin = False
        SegArc = float(config.segarc.get())
        TYPE = fileExtension.upper()
        if TYPE == ".DXF":
            try:
                fd = open(file_full)
                self.font = parse_dxf(
                    fd, SegArc, message, new_origin
                )  # build stroke lists from font file
                fd.close()
                config.input_type.set("image")
            except:
                message.fmessage(
                    "Unable To open Drawing Exchange File (DXF) file."
                )

        elif (
            TYPE == ".BMP"
            or TYPE == ".PBM"
            or TYPE == ".PPM"
            or TYPE == ".PGM"
            or TYPE == ".PNM"
        ):
            try:
                # cmd = ["potrace","-b","dxf",file_full,"-o","-"]
                if config.bmp_longcurve.get() == 1:
                    cmd = [
                        "potrace",
                        "-z",
                        config.bmp_turnpol.get(),
                        "-t",
                        config.bmp_turdsize.get(),
                        "-a",
                        config.bmp_alphamax.get(),
                        "-O",
                        config.bmp_opttolerance.get(),
                        "-b",
                        "dxf",
                        file_full,
                        "-o",
                        "-",
                    ]
                else:
                    cmd = [
                        "potrace",
                        "-z",
                        config.bmp_turnpol.get(),
                        "-t",
                        config.bmp_turdsize.get(),
                        "-a",
                        config.bmp_alphamax.get(),
                        "-n",
                        "-b",
                        "dxf",
                        file_full,
                        "-o",
                        "-",
                    ]

                p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                stdout, stderr = p.communicate()
                if VERSION == 3:
                    fd = bytes.decode(stdout).split("\n")
                else:
                    fd = stdout.split("\n")
                self.font = parse_dxf(
                    fd, SegArc, message, new_origin
                )  # build stroke lists from font file
                config.input_type.set("image")
            except:
                message.fmessage(
                    "Unable To create path data from bitmap File."
                )

        elif (
            TYPE == ".JPG"
            or TYPE == ".PNG"
            or TYPE == ".GIF"
            or TYPE == ".TIF"
        ):
            if PIL:
                try:
                    PIL_im = Image.open(file_full)
                    mode = PIL_im.mode
                    if len(mode) > 3:
                        blank = Image.new("RGB", PIL_im.size, (255, 255, 255))
                        blank.paste(PIL_im, (0, 0), PIL_im)
                        PIL_im = blank

                    PIL_im = PIL_im.convert("1")
                    file_full_tmp = self.HOME_DIR + "/fengrave_tmp.bmp"
                    PIL_im.save(file_full_tmp, "bmp")

                    # cmd = ["potrace","-b","dxf",file_full,"-o","-"]
                    if config.bmp_longcurve.get() == 1:
                        cmd = [
                            "potrace",
                            "-z",
                            config.bmp_turnpol.get(),
                            "-t",
                            config.bmp_turdsize.get(),
                            "-a",
                            config.bmp_alphamax.get(),
                            "-O",
                            config.bmp_opttolerance.get(),
                            "-b",
                            "dxf",
                            file_full_tmp,
                            "-o",
                            "-",
                        ]
                    else:
                        cmd = [
                            "potrace",
                            "-z",
                            config.bmp_turnpol.get(),
                            "-t",
                            config.bmp_turdsize.get(),
                            "-a",
                            config.bmp_alphamax.get(),
                            "-n",
                            "-b",
                            "dxf",
                            file_full_tmp,
                            "-o",
                            "-",
                        ]

                    p = Popen(cmd, stdout=PIPE, stderr=PIPE)
                    stdout, stderr = p.communicate()
                    if VERSION == 3:
                        fd = bytes.decode(stdout).split("\n")
                    else:
                        fd = stdout.split("\n")
                    # build stroke lists from font file
                    self.font = parse_dxf(fd, SegArc, message, new_origin)
                    config.input_type.set("image")
                    try:
                        os.remove(file_full_tmp)
                    except:
                        pass
                except:
                    message.fmessage(
                        "PIL encountered an error. Unable To create path data"
                        " from the selected image File."
                    )
                    message.fmessage(
                        "Converting the image file to a BMP file may resolve "
                        "the issue."
                    )
            else:
                message.fmessage(
                    "PIL is required for reading JPG, PNG, GIF and TIF files."
                )
        else:
            pass

        # Reset Entry Fields in Bitmap Settings
        if not config.batch.get():
            self.entry_set(
                self.Entry_BMPoptTolerance,
                self.Entry_BMPoptTolerance_Check(),
                1,
            )
            self.entry_set(
                self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), 1
            )
            self.entry_set(
                self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), 1
            )
            self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 1)
            self.menu_View_Refresh()

    ##########################################
    #        CANVAS PLOTTING STUFF           #
    ##########################################
    def Plot_Data(self):
        config = self.config
        if (self.delay_calc == 1) or (self.delay_calc == 1):
            return
        self.master.update_idletasks()
        # erase old segs/display objects
        self.PreviewCanvas.delete(ALL)
        self.segID = []
        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )

        cszw = int(self.PreviewCanvas.cget("width"))
        cszh = int(self.PreviewCanvas.cget("height"))
        buff = 10

        maxx = self.MAXX
        minx = self.MINX
        maxy = self.MAXY
        miny = self.MINY
        midx = (maxx + minx) / 2
        midy = (maxy + miny) / 2

        if config.cut_type.get() == "v-carve":
            Thick = 0.0
        else:
            Thick = float(config.STHICK.get())

        if config.input_type.get() == "text":
            Radius_in = float(config.TRADIUS.get())
        else:
            Radius_in = 0.0

        PlotScale = max(
            (maxx - minx + Thick) / (cszw - buff),
            (maxy - miny + Thick) / (cszh - buff),
        )
        if PlotScale <= 0:
            PlotScale = 1.0
        self.pscale = PlotScale

        Radius_plot = 0
        if config.plotbox.get() and config.cut_type.get() == "engrave":
            if Radius_in != 0:
                Radius_plot = float(self.RADIUS_PLOT)

        x_lft = cszw / 2 + (minx - midx) / PlotScale
        x_rgt = cszw / 2 + (maxx - midx) / PlotScale
        y_bot = cszh / 2 + (maxy - midy) / PlotScale
        y_top = cszh / 2 + (miny - midy) / PlotScale

        if config.show_box.get():
            self.segID.append(
                self.PreviewCanvas.create_rectangle(
                    x_lft,
                    y_bot,
                    x_rgt,
                    y_top,
                    fill="gray80",
                    outline="gray80",
                    width=0,
                )
            )

        if Radius_in != 0:
            Rx_lft = cszw / 2 + (-Radius_in - midx) / PlotScale
            Rx_rgt = cszw / 2 + (Radius_in - midx) / PlotScale
            Ry_bot = cszh / 2 + (Radius_in + midy) / PlotScale
            Ry_top = cszh / 2 + (-Radius_in + midy) / PlotScale
            self.segID.append(
                self.PreviewCanvas.create_oval(
                    Rx_lft,
                    Ry_bot,
                    Rx_rgt,
                    Ry_top,
                    outline="gray90",
                    width=0,
                    dash=3,
                )
            )

        if config.show_thick.get():
            plot_width = Thick / PlotScale
        else:
            plot_width = 1.0

        x_zero = self.Xzero
        y_zero = self.Yzero

        # Plot circle radius with radius equal to Radius_plot
        if Radius_plot != 0:
            Rpx_lft = cszw / 2 + (-Radius_plot - midx - x_zero) / PlotScale
            Rpx_rgt = cszw / 2 + (Radius_plot - midx - x_zero) / PlotScale
            Rpy_bot = cszh / 2 + (Radius_plot + midy + y_zero) / PlotScale
            Rpy_top = cszh / 2 + (-Radius_plot + midy + y_zero) / PlotScale
            self.segID.append(
                self.PreviewCanvas.create_oval(
                    Rpx_lft,
                    Rpy_bot,
                    Rpx_rgt,
                    Rpy_top,
                    outline="black",
                    width=plot_width,
                )
            )

        for line in self.coords:
            XY = line
            x1 = cszw / 2 + (XY[0] - midx) / PlotScale
            x2 = cszw / 2 + (XY[2] - midx) / PlotScale
            y1 = cszh / 2 - (XY[1] - midy) / PlotScale
            y2 = cszh / 2 - (XY[3] - midy) / PlotScale
            self.segID.append(
                self.PreviewCanvas.create_line(
                    x1,
                    y1,
                    x2,
                    y2,
                    fill="black",
                    width=plot_width,
                    capstyle="round",
                )
            )
        XOrigin = float(config.xorigin.get())
        YOrigin = float(config.yorigin.get())
        axis_length = (maxx - minx) / 4
        axis_x1 = cszw / 2 + (-midx + XOrigin) / PlotScale
        axis_x2 = cszw / 2 + (axis_length - midx + XOrigin) / PlotScale
        axis_y1 = cszh / 2 - (-midy + YOrigin) / PlotScale
        axis_y2 = cszh / 2 - (axis_length - midy + YOrigin) / PlotScale

        #########################################
        # V-carve Plotting Stuff
        #########################################
        if config.cut_type.get() == "v-carve":
            loop_old = -1
            r_inlay_top = self.calc_r_inlay_top(bit)

            if config.show_v_area.get():
                for line in self.vcoords:
                    XY = line
                    x1 = XY[0]
                    y1 = XY[1]
                    r = XY[2]
                    color = "black"

                    rbit = calc_vbit_dia(config, bit) / 2.0
                    if bit.shape == "FLAT":
                        if r >= rbit:
                            self.Plot_Circ(
                                x1,
                                y1,
                                midx,
                                midy,
                                cszw,
                                cszh,
                                PlotScale,
                                color,
                                r,
                                1,
                            )
                    else:
                        if config.inlay.get():
                            self.Plot_Circ(
                                x1,
                                y1,
                                midx,
                                midy,
                                cszw,
                                cszh,
                                PlotScale,
                                color,
                                r - r_inlay_top,
                                1,
                            )
                        else:
                            self.Plot_Circ(
                                x1,
                                y1,
                                midx,
                                midy,
                                cszw,
                                cszh,
                                PlotScale,
                                color,
                                r,
                                1,
                            )

            loop_old = -1
            rold = -1

            if config.show_v_path.get():
                # Avoid pylava warnings
                rold = 0
                xold = 0
                yold = 0

                for line in self.vcoords:
                    XY = line
                    x1 = XY[0]
                    y1 = XY[1]
                    r = XY[2]
                    loop = XY[3]
                    color = "white"
                    # check and see if we need to move to a new discontinuous
                    # start point
                    plot_flat = False
                    if config.bit_shape.get() == "FLAT":
                        if (r == rold) and (r >= rbit):
                            plot_flat = True
                    else:
                        plot_flat = True

                    if (loop == loop_old) and plot_flat:
                        self.Plot_Line(
                            xold,
                            yold,
                            x1,
                            y1,
                            midx,
                            midy,
                            cszw,
                            cszh,
                            PlotScale,
                            color,
                        )
                    loop_old = loop
                    rold = r
                    xold = x1
                    yold = y1

        ########################################
        # Plot cleanup data
        ########################################
        if config.cut_type.get() == "v-carve":
            loop_old = -1
            # Avoid pylava warnings
            xold = 0
            yold = 0

            for line in self.clean_coords_sort:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                loop = XY[3]
                color = "brown"
                if loop == loop_old:
                    self.Plot_Line(
                        xold,
                        yold,
                        x1,
                        y1,
                        midx,
                        midy,
                        cszw,
                        cszh,
                        PlotScale,
                        color,
                        r,
                    )
                loop_old = loop
                xold = x1
                yold = y1

            loop_old = -1
            # Avoid pylava warnings
            xold = 0
            yold = 0

            for line in self.clean_coords_sort:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                loop = XY[3]
                color = "white"
                # check and see if we need to move to a new discontinuous
                # start point
                if loop == loop_old:
                    self.Plot_Line(
                        xold,
                        yold,
                        x1,
                        y1,
                        midx,
                        midy,
                        cszw,
                        cszh,
                        PlotScale,
                        color,
                    )
                loop_old = loop
                xold = x1
                yold = y1

            loop_old = -1
            # Avoid pylava warnings
            xold = 0
            yold = 0

            for line in self.v_clean_coords_sort:
                XY = line
                x1 = XY[0]
                y1 = XY[1]
                r = XY[2]
                loop = XY[3]
                color = "yellow"
                if loop == loop_old:
                    self.Plot_Line(
                        xold,
                        yold,
                        x1,
                        y1,
                        midx,
                        midy,
                        cszw,
                        cszh,
                        PlotScale,
                        color,
                    )
                loop_old = loop
                xold = x1
                yold = y1

        #########################################
        # End V-carve Plotting Stuff
        #########################################

        if config.show_axis.get():
            # Plot coordinate system origin
            self.segID.append(
                self.PreviewCanvas.create_line(
                    axis_x1, axis_y1, axis_x2, axis_y1, fill="red", width=0
                )
            )
            self.segID.append(
                self.PreviewCanvas.create_line(
                    axis_x1, axis_y1, axis_x1, axis_y2, fill="green", width=0
                )
            )

    # Perform  Calculations
    def DoIt(self):
        config = self.config
        if (self.delay_calc == 1) or (self.delay_calc == 1):
            return

        self.menu_View_Refresh()

        if not config.batch.get():
            if config.cut_type.get() == "v-carve":
                self.V_Carve_Calc.configure(state="normal", command=None)
            else:
                self.V_Carve_Calc.configure(state="disabled", command=None)

        if self.Check_All_Variables() > 0:
            return

        if not config.batch.get():
            self.statusbar.configure(bg="yellow")
            self.statusMessage.set(" Calculating.........")
            self.master.update_idletasks()
            self.PreviewCanvas.delete(ALL)

        # erase old data
        self.segID = []
        self.coords = []
        self.vcoords = []
        self.clean_coords = []
        self.clean_segment = []
        self.clean_coords_sort = []
        self.v_clean_coords_sort = []

        self.RADIUS_PLOT = 0

        if len(self.font) == 0 and (not config.batch.get()):
            self.statusbar.configure(bg="red")
            if config.input_type.get() == "text":
                self.statusMessage.set("No Font Characters Loaded")
            else:
                self.statusMessage.set("No Image Loaded")
            return

        if config.input_type.get() == "text":
            if not config.batch.get():
                String = self.Input.get(1.0, END)
            else:
                String = self.default_text

            Radius_in = float(config.TRADIUS.get())
        else:
            String = "F"
            Radius_in = 0.0
        try:
            float(config.segarc.get())
            YScale_in = float(config.YSCALE.get())
            CSpaceP = float(config.CSPACE.get())
            WSpaceP = float(config.WSPACE.get())
            LSpace = float(config.LSPACE.get())
            Angle = float(config.TANGLE.get())
            Thick = float(config.STHICK.get())
            XOrigin = float(config.xorigin.get())
            YOrigin = float(config.yorigin.get())
            v_flop = bool(config.v_flop.get())
        except:
            self.statusMessage.set(
                " Unable to create paths.  Check Settings Entry Values."
            )
            self.statusbar.configure(bg="red")
            return

        if config.cut_type.get() == "v-carve":
            Thick = 0.0

        line_maxx = []
        line_maxy = []
        line_maxa = []
        line_mina = []
        line_miny = []
        line_minx = []

        maxx_tmp = -99991.0
        maxy_tmp = -99992.0
        maxa_tmp = -99993.0
        mina_tmp = 99993.0
        miny_tmp = 99994.0
        minx_tmp = 99995.0

        font_word_space = 0
        INF = 1e10
        font_line_height = -INF
        font_char_width = -INF
        font_used_height = -INF
        font_used_width = -INF
        font_used_depth = INF

        ################################
        ##      Font Index Preview    ##
        ################################
        if config.fontdex.get():
            Radius_in = 0.0
            String = ""
            for key in self.font:
                if config.ext_char.get():
                    String = String + unichr(key)
                elif int(key) < 256:
                    String = String + unichr(key)

            Strings = sorted(String)
            mcnt = 0
            String = ""

            if config.ext_char.get():
                pcols = int(1.5 * sqrt(float(len(self.font))))
            else:
                pcols = 15

            for char in Strings:
                mcnt = mcnt + 1
                String = String + char
                if mcnt > pcols:
                    String = String + "\n"
                    mcnt = 0

        ##################################
        ## Font Height/Width Calculation #
        ##################################
        for char in String:
            try:
                font_used_height = max(
                    self.font[ord(char)].get_ymax(), font_used_height
                )
                font_used_width = max(
                    self.font[ord(char)].get_xmax(), font_used_width
                )
                font_used_depth = min(
                    self.font[ord(char)].get_ymin(), font_used_depth
                )
            except:
                pass

        if config.H_CALC.get() == "max_all":
            font_line_height = max(
                self.font[key].get_ymax() for key in self.font
            )
            font_line_depth = min(
                self.font[key].get_ymin() for key in self.font
            )
        elif config.H_CALC.get() == "max_use":
            font_line_height = font_used_height
            font_line_depth = font_used_depth

        if font_line_height > -INF:
            if config.useIMGsize.get() and config.input_type.get() == "image":
                YScale = YScale_in / 100.0
            else:
                try:
                    YScale = (YScale_in - Thick) / (
                        font_line_height - font_line_depth
                    )
                except:
                    YScale = 0.1
                if YScale <= Zero:
                    YScale = 0.1
        else:
            if not config.batch.get():
                self.statusbar.configure(bg="red")
            if config.H_CALC.get() == "max_all":
                if not config.batch.get():
                    self.statusMessage.set("No Font Characters Found")
                else:
                    message.fmessage("(No Font Characters Found)")
            elif config.H_CALC.get() == "max_use":
                if config.input_type.get() == "image":
                    error_text = (
                        "Image contains no design information. "
                        "(Empty DXF File)"
                    )
                else:
                    error_text = (
                        "Input Characters Were Not Found in the Current Font"
                    )

                if not config.batch.get():
                    self.statusMessage.set(error_text)
                else:
                    message.fmessage("(" + error_text + ")")
            return
        font_char_width = max(self.font[key].get_xmax() for key in self.font)
        font_word_space = font_char_width * (WSpaceP / 100.0)

        XScale = float(config.XSCALE.get()) * YScale / 100
        font_char_space = font_char_width * (CSpaceP / 100.0)

        if Radius_in != 0.0:
            if config.outer.get():
                if config.upper.get():
                    Radius = (
                        Radius_in + Thick / 2 + YScale * (-font_line_depth)
                    )
                else:
                    Radius = (
                        -Radius_in - Thick / 2 - YScale * (font_line_height)
                    )
            else:
                if config.upper.get():
                    Radius = (
                        Radius_in - Thick / 2 - YScale * (font_line_height)
                    )
                else:
                    Radius = (
                        -Radius_in + Thick / 2 + YScale * (-font_line_depth)
                    )
        else:
            Radius = Radius_in

        font_line_space = (
            font_line_height - font_line_depth + Thick / YScale
        ) * LSpace

        xposition = 0.0
        yposition = 0.0
        line_cnt = 0.0
        char_cnt = 0
        no_font_record = []
        message2 = ""
        for char in String:
            char_cnt = char_cnt + 1

            if char == " ":
                xposition += font_word_space
                continue
            if char == "\t":
                xposition += 3 * font_word_space
                continue
            if char == "\n":
                xposition = 0
                yposition += font_line_space
                line_cnt = line_cnt + 1
                line_minx.append(minx_tmp)
                line_miny.append(miny_tmp)
                line_maxx.append(maxx_tmp)
                line_maxy.append(maxy_tmp)
                line_maxa.append(maxa_tmp)
                line_mina.append(mina_tmp)
                maxx_tmp = -99919.0
                maxy_tmp = -99929.0
                maxa_tmp = -99939.0
                mina_tmp = 99949.0
                miny_tmp = 99959.0
                minx_tmp = 99969.0
                continue

            try:
                font_line_height = self.font[ord(char)].get_ymax()
            except:
                flag = 0
                for norec in no_font_record:
                    if norec == char:
                        flag = 1
                if flag == 0:
                    no_font_record.append(char)
                    message2 = ", CHECK OUTPUT! "
                    "Some characters not found in font file."
                continue
            for stroke in self.font[ord(char)].stroke_list:
                x1 = stroke.xstart + xposition
                y1 = stroke.ystart - yposition
                x2 = stroke.xend + xposition
                y2 = stroke.yend - yposition

                # Perform scaling
                x1, y1 = CoordScale(x1, y1, XScale, YScale)
                x2, y2 = CoordScale(x2, y2, XScale, YScale)

                self.coords.append([x1, y1, x2, y2, line_cnt, char_cnt])

                maxx_tmp = max(maxx_tmp, x1, x2)
                minx_tmp = min(minx_tmp, x1, x2)
                miny_tmp = min(miny_tmp, y1, y2)
                maxy_tmp = max(maxy_tmp, y1, y2)

            char_width = self.font[
                ord(char)
            ].get_xmax()  # move over for next character
            xposition += font_char_space + char_width
        # END Char in String

        maxx = maxy = -99999.0
        miny = minx = 99999.0
        cnt = 0

        for maxx_val in line_maxx:
            maxx = max(maxx, line_maxx[cnt])
            minx = min(minx, line_minx[cnt])
            miny = min(miny, line_miny[cnt])
            maxy = max(maxy, line_maxy[cnt])
            cnt = cnt + 1
        ##########################################
        #      TEXT LEFT JUSTIFY STUFF           #
        ##########################################
        if config.justify.get() == "Left":
            pass
        ##########################################
        #          TEXT CENTERING STUFF          #
        ##########################################
        if config.justify.get() == "Center":
            cnt = 0
            for line in self.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    self.coords[cnt][0] = (
                        XY[0] + (maxx - line_maxx[line_num]) / 2
                    )
                    self.coords[cnt][2] = (
                        XY[2] + (maxx - line_maxx[line_num]) / 2
                    )
                except:
                    pass
                cnt = cnt + 1

        ##########################################
        #        TEXT RIGHT JUSTIFY STUFF        #
        ##########################################
        if config.justify.get() == "Right":
            for line in self.coords:
                XY = line
                line_num = int(XY[4])
                try:
                    XY[0] = XY[0] + (maxx - line_maxx[line_num])
                    XY[2] = XY[2] + (maxx - line_maxx[line_num])
                except:
                    pass
                cnt = cnt + 1

        ##########################################
        #         TEXT ON RADIUS STUFF           #
        ##########################################
        mina = 99996.0
        maxa = -99993.0
        if Radius != 0.0:
            for line in self.coords:
                XY = line
                XY[0], XY[1], A1 = Rotn(XY[0], XY[1], 0, Radius)
                XY[2], XY[3], A2 = Rotn(XY[2], XY[3], 0, Radius)
                maxa = max(maxa, A1, A2)
                mina = min(mina, A1, A2)
            mida = (mina + maxa) / 2
            ##########################################
            #         TEXT LEFT JUSTIFY STUFF        #
            ##########################################
            if config.justify.get() == "Left":
                pass
            ##########################################
            #          TEXT CENTERING STUFF          #
            ##########################################
            if config.justify.get() == "Center":
                for line in self.coords:
                    XY = line
                    XY[0], XY[1] = Transform(XY[0], XY[1], mida)
                    XY[2], XY[3] = Transform(XY[2], XY[3], mida)
            ##########################################
            #        TEXT RIGHT JUSTIFY STUFF        #
            ##########################################
            if config.justify.get() == "Right":
                for line in self.coords:
                    XY = line
                    if config.upper.get():
                        XY[0], XY[1] = Transform(XY[0], XY[1], maxa)
                        XY[2], XY[3] = Transform(XY[2], XY[3], maxa)
                    else:
                        XY[0], XY[1] = Transform(XY[0], XY[1], mina)
                        XY[2], XY[3] = Transform(XY[2], XY[3], mina)

        ##########################################
        #    TEXT FLIP / MIRROR STUFF / ANGLE    #
        ##########################################
        mirror_flag = config.mirror.get()
        flip_flag = config.flip.get()

        maxx = -99991.0
        maxy = -99992.0
        miny = 99994.0
        minx = 99995.0

        ##        Commented this section out in Version 1.66
        ##        because....

        ##        if Radius == 0.0:
        ##            if Angle == 0.0:
        ##                if flip_flag:
        ##                    miny  =  -font_line_height*YScale
        ##                else:
        ##                    maxy  =  font_line_height*YScale
        ##
        ##            elif (Angle == 90.0) or (Angle == -270.0):
        ##                if not mirror_flag:
        ##                    minx  =  -font_line_height*YScale
        ##                else:
        ##                    maxx  =  font_line_height*YScale
        ##
        ##            elif (Angle == 270.0) or (Angle == -90.0):
        ##                if not mirror_flag:
        ##                    maxx  =   font_line_height*YScale
        ##                else:
        ##                    minx  =  -font_line_height*YScale
        ##
        ##            elif (Angle == 180.0) or (Angle == -180.0):
        ##                if flip_flag:
        ##                    maxy  = font_line_height*YScale
        ##                else:
        ##                    miny  = -font_line_height*YScale

        maxr2 = 0.0
        for line in self.coords:
            XY = line
            if Angle != 0.0:
                XY[0], XY[1], A1 = Rotn(XY[0], XY[1], Angle, 0)
                XY[2], XY[3], A2 = Rotn(XY[2], XY[3], Angle, 0)

            if mirror_flag:
                XY[0] = -XY[0]
                XY[2] = -XY[2]
                v_flop = not (v_flop)

            if flip_flag:
                XY[1] = -XY[1]
                XY[3] = -XY[3]
                v_flop = not (v_flop)

            maxx = max(maxx, XY[0], XY[2])
            maxy = max(maxy, XY[1], XY[3])

            minx = min(minx, XY[0], XY[2])
            miny = min(miny, XY[1], XY[3])

            maxr2 = max(
                maxr2,
                float(XY[0] * XY[0] + XY[1] * XY[1]),
                float(XY[2] * XY[2] + XY[3] * XY[3]),
            )

        maxx = maxx + Thick / 2
        maxy = maxy + Thick / 2
        minx = minx - Thick / 2
        miny = miny - Thick / 2

        midx = (minx + maxx) / 2
        midy = (miny + maxy) / 2

        #############################
        #   Engrave box or circle   #
        #############################
        Delta = 0
        Radius_plot = 0
        Delta = Thick / 2 + float(config.boxgap.get())
        if config.plotbox.get():
            if Radius_in == 0 or config.cut_type.get() == "v-carve":
                # Add coords for box
                # self.coords.append([ minx-Delta, miny-Delta, maxx+Delta, miny-Delta, 0, 0])
                # self.coords.append([ maxx+Delta, miny-Delta, maxx+Delta, maxy+Delta, 0, 0])
                # self.coords.append([ maxx+Delta, maxy+Delta, minx-Delta, maxy+Delta, 0, 0])
                # self.coords.append([ minx-Delta, maxy+Delta, minx-Delta, miny-Delta, 0, 0])

                if bool(config.mirror.get()) ^ bool(config.flip.get()):
                    self.coords.append(
                        [
                            minx - Delta,
                            miny - Delta,
                            minx - Delta,
                            maxy + Delta,
                            0,
                            0,
                        ]
                    )
                    self.coords.append(
                        [
                            minx - Delta,
                            maxy + Delta,
                            maxx + Delta,
                            maxy + Delta,
                            0,
                            0,
                        ]
                    )
                    self.coords.append(
                        [
                            maxx + Delta,
                            maxy + Delta,
                            maxx + Delta,
                            miny - Delta,
                            0,
                            0,
                        ]
                    )
                    self.coords.append(
                        [
                            maxx + Delta,
                            miny - Delta,
                            minx - Delta,
                            miny - Delta,
                            0,
                            0,
                        ]
                    )
                else:
                    self.coords.append(
                        [
                            minx - Delta,
                            miny - Delta,
                            maxx + Delta,
                            miny - Delta,
                            0,
                            0,
                        ]
                    )
                    self.coords.append(
                        [
                            maxx + Delta,
                            miny - Delta,
                            maxx + Delta,
                            maxy + Delta,
                            0,
                            0,
                        ]
                    )
                    self.coords.append(
                        [
                            maxx + Delta,
                            maxy + Delta,
                            minx - Delta,
                            maxy + Delta,
                            0,
                            0,
                        ]
                    )
                    self.coords.append(
                        [
                            minx - Delta,
                            maxy + Delta,
                            minx - Delta,
                            miny - Delta,
                            0,
                            0,
                        ]
                    )

                if config.cut_type.get() != "v-carve":
                    Delta = Delta + Thick / 2
                minx = minx - Delta
                maxx = maxx + Delta
                miny = miny - Delta
                maxy = maxy + Delta
            else:
                Radius_plot = sqrt(maxr2) + Thick + float(config.boxgap.get())
                minx = -Radius_plot - Thick / 2
                maxx = -minx
                miny = minx
                maxy = maxx
                midx = 0
                midy = 0
                self.RADIUS_PLOT = Radius_plot
                # Don't create the circle coords here a g-code circle command
                # is generated later when not v-carving

        # The ^ operator used on the next line bitwise is XOR
        # if (bool(self.v_flop.get()) ^ bool(self.inlay.get())) and (self.cut_type.get() == "v-carve"):
        #
        #    if (bool(self.mirror.get()) ^ bool(self.flip.get())):
        #        self.coords.append([ minx-Delta, miny-Delta, minx-Delta, maxy+Delta, 0, 0])
        #        self.coords.append([ minx-Delta, maxy+Delta, maxx+Delta, maxy+Delta, 0, 0])
        #        self.coords.append([ maxx+Delta, maxy+Delta, maxx+Delta, miny-Delta, 0, 0])
        #        self.coords.append([ maxx+Delta, miny-Delta, minx-Delta, miny-Delta, 0, 0])
        #    else:
        #        self.coords.append([ minx-Delta, miny-Delta, maxx+Delta, miny-Delta, 0, 0])
        #        self.coords.append([ maxx+Delta, miny-Delta, maxx+Delta, maxy+Delta, 0, 0])
        #        self.coords.append([ maxx+Delta, maxy+Delta, minx-Delta, maxy+Delta, 0, 0])
        #        self.coords.append([ minx-Delta, maxy+Delta, minx-Delta, miny-Delta, 0, 0])
        #    Delta = Delta + Thick/2
        #    minx = minx - Delta
        #    maxx = maxx + Delta
        #    miny = miny - Delta
        #    maxy = maxy + Delta

        ##########################################
        #         ORIGIN LOCATING STUFF          #
        ##########################################
        CASE = str(config.origin.get())
        if CASE == "Top-Left":
            x_zero = minx
            y_zero = maxy
        elif CASE == "Top-Center":
            x_zero = midx
            y_zero = maxy
        elif CASE == "Top-Right":
            x_zero = maxx
            y_zero = maxy
        elif CASE == "Mid-Left":
            x_zero = minx
            y_zero = midy
        elif CASE == "Mid-Center":
            x_zero = midx
            y_zero = midy
        elif CASE == "Mid-Right":
            x_zero = maxx
            y_zero = midy
        elif CASE == "Bot-Left":
            x_zero = minx
            y_zero = miny
        elif CASE == "Bot-Center":
            x_zero = midx
            y_zero = miny
        elif CASE == "Bot-Right":
            x_zero = maxx
            y_zero = miny
        elif CASE == "Arc-Center":
            x_zero = 0
            y_zero = 0
        else:  # "Default"
            x_zero = 0
            y_zero = 0

        cnt = 0
        for line in self.coords:
            XY = line
            self.coords[cnt][0] = XY[0] - x_zero + XOrigin
            self.coords[cnt][1] = XY[1] - y_zero + YOrigin
            self.coords[cnt][2] = XY[2] - x_zero + XOrigin
            self.coords[cnt][3] = XY[3] - y_zero + YOrigin
            cnt = cnt + 1

        self.MAXX = maxx - x_zero + XOrigin
        self.MINX = minx - x_zero + XOrigin
        self.MAXY = maxy - y_zero + YOrigin
        self.MINY = miny - y_zero + YOrigin

        self.Xzero = x_zero
        self.Yzero = y_zero

        if not config.batch.get():
            # Reset Status Bar and Entry Fields
            self.Input.configure(bg="white")
            self.entry_set(self.Entry_Yscale, self.Entry_Yscale_Check(), 1)
            self.entry_set(self.Entry_Xscale, self.Entry_Xscale_Check(), 1)
            self.entry_set(self.Entry_Sthick, self.Entry_Sthick_Check(), 1)
            self.entry_set(self.Entry_Lspace, self.Entry_Lspace_Check(), 1)
            self.entry_set(self.Entry_Cspace, self.Entry_Cspace_Check(), 1)
            self.entry_set(self.Entry_Wspace, self.Entry_Wspace_Check(), 1)
            self.entry_set(self.Entry_Tangle, self.Entry_Tangle_Check(), 1)
            self.entry_set(self.Entry_Tradius, self.Entry_Tradius_Check(), 1)
            self.entry_set(self.Entry_Feed, self.Entry_Feed_Check(), 1)
            self.entry_set(self.Entry_Plunge, self.Entry_Plunge_Check(), 1)
            self.entry_set(self.Entry_Zsafe, self.Entry_Zsafe_Check(), 1)
            self.entry_set(self.Entry_Zcut, self.Entry_Zcut_Check(), 1)
            self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 1)
            self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 1)

            config.bounding_box.set(
                "Bounding Box (WxH) = "
                + "%.3g" % (maxx - minx)
                + " %s " % config.units.get()
                + " x "
                + "%.3g" % (maxy - miny)
                + " %s " % config.units.get()
                + " %s" % message2
            )
            self.statusMessage.set(config.bounding_box.get())

        if no_font_record != []:
            if not config.batch.get():
                self.statusbar.configure(bg="orange")
            message.fmessage("Characters not found in font file:", False)
            message.fmessage("(", False)
            for entry in no_font_record:
                message.fmessage("%s," % (entry), False)
            message.fmessage(")")

        if not config.batch.get():
            self.Plot_Data()
        ################
        #   End DoIt   #
        ################

    ##################################################
    def V_Carve_It(self, clean_flag=0, DXF_FLAG=False):
        config = self.config
        timestamp = 0
        self.master.unbind("<Configure>")
        self.STOP_CALC = False
        bit = bit_from_shape(
            config.bit_shape.get(), config.v_bit_dia.get(), config.v_bit_angle.get()
        )

        if config.units.get() == "mm":
            if float(config.v_step_len.get()) < MIN_METRIC_STEP_LEN:
                config.v_step_len.set(str(MIN_METRIC_STEP_LEN))
        else:
            if float(config.v_step_len.get()) < MIN_IMP_STEP_LEN:
                config.v_step_len.set(str(MIN_IMP_STEP_LEN))

        if self.Check_All_Variables() > 0:
            return
        if clean_flag != 1:
            self.DoIt()
            self.clean_coords = []
            self.clean_coords_sort = []
            self.v_clean_coords_sort = []
            self.clean_segment = []
        elif self.clean_coords_sort != [] or self.v_clean_coords_sort != []:
            # If there is existing cleanup data clear the screen before
            # computing.
            self.clean_coords = []
            self.clean_coords_sort = []
            self.v_clean_coords_sort = []
            self.Plot_Data()

        if not config.batch.get():
            self.statusbar.configure(bg="yellow")
            self.statusMessage.set("Preparing for V-Carve Calculations")
            self.master.update()

        #########################################
        # V-Carve Stuff
        #########################################
        if config.cut_type.get() == "v-carve" and not config.fontdex.get():

            v_flop = get_flop_status(config)
            if not config.batch.get():
                cszw = int(self.PreviewCanvas.cget("width"))
                cszh = int(self.PreviewCanvas.cget("height"))
                if config.v_pplot.get():
                    self.Plot_Data()

            PlotScale = self.pscale
            maxx = self.MAXX
            minx = self.MINX
            maxy = self.MAXY
            miny = self.MINY
            midx = (maxx + minx) / 2
            midy = (maxy + miny) / 2

            dline = float(config.v_step_len.get())
            ###############################################################
            rbit = calc_vbit_dia(config, bit) / 2.0
            clean_dia = float(config.clean_dia.get())

            if clean_flag != 1:
                rmax = rbit
            else:
                rmax = rbit + clean_dia / 2
            ###############################################################
            v_stp_crner = float(config.v_stp_crner.get())
            if config.inlay.get():
                v_drv_crner = 360 - v_stp_crner
            else:
                v_drv_crner = float(config.v_drv_crner.get())

            CHK_STRING = str(config.v_check_all.get())
            not_b_carve = not bool(config.bit_shape.get() == "BALL")

            if config.input_type.get() != "text":
                CHK_STRING = "all"

            BIT_ANGLE = bit.angle

            dangle = degrees(dline / rbit)
            if dangle < 2.0:
                dangle = 2.0

            if (config.input_type.get() == "image") and (clean_flag == 0):
                self.coords = sort_for_v_carve(
                    self.coords,
                    float(config.accuracy.get()),
                    self.sort_for_v_carve_status_callback,
                )

            if DXF_FLAG:
                return

            # set variable for first point in loop
            xa = 9999
            ya = 9999
            xb = 9999
            yb = 9999
            # set variable for the point previously calculated in a loop
            x0 = 9999
            y0 = 9999
            seg_sin0 = 2
            seg_cos0 = 2
            char_num0 = -1
            theta = 9999.0
            loop_cnt = 0
            if not v_flop:
                v_inc = 1
                v_index = -1
                i_x1 = 0
                i_y1 = 1
                i_x2 = 2
                i_y2 = 3
            else:
                v_inc = -1
                v_index = len(self.coords)
                i_x1 = 2
                i_y1 = 3
                i_x2 = 0
                i_y2 = 1

            coord_radius = []
            #########################
            # Setup Grid Partitions #
            #########################
            xLength = self.MAXX - self.MINX
            yLength = self.MAXY - self.MINY

            xN = 0
            yN = 0

            xN_minus_1 = max(int(xLength / ((2 * rmax + dline) * 1.1)), 1)
            yN_minus_1 = max(int(yLength / ((2 * rmax + dline) * 1.1)), 1)

            xPartitionLength = xLength / xN_minus_1
            yPartitionLength = yLength / yN_minus_1

            xN = xN_minus_1 + 1
            yN = yN_minus_1 + 1

            if xPartitionLength < Zero:
                xPartitionLength = 1
            if yPartitionLength < Zero:
                yPartitionLength = 1

            partitionList = []

            for xCount in range(0, xN):
                partitionList.append([])
                for yCount in range(0, yN):
                    partitionList[xCount].append([])

            ###############################
            # End Setup Grid Partitions   #
            ###############################

            CUR_CNT = -1
            while len(self.coords) > CUR_CNT + 1:
                CUR_CNT = CUR_CNT + 1
                XY_R = self.coords[CUR_CNT][:]
                x1_R = XY_R[0]
                y1_R = XY_R[1]
                x2_R = XY_R[2]
                y2_R = XY_R[3]
                LENGTH = sqrt(
                    (x2_R - x1_R) * (x2_R - x1_R)
                    + (y2_R - y1_R) * (y2_R - y1_R)
                )

                R_R = LENGTH / 2 + rmax
                X_R = (x1_R + x2_R) / 2
                Y_R = (y1_R + y2_R) / 2
                coord_radius.append([X_R, Y_R, R_R])

                #####################################################
                # Determine active partitions for each line segment #
                #####################################################
                coded_index = []
                # Find the local coordinates of the line segment ends
                x1_G = XY_R[0] - self.MINX
                y1_G = XY_R[1] - self.MINY
                x2_G = XY_R[2] - self.MINX
                y2_G = XY_R[3] - self.MINY

                # Find the grid box index for each line segment end
                X1i = int(x1_G / xPartitionLength)
                X2i = int(x2_G / xPartitionLength)
                Y1i = int(y1_G / yPartitionLength)
                Y2i = int(y2_G / yPartitionLength)

                # Find the max/min grid box locations
                Xindex_min = min(X1i, X2i)
                Xindex_max = max(X1i, X2i)
                Yindex_min = min(Y1i, Y2i)
                Yindex_max = max(Y1i, Y2i)

                check_points = []
                if (Xindex_max > Xindex_min) and (abs(x2_G - x1_G) > Zero):
                    if (Yindex_max > Yindex_min) and (abs(y2_G - y1_G) > Zero):
                        check_points.append([X1i, Y1i])
                        check_points.append([X2i, Y2i])
                        # Establish line equation variables: y=m*x+b
                        m_G = (y2_G - y1_G) / (x2_G - x1_G)
                        b_G = y1_G - m_G * x1_G
                        # Add check point in each partition in the range of X
                        # values
                        x_ind_check = Xindex_min + 1
                        while x_ind_check <= Xindex_max - 1:
                            x_val = x_ind_check * xPartitionLength
                            y_val = m_G * x_val + b_G
                            y_ind_check = int(y_val / yPartitionLength)
                            check_points.append([x_ind_check, y_ind_check])
                            x_ind_check = x_ind_check + 1
                        # Add check point in each partition in the range of Y
                        # values
                        y_ind_check = Yindex_min + 1
                        while y_ind_check <= Yindex_max - 1:
                            y_val = y_ind_check * yPartitionLength
                            x_val = (y_val - b_G) / m_G
                            x_ind_check = int(x_val / xPartitionLength)
                            check_points.append([x_ind_check, y_ind_check])
                            y_ind_check = y_ind_check + 1
                    else:
                        x_ind_check = Xindex_min
                        y_ind_check = Yindex_min
                        while x_ind_check <= Xindex_max:
                            check_points.append([x_ind_check, y_ind_check])
                            x_ind_check = x_ind_check + 1
                else:
                    x_ind_check = Xindex_min
                    y_ind_check = Yindex_min
                    while y_ind_check <= Yindex_max:
                        check_points.append([x_ind_check, y_ind_check])
                        y_ind_check = y_ind_check + 1

                # For each grid box in check_points add the grid box and all
                # adjacent grid boxes to the list of boxes for this line
                # segment
                for xy_point in check_points:
                    xy_p = xy_point
                    xIndex = xy_p[0]
                    yIndex = xy_p[1]
                    for i in range(max(xIndex - 1, 0), min(xN, xIndex + 2)):
                        for j in range(
                            max(yIndex - 1, 0), min(yN, yIndex + 2)
                        ):
                            coded_index.append(int(i + j * xN))

                codedIndexSet = set(coded_index)

                for thisCode in codedIndexSet:
                    thisIndex = thisCode
                    line_R_appended = XY_R
                    line_R_appended.append(X_R)
                    line_R_appended.append(Y_R)
                    line_R_appended.append(R_R)
                    partitionList[int(thisIndex % xN)][
                        int(thisIndex / xN)
                    ].append(line_R_appended)
            #########################################################
            # End Determine active partitions for each line segment #
            #########################################################
            # Loop through again just to determine the total length of segments
            # For the percent complete calculation
            if v_index >= len(self.coords):
                v_index = len(self.coords)
            v_ind = v_index

            CUR_CNT = -1
            TOT_LENGTH = 0.0

            for line in range(len(self.coords)):
                CUR_CNT = CUR_CNT + 1
                v_ind = v_ind + v_inc
                x1 = self.coords[v_ind][i_x1]
                y1 = self.coords[v_ind][i_y1]
                x2 = self.coords[v_ind][i_x2]
                y2 = self.coords[v_ind][i_y2]
                LENGTH = sqrt((x2 - x1) * (x2 - x1) + (y2 - y1) * (y2 - y1))
                if clean_flag == 1:
                    if self.clean_segment[CUR_CNT] != 0:
                        TOT_LENGTH = TOT_LENGTH + LENGTH
                else:
                    TOT_LENGTH = TOT_LENGTH + LENGTH

            CUR_LENGTH = 0.0
            MAX_CNT = len(self.coords)
            CUR_CNT = -1
            START_TIME = time()

            # Update canvas with modified paths
            if not config.batch.get():
                self.Plot_Data()

            if TOT_LENGTH > 0.0:
                calc_flag = 1
                for line in range(len(self.coords)):
                    CUR_CNT = CUR_CNT + 1

                    if clean_flag == 0:
                        self.clean_segment.append(0)
                    elif len(self.clean_segment) != len(self.coords):
                        message.fmessage("Need to Recalculate V-Carve Path")
                        break
                    else:
                        calc_flag = self.clean_segment[CUR_CNT]

                    if not config.batch.get():
                        stamp = int(3 * time())  # update every 1/3 of a second
                        if stamp != timestamp:
                            timestamp = stamp  # interlock

                            CUR_PCT = float(CUR_LENGTH) / TOT_LENGTH * 100.0
                            if CUR_PCT > 0.0:
                                MIN_REMAIN = (
                                    (time() - START_TIME)
                                    / 60
                                    * (100 - CUR_PCT)
                                    / CUR_PCT
                                )
                                MIN_TOTAL = (
                                    100.0
                                    / CUR_PCT
                                    * (time() - START_TIME)
                                    / 60
                                )
                            else:
                                MIN_REMAIN = -1
                                MIN_TOTAL = -1

                            self.statusMessage.set(
                                "%.1f %% ( %.1f Minutes Remaining "
                                "| %.1f Minutes Total )"
                                % (CUR_PCT, MIN_REMAIN, MIN_TOTAL)
                            )
                            self.statusbar.configure(bg="yellow")
                            self.PreviewCanvas.update()

                    if self.STOP_CALC:
                        self.STOP_CALC = False

                        if clean_flag != 1:
                            self.vcoords = []
                        else:
                            self.clean_coords = []
                            calc_flag = 0
                        break

                    v_index = v_index + v_inc
                    New_Loop = 0
                    x1 = self.coords[v_index][i_x1]
                    y1 = self.coords[v_index][i_y1]
                    x2 = self.coords[v_index][i_x2]
                    y2 = self.coords[v_index][i_y2]
                    char_num = int(self.coords[v_index][5])
                    dx = x2 - x1
                    dy = y2 - y1
                    Lseg = sqrt(dx * dx + dy * dy)

                    if Lseg < Zero:  # was Acc
                        continue

                    # calculate the sin and cos of the coord transformation
                    # needed for the distance calculations
                    seg_sin = dy / Lseg
                    seg_cos = -dx / Lseg
                    phi = Get_Angle(seg_sin, seg_cos)

                    if calc_flag != 0:
                        CUR_LENGTH = CUR_LENGTH + Lseg
                    else:
                        theta = (
                            phi  # commented out in V1.62 brought back in V1.72
                        )
                        x0 = x2  # commented out in V1.62 brought back in V1.72
                        y0 = y2  # commented out in V1.62 brought back in V1.72
                        seg_sin0 = seg_sin  # commented out in V1.62 brought
                                            # back in V1.72
                        seg_cos0 = seg_cos  # commented out in V1.62 brought
                                            # back in V1.72
                        char_num0 = char_num  # commented out in V1.62 brought
                                              # back in V1.72
                        # Brought back because...
                        continue

                    if (
                        (fabs(x1 - x0) > Zero)
                        or (fabs(y1 - y0) > Zero)
                        or (char_num != char_num0)
                    ):
                        New_Loop = 1
                        loop_cnt = loop_cnt + 1
                        xa = float(x1)
                        ya = float(y1)
                        xb = float(x2)
                        yb = float(y2)
                        theta = 9999.0
                        seg_sin0 = 2
                        seg_cos0 = 2

                    if seg_cos0 > 1.0:
                        delta = 180
                    else:
                        xtmp1 = (x2 - x1) * seg_cos0 - (y2 - y1) * seg_sin0
                        ytmp1 = (x2 - x1) * seg_sin0 + (y2 - y1) * seg_cos0
                        Ltmp = sqrt(xtmp1 * xtmp1 + ytmp1 * ytmp1)
                        d_seg_sin = ytmp1 / Ltmp
                        d_seg_cos = xtmp1 / Ltmp
                        delta = Get_Angle(d_seg_sin, d_seg_cos)
                    if (
                        delta < float(v_drv_crner)
                        and BIT_ANGLE != 0
                        and not_b_carve
                        and clean_flag != 1
                    ):
                        # drive to corner
                        self.vcoords.append([x1, y1, 0.0, loop_cnt])

                    if delta > float(v_stp_crner):
                        # add sub-steps around corner
                        ###########################
                        phisteps = max(floor((delta - 180) / dangle), 2)
                        step_phi = (delta - 180) / phisteps
                        pcnt = 0
                        while pcnt < phisteps - 1:
                            pcnt = pcnt + 1
                            sub_phi = radians(-pcnt * step_phi + theta)
                            sub_seg_cos = cos(sub_phi)
                            sub_seg_sin = sin(sub_phi)

                            rout = find_max_circle(
                                x1,
                                y1,
                                rmax,
                                char_num,
                                sub_seg_sin,
                                sub_seg_cos,
                                1,
                                CHK_STRING,
                                self.MINX,
                                self.MINY,
                                xPartitionLength,
                                yPartitionLength,
                                partitionList,
                            )
                            if clean_flag != 1:
                                coords_destination = self.vcoords
                            else:
                                coords_destination = self.clean_coords
                            xv, yv, rv, clean_seg = record_v_carve_data(
                                x1,
                                y1,
                                sub_phi,
                                rout,
                                loop_cnt,
                                clean_flag,
                                rbit,
                                coords_destination,
                            )
                            self.clean_segment[CUR_CNT] = bool(
                                self.clean_segment[CUR_CNT]
                            ) or bool(clean_seg)
                            if (
                                config.v_pplot.get()
                                and (not config.batch.get())
                                and (clean_flag != 1)
                            ):
                                self.Plot_Circ(
                                    xv,
                                    yv,
                                    midx,
                                    midy,
                                    cszw,
                                    cszh,
                                    PlotScale,
                                    "blue",
                                    rv,
                                    0,
                                )
                    #############################
                    ### end for linec in self.coords
                    theta = phi
                    x0 = x2
                    y0 = y2
                    seg_sin0 = seg_sin
                    seg_cos0 = seg_cos
                    char_num0 = char_num

                    # Calculate the number of steps then the dx and dy for each
                    # step.
                    # Don't calculate at the joints.
                    nsteps = max(floor(Lseg / dline), 2)
                    dxpt = dx / nsteps
                    dypt = dy / nsteps

                    # This makes sure the first cut start at the beginning of
                    # the first segment
                    cnt = 0
                    if New_Loop == 1 and BIT_ANGLE != 0 and not_b_carve:
                        cnt = -1

                    seg_sin = dy / Lseg
                    seg_cos = -dx / Lseg
                    phi2 = radians(Get_Angle(seg_sin, seg_cos))
                    while cnt < nsteps - 1:
                        cnt = cnt + 1
                        # determine location of next step along outline
                        # (xpt, ypt)
                        xpt = x1 + dxpt * cnt
                        ypt = y1 + dypt * cnt

                        rout = find_max_circle(
                            xpt,
                            ypt,
                            rmax,
                            char_num,
                            seg_sin,
                            seg_cos,
                            0,
                            CHK_STRING,
                            self.MINX,
                            self.MINY,
                            xPartitionLength,
                            yPartitionLength,
                            partitionList,
                        )
                        # Make the first cut drive down at an angle instead of
                        # straight down plunge
                        if cnt == 0 and not_b_carve:
                            rout = 0.0
                        if clean_flag != 1:
                            coords_destination = self.vcoords
                        else:
                            coords_destination = self.clean_coords
                        xv, yv, rv, clean_seg = record_v_carve_data(
                            xpt,
                            ypt,
                            phi2,
                            rout,
                            loop_cnt,
                            clean_flag,
                            rbit,
                            coords_destination,
                        )

                        self.clean_segment[CUR_CNT] = bool(
                            self.clean_segment[CUR_CNT]
                        ) or bool(clean_seg)
                        if (
                            config.v_pplot.get()
                            and (not config.batch.get())
                            and (clean_flag != 1)
                        ):
                            self.master.update_idletasks()
                            self.Plot_Circ(
                                xv,
                                yv,
                                midx,
                                midy,
                                cszw,
                                cszh,
                                PlotScale,
                                "blue",
                                rv,
                                0,
                            )

                        if New_Loop == 1 and cnt == 1:
                            xpta = xpt
                            ypta = ypt
                            phi2a = phi2
                            routa = rout

                    #################################################
                    # Check to see if we need to close an open loop #
                    #################################################
                    if abs(x2 - xa) < Zero and abs(y2 - ya) < Zero:
                        xtmp1 = (xb - xa) * seg_cos0 - (yb - ya) * seg_sin0
                        ytmp1 = (xb - xa) * seg_sin0 + (yb - ya) * seg_cos0
                        Ltmp = sqrt(xtmp1 * xtmp1 + ytmp1 * ytmp1)
                        d_seg_sin = ytmp1 / Ltmp
                        d_seg_cos = xtmp1 / Ltmp
                        delta = Get_Angle(d_seg_sin, d_seg_cos)
                        if delta < v_drv_crner and clean_flag != 1:
                            # Drive to corner
                            self.vcoords.append([xa, ya, 0.0, loop_cnt])

                        elif delta > v_stp_crner:
                            # Add sub-steps around corner
                            phisteps = max(floor((delta - 180) / dangle), 2)
                            step_phi = (delta - 180) / phisteps
                            pcnt = 0

                            while pcnt < phisteps - 1:
                                pcnt = pcnt + 1
                                sub_phi = radians(-pcnt * step_phi + theta)
                                sub_seg_cos = cos(sub_phi)
                                sub_seg_sin = sin(sub_phi)

                                rout = find_max_circle(
                                    xa,
                                    ya,
                                    rmax,
                                    char_num,
                                    sub_seg_sin,
                                    sub_seg_cos,
                                    1,
                                    CHK_STRING,
                                    self.MINX,
                                    self.MINY,
                                    xPartitionLength,
                                    yPartitionLength,
                                    partitionList,
                                )
                                if clean_flag != 1:
                                    coords_destination = self.vcoords
                                else:
                                    coords_destination = self.clean_coords
                                xv, yv, rv, clean_seg = record_v_carve_data(
                                    xa,
                                    ya,
                                    sub_phi,
                                    rout,
                                    loop_cnt,
                                    clean_flag,
                                    rbit,
                                    coords_destination,
                                )
                                self.clean_segment[CUR_CNT] = bool(
                                    self.clean_segment[CUR_CNT]
                                ) or bool(clean_seg)
                                if (
                                    (config.v_pplot.get())
                                    and (not config.batch.get())
                                    and (clean_flag != 1)
                                ):
                                    self.Plot_Circ(
                                        xv,
                                        yv,
                                        midx,
                                        midy,
                                        cszw,
                                        cszh,
                                        PlotScale,
                                        "blue",
                                        rv,
                                        0,
                                    )

                            if clean_flag != 1:
                                coords_destination = self.vcoords
                            else:
                                coords_destination = self.clean_coords
                            xv, yv, rv, clean_seg = record_v_carve_data(
                                xpta,
                                ypta,
                                phi2a,
                                routa,
                                loop_cnt,
                                clean_flag,
                                rbit,
                                coords_destination,
                            )
                            self.clean_segment[CUR_CNT] = bool(
                                self.clean_segment[CUR_CNT]
                            ) or bool(clean_seg)
                        else:
                            # Add closing segment
                            if clean_flag != 1:
                                coords_destination = self.vcoords
                            else:
                                coords_destination = self.clean_coords
                            xv, yv, rv, clean_seg = record_v_carve_data(
                                xpta,
                                ypta,
                                phi2a,
                                routa,
                                loop_cnt,
                                clean_flag,
                                rbit,
                                coords_destination,
                            )
                            self.clean_segment[CUR_CNT] = bool(
                                self.clean_segment[CUR_CNT]
                            ) or bool(clean_seg)

                # end for line in self coords

                # Reset Entry Fields in V-Carve Settings
                if not config.batch.get():
                    self.entry_set(
                        self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), 1
                    )
                    self.entry_set(
                        self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), 1
                    )
                    self.entry_set(
                        self.Entry_VDepthLimit,
                        self.Entry_VDepthLimit_Check(),
                        1,
                    )
                    self.entry_set(
                        self.Entry_InsideAngle,
                        self.Entry_InsideAngle_Check(),
                        1,
                    )
                    self.entry_set(
                        self.Entry_OutsideAngle,
                        self.Entry_OutsideAngle_Check(),
                        1,
                    )
                    self.entry_set(
                        self.Entry_StepSize, self.Entry_StepSize_Check(), 1
                    )
                    self.entry_set(
                        self.Entry_Allowance, self.Entry_Allowance_Check(), 1
                    )
                    self.entry_set(
                        self.Entry_Accuracy, self.Entry_Accuracy_Check(), 1
                    )
                    self.entry_set(
                        self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), 1
                    )
                    self.entry_set(
                        self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), 1
                    )
                    self.entry_set(
                        self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(), 1
                    )

            if CUR_CNT == MAX_CNT - 1 and (not config.batch.get()):
                self.statusMessage.set("Done -- " + config.bounding_box.get())
                self.statusbar.configure(bg="white")

        self.master.bind("<Configure>", self.Master_Configure)
        #########################################
        # End V-Carve Stuff
        #########################################

    def sort_for_v_carve_status_callback(
        self, status=None, initialize=False, check_for_timeout=False
    ):
        config = self.config
        if not config.batch.get():
            if initialize:
                self.timestamp = time() - 1.0
                self.STOP_CALC = False
                return True
            if not status:
                return True
            if not check_for_timeout:
                self.statusMessage.set(status)
                self.master.update()
            else:
                # update every 1/3 of a second
                now = time()
                elapsed_seconds = time() - self.timestamp
                if elapsed_seconds >= 1.0 / 3.0:
                    self.timestamp = now
                    self.statusMessage.set(status)
                    self.master.update()
                    if self.STOP_CALC:
                        return False
        return True

    def Clean_Path_Calc(self, bit_radius, bit_type="straight"):
        config = self.config
        v_flop = get_flop_status(config, CLEAN_FLAG=True)
        if v_flop:
            edge = 1
        else:
            edge = 0
        loop_cnt = 0
        loop_cnt_out = 0
        #######################################
        # reorganize clean_coords              #
        #######################################
        if bit_type == "straight":
            test_clean = (
                config.clean_P.get() + config.clean_X.get() + config.clean_Y.get()
            )
        else:
            test_clean = (
                config.v_clean_P.get()
                + config.v_clean_Y.get()
                + config.v_clean_X.get()
            )

        check_coords = []

        self.statusbar.configure(bg="yellow")
        if bit_type == "straight":
            self.statusMessage.set("Calculating Cleanup Cut Paths")
            self.master.update()
            self.clean_coords_sort = []
            clean_dia = float(config.clean_dia.get())  # diameter of cleanup bit
            step_over = float(config.clean_step.get())  # percent of cut DIA
            clean_step = step_over / 100.0
            Radjust = clean_dia / 2.0 + bit_radius
            check_coords = self.clean_coords

        elif bit_type == "v-bit":
            self.statusMessage.set("Calculating V-Bit Cleanup Cut Paths")
            skip = 1
            clean_step = 1.0

            self.master.update()
            self.v_clean_coords_sort = []

            clean_dia = float(
                config.clean_v.get()
            )  # effective diameter of clean-up v-bit
            if float(clean_dia) < Zero:
                return
            # The next line allows the cutter to get within 1/4 of the
            # v-clean step of the v-carved surface.
            offset = clean_dia / 4.0
            Radjust = bit_radius + offset
            flat_clean_r = float(config.clean_dia.get()) / 2.0
            for line in self.clean_coords:
                XY = line
                R = XY[2] - Radjust
                if (R > 0.0) and (R < flat_clean_r - offset - Zero):
                    check_coords.append(XY)

        clean_coords_out = []
        if (
            config.cut_type.get() == "v-carve"
            and len(self.clean_coords) > 1
            and test_clean > 0
        ):
            DX = clean_dia * clean_step
            DY = DX

            if bit_type == "straight":
                MAXD = clean_dia
            else:
                MAXD = sqrt(DX ** 2 + DY ** 2) * 1.1  # fudge factor

            Xclean_coords = []
            Yclean_coords = []
            clean_coords_out = []

            ## NEW STUFF FOR STRAIGHT BIT ##
            if bit_type == "straight":
                MaxLoop = 0
                clean_dia = float(
                    config.clean_dia.get()
                )  # diameter of cleanup bit
                step_over = float(config.clean_step.get())  # percent of cut DIA
                clean_step = step_over / 100.0
                Rperimeter = bit_radius + (clean_dia / 2.0)

                ###################################################
                # Extract straight bit points from clean_coords
                ###################################################
                check_coords = []
                junk = -1
                for line in self.clean_coords:
                    XY = line
                    R = XY[2]
                    if R >= Rperimeter - Zero:
                        check_coords.append(XY)
                    elif len(check_coords) > 0:
                        junk = junk - 1
                        check_coords.append([None, None, None, junk])
                        # check_coords[len(check_coords)-1][3]=junk
                ###################################################
                # Calculate Straight bit "Perimeter" tool path ####
                ###################################################
                P_coords = []
                loop_coords = Clean_coords_to_Path_coords(check_coords)
                loop_coords = sort_for_v_carve(
                    loop_coords,
                    float(config.accuracy.get()),
                    self.sort_for_v_carve_status_callback,
                )

                #######################
                # Line fit loop_coords
                #######################
                P_coords = []
                if loop_coords:
                    cuts = []
                    Ln_last = loop_coords[0][4]
                    for i in range(len(loop_coords)):
                        Ln = loop_coords[i][4]
                        if Ln != Ln_last:
                            for move, (x, y, z), cent in douglas(
                                cuts, tolerance=0.0001, plane=None
                            ):
                                P_coords.append([x, y, clean_dia / 2, Ln_last])
                            cuts = []
                        cuts.append([loop_coords[i][0], loop_coords[i][1], 0])
                        cuts.append([loop_coords[i][2], loop_coords[i][3], 0])
                        Ln_last = Ln
                    if cuts:
                        for move, (x, y, z), cent in douglas(
                            cuts, tolerance=0.0001, plane=None
                        ):
                            P_coords.append([x, y, clean_dia / 2, Ln_last])
                #####################
                loop_coords = Clean_coords_to_Path_coords(P_coords)
                # Find min/max values for x,y and the highest loop number
                x_pmin = 99999
                x_pmax = -99999
                y_pmin = 99999
                y_pmax = -99999
                for i in range(len(P_coords)):
                    MaxLoop = max(MaxLoop, P_coords[i][3])
                    x_pmin = min(x_pmin, P_coords[i][0])
                    x_pmax = max(x_pmax, P_coords[i][0])
                    y_pmin = min(y_pmin, P_coords[i][1])
                    y_pmax = max(y_pmax, P_coords[i][1])
                loop_cnt_out = loop_cnt_out + MaxLoop

                if config.clean_P.get():
                    clean_coords_out = P_coords

                offset = DX / 2.0
                if config.clean_X.get():
                    y_pmax = y_pmax - offset
                    y_pmin = y_pmin + offset
                    Ysize = y_pmax - y_pmin
                    Ysteps = ceil(Ysize / (clean_dia * clean_step))
                    if Ysteps > 0:
                        for iY in range(0, int(Ysteps + 1)):
                            y = y_pmin + iY / Ysteps * (y_pmax - y_pmin)
                            intXYlist = DetectIntersect(
                                [x_pmin - 1, y],
                                [x_pmax + 1, y],
                                loop_coords,
                                XY_T_F=True,
                            )
                            intXY_len = len(intXYlist)

                            for i in range(edge, intXY_len - 1 - edge, 2):
                                x1 = intXYlist[i][0]
                                y1 = intXYlist[i][1]
                                x2 = intXYlist[i + 1][0]
                                y2 = intXYlist[i + 1][1]
                                if (x2 - x1) > offset * 2:
                                    loop_cnt = loop_cnt + 1
                                    Xclean_coords.append(
                                        [x1 + offset, y1, loop_cnt]
                                    )
                                    Xclean_coords.append(
                                        [x2 - offset, y2, loop_cnt]
                                    )

                if config.clean_Y.get():
                    x_pmax = x_pmax - offset
                    x_pmin = x_pmin + offset
                    Xsize = x_pmax - x_pmin
                    Xsteps = ceil(Xsize / (clean_dia * clean_step))
                    if Xsteps > 0:
                        for iX in range(0, int(Xsteps + 1)):
                            x = x_pmin + iX / Xsteps * (x_pmax - x_pmin)
                            intXYlist = DetectIntersect(
                                [x, y_pmin - 1],
                                [x, y_pmax + 1],
                                loop_coords,
                                XY_T_F=True,
                            )
                            intXY_len = len(intXYlist)
                            for i in range(edge, intXY_len - 1 - edge, 2):
                                x1 = intXYlist[i][0]
                                y1 = intXYlist[i][1]
                                x2 = intXYlist[i + 1][0]
                                y2 = intXYlist[i + 1][1]
                                if (y2 - y1) > offset * 2:
                                    loop_cnt = loop_cnt + 1
                                    Yclean_coords.append(
                                        [x1, y1 + offset, loop_cnt]
                                    )
                                    Yclean_coords.append(
                                        [x2, y2 - offset, loop_cnt]
                                    )
            ## END NEW STUFF FOR STRAIGHT BIT ##

            #######################################
            ## START V-BIT CLEANUP CALCULATIONS  ##
            #######################################
            elif bit_type == "v-bit":
                # Find ends of horizontal lines for carving clean-up
                Xclean_perimeter, Xclean_coords = Find_Paths(
                    check_coords, clean_dia, Radjust, clean_step, skip, "X"
                )

                # Find ends of Vertical lines for carving clean-up
                Yclean_perimeter, Yclean_coords = Find_Paths(
                    check_coords, clean_dia, Radjust, clean_step, skip, "Y"
                )

                #######################################################
                # Find new order based on distance                    #
                #######################################################
                if config.v_clean_P.get():
                    ########################################
                    ecoords = []
                    for line in Xclean_perimeter:
                        XY = line
                        ecoords.append([XY[0], XY[1]])

                    for line in Yclean_perimeter:
                        XY = line
                        ecoords.append([XY[0], XY[1]])

                    ################
                    ###   ends   ###
                    ################
                    Lbeg = []
                    for i in range(1, len(ecoords)):
                        Lbeg.append(i)

                    ########################################
                    order_out = []
                    if len(ecoords) > 0:
                        order_out.append(Lbeg[0])
                    inext = 0
                    total = len(Lbeg)
                    for i in range(total - 1):
                        ii = Lbeg.pop(inext)
                        Xcur = ecoords[ii][0]
                        Ycur = ecoords[ii][1]
                        dx = Xcur - ecoords[Lbeg[0]][0]
                        dy = Ycur - ecoords[Lbeg[0]][1]
                        min_dist = dx * dx + dy * dy

                        inext = 0
                        for j in range(1, len(Lbeg)):
                            dx = Xcur - ecoords[Lbeg[j]][0]
                            dy = Ycur - ecoords[Lbeg[j]][1]
                            dist = dx * dx + dy * dy
                            if dist < min_dist:
                                min_dist = dist
                                inext = j
                        order_out.append(Lbeg[inext])

                    x_start_loop = -8888
                    y_start_loop = -8888
                    x_old = -999
                    y_old = -999
                    for i in order_out:
                        x1 = ecoords[i][0]
                        y1 = ecoords[i][1]
                        dx = x1 - x_old
                        dy = y1 - y_old
                        dist = sqrt(dx * dx + dy * dy)
                        if dist > MAXD:
                            dx = x_start_loop - x_old
                            dy = y_start_loop - y_old
                            dist = sqrt(dx * dx + dy * dy)
                            # Fully close loop if the current point is close
                            # enough to the start of the loop
                            if dist < MAXD:
                                clean_coords_out.append(
                                    [
                                        x_start_loop,
                                        y_start_loop,
                                        clean_dia / 2,
                                        loop_cnt_out,
                                    ]
                                )
                            loop_cnt_out = loop_cnt_out + 1
                            x_start_loop = x1
                            y_start_loop = y1
                        clean_coords_out.append(
                            [x1, y1, clean_dia / 2, loop_cnt_out]
                        )
                        x_old = x1
                        y_old = y1
            #####################################
            ## END V-BIT CLEANUP CALCULATIONS  ##
            #####################################

            ###########################################################
            # Now deal with the horizontal line cuts
            ###########################################################
            if (config.clean_X.get() and bit_type != "v-bit") or (
                config.v_clean_X.get() and bit_type == "v-bit"
            ):
                x_old = -999
                y_old = -999
                order_out = Sort_Paths(Xclean_coords)
                loop_old = -1
                for line in order_out:
                    temp = line
                    if temp[0] > temp[1]:
                        step = -1
                    else:
                        step = 1
                    for i in range(temp[0], temp[1] + step, step):
                        x1 = Xclean_coords[i][0]
                        y1 = Xclean_coords[i][1]
                        loop = Xclean_coords[i][2]
                        dx = x1 - x_old
                        dy = y1 - y_old
                        dist = sqrt(dx * dx + dy * dy)
                        if dist > MAXD and loop != loop_old:
                            loop_cnt_out = loop_cnt_out + 1
                        clean_coords_out.append(
                            [x1, y1, clean_dia / 2, loop_cnt_out]
                        )
                        x_old = x1
                        y_old = y1
                        loop_old = loop

            ###########################################################
            # Now deal with the vertical line cuts
            ###########################################################
            if (config.clean_Y.get() and bit_type != "v-bit") or (
                config.v_clean_Y.get() and bit_type == "v-bit"
            ):
                x_old = -999
                y_old = -999
                order_out = Sort_Paths(Yclean_coords)
                loop_old = -1
                for line in order_out:
                    temp = line
                    if temp[0] > temp[1]:
                        step = -1
                    else:
                        step = 1
                    for i in range(temp[0], temp[1] + step, step):
                        x1 = Yclean_coords[i][0]
                        y1 = Yclean_coords[i][1]
                        loop = Yclean_coords[i][2]
                        dx = x1 - x_old
                        dy = y1 - y_old
                        dist = sqrt(dx * dx + dy * dy)
                        if dist > MAXD and loop != loop_old:
                            loop_cnt_out = loop_cnt_out + 1
                        clean_coords_out.append(
                            [x1, y1, clean_dia / 2, loop_cnt_out]
                        )
                        x_old = x1
                        y_old = y1
                        loop_old = loop

            self.entry_set(
                self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), 1
            )
            self.entry_set(
                self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), 1
            )
            self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(), 1)

            if bit_type == "v-bit":
                self.v_clean_coords_sort = clean_coords_out
            else:
                self.clean_coords_sort = clean_coords_out
        self.statusMessage.set("Done Calculating Cleanup Cut Paths")
        self.statusbar.configure(bg="white")
        self.master.update_idletasks()

    #######################################
    # End Reorganize                       #
    #######################################

    # Bitmap Settings Window
    # Algorithm options:
    # -z, --turnpolicy policy    - how to resolve ambiguities in path
    #                              decomposition
    # -t, --turdsize n           - suppress speckles of up to this size
    #                              (default 2)
    # -a, --alphama n           - corner threshold parameter (default 1)
    # -n, --longcurve            - turn off curve optimization
    # -O, --opttolerance n       - curve optimization tolerance (default 0.2)
    def PBM_Settings_Window(self):
        config = self.config
        pbm_settings = Toplevel(width=525, height=250)
        # Use grab_set to prevent user input in the
        # main window during calculations
        pbm_settings.grab_set()
        pbm_settings.resizable(0, 0)
        pbm_settings.title("Bitmap Settings")
        pbm_settings.iconname("Bitmap Settings")

        D_Yloc = 12
        D_dY = 24
        xd_label_L = 12

        w_label = 100
        w_entry = 60
        xd_entry_L = xd_label_L + w_label + 10

        D_Yloc = D_Yloc + D_dY
        self.Label_BMPturnpol = Label(pbm_settings, text="Turn Policy")
        self.Label_BMPturnpol.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )

        self.BMPturnpol_OptionMenu = OptionMenu(
            pbm_settings,
            config.bmp_turnpol.TK,
            "black",
            "white",
            "right",
            "left",
            "minority",
            "majority",
            "random",
        )
        self.BMPturnpol_OptionMenu.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry + 40, height=23
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_BMPturdsize = Label(pbm_settings, text="Turd Size")
        self.Label_BMPturdsize.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Entry_BMPturdsize = Entry(pbm_settings, width="15")
        self.Entry_BMPturdsize.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_BMPturdsize.configure(textvariable=config.bmp_turdsize.TK)
        config.bmp_turdsize.TK.trace_variable("w", self.Entry_BMPturdsize_Callback)
        self.Label_BMPturdsize2 = Label(
            pbm_settings, text="Suppress speckles of up to this pixel size"
        )
        self.Label_BMPturdsize2.place(
            x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21
        )
        self.entry_set(
            self.Entry_BMPturdsize, self.Entry_BMPturdsize_Check(), 2
        )

        D_Yloc = D_Yloc + D_dY + 5
        self.Label_BMPalphamax = Label(pbm_settings, text="Alpha Max")
        self.Label_BMPalphamax.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Entry_BMPalphamax = Entry(pbm_settings, width="15")
        self.Entry_BMPalphamax.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_BMPalphamax.configure(textvariable=config.bmp_alphamax.TK)
        config.bmp_alphamax.TK.trace_variable("w", self.Entry_BMPalphamax_Callback)
        self.Label_BMPalphamax2 = Label(
            pbm_settings, text="0.0 = sharp corners, 1.33 = smoothed corners"
        )
        self.Label_BMPalphamax2.place(
            x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21
        )
        self.entry_set(
            self.Entry_BMPalphamax, self.Entry_BMPalphamax_Check(), 2
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_BMP_longcurve = Label(pbm_settings, text="Long Curve")
        self.Label_BMP_longcurve.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Checkbutton_BMP_longcurve = Checkbutton(
            pbm_settings, text="", anchor=W
        )
        self.Checkbutton_BMP_longcurve.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_BMP_longcurve.configure(variable=config.bmp_longcurve.TK)
        self.Label_BMP_longcurve2 = Label(
            pbm_settings, text="Enable Curve Optimization"
        )
        self.Label_BMP_longcurve2.place(
            x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_BMPoptTolerance = Label(pbm_settings, text="Opt Tolerance")
        self.Label_BMPoptTolerance.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Entry_BMPoptTolerance = Entry(pbm_settings, width="15")
        self.Entry_BMPoptTolerance.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_BMPoptTolerance.configure(
            textvariable=config.bmp_opttolerance.TK
        )
        self.bmp_opttolerance.TK.trace_variable(
            "w", self.Entry_BMPoptTolerance_Callback
        )
        self.Label_BMPoptTolerance2 = Label(
            pbm_settings, text="Curve Optimization Tolerance"
        )
        self.Label_BMPoptTolerance2.place(
            x=xd_entry_L + w_entry * 1.5, y=D_Yloc, width=300, height=21
        )
        self.entry_set(
            self.Entry_BMPoptTolerance, self.Entry_BMPoptTolerance_Check(), 2
        )

        pbm_settings.update_idletasks()
        Ybut = int(pbm_settings.winfo_height()) - 30
        Xbut = int(pbm_settings.winfo_width() / 2)

        self.PBM_Reload = Button(pbm_settings, text="Re-Load Image")
        self.PBM_Reload.place(x=Xbut, y=Ybut, width=130, height=30, anchor="e")
        self.PBM_Reload.bind("<ButtonRelease-1>", self.Settings_ReLoad_Click)

        self.PBM_Close = Button(pbm_settings, text="Close")
        self.PBM_Close.place(x=Xbut, y=Ybut, width=130, height=30, anchor="w")
        self.PBM_Close.bind(
            "<ButtonRelease-1>", self.Close_Current_Window_Click
        )

        try:
            pbm_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                pbm_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

    # General Settings Window
    def GEN_Settings_Window(self):
        config = self.config
        gen_settings = Toplevel(width=600, height=500)
        # Use grab_set to prevent user input in the
        # main window during calculations
        gen_settings.grab_set()
        gen_settings.resizable(0, 0)
        gen_settings.title("Settings")
        gen_settings.iconname("Settings")

        try:
            gen_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                gen_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

        D_Yloc = 6
        D_dY = 24
        xd_label_L = 12

        dlta = 40
        w_label = 110 + 25 + dlta
        w_entry = 60
        w_units = 35
        xd_entry_L = xd_label_L + w_label + 10 + dlta
        xd_units_L = xd_entry_L + w_entry + 5
        x_radio_offset = 62

        # Radio Button
        D_Yloc = D_Yloc + D_dY
        self.Label_Units = Label(gen_settings, text="Units")
        self.Label_Units.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )

        self.Radio_Units_IN = Radiobutton(
            gen_settings, text="inch", value="in", width="100", anchor=W
        )
        self.Radio_Units_IN.place(
            x=w_label + x_radio_offset, y=D_Yloc, width=75, height=23
        )
        self.Radio_Units_IN.configure(
            variable=config.units.TK, command=self.Entry_units_var_Callback
        )

        self.Radio_Units_MM = Radiobutton(
            gen_settings, text="mm", value="mm", width="100", anchor=W
        )
        self.Radio_Units_MM.place(
            x=w_label + x_radio_offset + 60, y=D_Yloc, width=75, height=23
        )
        self.Radio_Units_MM.configure(
            variable=config.units.TK, command=self.Entry_units_var_Callback
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_Xoffset = Label(gen_settings, text="X Offset")
        self.Label_Xoffset.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_Xoffset_u = Label(
            gen_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_Xoffset_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_Xoffset = Entry(gen_settings, width="15")
        self.Entry_Xoffset.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_Xoffset.configure(textvariable=config.xorigin.TK)
        config.xorigin.TK.trace_variable("w", self.Entry_Xoffset_Callback)
        self.entry_set(self.Entry_Xoffset, self.Entry_Xoffset_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Yoffset = Label(gen_settings, text="Y Offset")
        self.Label_Yoffset.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_Yoffset_u = Label(
            gen_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_Yoffset_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_Yoffset = Entry(gen_settings, width="15")
        self.Entry_Yoffset.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_Yoffset.configure(textvariable=config.yorigin.TK)
        config.yorigin.TK.trace_variable("w", self.Entry_Yoffset_Callback)
        self.entry_set(self.Entry_Yoffset, self.Entry_Yoffset_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_ArcAngle = Label(gen_settings, text="Arc Angle")
        self.Label_ArcAngle.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_ArcAngle_u = Label(gen_settings, text="deg", anchor=W)
        self.Label_ArcAngle_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_ArcAngle = Entry(gen_settings, width="15")
        self.Entry_ArcAngle.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_ArcAngle.configure(textvariable=config.segarc.TK)
        config.segarc.TK.trace_variable("w", self.Entry_ArcAngle_Callback)
        self.entry_set(self.Entry_ArcAngle, self.Entry_ArcAngle_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Accuracy = Label(gen_settings, text="Accuracy")
        self.Label_Accuracy.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_Accuracy_u = Label(
            gen_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_Accuracy_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_Accuracy = Entry(gen_settings, width="15")
        self.Entry_Accuracy.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_Accuracy.configure(textvariable=config.accuracy.TK)
        config.accuracy.TK.trace_variable("w", self.Entry_Accuracy_Callback)
        self.entry_set(self.Entry_Accuracy, self.Entry_Accuracy_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_ext_char = Label(gen_settings, text="Extended Characters")
        self.Label_ext_char.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Checkbutton_ext_char = Checkbutton(
            gen_settings, text="", anchor=W
        )
        self.Checkbutton_ext_char.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_ext_char.configure(variable=config.ext_char.TK)
        config.ext_char.TK.trace_variable("w", self.Settings_ReLoad_Click)

        D_Yloc = D_Yloc + D_dY
        self.Label_arcfit = Label(gen_settings, text="Arc Fitting")
        self.Label_arcfit.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Radio_arcfit_none = Radiobutton(
            gen_settings, text="None", value="none", width="110", anchor=W
        )
        self.Radio_arcfit_none.place(
            x=w_label + x_radio_offset, y=D_Yloc, width=90, height=23
        )
        self.Radio_arcfit_none.configure(variable=config.arc_fit.TK)
        self.Radio_arcfit_radius = Radiobutton(
            gen_settings,
            text="Radius Format",
            value="radius",
            width="110",
            anchor=W,
        )
        self.Radio_arcfit_radius.place(
            x=w_label + x_radio_offset + 65, y=D_Yloc, width=100, height=23
        )
        self.Radio_arcfit_radius.configure(variable=config.arc_fit.TK)
        self.Radio_arcfit_center = Radiobutton(
            gen_settings,
            text="Center Format",
            value="center",
            width="110",
            anchor=W,
        )
        self.Radio_arcfit_center.place(
            x=w_label + x_radio_offset + 65 + 115,
            y=D_Yloc,
            width=100,
            height=23,
        )
        self.Radio_arcfit_center.configure(variable=config.arc_fit.TK)

        D_Yloc = D_Yloc + D_dY
        self.Label_no_com = Label(gen_settings, text="Suppress Comments")
        self.Label_no_com.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Checkbutton_no_com = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_no_com.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_no_com.configure(variable=config.no_comments.TK)

        D_Yloc = D_Yloc + D_dY
        self.Label_Gpre = Label(gen_settings, text="G Code Header")
        self.Label_Gpre.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)
        self.Entry_Gpre = Entry(gen_settings, width="15")
        self.Entry_Gpre.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpre.configure(textvariable=config.gpre.TK)

        D_Yloc = D_Yloc + D_dY
        self.Label_Gpost = Label(gen_settings, text="G Code Postscript")
        self.Label_Gpost.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Entry_Gpost = Entry(gen_settings)
        self.Entry_Gpost.place(x=xd_entry_L, y=D_Yloc, width=300, height=23)
        self.Entry_Gpost.configure(textvariable=config.gpost.TK)

        D_Yloc = D_Yloc + D_dY
        self.Label_var_dis = Label(gen_settings, text="Disable Variables")
        self.Label_var_dis.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Checkbutton_var_dis = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_var_dis.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_var_dis.configure(variable=config.var_dis.TK)

        D_Yloc = D_Yloc + D_dY
        font_entry_width = 215
        self.Label_Fontdir = Label(gen_settings, text="Font Directory")
        self.Label_Fontdir.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Entry_Fontdir = Entry(gen_settings, width="15")
        self.Entry_Fontdir.place(
            x=xd_entry_L, y=D_Yloc, width=font_entry_width, height=23
        )
        self.Entry_Fontdir.configure(textvariable=config.fontdir.TK)
        self.Fontdir = Button(gen_settings, text="Select Dir")
        self.Fontdir.place(
            x=xd_entry_L + font_entry_width + 10,
            y=D_Yloc,
            width=w_label - 80,
            height=23,
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_Hcalc = Label(gen_settings, text="Height Calculation")
        self.Label_Hcalc.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )

        self.Radio_Hcalc_USE = Radiobutton(
            gen_settings,
            text="Max Used",
            value="max_use",
            width="110",
            anchor=W,
        )
        self.Radio_Hcalc_USE.place(
            x=w_label + x_radio_offset, y=D_Yloc, width=90, height=23
        )
        self.Radio_Hcalc_USE.configure(variable=config.H_CALC.TK)

        self.Radio_Hcalc_ALL = Radiobutton(
            gen_settings,
            text="Max All",
            value="max_all",
            width="110",
            anchor=W,
        )
        self.Radio_Hcalc_ALL.place(
            x=w_label + x_radio_offset + 90, y=D_Yloc, width=90, height=23
        )
        self.Radio_Hcalc_ALL.configure(variable=config.H_CALC.TK)

        if config.input_type.get() != "text":
            self.Entry_Fontdir.configure(state="disabled")
            self.Fontdir.configure(state="disabled")
            self.Radio_Hcalc_ALL.configure(state="disabled")
            self.Radio_Hcalc_USE.configure(state="disabled")
        else:
            self.Fontdir.bind("<ButtonRelease-1>", self.Fontdir_Click)

        D_Yloc = D_Yloc + 24
        self.Label_Box = Label(gen_settings, text="Add Box/Circle")
        self.Label_Box.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Checkbutton_plotbox = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_plotbox.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_plotbox.configure(variable=config.plotbox.TK)
        config.plotbox.TK.trace_variable("w", self.Entry_Box_Callback)

        self.Label_BoxGap = Label(
            gen_settings, text="Box/Circle Gap:", anchor=E
        )
        self.Label_BoxGap.place(
            x=w_label + x_radio_offset + 25, y=D_Yloc, width=125, height=21
        )
        self.Entry_BoxGap = Entry(gen_settings)
        self.Entry_BoxGap.place(
            x=w_label + x_radio_offset + 165,
            y=D_Yloc,
            width=w_entry,
            height=23,
        )
        self.Entry_BoxGap.configure(textvariable=config.boxgap.TK)
        config.boxgap.TK.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(
            gen_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_BoxGap_u.place(
            x=w_label + x_radio_offset + 230, y=D_Yloc, width=100, height=21
        )
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_v_pplot = Label(
            gen_settings, text="Plot During V-Carve Calculation"
        )
        self.Label_v_pplot.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Checkbutton_v_pplot = Checkbutton(gen_settings, text="", anchor=W)
        self.Checkbutton_v_pplot.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_v_pplot.configure(variable=config.v_pplot.TK)

        D_Yloc = D_Yloc + D_dY + 10
        self.Label_SaveConfig = Label(gen_settings, text="Configuration File")
        self.Label_SaveConfig.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.GEN_SaveConfig = Button(gen_settings, text="Save")
        self.GEN_SaveConfig.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=21, anchor="nw"
        )
        self.GEN_SaveConfig.bind("<ButtonRelease-1>", self.Write_Config_File)

        ## Buttons ##
        gen_settings.update_idletasks()
        Ybut = int(gen_settings.winfo_height()) - 30
        Xbut = int(gen_settings.winfo_width() / 2)

        self.GEN_Reload = Button(gen_settings, text="Recalculate")
        self.GEN_Reload.place(
            x=Xbut - 65, y=Ybut, width=130, height=30, anchor="e"
        )
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Recalculate_Click)

        self.GEN_Recalculate = Button(gen_settings, text="Re-Load Image")
        self.GEN_Recalculate.place(
            x=Xbut, y=Ybut, width=130, height=30, anchor="c"
        )
        self.GEN_Recalculate.bind(
            "<ButtonRelease-1>", self.Settings_ReLoad_Click
        )

        self.GEN_Close = Button(gen_settings, text="Close")
        self.GEN_Close.place(
            x=Xbut + 65, y=Ybut, width=130, height=30, anchor="w"
        )
        self.GEN_Close.bind(
            "<ButtonRelease-1>", self.Close_Current_Window_Click
        )

    # V-Carve Settings window
    def VCARVE_Settings_Window(self):
        config = self.config
        vcarve_settings = Toplevel(width=580, height=690)
        # Use grab_set to prevent user input in the
        # main window during calculations
        vcarve_settings.grab_set()
        vcarve_settings.resizable(0, 0)
        vcarve_settings.title("V-Carve Settings")
        vcarve_settings.iconname("V-Carve Settings")

        try:
            vcarve_settings.iconbitmap(bitmap="@emblem64")
        except:
            try:  # Attempt to create temporary icon bitmap file
                temp_icon("f_engrave_icon")
                vcarve_settings.iconbitmap("@f_engrave_icon")
                os.remove("f_engrave_icon")
            except:
                pass

        D_Yloc = 12
        D_dY = 24
        xd_label_L = 12

        w_label = 250
        w_entry = 60
        w_units = 35
        xd_entry_L = xd_label_L + w_label + 10
        xd_units_L = xd_entry_L + w_entry + 5

        # ----------------------
        self.Label_cutter_type = Label(vcarve_settings, text="Cutter Type")
        self.Label_cutter_type.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )

        self.Radio_Type_VBIT = Radiobutton(
            vcarve_settings, text="V-Bit", value="VBIT", width="100", anchor=W
        )
        self.Radio_Type_VBIT.place(
            x=xd_entry_L, y=D_Yloc, width=w_label, height=21
        )
        self.Radio_Type_VBIT.configure(variable=config.bit_shape.TK)

        D_Yloc = D_Yloc + 24
        self.Radio_Type_BALL = Radiobutton(
            vcarve_settings,
            text="Ball Nose",
            value="BALL",
            width="100",
            anchor=W,
        )
        self.Radio_Type_BALL.place(
            x=xd_entry_L, y=D_Yloc, width=w_label, height=21
        )
        self.Radio_Type_BALL.configure(variable=config.bit_shape.TK)

        D_Yloc = D_Yloc + 24
        self.Radio_Type_STRAIGHT = Radiobutton(
            vcarve_settings,
            text="Straight",
            value="FLAT",
            width="100",
            anchor=W,
        )
        self.Radio_Type_STRAIGHT.place(
            x=xd_entry_L, y=D_Yloc, width=w_label, height=21
        )
        self.Radio_Type_STRAIGHT.configure(variable=config.bit_shape.TK)

        config.bit_shape.TK.trace_variable("w", self.Entry_Bit_Shape_var_Callback)
        # ----------------------

        D_Yloc = D_Yloc + D_dY
        self.Label_Vbitangle = Label(vcarve_settings, text="V-Bit Angle")
        self.Label_Vbitangle.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_Vbitangle_u = Label(vcarve_settings, text="deg", anchor=W)
        self.Label_Vbitangle_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_Vbitangle = Entry(vcarve_settings, width="15")
        self.Entry_Vbitangle.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_Vbitangle.configure(textvariable=config.v_bit_angle.TK)
        config.v_bit_angle.TK.trace_variable("w", self.Entry_Vbitangle_Callback)
        self.entry_set(self.Entry_Vbitangle, self.Entry_Vbitangle_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_Vbitdia = Label(vcarve_settings, text="V-Bit Diameter")
        self.Label_Vbitdia.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_Vbitdia_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_Vbitdia_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_Vbitdia = Entry(vcarve_settings, width="15")
        self.Entry_Vbitdia.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_Vbitdia.configure(textvariable=config.v_bit_dia.TK)
        config.v_bit_dia.TK.trace_variable("w", self.Entry_Vbitdia_Callback)
        self.entry_set(self.Entry_Vbitdia, self.Entry_Vbitdia_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_VDepthLimit = Label(vcarve_settings, text="Cut Depth Limit")
        self.Label_VDepthLimit.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_VDepthLimit_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_VDepthLimit_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_VDepthLimit = Entry(vcarve_settings, width="15")
        self.Entry_VDepthLimit.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_VDepthLimit.configure(textvariable=config.v_depth_lim.TK)
        config.v_depth_lim.TK.trace_variable("w", self.Entry_VDepthLimit_Callback)
        self.entry_set(
            self.Entry_VDepthLimit, self.Entry_VDepthLimit_Check(), 2
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_maxcut = Label(vcarve_settings, text="Max Cut Depth")
        self.Label_maxcut.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_maxcut_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_maxcut_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Label_maxcut_i = Label(
            vcarve_settings, textvariable=config.maxcut.TK, anchor=W
        )
        self.Label_maxcut_i.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=21
        )

        D_Yloc = D_Yloc + D_dY + 5
        self.Label_StepSize = Label(vcarve_settings, text="Sub-Step Length")
        self.Label_StepSize.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_StepSize_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_StepSize_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_StepSize = Entry(vcarve_settings, width="15")
        self.Entry_StepSize.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_StepSize.configure(textvariable=config.v_step_len.TK)
        config.v_step_len.TK.trace_variable("w", self.Entry_StepSize_Callback)
        self.entry_set(self.Entry_StepSize, self.Entry_StepSize_Check(), 2)

        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator00 = Frame(
            vcarve_settings, height=2, bd=1, relief=SUNKEN
        )
        self.vcarve_separator00.place(x=0, y=D_Yloc, width=580, height=2)

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_v_flop = Label(
            vcarve_settings, text="Flip Normals (Cut Outside)"
        )
        self.Label_v_flop.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Checkbutton_v_flop = Checkbutton(
            vcarve_settings, text="", anchor=W
        )
        self.Checkbutton_v_flop.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_v_flop.configure(variable=config.v_flop.TK)
        config.v_flop.TK.trace_variable("w", self.Entry_recalc_var_Callback)

        x_radio_offset = 62 - 40
        D_Yloc = D_Yloc + 24
        self.Label_vBox = Label(vcarve_settings, text="Add Box (Flip Normals)")
        self.Label_vBox.place(x=xd_label_L, y=D_Yloc, width=w_label, height=21)

        self.Checkbutton_plotbox = Checkbutton(
            vcarve_settings, text="", anchor=W
        )
        self.Checkbutton_plotbox.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_plotbox.configure(variable=config.plotbox.TK)
        config.plotbox.TK.trace_variable("w", self.Entry_Box_Callback)

        self.Label_BoxGap = Label(vcarve_settings, text="Box Gap:", anchor=E)
        self.Label_BoxGap.place(
            x=w_label + x_radio_offset + 25, y=D_Yloc, width=75, height=21
        )
        self.Entry_BoxGap = Entry(vcarve_settings)
        self.Entry_BoxGap.place(
            x=w_label + x_radio_offset + 110,
            y=D_Yloc,
            width=w_entry,
            height=23,
        )
        self.Entry_BoxGap.configure(textvariable=config.boxgap.TK)
        config.boxgap.TK.trace_variable("w", self.Entry_BoxGap_Callback)
        self.Label_BoxGap_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_BoxGap_u.place(
            x=w_label + x_radio_offset + 305, y=D_Yloc, width=100, height=21
        )
        self.entry_set(self.Entry_BoxGap, self.Entry_BoxGap_Check(), 2)

        self.Label_BoxGap_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_BoxGap_u.place(
            x=w_label + x_radio_offset + 175, y=D_Yloc, width=100, height=21
        )

        self.GEN_Reload = Button(vcarve_settings, text="Recalculate")
        self.GEN_Reload.place(
            x=580 - 10, y=D_Yloc, width=90, height=25, anchor="ne"
        )
        self.GEN_Reload.bind("<ButtonRelease-1>", self.Recalculate_Click)

        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator0 = Frame(
            vcarve_settings, height=2, bd=1, relief=SUNKEN
        )
        self.vcarve_separator0.place(x=0, y=D_Yloc, width=580, height=2)

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_inlay = Label(
            vcarve_settings, text="Prismatic (For inlay also select Add Box)"
        )
        self.Label_inlay.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Checkbutton_inlay = Checkbutton(
            vcarve_settings, text="", anchor=W
        )
        self.Checkbutton_inlay.place(
            x=xd_entry_L, y=D_Yloc, width=75, height=23
        )
        self.Checkbutton_inlay.configure(variable=config.inlay.TK)
        config.inlay.TK.trace_variable("w", self.Entry_Prismatic_Callback)

        D_Yloc = D_Yloc + D_dY
        self.Label_Allowance = Label(vcarve_settings, text="Prismatic Overcut")
        self.Label_Allowance.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_Allowance_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_Allowance_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_Allowance = Entry(vcarve_settings, width="15")
        self.Entry_Allowance.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_Allowance.configure(textvariable=config.allowance.TK)
        config.allowance.TK.trace_variable("w", self.Entry_Allowance_Callback)
        self.entry_set(self.Entry_Allowance, self.Entry_Allowance_Check(), 2)

        ### Update Idle tasks before requesting anything from winfo
        vcarve_settings.update_idletasks()
        center_loc = int(float(vcarve_settings.winfo_width()) / 2)

        ## Multi-pass Settings ##
        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator1 = Frame(
            vcarve_settings, height=2, bd=1, relief=SUNKEN
        )
        self.vcarve_separator1.place(x=0, y=D_Yloc, width=580, height=2)

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_multipass = Label(vcarve_settings, text="Multipass Cutting")
        self.Label_multipass.place(
            x=center_loc, y=D_Yloc, width=w_label, height=21, anchor=CENTER
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_v_rough_stk = Label(
            vcarve_settings, text="V-Carve Finish Pass Stock"
        )
        self.Label_v_rough_stk.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_v_rough_stk_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_v_rough_stk_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )

        self.Label_right_v_rough_stk = Label(
            vcarve_settings, text="(Zero disables multipass cutting)", anchor=W
        )
        self.Label_right_v_rough_stk.place(
            x=xd_units_L + 20, y=D_Yloc, width=w_label, height=21
        )

        self.Entry_v_rough_stk = Entry(vcarve_settings, width="15")
        self.Entry_v_rough_stk.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_v_rough_stk.configure(textvariable=config.v_rough_stk.TK)
        config.v_rough_stk.TK.trace_variable("w", self.Entry_v_rough_stk_Callback)
        self.entry_set(
            self.Entry_v_rough_stk, self.Entry_v_rough_stk_Check(), 2
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_v_max_cut = Label(
            vcarve_settings, text="V-Carve Max Depth per Pass"
        )
        self.Label_v_max_cut.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_v_max_cut_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_v_max_cut_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_v_max_cut = Entry(vcarve_settings, width="15")
        self.Entry_v_max_cut.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_v_max_cut.configure(textvariable=config.v_max_cut.TK)
        config.v_max_cut.TK.trace_variable("w", self.Entry_v_max_cut_Callback)
        self.entry_set(self.Entry_v_max_cut, self.Entry_v_max_cut_Check(), 2)

        if float(config.v_rough_stk.get()) == 0.0:
            self.Label_v_max_cut.configure(state="disabled")
            self.Label_v_max_cut_u.configure(state="disabled")
            self.Entry_v_max_cut.configure(state="disabled")
        else:
            self.Label_v_max_cut.configure(state="normal")
            self.Label_v_max_cut_u.configure(state="normal")
            self.Entry_v_max_cut.configure(state="normal")

        if not bool(config.inlay.get()):
            self.Label_Allowance.configure(state="disabled")
            self.Entry_Allowance.configure(state="disabled")
            self.Label_Allowance_u.configure(state="disabled")
        else:
            self.Label_Allowance.configure(state="normal")
            self.Entry_Allowance.configure(state="normal")
            self.Label_Allowance_u.configure(state="normal")

        if not bool(config.plotbox.get()):
            self.Label_BoxGap.configure(state="disabled")
            self.Entry_BoxGap.configure(state="disabled")
            self.Label_BoxGap_u.configure(state="disabled")
        else:
            self.Label_BoxGap.configure(state="normal")
            self.Entry_BoxGap.configure(state="normal")
            self.Label_BoxGap_u.configure(state="normal")

        ## Cleanup Settings ##
        D_Yloc = D_Yloc + D_dY + 12
        self.vcarve_separator1 = Frame(
            vcarve_settings, height=2, bd=1, relief=SUNKEN
        )
        self.vcarve_separator1.place(x=0, y=D_Yloc, width=580, height=2)

        right_but_loc = int(vcarve_settings.winfo_width()) - 10
        width_cb = 100
        height_cb = 35

        D_Yloc = D_Yloc + D_dY - 12
        self.Label_clean = Label(vcarve_settings, text="Cleanup Operations")
        self.Label_clean.place(
            x=center_loc, y=D_Yloc, width=w_label, height=21, anchor=CENTER
        )

        self.CLEAN_Recalculate = Button(
            vcarve_settings,
            text="Calculate\nCleanup",
            command=self.CLEAN_Recalculate_Click,
        )
        self.CLEAN_Recalculate.place(
            x=right_but_loc,
            y=D_Yloc,
            width=width_cb,
            height=height_cb * 1.5,
            anchor="ne",
        )

        D_Yloc = D_Yloc + D_dY
        self.Label_CLEAN_DIA = Label(
            vcarve_settings, text="Cleanup Cut Diameter"
        )
        self.Label_CLEAN_DIA.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_CLEAN_DIA_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_CLEAN_DIA_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_CLEAN_DIA = Entry(vcarve_settings, width="15")
        self.Entry_CLEAN_DIA.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_CLEAN_DIA.configure(textvariable=config.clean_dia.TK)
        config.clean_dia.TK.trace_variable("w", self.Entry_CLEAN_DIA_Callback)
        self.entry_set(self.Entry_CLEAN_DIA, self.Entry_CLEAN_DIA_Check(), 2)

        D_Yloc = D_Yloc + D_dY
        self.Label_STEP_OVER = Label(
            vcarve_settings, text="Cleanup Cut Step Over"
        )
        self.Label_STEP_OVER.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_STEP_OVER_u = Label(vcarve_settings, text="%", anchor=W)
        self.Label_STEP_OVER_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_STEP_OVER = Entry(vcarve_settings, width="15")
        self.Entry_STEP_OVER.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_STEP_OVER.configure(textvariable=config.clean_step.TK)
        config.clean_step.TK.trace_variable("w", self.Entry_STEP_OVER_Callback)
        self.entry_set(self.Entry_STEP_OVER, self.Entry_STEP_OVER_Check(), 2)

        D_Yloc = D_Yloc + 24
        check_delta = 40
        self.Label_clean_P = Label(
            vcarve_settings, text="Cleanup Cut Directions"
        )
        self.Label_clean_P.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )

        self.Write_Clean = Button(
            vcarve_settings,
            text="Save Cleanup\nG-Code",
            command=self.Write_Clean_Click,
        )
        self.Write_Clean.place(
            x=right_but_loc,
            y=D_Yloc,
            width=width_cb,
            height=height_cb,
            anchor="e",
        )

        self.Checkbutton_clean_P = Checkbutton(
            vcarve_settings, text="P", anchor=W
        )
        self.Checkbutton_clean_P.configure(variable=config.clean_P.TK)
        self.Checkbutton_clean_P.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry + 40, height=23
        )
        self.Checkbutton_clean_X = Checkbutton(
            vcarve_settings, text="X", anchor=W
        )
        self.Checkbutton_clean_X.configure(variable=config.clean_X.TK)
        self.Checkbutton_clean_X.place(
            x=xd_entry_L + check_delta, y=D_Yloc, width=w_entry + 40, height=23
        )
        self.Checkbutton_clean_Y = Checkbutton(
            vcarve_settings, text="Y", anchor=W
        )
        self.Checkbutton_clean_Y.configure(variable=config.clean_Y.TK)
        self.Checkbutton_clean_Y.place(
            x=xd_entry_L + check_delta * 2,
            y=D_Yloc,
            width=w_entry + 40,
            height=23,
        )

        D_Yloc = D_Yloc + 12

        D_Yloc = D_Yloc + D_dY
        self.Label_V_CLEAN = Label(vcarve_settings, text="V-Bit Cleanup Step")
        self.Label_V_CLEAN.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )
        self.Label_V_CLEAN_u = Label(
            vcarve_settings, textvariable=config.units.TK, anchor=W
        )
        self.Label_V_CLEAN_u.place(
            x=xd_units_L, y=D_Yloc, width=w_units, height=21
        )
        self.Entry_V_CLEAN = Entry(vcarve_settings, width="15")
        self.Entry_V_CLEAN.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry, height=23
        )
        self.Entry_V_CLEAN.configure(textvariable=config.clean_v.TK)
        config.clean_v.TK.trace_variable("w", self.Entry_V_CLEAN_Callback)
        self.entry_set(self.Entry_V_CLEAN, self.Entry_V_CLEAN_Check(), 2)

        D_Yloc = D_Yloc + 24
        self.Label_v_clean_P = Label(
            vcarve_settings, text="V-Bit Cut Directions"
        )
        self.Label_v_clean_P.place(
            x=xd_label_L, y=D_Yloc, width=w_label, height=21
        )

        self.Write_V_Clean = Button(
            vcarve_settings,
            text="Save V Cleanup\nG-Code",
            command=self.Write_V_Clean_Click,
        )
        self.Write_V_Clean.place(
            x=right_but_loc,
            y=D_Yloc,
            width=width_cb,
            height=height_cb,
            anchor="e",
        )

        self.Checkbutton_v_clean_P = Checkbutton(
            vcarve_settings, text="P", anchor=W
        )
        self.Checkbutton_v_clean_P.configure(variable=config.v_clean_P.TK)
        self.Checkbutton_v_clean_P.place(
            x=xd_entry_L, y=D_Yloc, width=w_entry + 40, height=23
        )
        self.Checkbutton_v_clean_X = Checkbutton(
            vcarve_settings, text="X", anchor=W
        )
        self.Checkbutton_v_clean_X.configure(variable=config.v_clean_X.TK)
        self.Checkbutton_v_clean_X.place(
            x=xd_entry_L + check_delta, y=D_Yloc, width=w_entry + 40, height=23
        )
        self.Checkbutton_v_clean_Y = Checkbutton(
            vcarve_settings, text="Y", anchor=W
        )
        self.Checkbutton_v_clean_Y.configure(variable=config.v_clean_Y.TK)
        self.Checkbutton_v_clean_Y.place(
            x=xd_entry_L + check_delta * 2,
            y=D_Yloc,
            width=w_entry + 40,
            height=23,
        )

        ## V-Bit Picture ##
        self.PHOTO = PhotoImage(
            format="gif",
            data="R0lGODlhoABQAIABAAAAAP///yH+EUNyZWF0ZWQgd2l0aCBHSU1QACH5BAEK"
            + "AAEALAAAAACgAFAAAAL+jI+pBu2/opy02ouzvg+G7m3iSJam1XHpybbuezhk"
            + "CFNyjZ9AS+ff6gtqdq5eMUQUKlG4GwsYW0ptPiMGmkhOtwhtzioBd7nkqBTk"
            + "BV3LZe8Z7Vyzue75zL6t4zf6fa3vxxGoBDhIZViFKFKoeNeYwfjIJylHyWPJ"
            + "hPmkechZEmkJ6hk2GiFaqnD6qIpq1ur6WhnL+kqLaIuKO6g7yuvnywmMJ4xJ"
            + "PGdMidxmkpaFxDClTMar1ZA1hr0kTcecDUu0Exe0nacDy/D8ER17vgidugK+"
            + "zq7OHB5jXf1Onkpf311HXz1+1+gBs7ZAzcB57Aj+IPUFoUNC6CbCgKMGYa3+"
            + "cBjhBOtisUkzf2FCXjT5C+UTlSl7sQykMRQxhf8+RSxmrFrOKi9VXCwI7gbH"
            + "h/iCGgX56SAae3+AEg36FN0+qQt10BIHj1XMIk6xJZH3D+zXd1Yhab2ybaRR"
            + "sFXjVZR4JJOjCVtf6IQ2NuzUrt7KlrwUkB/NoXD35hM7tOZKvjy21v0D6NRI"
            + "xZBBKovzmCTPojeJao6WeFzmz6InjiYtmtBp1Jtb9/y8eoZA1nmkxaYt5LbZ"
            + "frhrx+29R7eNPq9JCzcVGTgdXLGLG7/qXHlCVcel+/Y5vGBRjWyR7n6OAtTs"
            + "b9otfwdPV9R4sgux3sN7NzHWjX8htQPSfW/UgYRL888KPAllP3jgX14GRpFP"
            + "O/85405YCZpRIIEQIsjRfAtStYgeAuUX34TwCajZYUkhJ6FizRgIgYggNlTd"
            + "EMR1Ux5q0Q2BoXUbTVQAADs=",
        )

        self.Label_photo = Label(vcarve_settings, image=self.PHOTO)
        self.Label_photo.place(x=w_label + 150, y=40)
        self.Entry_Bit_Shape_Check()

        ## Buttons ##

        Ybut = int(vcarve_settings.winfo_height()) - 30
        Xbut = int(vcarve_settings.winfo_width() / 2)

        self.VCARVE_Recalculate = Button(
            vcarve_settings,
            text="Calculate V-Carve",
            command=self.VCARVE_Recalculate_Click,
        )
        self.VCARVE_Recalculate.place(
            x=Xbut, y=Ybut, width=130, height=30, anchor="e"
        )

        if config.cut_type.get() == "v-carve":
            self.VCARVE_Recalculate.configure(state="normal", command=None)
        else:
            self.VCARVE_Recalculate.configure(state="disabled", command=None)

        self.VCARVE_Close = Button(vcarve_settings, text="Close")
        self.VCARVE_Close.place(
            x=Xbut, y=Ybut, width=130, height=30, anchor="w"
        )
        self.VCARVE_Close.bind(
            "<ButtonRelease-1>", self.Close_Current_Window_Click
        )


# Start Application
root = Tk()
app = Application(root)
app.master.title("F-Engrave V" + version)
app.master.iconname("F-Engrave")
app.master.minsize(780, 540)
try:
    try:
        import tkFont

        default_font = tkFont.nametofont("TkDefaultFont")
    except:
        import tkinter.font

        default_font = tkinter.font.nametofont("TkDefaultFont")

    default_font.configure(size=9)
    default_font.configure(family="arial")
    # print(default_font.cget("size"))
    # print(default_font.cget("family"))
except:
    message.debug_message("Font Set Failed.")

try:
    try:
        app.master.iconbitmap(r"emblem")
    except:
        app.master.iconbitmap(bitmap="@emblem64")
except:
    try:  # Attempt to create temporary icon bitmap file
        temp_icon("f_engrave_icon")
        app.master.iconbitmap(bitmap="@f_engrave_icon")
        os.remove("f_engrave_icon")
    except:
        message.fmessage("Unable to create temporary icon file.")

app.f_engrave_init()
root.mainloop()
