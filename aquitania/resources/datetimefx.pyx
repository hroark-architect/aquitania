########################################################################################################################
# |||||||||||||||||||||||||||||||||||||||||||||||||| AQUITANIA ||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
# |||| To be a thinker means to go by the factual evidence of a case, not by the judgment of others |||||||||||||||||| #
# |||| As there is no group stomach to digest collectively, there is no group mind to think collectively. |||||||||||| #
# |||| Each man must accept responsibility for his own life, each must be sovereign by his own judgment. ||||||||||||| #
# |||| If a man believes a claim to be true, then he must hold to this belief even though society opposes him. ||||||| #
# |||| Not only know what you want, but be willing to break all established conventions to accomplish it. |||||||||||| #
# |||| The merit of a design is the only credential that you require. |||||||||||||||||||||||||||||||||||||||||||||||| #
# |||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||| #
########################################################################################################################

"""
.. moduleauthor:: H Roark

These were one of the first files ever to be built. Since then Aquitania became each time more object-oriented and I
have been not using some much these libraries of static functions. This one was one of the few useful survivors.
"""

import pytz
import datetime as dtm
import pandas as pd
from cpython.datetime cimport datetime

cpdef str now():
    return '[{}]: '.format(str(dtm.datetime.now())[0:19])

# TODO this module needs a big review and refactor
cpdef datetime dt_from_ts(double dt):
    return aware_to_naive(pd.to_datetime(dt * 1e9, utc=True))

def instantiates_tz(time, tz_object):
    if time.tzinfo is None or time.tzinfo.utcoffset(time) is None:
        return tz_object.localize(time)

cpdef bint is_fx_working_hours(datetime dt):
    return dt.weekday() < 4 or (dt.weekday() == 4 and dt.hour < 17) or (dt.weekday() == 6 and dt.hour >= 17)

def is_fx_working_hours_from_tz(candle_time):
    # TODO create more elaborate method to consider the working hours of each individual asset
    """
    Evaluates if a candle is part of the normal FX working hours.

    :param candle_time: Datetime that will be evaluated for being in the 17-17 NY TZ
    :param tz: candle_time timezone to be evaluated

    :return: Returns True if the candle is a valid working hour in 17-17 NY TZ
    :rtype: Boolean
    """
    #  Instantiates NY TimeZone
    ny_tz = pytz.timezone('America/New_York')

    # If naive transforms to aware
    gmt_time = transform_to_gmt(candle_time)
    ny_time = gmt_time.astimezone(ny_tz)
    return is_fx_working_hours(ny_time)

def transform_to_tz(candle_time, tz_name):
    gmt_tz = pytz.timezone('GMT')

    if candle_time.tzinfo is None or candle_time.tzinfo.utcoffset(candle_time) is None:
        # TODO ensure this routine works perfectly, if not find a way to guarantee Aquitania runs independent of OS tz
        candle_time = gmt_tz.localize(candle_time)

    tz = pytz.timezone(tz_name)
    return candle_time.astimezone(tz)

def transform_to_nyt(candle_time):
    return transform_to_tz(candle_time, 'America/New_York')

def transform_to_gmt(candle_time):
    return transform_to_tz(candle_time, 'GMT')

def last_market_candle(datetime_var):
    """
    Returns value of the last possible traded candle on FX markets.

    :return: Datetime value of last possible traded candle given current time in GMT
    :rtype: datetime
    """
    if is_fx_working_hours_from_tz(datetime_var):
        return datetime_var
    else:
        return last_market_close(datetime_var)

def datetime_as_ny(candle_time):
    """
    Converts datetime to NY time.

    If naive timestamp it will be converted to GMT.

    :param candle_time: GMT datetime to calculate NY datetime.
    :return: NY datetime given GMT datetime
    :rtype: datetime
    """
    gmt_tz = pytz.timezone('GMT')
    ny_tz = pytz.timezone('America/New_York')
    if candle_time.tzinfo is None or candle_time.tzinfo.utcoffset(candle_time) is None:
        candle_time = gmt_tz.localize(candle_time)
    return candle_time.astimezone(ny_tz)

def last_market_close(datetime_value):
    """
    Returns value for last market close on FX given a datetime.

    :param datetime_value: datetime that will be used as reference to calculate last market close
    :return: Datetime of the last market close in GMT hours
    :rtype: datetime
    """

    datetime_value = datetime_as_ny(datetime_value)

    weekday = datetime_value.weekday()
    hour_value = datetime_value.hour
    if weekday <= 4:
        if weekday < 4:
            weekday += 7
        elif hour_value < 17:
            weekday += 7

    datetime_value = datetime_value + dtm.timedelta(days=4 - weekday)
    datetime_value = datetime_value.replace(hour=16, minute=59)

    gmt_tz = pytz.timezone('GMT')
    return datetime_value.astimezone(gmt_tz).replace(tzinfo=None)

cpdef datetime next_market_close(datetime datetime_value):
    """
    Returns the next FX market open given a datetime value.

    :param: candle_time Reference candle from which the next FX market open will be calculated
    :return: Returns the date and time of the next FX market open
    :rtype: datetime
    """
    datetime_value = datetime_as_ny(datetime_value)

    weekday = datetime_value.weekday()
    weekday = weekday if weekday <= 4 else weekday - 7

    datetime_value = datetime_value + dtm.timedelta(days=4 - weekday)
    datetime_value = datetime_value.replace(hour=16, minute=59)
    return datetime_value.astimezone(pytz.timezone('GMT')).replace(tzinfo=None)

