from constants import Plane, Zero
from douglas import douglas
from math import sqrt
import sys


VERSION = sys.version_info[0]

if VERSION == 3:
    MAXINT = sys.maxsize
else:
    MAXINT = sys.maxint


####################################
# Gcode class for creating G-Code
####################################
class Gcode(list):
    def __init__(self,
                 message,
                 safetyheight=0.04,
                 tolerance=0.001,
                 arc_fit="none",
                 metric=False,
                 enable_variables=False):
        super(Gcode, self).__init__()

        self.lastx = self.lasty = self.lastz = self.lastf = None
        self.feed = None
        self.plane = None
        self.cuts = []
        self.metric = metric
        self.enable_variables = enable_variables
        if self.metric:
            self.dp = 3
            self.dpfeed = 1
        else:  # Imperial
            self.dp = 4
            self.dpfeed = 2

        self.safetyheight = safetyheight
        self.tolerance = tolerance
        self.write = lambda s: self.append(s)
        self.arc_fit = arc_fit
        self.message = message

    def set_plane(self, plane):
        if (self.arc_fit != "none"):
            assert plane in (Plane.xy, Plane.xz, Plane.yz)
            if plane != self.plane:
                self.plane = plane
                self.write("G%d" % plane)

    # If any 'cut' moves are stored up, send them to the simplification
    # algorithm and actually output them.
    # This function is usually used internally (e.g., when changing from a cut
    # to a rapid) but can be called manually as well.  For instance, when
    # a contouring program reaches the end of a row, it may be desirable to
    # enforce that the last 'cut' coordinate is actually in the output file,
    # and it may give better performance because this means that the
    # simplification algorithm will examine fewer points per run.
    def flush(self):
        if not self.cuts:
            return
        for move, (x, y, z), cent in \
                douglas(self.cuts, self.tolerance, self.plane):
            if cent:
                self.move_common(x, y, z, I_offset=cent[0], J_offset=cent[1],
                                 gcode=move)
            else:
                self.move_common(x, y, z, gcode="G1")
        self.cuts = []

    def end(self):
        self.flush()
        self.safety()

    def rapid(self, x=None, y=None, z=None):
        # Perform a rapid move to the specified coordinates
        self.flush()
        self.move_common(x, y, z, gcode="G0")

    def arc(self, cw, I_offset, J_offset):
        if cw:
            cmd = "G2"
        else:
            cmd = "G3"
        self.move_common(I_offset=I_offset, J_offset=J_offset, gcode=cmd)

    def move_common(self, x=None, y=None, z=None, I_offset=None, J_offset=None,
                    gcode="G0", feed=None):
        if feed is None:
            feed = self.feed
        # An internal function used for G0 and G1 moves
        gcodestring = xstring = ystring = zstring = Istring = Jstring = \
            Rstring = fstring = ""
        if x is None:
            x = self.lastx
        if y is None:
            y = self.lasty
        if z is None:
            z = self.lastz
        if (feed != self.lastf):
            fstring = " " + feed
            self.lastf = feed
        FORMAT = "%%.%df" % (self.dp)

        if (gcode == "G2" or gcode == "G3"):
            XC = self.lastx + I_offset
            YC = self.lasty + J_offset
            R_check_1 = sqrt((XC - self.lastx) ** 2 + (YC - self.lasty) ** 2)
            R_check_2 = sqrt((XC - x) ** 2 + (YC - y) ** 2)

            Rstring = " R" + FORMAT % ((R_check_1 + R_check_2) / 2.0)
            if abs(R_check_1 - R_check_2) > Zero:
                self.message.fmessage(
                    "-- G-Code Curve Fitting Anomaly - Check Output --")
                self.message.fmessage(
                    "R_start: %f R_end %f" % (R_check_1, R_check_2))
                self.message.fmessage(
                    "Begining and end radii do not match: delta = %f" %
                    (abs(R_check_1 - R_check_2)))

        if x != self.lastx:
            xstring = " X" + FORMAT % (x)
            self.lastx = x
        if y != self.lasty:
            ystring = " Y" + FORMAT % (y)
            self.lasty = y
        if z != self.lastz:
            zstring = " Z" + FORMAT % (z)
            self.lastz = z
        if I_offset:
            Istring = " I" + FORMAT % (I_offset)
        if J_offset:
            Jstring = " J" + FORMAT % (J_offset)
        if xstring == ystring == zstring == fstring == Istring == \
                Jstring == "":
            return

        gcodestring = gcode
        if (self.arc_fit == "radius"):
            cmd = "".join([gcodestring, xstring, ystring, zstring, Rstring,
                           fstring])
        else:
            cmd = "".join([gcodestring, xstring, ystring, zstring, Istring,
                           Jstring, fstring])

        if cmd:
            self.write(cmd)

    def set_feed(self, feed, write_it=False):
        # Set the feed rate to the given value
        self.flush()
        self.feed_val = float(feed)
        FORMAT = 'F%%.%df' % (self.dpfeed)
        self.feed = FORMAT % self.feed_val
        self.lastf = None
        if write_it:
            self.write(self.feed)
            self.lastf = self.feed

    def set_z_feed(self, z_feed):
        # Set the z axis feed rate to the given value
        self.flush()
        self.z_feed_val = float(z_feed)
        FORMAT = 'F%%.%df' % (self.dpfeed)
        zero_feed = FORMAT % (float(0.0))
        feed = FORMAT % (self.z_feed_val)
        if feed == zero_feed:
            feed = self.feed
        self.z_feed = feed

    def set_depth(self, depth):
        self.depth = depth
        FORMAT = '%%.%df' % (self.dp)
        self.depth_val = FORMAT % (depth)
        self.append_comment("Engraving Depth Z: " + self.depth_val)
        # TODO: Support variables.

    def cut(self, x=None, y=None, z=None):
        # Perform a cutting move at the specified feed rate to the specified
        # coordinates
        if self.cuts:
            lastx, lasty, lastz = self.cuts[-1]
        else:
            lastx, lasty, lastz = self.lastx, self.lasty, self.lastz
        if x is None:
            x = lastx
        if y is None:
            y = lasty
        if z is None:
            z = lastz
        self.cuts.append([x, y, z])

    def safety(self):
        # Go to the 'safety' height at rapid speed
        self.flush()
        self.rapid(z=self.safetyheight)

    def plunge_z(self, depth=None):
        if depth is None:
            depth = self.depth
        self.move_common(z=depth, gcode="G1", feed=self.z_feed)

    def append_comment(self, comment):
        self.write("(" + comment + ")")

    def _append_pre_post_amble(self, commands, comment):
        self.append_comment(comment)
        for line in commands.split('|'):
            self.write(line)
        self.append_comment("End %s" % (comment))

    def append_preamble(self, commands):
        self._append_pre_post_amble(commands, "Header")

    def append_postamble(self, commands):
        self._append_pre_post_amble(commands, "Post script")

    def append_mode(self):
        # G90        ; Sets absolute distance mode
        self.write('G90 (absolute)')
        # G91.1      ; Sets Incremental Distance Mode for I, J & K arc offsets.
        if (self.arc_fit == "center"):
            self.write('G91.1')

    def append_units(self):
        if self.metric:
            # G21 ; sets units to mm
            self.write('G21 (mm)')
        else:
            # G20 ; sets units to inches
            self.write('G20 (in)')
