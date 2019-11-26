import datetime

from tripplanner.models import Service
from tripplannersite.settings import CALENDAR


def datetime2ServiceTYPE(t: datetime.datetime):
    if is_weekend(t):
        return Service.WEEKEND
    elif is_holiday(t):
        return Service.HOLIDAY
    else:
        return Service.NORMAL


def is_weekend(t: datetime.datetime):
    return t.weekday() >= 5


def is_holiday(t: datetime.datetime):
    return t in CALENDAR
