import pytest
from datetime import datetime

import pandas as pd

from utils.interval import intersect_intervals, is_intersecting, Interval, find_intervals

# ----------------------------------------------------------------------------------------------------------------------

intersect_data = [(Interval(1, 1), Interval(1, 1), True),
                  (Interval(1, 4), Interval(2, 3), True),
                  (Interval(2, 5), Interval(1, 7), True),
                  (Interval(1, 7), Interval(6, 8), True),
                  (Interval(3, 9), Interval(2, 4), True),
                  (Interval(0, 1), Interval(2, 3), False),
                  (Interval(3, 6), Interval(1, 2), False),
                  (Interval(1, 5), Interval(5, 7), True),
                  (Interval(2, 5), Interval(1, 2), True)]

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("a, b, intersect", intersect_data)
def test_is_intersecting(a, b, intersect: bool):
    assert is_intersecting(a, b) == intersect
    assert is_intersecting(b, a) == intersect

# ----------------------------------------------------------------------------------------------------------------------


def t(time_input: str):
    try:
        return datetime.strptime(f"2020-03-16 {time_input}", "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return datetime.strptime(f"2020-03-16 {time_input}", "%Y-%m-%d %H:%M:%S.%f")


# ----------------------------------------------------------------------------------------------------------------------

intersection_data = [
    dict(a=[],
         b=[],
         c=[]),
    dict(a=[(1, 2)],
         b=[],
         c=[]),
    dict(a=[],
         b=[(1, 2), (4, 6)],
         c=[]),
    dict(a=[(3, 4), (7, 8), (9, 10)],
         b=[(1, 2), (5, 6)],
         c=[]),
    dict(a=[(1, 2)],
         b=[(1, 2)],
         c=[(1, 2)]),
    dict(a=[(1, 2), (5, 7)],
         b=[(1, 2), (5, 7)],
         c=[(1, 2), (5, 7)]),
    dict(a=[(1, 2), (5, 7), (10, 12)],
         b=[(1, 2), (5, 7)],
         c=[(1, 2), (5, 7)]),
    dict(a=[(1, 2), (5, 7), (10, 12), (17, 20), (22, 23)],
         b=[(1, 2), (5, 7)],
         c=[(1, 2), (5, 7)]),
    dict(a=[(3, 5)],
         b=[(1, 4)],
         c=[(3, 4)]),
    dict(a=[(1, 7)],
         b=[(3, 5)],
         c=[(3, 5)]),
    dict(a=[(3, 4), (5, 7), (9, 10)],
         b=[(1, 7)],
         c=[(3, 4), (5, 7)]),
    dict(a=[(0, 2)],
         b=[(4, 13), (16, 18), (19, 22), (24, 26), (30, 31)],
         c=[]),
    dict(a=[(0, 2), (3, 4)],
         b=[(4, 13), (16, 18), (19, 22), (24, 26), (30, 31)],
         c=[(4, 4)]),
    dict(a=[(0, 2), (3, 4), (5, 7)],
         b=[(4, 13), (16, 18), (19, 22), (24, 26), (30, 31)],
         c=[(4, 4), (5, 7)]),
    dict(a=[(0, 2), (3, 4), (5, 7), (9, 10)],
         b=[(4, 13), (16, 18), (19, 22), (24, 26), (30, 31)],
         c=[(4, 4), (5, 7), (9, 10)]),
    dict(a=[(0, 2), (3, 4), (5, 7), (9, 10), (11, 15)],
         b=[(4, 13), (16, 18), (19, 22), (24, 26), (30, 31)],
         c=[(4, 4), (5, 7), (9, 10), (11, 13)]),
    dict(a=[(0, 2), (3, 4)],
         b=[(0, 4)],
         c=[(0, 2), (3, 4)]),
    dict(a=[(0, 2), (3, 4)],
         b=[(1, 10)],
         c=[(1, 2), (3, 4)]),
    dict(a=[(0, 2), (9, 11)],
         b=[(1, 10)],
         c=[(1, 2), (9, 10)]),
    dict(a=[(0, 2), (3, 5), (9, 11)],
         b=[(1, 10)],
         c=[(1, 2), (3, 5), (9, 10)]),
    dict(a=[(0, 2), (3, 4), (5, 7), (9, 10), (11, 15), (20, 25)],
         b=[(4, 13), (16, 18), (19, 22), (24, 26), (30, 31)],
         c=[(4, 4), (5, 7), (9, 10), (11, 13), (20, 22), (24, 25)]),
    dict(a=[(t("10:00:00"), t("11:05:00"))],
         b=[(t("9:34:53"), t("11:03:34"))],
         c=[(t("10:00:00"), t("11:03:34"))]),
    dict(a=[(t("11:01:27.834999"), t("12:15:41.037585")),
            (t("12:18:17.408448"), t("12:20:18.027845")),
            (t("12:23:48.719316"), t("15:28:20.845609")),
            (t("15:31:09.530427"), t("23:59:59.000000"))],
         b=[(t("01:54:52.167262"), t("01:55:22.830804")),
            (t("02:03:21.645642"), t("02:03:40.554239")),
            (t("08:29:40.462335"), t("08:43:38.797088")),
            (t("08:44:39.785051"), t("08:50:03.255949")),
            (t("08:57:13.152302"), t("09:12:44.638700")),
            (t("09:13:30.258904"), t("09:33:01.231312")),
            (t("09:37:22.225314"), t("09:38:27.977446")),
            (t("09:38:45.604175"), t("09:39:22.195649")),
            (t("09:40:49.781471"), t("09:52:13.633493")),
            (t("09:53:07.025995"), t("09:59:16.342491")),
            (t("10:01:55.371701"), t("10:02:02.922624")),
            (t("10:04:00.259148"), t("10:04:10.709589")),
            (t("10:06:51.662356"), t("10:07:18.613433")),
            (t("10:08:07.307537"), t("10:16:38.275054")),
            (t("10:17:21.692835"), t("10:22:37.325446")),
            (t("10:22:48.695285"), t("10:49:10.855595")),
            (t("10:51:51.887570"), t("10:54:59.191939")),
            (t("11:00:21.323844"), t("11:01:57.363839")),
            (t("11:02:27.776184"), t("12:29:24.135825")),
            (t("12:54:39.705964"), t("13:19:57.913696")),
            (t("13:20:30.002676"), t("13:49:34.438984")),
            (t("13:49:46.009046"), t("13:54:25.240610")),
            (t("14:12:53.877655"), t("15:10:23.599668")),
            (t("15:12:15.618124"), t("15:48:40.993915")),
            (t("15:48:56.230357"), t("16:00:10.028289")),
            (t("16:02:08.531197"), t("16:03:12.287722")),
            (t("16:04:02.840217"), t("16:11:40.236731")),
            (t("16:11:52.221607"), t("16:24:02.252456")),
            (t("16:24:18.093914"), t("16:41:14.417678")),
            (t("16:42:30.515474"), t("17:05:09.778303")),
            (t("17:07:19.507349"), t("18:02:36.084452"))],
         c=[(t("11:01:27.834999"), t("11:01:57.363839")),
            (t("11:02:27.776184"), t("12:15:41.037585")),
            (t("12:18:17.408448"), t("12:20:18.027845")),
            (t("12:23:48.719316"), t("12:29:24.135825")),
            (t("12:54:39.705964"), t("13:19:57.913696")),
            (t("13:20:30.002676"), t("13:49:34.438984")),
            (t("13:49:46.009046"), t("13:54:25.240610")),
            (t("14:12:53.877655"), t("15:10:23.599668")),
            (t("15:12:15.618124"), t("15:28:20.845609")),
            (t("15:31:09.530427"), t("15:48:40.993915")),
            (t("15:48:56.230357"), t("16:00:10.028289")),
            (t("16:02:08.531197"), t("16:03:12.287722")),
            (t("16:04:02.840217"), t("16:11:40.236731")),
            (t("16:11:52.221607"), t("16:24:02.252456")),
            (t("16:24:18.093914"), t("16:41:14.417678")),
            (t("16:42:30.515474"), t("17:05:09.778303")),
            (t("17:07:19.507349"), t("18:02:36.084452"))])
    ]

# ----------------------------------------------------------------------------------------------------------------------


@pytest.mark.parametrize("data", intersection_data)
def test_intersect_interval(data):
    def df(intervals):
        return pd.DataFrame(intervals, columns=['begin', 'end'])

    a = df(data['a'])
    b = df(data['b'])
    c = df(data['c'])

    assert intersect_intervals(a, b).to_dict() == c.to_dict()
    assert intersect_intervals(b, a).to_dict() == c.to_dict()

# ----------------------------------------------------------------------------------------------------------------------


def test_find_intervals_empty():
    data = find_intervals(pd.DataFrame())
    assert data.empty

# ----------------------------------------------------------------------------------------------------------------------