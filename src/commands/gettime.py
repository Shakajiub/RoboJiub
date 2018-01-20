from pytz import timezone, UnknownTimeZoneError
from datetime import datetime

def gettime(args):
    if len(args[2]) != 2:
        return False
    user_input = args[2][1]
    try:
        zone = timezone(user_input)
        time = datetime.now(zone)
    except UnknownTimeZoneError:
        return "I don't recognize that timezone :("
    return time.strftime('%Y-%m-%d - %H:%M:%S')
