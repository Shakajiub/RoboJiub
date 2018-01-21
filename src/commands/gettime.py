from pytz import timezone, UnknownTimeZoneError
from datetime import datetime

def gettime(args):
    """Get the time in the given timezone."""
    usage = "usage: s!gettime (timezone)"

    if len(args[2]) != 2:
        return usage

    viewer = args[1]
    tz = args[2][1]
    try:
        zone = timezone(tz)
        time = datetime.now(zone)
    except UnknownTimeZoneError:
        return "@{0} - I don't recognize that timezone :(".format(viewer)

    return time.strftime('%Y-%m-%d - %H:%M:%S')
