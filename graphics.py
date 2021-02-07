from math import degrees, acos, sin, cos, sqrt, atan2, radians, fabs
from constants import Zero


class Character:
    def __init__(self, key):
        self.key = key
        self.stroke_list = []

    def __repr__(self):
        return "%%s" % (self.stroke_list)

    def get_xmax(self):
        try:
            return max([s.xmax for s in self.stroke_list])
        except ValueError:
            return 0

    def get_ymax(self):
        try:
            return max([s.ymax for s in self.stroke_list])
        except ValueError:
            return 0

    def get_ymin(self):
        try:
            return min([s.ymin for s in self.stroke_list])
        except ValueError:
            return 0


class Line:
    def __init__(self, coords):

        self.xstart, self.ystart, self.xend, self.yend = coords
        self.xmax = max(self.xstart, self.xend)
        self.ymax = max(self.ystart, self.yend)
        self.ymin = min(self.ystart, self.yend)

    def __repr__(self):
        return "Line([%s, %s, %s, %s])" \
            % (self.xstart, self.ystart, self.xend, self.yend)


############################################################################
# routine takes an sin and cos and returns the angle (between 0 and 360)   #
############################################################################
def Get_Angle(s, c):
    if s >= 0.0 and c >= 0.0:
        angle = degrees(acos(c))
    elif s >= 0.0 and c < 0.0:
        angle = degrees(acos(c))
    elif s < 0.0 and c <= 0.0:
        angle = 360 - degrees(acos(c))
    elif (s < 0.0 and c > 0.0):
        angle = 360 - degrees(acos(c))
    else:
        pass
    if angle < 0.001 and s < 0:
        angle == 360.0
    if angle > 359.999 and s >= 0:
        angle == 0.0
    return angle


############################################################################
# routine takes an x and a y coords and does a coordinate transformation   #
# to a new coordinate system at angle from the initial coordinate system   #
# Returns new x,y tuple                                                    #
############################################################################
def Transform(x, y, angle):
    newx = x * cos(angle) - y * sin(angle)
    newy = x * sin(angle) + y * cos(angle)
    return newx, newy


def Rotn(x, y, angle, radius):
    if radius > 0.0:
        alpha = x / radius
        xx = (radius + y) * sin(alpha)
        yy = (radius + y) * cos(alpha)
    elif radius < 0.0:
        alpha = x / radius
        xx = (radius + y) * sin(alpha)
        yy = (radius + y) * cos(alpha)
    else:  # radius is 0
        alpha = 0
        xx = x
        yy = y

    rad = sqrt(xx * xx + yy * yy)
    theta = atan2(yy, xx)
    newx = rad * cos(theta + radians(angle))
    newy = rad * sin(theta + radians(angle))

    return newx, newy, alpha


def CoordScale(x, y, xscale, yscale):
    newx = x * xscale
    newy = y * yscale
    return newx, newy


#####################################################
# Determine if a point is inside a given polygon or not
# Polygon is a list of (x,y) pairs.
# http://www.ariel.com.au/a/python-point-int-poly.html
#####################################################
def point_inside_polygon(x, y, poly):
    n = len(poly)
    inside = -1
    p1x = poly[0][0]
    p1y = poly[0][1]
    for i in range(n + 1):
        p2x = poly[i % n][0]
        p2y = poly[i % n][1]
        if y > min(p1y, p2y):
            if y <= max(p1y, p2y):
                if x <= max(p1x, p2x):
                    if p1y != p2y:
                        xinters = (y - p1y) * (p2x - p1x) / (p2y - p1y) + p1x
                    if p1x == p2x or x <= xinters:
                        inside = inside * -1
        p1x, p1y = p2x, p2y

    return inside


