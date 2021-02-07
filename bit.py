from math import radians, tan, sqrt


class Bit(object):
    def __init__(self, shape, diameter, angle):
        self._shape = shape
        self._diameter = float(diameter)
        self._radius = self._diameter / 2.0
        self._angle = float(angle)
        self._half_angle = radians(self._angle) / 2.0

    def diameter(self, depth_limit, inlay, allowance):
        # TODO: raise an exception. Subclasses should have their own.
        return None

    def depth(self):
        # TODO: raise an exception. Subclasses should have their own.
        return None


class VBit(Bit):
    def __init__(self, shape, diameter, angle):
        super(VBit, self).__init__(shape, diameter, angle)

    def diameter(self, depth_limit, inlay, allowance):
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


class FlatBit(Bit):
    def __init__(self, shape, diameter, angle):
        super(FlatBit, self).__init__(shape, diameter, angle)

    def diameter(self, depth_limit, inlay, allowance):
        bit_dia = self._diameter

        return bit_dia

    def depth(self):
        bit_depth = -self._radius

        return bit_depth


class BallBit(Bit):
    def __init__(self, shape, diameter, angle):
        super(BallBit, self).__init__(shape, diameter, angle)

    def diameter(self, depth_limit, inlay, allowance):
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


def bit_from_shape(shape, diameter, angle):
    if shape == "VBIT":
        return VBit(shape, diameter, angle)
    elif shape == "FLAT":
        return FlatBit(shape, diameter, angle)
    elif shape == "BALL":
        return BallBit(shape, diameter, angle)
    else:
        return None
