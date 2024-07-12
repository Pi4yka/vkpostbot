class CronScheduleException(Exception):
    """
    Exception thrown when an invalid cron schedule is specified.
    """
    def __init__(self, message):
        super().__init__(message)


class InvalidTimezoneException(Exception):
    """
    Exception thrown when an invalid timezone is specified.
    """
    def __init__(self, message):
        super().__init__(message)


class EmptyUrlException(Exception):
    """
    Exception thrown when url passed in is empty (none).
    """
    def __init__(self, message):
        super().__init__(message)