# Find intersecting lines
def DetectIntersect(Coords0, Coords1, lcoords, XY_T_F=True):
    [x0, y0] = Coords0
    [x1, y1] = Coords1
    Zero = 1e-6
    all_intersects = []
    Xint_list = []
    numcoords = len(lcoords)
    if numcoords < 1:
        return False

    dx = x1 - x0
    dy = y1 - y0
    len_seg = sqrt(dx * dx + dy * dy)

    if len_seg < Zero:
        if not XY_T_F:
            # Why return False? The caller would generate an
            # exception when doing len(DetectIntersect) if
            # XY_T_F was False (currently always True).
            return False
        else:
            return []

    seg_sin = dy / len_seg
    seg_cos = dx / len_seg
    Xint_local = 0

    for ii in range(0, numcoords):
        x2 = lcoords[ii][0]
        y2 = lcoords[ii][1]
        x3 = lcoords[ii][2]
        y3 = lcoords[ii][3]

        xr0 = (x2 - x0) * seg_cos + (y2 - y0) * seg_sin
        yr0 = (x2 - x0) * seg_sin - (y2 - y0) * seg_cos
        xr1 = (x3 - x0) * seg_cos + (y3 - y0) * seg_sin
        yr1 = (x3 - x0) * seg_sin - (y3 - y0) * seg_cos
        yrmax = max(yr0, yr1)
        yrmin = min(yr0, yr1)
        if yrmin < Zero and yrmax > Zero:
            dxr = xr1 - xr0
            if abs(dxr) < Zero:
                if xr0 > Zero and xr0 < len_seg - Zero:
                    Xint_local = xr0  # True
            else:
                dyr = yr1 - yr0
                mr = dyr / dxr
                br = yr1 - mr * xr1
                xint = -br / mr
                if xint > Zero and xint < len_seg - Zero:
                    Xint_local = xint  # True

            # Check if there was a intersection detected
            if Xint_local != 0:
                if not XY_T_F:
                    return True
                else:
                    Xint_list.append(Xint_local)
                    Xint_local = 0

    if not XY_T_F:
        return False  # Why return False?
    else:
        if len(Xint_list) > 0:
            Xint_list.sort()
            for Xint_local in Xint_list:
                Xint = Xint_local * seg_cos + x0
                Yint = Xint_local * seg_sin + y0
                all_intersects.append([Xint, Yint])
        return all_intersects


def Clean_coords_to_Path_coords(clean_coords_in):
    path_coords_out = []
    # Clean coords format ([xnormv, ynormv, rout, loop_cnt]) - clean_coords
    # Path coords format  ([x1, y1, x2, y2, line_cnt, char_cnt]) - coords
    for i in range(1, len(clean_coords_in)):
        if clean_coords_in[i][3] == clean_coords_in[i - 1][3]:
            path_coords_out.append(
                [
                    clean_coords_in[i - 1][0],
                    clean_coords_in[i - 1][1],
                    clean_coords_in[i][0],
                    clean_coords_in[i][1],
                    0,
                    0,
                ]
            )
    return path_coords_out


