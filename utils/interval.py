from dataclasses import dataclass

import pandas as pd

# ----------------------------------------------------------------------------------------------------------------------


@dataclass
class Interval:
    begin: int
    end: int

# ----------------------------------------------------------------------------------------------------------------------


def is_intersecting(a, b):
    # we assume a begins before b, otherwise swap the intervals
    if a.begin > b.begin:
        a, b = b, a

    return a.end >= b.begin

# ----------------------------------------------------------------------------------------------------------------------


class IntervalGenerator:
    def __init__(self, intervals):
        self.generator = intervals.iterrows()

    def next(self):
        try:
            return next(self.generator)[1]
        except StopIteration:
            return None

# ----------------------------------------------------------------------------------------------------------------------


def intersect_intervals(intervals_1, intervals_2):
    intersections = []
    generator_1 = IntervalGenerator(intervals_1)
    generator_2 = IntervalGenerator(intervals_2)

    interval_1 = generator_1.next()
    interval_2 = generator_2.next()
    while True:
        if interval_1 is None or interval_2 is None:
            return pd.DataFrame(intersections, columns=["begin", "end"])

        if not is_intersecting(interval_1, interval_2):
            if interval_1.begin < interval_2.begin:
                interval_1 = generator_1.next()
            else:
                interval_2 = generator_2.next()
            continue

        # intervals intersect

        if interval_1.begin <= interval_2.begin:
            if interval_1.end <= interval_2.end:
                # interval_1:    >----------------------<
                # interval_2:           >---------------------<
                # intersection:         >---------------<
                intersections.append((interval_2.begin, interval_1.end))
                interval_1 = generator_1.next()
            else:
                # interval_1:    >----------------------<
                # interval_2:           >----------<
                # intersection:         >----------<
                intersections.append((interval_2.begin, interval_2.end))
                interval_2 = generator_2.next()
        else:
            if interval_1.end >= interval_2.end:
                # interval_1:           >---------------------<
                # interval_2:    >----------------------<
                # intersection:         >---------------<
                intersections.append((interval_1.begin, interval_2.end))
                interval_2 = generator_2.next()
            else:
                # interval_1:           >----------<
                # interval_b:    >----------------------<
                # intersection:         >----------<
                intersections.append((interval_1.begin, interval_1.end))
                interval_1 = generator_1.next()

# ----------------------------------------------------------------------------------------------------------------------
