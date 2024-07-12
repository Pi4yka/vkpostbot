import re
import sys
import time

from datetime import datetime

from _exceptions import InvalidTimezoneException

# conditional use of timezone module depending on python version
if sys.version_info < (3, 2):
    # Python 3.0, 3.1
    def utcnow():
        """
        Retrieves current time in UTC.

        :return: current time in UTC
        """
        return datetime.utcnow()
else:
    # Python 3.2 and later
    from datetime import timezone

    def utcnow():
        """
        Retrieves current time in UTC.

        :return: current time in UTC
        """
        return datetime.now(timezone.utc)


def get_system_timezone() -> str:
    """
    Retrieves the timezone for the system in UTC (e.g., UTC+08:00).

    :return: system timezone in UTC
    """
    offset_seconds = -time.timezone
    offset_hours = offset_seconds // 3600
    offset_minutes = (offset_seconds % 3600) // 60
    sign = "+" if offset_seconds >= 0 else "-"
    utc_offset_str = "{}{:02d}:{:02d}".format(sign, abs(offset_hours), abs(offset_minutes))

    # todo: allow specifying with GMT etc?
    return "UTC" + utc_offset_str


def get_timezone_offset(timezone_str: str) -> int:
    """
    Retrieves the timezone offset in seconds compared to UTC.

    :param timezone_str: timezone to get offset for
    :raises InvalidTimezoneException: an invalid timezone has been provided
    :return: number representing timezone offset in seconds
    """
    pattern = re.compile(
        r'^utc([+-])(1[0-4]|0?[0-9])'
        r'(:[0-5][0-9])?$',
        re.IGNORECASE
    )
    match = pattern.match(timezone_str)

    if match:
        sign = match.group(1)
        hours = int(match.group(2))
        minutes = int(match.group(3)[1:]) if match.group(3) else 0
        offset_seconds = (1 if sign == '+' else -1) * (hours * 3600 + minutes * 60)
        return offset_seconds
    else:
        raise InvalidTimezoneException("Invalid Timezone, must be of UTC format!")