def Find_Paths(check_coords_in,
               clean_dia,
               Radjust,
               clean_step,
               skip,
               direction):
    check_coords = []

    if direction == "Y":
        cnt = -1
        for line in check_coords_in:
            cnt = cnt + 1
            XY = line
            check_coords.append([XY[1], XY[0], XY[2]])
    else:
        check_coords = check_coords_in

    minx_c = 0
    maxx_c = 0
    miny_c = 0
    maxy_c = 0
    if len(check_coords) > 0:
        minx_c = check_coords[0][0] - check_coords[0][2]
        maxx_c = check_coords[0][0] + check_coords[0][2]
        miny_c = check_coords[0][1] - check_coords[0][2]
        maxy_c = check_coords[0][1] + check_coords[0][2]
    for line in check_coords:
        XY = line
        minx_c = min(minx_c, XY[0] - XY[2])
        maxx_c = max(maxx_c, XY[0] + XY[2])
        miny_c = min(miny_c, XY[1] - XY[2])
        maxy_c = max(maxy_c, XY[1] + XY[2])

    DX = clean_dia * clean_step
    DY = DX
    Xclean_coords = []
    Xclean_coords_short = []

    if direction != "None":
        # Find ends of horizontal lines for carving clean-up
        loop_cnt = 0
        Y = miny_c
        line_cnt = skip - 1
        while Y <= maxy_c:
            line_cnt = line_cnt + 1
            X = minx_c
            x1 = X
            x2 = X
            x1_old = x1
            x2_old = x2

            # Find relevant clean_coord_data
            ################################
            temp_coords = []
            for line in check_coords:
                XY = line
                if Y < XY[1] + XY[2] and Y > XY[1] - XY[2]:
                    temp_coords.append(XY)

            while X <= maxx_c:
                for line in temp_coords:
                    XY = line
                    h = XY[0]
                    k = XY[1]
                    R = XY[2] - Radjust
                    dist = sqrt((X - h) ** 2 + (Y - k) ** 2)
                    if dist <= R:
                        Root = sqrt(R ** 2 - (Y - k) ** 2)
                        XL = h - Root
                        XR = h + Root
                        if XL < x1:
                            x1 = XL
                        if XR > x2:
                            x2 = XR
                if x1 == x2:
                    X = X + DX
                    x1 = X
                    x2 = X
                elif (x1 == x1_old) and (x2 == x2_old):
                    loop_cnt = loop_cnt + 1
                    Xclean_coords.append([x1, Y, loop_cnt])
                    Xclean_coords.append([x2, Y, loop_cnt])
                    if line_cnt == skip:
                        Xclean_coords_short.append([x1, Y, loop_cnt])
                        Xclean_coords_short.append([x2, Y, loop_cnt])

                    X = X + DX
                    x1 = X
                    x2 = X
                else:
                    X = x2
                x1_old = x1
                x2_old = x2
            if line_cnt == skip:
                line_cnt = 0
            Y = Y + DY

    if True is False:  # Why is this code disabled?
        # Loop over circles recording "pixels" that are covered by the circles
        loop_cnt = 0
        Y = miny_c
        while Y <= maxy_c:
            line_cnt = line_cnt + 1
            X = minx_c
            x1 = X
            x2 = X
            x1_old = x1
            x2_old = x2

            # Find relevant clean_coord_data
            temp_coords = []
            for line in check_coords:
                XY = line
                if Y < XY[1] + XY[2] and Y > XY[1] - XY[2]:
                    temp_coords.append(XY)

            while X <= maxx_c:
                for line in temp_coords:
                    XY = line
                    h = XY[0]
                    k = XY[1]
                    R = XY[2] - Radjust
                    dist = sqrt((X - h) ** 2 + (Y - k) ** 2)
                    if dist <= R:
                        Root = sqrt(R ** 2 - (Y - k) ** 2)
                        XL = h - Root
                        XR = h + Root
                        if XL < x1:
                            x1 = XL
                        if XR > x2:
                            x2 = XR
                if x1 == x2:
                    X = X + DX
                    x1 = X
                    x2 = X
                elif (x1 == x1_old) and (x2 == x2_old):
                    loop_cnt = loop_cnt + 1
                    Xclean_coords.append([x1, Y, loop_cnt])
                    Xclean_coords.append([x2, Y, loop_cnt])
                    if line_cnt == skip:
                        Xclean_coords_short.append([x1, Y, loop_cnt])
                        Xclean_coords_short.append([x2, Y, loop_cnt])

                    X = X + DX
                    x1 = X
                    x2 = X
                else:
                    X = x2
                x1_old = x1
                x2_old = x2
            if line_cnt == skip:
                line_cnt = 0
            Y = Y + DY

    Xclean_coords_out = []
    Xclean_coords_short_out = []
    if direction == "Y":

        cnt = -1
        for line in Xclean_coords:
            cnt = cnt + 1
            XY = line
            Xclean_coords_out.append([XY[1], XY[0], XY[2]])

        cnt = -1
        for line in Xclean_coords_short:
            cnt = cnt + 1
            XY = line
            Xclean_coords_short_out.append([XY[1], XY[0], XY[2]])
    else:
        Xclean_coords_out = Xclean_coords
        Xclean_coords_short_out = Xclean_coords_short

    return Xclean_coords_out, Xclean_coords_short_out


def record_v_carve_data(x1,
                        y1,
                        phi,
                        rout,
                        loop_cnt,
                        clean_flag,
                        rbit,
                        coords):

    Lx, Ly = Transform(0, rout, -phi)
    xnormv = x1 + Lx
    ynormv = y1 + Ly
    need_clean = 0

    if int(clean_flag) != 1:
        coords.append([xnormv, ynormv, rout, loop_cnt])
        if abs(rbit - rout) <= Zero:
            need_clean = 1
    else:
        if rout >= rbit:
            coords.append([xnormv, ynormv, rout, loop_cnt])

    return xnormv, ynormv, rout, need_clean


