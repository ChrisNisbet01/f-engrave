class GCode(list):
    def __init__(self, enable_variables, accuracy, metric):
        super(list, self).__init__()
        self.enable_variables = enable_variables
        self.accuracy = accuracy
        self.metric = metric
        if self.metric:
            self.dp = 3
            self.dpfeed = 1
        else:  # Imperial
            self.dp = 4
            self.dpfeed = 2

    def assign_safe_z(self, safe_z):
        if self.enable_variables:
            FORMAT = '#1 = %%.%df  ( Safe Z )' % (self.dp)
            self.append(FORMAT % (safe_z))
            self.safe_val = '#1'
        else:
            FORMAT = '%%.%df' % (self.dp)
            self.safe_val = FORMAT % (safe_z)
            self.append_comment("Safe Z: " + self.safe_val)

    def assign_depth(self, depth):
        if self.enable_variables:
            FORMAT = '#2 = %%.%df  ( Engraving Depth Z )' % (self.dp)
            self.append(FORMAT % (depth))
            self.depth_val = '#2'
        else:
            FORMAT = '%%.%df' % (self.dp)
            self.depth_val = FORMAT % (depth)
            self.append_comment("Engraving Depth Z: " + self.depth_val)

    def append_comment(self, comment):
        self.append("(" + comment + ")")

    def retract_z(self):
        self.append("G0 Z%s" % (self.safe_val))

    def set_feed_rate(self, feed_rate):
        FORMAT = '%%.%df' % (self.dpfeed)
        self.feed_str = FORMAT % (float(feed_rate))
        self.append("F%s" % self.feed_str)

    def set_plunge_rate(self, plunge_rate):
        FORMAT = '%%.%df' % (self.dpfeed)
        zero_feed = FORMAT % (float(0.0))
        self.plunge_str = FORMAT % (float(plunge_rate))
        if self.plunge_str == zero_feed:
            self.plunge_str = self.feed_str

    def plunge_z(self, depth_val=None):
        if depth_val is None:
            depth_str = self.depth_val
        else:
            FORMAT = '%%.%df' % (self.dp)
            depth_str = FORMAT % (float(depth_val))
        if (self.feed_str == self.plunge_str):
            self.append('G1 Z%s' % (depth_str))
            return None
        self.append('G1 Z%s F%s' % (depth_str, self.plunge_str))
        # Caller needs to know the normal feed rate
        return self.feed_str

    def rapid(self, x, y):
        FORMAT = 'G0 X%%.%df Y%%.%df' % (self.dp, self.dp)
        self.append(FORMAT % (x, y))

    def arc(self, cw, I, J):
        if cw:
            cmd = "G2"
        else:
            cmd="G3"
        FORMAT = '%s I%%.%df J%%.%df F%%s' % (cmd, self.dp, self.dp)
        self.append(FORMAT % (I, J, self.feed_str))