def next_market_open(candle_time):
    """
    Returns the next FX market open given a datetime value.

    :param: candle_time Reference candle from which the next FX market open will be calculated
    :return: Returns the date and time of the next FX market open
    :rtype: datetime
    """
    ny_time = datetime_as_ny(candle_time)
    ny_time = ny_time + dtm.timedelta(days=6 - ny_time.weekday())
    ny_time = ny_time.replace(hour=17)

    gmt_tz = pytz.timezone('GMT')
    return ny_time.astimezone(gmt_tz)

cpdef datetime aware_to_naive(datetime candle_time):
    """
    Makes an aware timezone datetime a naive one.

    :param candle_time: object to be naivized
    :return: a naive datetime object
    :rtype: datetime NAIVE
    """
    return candle_time.replace(tzinfo=None)

def next_candle_time_working_hours(candle_time, ts_in_minutes):
    """
    Returns the next candle open_time.

    Does not account for FX working hours.

    :candletime current candle open_time
    :ts_in_minutes timestamp in minutes
    """
    time_diff = dtm.timedelta(minutes=ts_in_minutes)
    candle_time = candle_time + time_diff
    if is_fx_working_hours_from_tz(candle_time):
        return candle_time
    else:
        return next_market_open(candle_time)

def previous_candle(candle_time, ts_in_minutes):
    time_diff = dtm.timedelta(minutes=ts_in_minutes)
    return candle_time - time_diff

def next_candle_datetime(candle_time, ts_in_minutes):
    time_diff = dtm.timedelta(minutes=ts_in_minutes)
    return candle_time + time_diff

def ny_to_gmt(dt_tm):
    gmt_tz = pytz.timezone('GMT')
    ny_tz = pytz.timezone('America/New_York')
    if dt_tm.tzinfo is None or dt_tm.tzinfo.utcoffset(dt_tm) is None:
        dt_tm = ny_tz.localize(dt_tm)
    return dt_tm.astimezone(gmt_tz)

def is_last_g01_candle_day(dt_tm):
    if dt_tm.weekday == 4 and dt_tm.hour > 19:
        hour_close = ny_to_gmt(dt_tm.replace(hour=17)).hour
        if dt_tm.hour == hour_close - 1 and dt_tm.minute == 59:
            return True
    if dt_tm.hour == 23 and dt_tm.minute == 59:
        return True
    return False


cpdef tuple init_open_close_times(datetime dt, int ts):
        """
        Initializes Candle with open and close time values.

        :return: Candle open time, Candle close time
        :rtype: tuple of 2 datetime elements
        """
        if ts == -1:
            ts = ts
        # This if elif structure looks ridiculous but it is really fast.
        if ts == 0:
            return dt, dt
        elif ts == 1:
            return div_by_sec(dt, 300)
        elif ts == 2:
            return div_by_sec(dt, 900)
        elif ts == 3:
            return div_by_sec(dt, 1800)
        elif ts == 4:
            return div_by_sec(dt, 3600)
        elif ts == 5:
            return daily_criteria(dt)
        elif ts == 6:
            return weekly_criteria(dt)
        elif ts == 7:
            return monthly_criteria(dt)
        else:
            raise ValueError('Invalid Candle TimeStamp')

cdef tuple div_by_sec(datetime dt, int seconds):
    cdef:
        datetime open_time
        datetime close_time

    open_time = pd.Timestamp(dt.value // (seconds * 1e9) * seconds * 1e9)
    close_time = pd.Timestamp(open_time.value + (seconds - 60) * 1e9)

    return open_time, close_time

cdef tuple daily_criteria(datetime dt):
    open_time = (dt.timestamp() // 86400) * 86400
    close_time = open_time + 86400 - 60

    # Puts Monday together with Sunday
    if dt.weekday() == 0:
        open_time -= 86400
        open_time = dt_from_ts(open_time)
    else:
        open_time = dt_from_ts(open_time)

    if dt.weekday() == 6:
        close_time += 86400
        close_time = dt_from_ts(close_time)
    elif dt.weekday() == 4:
        close_time = next_market_close(dt)
    else:
        close_time = dt_from_ts(close_time)

    return open_time, close_time

cdef tuple weekly_criteria(datetime dt):
    # Need to divide in to groups:
    #  1. 3-5 Thursday to Saturday
    if 3 <= dt.weekday() <= 5:
        open_time = (dt.timestamp() // 604800) * 604800 - 345600
    # 2. Other weekdays
    else:
        open_time = (dt.timestamp() // 604800) * 604800 + 259200

    close_time = dt_from_ts(open_time + 604800 - 60)
    if 5 >= close_time.weekday() >= 4:
        close_time = next_market_close(dt)

    return dt_from_ts(open_time), close_time

cdef tuple monthly_criteria(datetime dt):
    cdef:
        datetime open_time
        datetime close_time
    open_time = dtm.datetime(dt.year, dt.month, 1)

    if dt.month == 12:
        close_time = previous_candle(dtm.datetime(dt.year + 1, 1, 1), 1)
    else:
        close_time = previous_candle(dtm.datetime(dt.year, dt.month + 1, 1), 1)

    if 5 >= close_time.weekday() >= 4:
        close_time = last_market_close(close_time)

    return open_time, close_time