############################################################################
# Routine finds the maximum radius that can be placed in the position      #
# xpt,ypt without interfering with other line segments (rmin is max R LOL) #
############################################################################
def find_max_circle(
    xpt, ypt, rmin, char_num, seg_sin, seg_cos, corner, CHK_STRING,
    MINX, MINY, xPartitionLength, yPartitionLength, partitionList
):
    rtmp = rmin
    xIndex = int((xpt - MINX) / xPartitionLength)
    yIndex = int((ypt - MINY) / yPartitionLength)

    coords_check = []
    R_A = abs(rmin)
    Bcnt = -1
    ############################################################
    # Loop over active partitions for the current line segment #
    ############################################################
    for line_B in partitionList[xIndex][yIndex]:
        Bcnt = Bcnt + 1
        X_B = line_B[len(line_B) - 3]
        Y_B = line_B[len(line_B) - 2]
        R_B = line_B[len(line_B) - 1]
        GAP = sqrt((X_B - xpt) * (X_B - xpt) + (Y_B - ypt) * (Y_B - ypt))
        if GAP < abs(R_A + R_B):
            coords_check.append(line_B)

    for linec in coords_check:
        XYc = linec
        xmaxt = max(XYc[0], XYc[2]) + rmin * 2
        xmint = min(XYc[0], XYc[2]) - rmin * 2
        ymaxt = max(XYc[1], XYc[3]) + rmin * 2
        ymint = min(XYc[1], XYc[3]) - rmin * 2
        if xpt >= xmint and ypt >= ymint and xpt <= xmaxt and ypt <= ymaxt:
            logic_full = True
        else:
            logic_full = False
            continue

        if CHK_STRING == "chr":
            logic_full = logic_full and (char_num == int(XYc[5]))

        if corner == 1:
            logic_full = (
                logic_full
                and ((fabs(xpt - XYc[0]) > Zero)
                     or (fabs(ypt - XYc[1]) > Zero))
                and ((fabs(xpt - XYc[2]) > Zero)
                     or (fabs(ypt - XYc[3]) > Zero))
            )

        if logic_full:
            xc1 = (XYc[0] - xpt) * seg_cos - (XYc[1] - ypt) * seg_sin
            yc1 = (XYc[0] - xpt) * seg_sin + (XYc[1] - ypt) * seg_cos
            xc2 = (XYc[2] - xpt) * seg_cos - (XYc[3] - ypt) * seg_sin
            yc2 = (XYc[2] - xpt) * seg_sin + (XYc[3] - ypt) * seg_cos

            if fabs(xc2 - xc1) < Zero and fabs(yc2 - yc1) > Zero:
                rtmp = fabs(xc1)
                if max(yc1, yc2) >= rtmp and min(yc1, yc2) <= rtmp:
                    rmin = min(rmin, rtmp)

            elif fabs(yc2 - yc1) < Zero and fabs(xc2 - xc1) > Zero:
                if max(xc1, xc2) >= 0.0 and min(xc1, xc2) <= 0.0 \
                        and yc1 > Zero:
                    rtmp = yc1 / 2.0
                    rmin = min(rmin, rtmp)

            if fabs(yc2 - yc1) > Zero and fabs(xc2 - xc1) > Zero:
                m = (yc2 - yc1) / (xc2 - xc1)
                b = yc1 - m * xc1
                sq = m + 1 / m
                A = 1 + m * m - 2 * m * sq
                B = -2 * b * sq
                C = -b * b
                try:
                    sq_root = sqrt(B * B - 4 * A * C)
                    xq1 = (-B + sq_root) / (2 * A)

                    if xq1 >= min(xc1, xc2) and xq1 <= max(xc1, xc2):
                        rtmp = xq1 * sq + b
                        if rtmp >= 0.0:
                            rmin = min(rmin, rtmp)

                    xq2 = (-B - sq_root) / (2 * A)

                    if xq2 >= min(xc1, xc2) and xq2 <= max(xc1, xc2):
                        rtmp = xq2 * sq + b
                        if rtmp >= 0.0:
                            rmin = min(rmin, rtmp)
                except:
                    pass

            if yc1 > Zero:
                rtmp = (xc1 * xc1 + yc1 * yc1) / (2 * yc1)
                rmin = min(rmin, rtmp)

            if yc2 > Zero:
                rtmp = (xc2 * xc2 + yc2 * yc2) / (2 * yc2)
                rmin = min(rmin, rtmp)

            if abs(yc1) < Zero and abs(xc1) < Zero:
                if yc2 > Zero:
                    rmin = 0.0
            if abs(yc2) < Zero and abs(xc2) < Zero:
                if yc1 > Zero:
                    rmin = 0.0

    return rmin
