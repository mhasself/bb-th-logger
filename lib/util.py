
#
# Date/Time Utilities
#
import time
import calendar

DEFAULT_FORMAT = '%Y-%m-%d %H:%M:%S'

def ctime_to_string(t, format=DEFAULT_FORMAT):
    """
    @brief Translate a ctime (int) to a formatted string.
    @param ctime int: ctime to translate
    @return str: formatted time string
    """
    return time.strftime(format, time.gmtime(t))

def string_to_ctime(s, format=DEFAULT_FORMAT):
    """
    @brief Translate a formatted time string to a ctime
    @param asctime str: formatted time string (see mobyManifest.timeFormat)
    @return int: ctime
    """
    return calendar.timegm(time.strptime(s, format))
