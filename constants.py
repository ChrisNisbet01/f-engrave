import os
from enum import IntEnum

Zero = 0.00001
IN_AXIS = "AXIS_PROGRESS_BAR" in os.environ
MIN_METRIC_STEP_LEN = 0.01
MIN_IMP_STEP_LEN = 0.0005

class Plane(IntEnum):
    xy = 17
    xz = 18
    yz = 19

class NumberCheck(IntEnum):
    is_valid = 0
    is_valid_no_recalc_required = 1
    is_invalid = 2
    is_not_a_number = 3

