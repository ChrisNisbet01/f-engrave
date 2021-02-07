from constants import Plane, Zero
from graphics import Get_Angle
from math import hypot, sqrt
import sys


VERSION = sys.version_info[0]

if VERSION == 3:
    MAXINT = sys.maxsize
else:
    MAXINT = sys.maxint


####################################
# Gcode class for creating G-Code
####################################
class Gcode:
    def __init__(self,
                 safetyheight=0.04,
                 tolerance=0.001,
                 target=lambda s: sys.stdout.write(s + "\n"),
                 arc_fit="none",
                 metric=False,
                 enable_variables=False,
                 message=None):

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
        self.write = target
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
                self.move_common(x, y, z, I=cent[0], J=cent[1], gcode=move)
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
        self.move_common(I=I_offset, J=J_offset, gcode=cmd)

    def move_common(self, x=None, y=None, z=None, I_offset=None, J=None,
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
            YC = self.lasty + J
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
        if J:
            Jstring = " J" + FORMAT % (J)
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


# Perform Douglas-Peucker simplification on the path 'st' with the specified
# tolerance.  The '_first' argument is for internal use only.
#
# The Douglas-Peucker simplification algorithm finds a subset of the input
# points whose path is never more than 'tolerance' away from the original input
# path.
#
# If 'plane' is specified as 17, 18, or 19, it may find helical arcs in the
# given plane in addition to lines.
#
# I modified the code so the note below does not apply when using plane 17
# Note that if there is movement in the plane perpendicular to the arc, it will
# be distorted, so 'plane' should usually be specified only when there is only
# movement on 2 axes
def douglas(st, tolerance=.001, plane=None, _first=True):
    if len(st) == 1:
        yield "G1", st[0], None
        return
    # if len(st) < 1:
    #    print "whaaaa!?"
    #    #yield "G1", st[0], None
    #    return

    L1 = st[0]
    L2 = st[-1]

    last_point = None
    while (abs(L1[0] - L2[0]) < Zero) and (abs(L1[1] - L2[1]) < Zero) and \
            (abs(L1[2] - L2[2]) < Zero):
        last_point = st.pop()
        try:
            L2 = st[-1]
        except:
            return

    worst_dist = 0
    worst_distz = 0  # added to fix out of plane inacuracy problem
    worst = 0
    min_rad = MAXINT
    max_arc = -1

    ps = st[0]
    pe = st[-1]

    for i, p in enumerate(st):
        if p is L1 or p is L2:
            continue
        dist = dist_lseg(L1, L2, p)
        # added to fix out of plane inacuracy problem
        distz = dist_lseg(L1, L2, p, z_only=True)
        if dist > worst_dist:
            worst = i
            worst_dist = dist
            rad = arc_rad(plane, ps, p, pe)
            if rad < min_rad:
                max_arc = i
                min_rad = rad
        if distz > worst_distz:  # added to fix out of plane inacuracy problem
            worst_distz = distz  # added to fix out of plane inacuracy problem

    worst_arc_dist = 0
    if min_rad != MAXINT:
        c1, c2 = arc_center(plane, ps, st[max_arc], pe)
        Lx, Ly, Lz = st[0]
        if one_quadrant(plane, (c1, c2), ps, st[max_arc], pe):
            for i, (x, y, z) in enumerate(st):
                if plane == Plane.xy:
                    dist1 = abs(hypot(c1 - x, c2 - y) - min_rad)
                    # added to fix out of plane inacuracy problem
                    dist = sqrt(worst_distz ** 2 + dist1 ** 2)
                elif plane == Plane.xz:
                    dist = abs(hypot(c1 - x, c2 - z) - min_rad)
                elif plane == Plane.yz:
                    dist = abs(hypot(c1 - y, c2 - z) - min_rad)
                else:
                    dist = MAXINT

                if dist > worst_arc_dist:
                    worst_arc_dist = dist

                mx = (x + Lx) / 2
                my = (y + Ly) / 2
                mz = (z + Lz) / 2
                if plane == Plane.xy:
                    dist = abs(hypot(c1 - mx, c2 - my) - min_rad)
                elif plane == Plane.xz:
                    dist = abs(hypot(c1 - mx, c2 - mz) - min_rad)
                elif plane == Plane.yz:
                    dist = abs(hypot(c1 - my, c2 - mz) - min_rad)
                else:
                    dist = MAXINT
                Lx, Ly, Lz = x, y, z
        else:
            worst_arc_dist = MAXINT
    else:
        worst_arc_dist = MAXINT

    if worst_arc_dist < tolerance and worst_arc_dist < worst_dist:
        ccw = arc_dir(plane, (c1, c2), ps, st[max_arc], pe)
        if plane == 18:
            ccw = not ccw
        yield "G1", ps, None
        if ccw:
            yield "G3", st[-1], arc_fmt(plane, c1, c2, ps)
        else:
            yield "G2", st[-1], arc_fmt(plane, c1, c2, ps)
    elif worst_dist > tolerance:
        if _first:
            yield "G1", st[0], None
        for i in douglas(st[:worst + 1], tolerance, plane, False):
            yield i
        yield "G1", st[worst], None
        for i in douglas(st[worst:], tolerance, plane, False):
            yield i
        if _first:
            yield "G1", st[-1], None
    else:
        if _first:
            yield "G1", st[0], None
        if _first:
            yield "G1", st[-1], None

    if last_point is not None:       # added to fix closed loop problem
        yield "G1", st[0], None  # added to fix closed loop problem


###############################################################################
#            Author.py                                                        #
#            A component of emc2                                              #
###############################################################################

# Compute the 3D distance from the line segment l1..l2 to the point p.
# (Those are lower case L1 and L2)
def dist_lseg(l1, l2, p, z_only=False):
    x0, y0, z0 = l1
    xa, ya, za = l2
    xi, yi, zi = p

    dx = xa - x0
    dy = ya - y0
    dz = za - z0
    d2 = dx * dx + dy * dy + dz * dz

    if d2 == 0:
        return 0

    t = (dx * (xi - x0) + dy * (yi - y0) + dz * (zi - z0)) / d2
    if t < 0:
        t = 0
    if t > 1:
        t = 1

    if (z_only):
        dist2 = (zi - z0 - t * dz) ** 2
    else:
        dist2 = (xi - x0 - t * dx) ** 2 + (yi - y0 - t * dy) ** 2 + \
            (zi - z0 - t * dz) ** 2

    return dist2 ** .5


def rad1(x1, y1, x2, y2, x3, y3):
    x12 = x1 - x2
    y12 = y1 - y2
    x23 = x2 - x3
    y23 = y2 - y3
    x31 = x3 - x1
    y31 = y3 - y1

    den = abs(x12 * y23 - x23 * y12)
    if abs(den) < 1e-5:
        return MAXINT
    return hypot(float(x12), float(y12)) * hypot(float(x23), float(y23)) * \
        hypot(float(x31), float(y31)) / 2 / den


class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return "<%f,%f>" % (self.x, self.y)

    def __sub__(self, other):
        return Point(self.x - other.x, self.y - other.y)

    def __add__(self, other):
        return Point(self.x + other.x, self.y + other.y)

    def __mul__(self, other):
        return Point(self.x * other, self.y * other)

    __rmul__ = __mul__

    def cross(self, other):
        return self.x * other.y - self.y * other.x

    def dot(self, other):
        return self.x * other.x + self.y * other.y

    def mag(self):
        return hypot(self.x, self.y)

    def mag2(self):
        return self.x ** 2 + self.y ** 2


def cent1(x1, y1, x2, y2, x3, y3):
    P1 = Point(x1, y1)
    P2 = Point(x2, y2)
    P3 = Point(x3, y3)

    den = abs((P1 - P2).cross(P2 - P3))
    if abs(den) < 1e-5:
        return MAXINT, MAXINT

    alpha = (P2 - P3).mag2() * (P1 - P2).dot(P1 - P3) / 2 / den / den
    beta = (P1 - P3).mag2() * (P2 - P1).dot(P2 - P3) / 2 / den / den
    gamma = (P1 - P2).mag2() * (P3 - P1).dot(P3 - P2) / 2 / den / den

    Pc = alpha * P1 + beta * P2 + gamma * P3
    return Pc.x, Pc.y


def arc_center(plane, p1, p2, p3):
    x1, y1, z1 = p1
    x2, y2, z2 = p2
    x3, y3, z3 = p3

    if plane == Plane.xy:
        return cent1(x1, y1, x2, y2, x3, y3)
    if plane == Plane.xz:
        return cent1(x1, z1, x2, z2, x3, z3)
    if plane == Plane.yz:
        return cent1(y1, z1, y2, z2, y3, z3)


def arc_rad(plane, P1, P2, P3):
    if plane is None:
        return MAXINT

    x1, y1, z1 = P1
    x2, y2, z2 = P2
    x3, y3, z3 = P3

    if plane == Plane.xy:
        return rad1(x1, y1, x2, y2, x3, y3)
    if plane == Plane.xz:
        return rad1(x1, z1, x2, z2, x3, z3)
    if plane == Plane.yz:
        return rad1(y1, z1, y2, z2, y3, z3)
    return None, 0


def get_pts(plane, x, y, z):
    if plane == Plane.xy:
        return x, y
    if plane == Plane.xz:
        return x, z
    if plane == Plane.yz:
        return y, z


def one_quadrant(plane, c, p1, p2, p3):
    xc, yc = c
    x1, y1 = get_pts(plane, p1[0], p1[1], p1[2])
    x2, y2 = get_pts(plane, p2[0], p2[1], p2[2])
    x3, y3 = get_pts(plane, p3[0], p3[1], p3[2])

    ###########################################################
    # Check the angle here and return false if it is too sharp
    ###########################################################
    La = hypot((x1 - x2), (y1 - y2))
    Lb = hypot((x3 - x2), (y3 - y2))

    cos1 = (x1 - x2) / La
    sin1 = (y1 - y2) / La

    cos2 = (x3 - x2) / Lb
    sin2 = (y3 - y2) / Lb

    theta_a = Get_Angle(sin1, cos1)
    theta_b = Get_Angle(sin2, cos2)

    if theta_a > theta_b:
        angle = theta_a - theta_b
    else:
        angle = theta_b - theta_a

    test_angle = 36
    if angle > 180 + test_angle or angle < 180 - test_angle:
        # pass
        return False

    #

    def sign(x):
        if abs(x) < 1e-5:
            return 0
        if x < 0:
            return -1
        return 1

    signs = set((
        (sign(x1 - xc), sign(y1 - yc)),
        (sign(x2 - xc), sign(y2 - yc)),
        (sign(x3 - xc), sign(y3 - yc))
        ))

    if len(signs) == 1:
        return True

    if (1, 1) in signs:
        signs.discard((1, 0))
        signs.discard((0, 1))
    if (1, -1) in signs:
        signs.discard((1, 0))
        signs.discard((0, -1))
    if (-1, 1) in signs:
        signs.discard((-1, 0))
        signs.discard((0, 1))
    if (-1, -1) in signs:
        signs.discard((-1, 0))
        signs.discard((0, -1))

    if len(signs) == 1:
        return True


def arc_dir(plane, c, p1, p2, p3):
    xc, yc = c
    x1, y1 = get_pts(plane, p1[0], p1[1], p1[2])
    x2, y2 = get_pts(plane, p2[0], p2[1], p2[2])
    x3, y3 = get_pts(plane, p3[0], p3[1], p3[2])

    #
    signedArea = \
        (x1 * y2 - x2 * y1) + (x2 * y3 - x3 * y2) + (x3 * y1 - x1 * y3)
    if signedArea > 0.0:
        ccw = True
    else:
        ccw = False
    return ccw

    #
    # signedArea = (x2-x1)*(y2+y1) + (x3-x2)*(y3+y2) + (x1-x3)*(y1+y3)
    # if signedArea > 0.0:
    #    cw2=False
    # else:
    #    cw2=True
    #
    # R = hypot( (x1-xc), (y1-yc) )
    # cos1 = (x1-xc)/R
    # sin1 = (y1-yc)/R
    # cos2 = (x2-xc)/R
    # sin2 = (y2-yc)/R
    # cos3 = (x3-xc)/R
    # sin3 = (y3-yc)/R
    # theta_start = Get_Angle(sin1, cos1)
    # theta_mid   = Get_Angle(sin2, cos2)
    # theta_end   = Get_Angle(sin3, cos3)
    # if theta_mid < theta_start:
    #    mid_angle = theta_mid - theta_start + 360.0
    # else:
    #    mid_angle = theta_mid - theta_start
    #
    # if theta_end < theta_start:
    #    end_angle = theta_end - theta_start + 360.0
    # else:
    #    end_angle = theta_end - theta_start
    #
    # if (end_angle > mid_angle):
    #    cw3=True
    # else:
    #    cw3=False


def arc_fmt(plane, c1, c2, p1):
    x, y, z = p1
    if plane == Plane.xy:
        return [c1 - x, c2 - y]
    if plane == Plane.xz:
        return [c1 - x, c2 - z]
    if plane == Plane.yz:
        return [c1 - y, c2 - z]
