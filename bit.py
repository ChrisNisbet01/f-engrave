from math import radians, tan, sqrt


class Bit(object):
    def __init__(self, shape, diameter, angle):
        self._shape = shape
        if not diameter:
            diameter = 0.0
        self._diameter = float(diameter)
        self._radius = self._diameter / 2.0
        if not angle:
            angle = 0.0
        self._angle = float(angle)
        self._half_angle = radians(self._angle) / 2.0

    def diameter(self, depth_limit=0.0, inlay=False, allowance=0.0):
        raise NotImplementedError

    def depth(self):
        raise NotImplementedError

    @property
    def angle(self):
        return self._angle

    @property
    def half_angle(self):
        return self._half_angle

    @property
    def radius(self):
        return self._radius

    @property
    def shape(self):
        return self._shape


class VBit(Bit):
    def __init__(self, shape, diameter, angle):
        super(VBit, self).__init__(shape, diameter, angle)

    def diameter(self, depth_limit=0.0, inlay=False, allowance=0.0):
        if inlay:
            allowance = float(allowance)
            bit_dia = -2 * allowance * tan(self._half_angle)
            bit_dia = max(bit_dia, 0.001)
        else:
            bit_dia = self._diameter
            depth_limit = float(depth_limit)
            if depth_limit < 0.0:
                bit_dia = -2 * depth_limit * tan(self._half_angle)

        return bit_dia

    def depth(self):
        bit_depth = -self._radius / tan(self._half_angle)

        return bit_depth

    def max_cut_depth(self, depth_limit):
        depth_limit = float(depth_limit)
        if depth_limit < 0.0:
            max_cut = max(self.bit_depth(), depth_limit)
        else:
            max_cut = self.depth()
        return max_cut


class FlatBit(Bit):
    def __init__(self, shape, diameter, angle):
        super(FlatBit, self).__init__(shape, diameter, angle)

    def diameter(self, depth_limit=0.0, inlay=False, allowance=0.0):
        bit_dia = self._diameter

        return bit_dia

    def depth(self):
        bit_depth = -self._radius

        return bit_depth

    def max_cut_depth(self, depth_limit):
        depth_limit = float(depth_limit)
        if depth_limit < 0.0:
            max_cut = depth_limit
        else:
            max_cut = self.depth()
        return max_cut


class BallBit(Bit):
    def __init__(self, shape, diameter, angle):
        super(BallBit, self).__init__(shape, diameter, angle)

    def diameter(self, depth_limit=0.0, inlay=False, allowance=0.0):
        bit_dia = self._diameter
        depth_limit = float(depth_limit)
        if depth_limit < 0.0:
            radius = self._radius
            if (depth_limit > -radius):
                bit_dia = 2 * sqrt(radius ** 2 - (radius + depth_limit) ** 2)

        return bit_dia

    def depth(self):
        bit_depth = -self._radius

        return bit_depth

    def max_cut_depth(self, depth_limit):
        depth_limit = float(depth_limit)
        if depth_limit < 0.0:
            max_cut = max(self.depth(), depth_limit)
        else:
            max_cut = self.depth()

        return max_cut


def bit_from_shape(shape, diameter, angle):
    if shape == "VBIT":
        return VBit(shape, diameter, angle)
    elif shape == "FLAT":
        return FlatBit(shape, diameter, angle)
    elif shape == "BALL":
        return BallBit(shape, diameter, angle)
    else:
        return None
