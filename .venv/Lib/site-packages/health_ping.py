import logging
import os
import threading
import urllib.request

from datetime import timedelta
from urllib.error import URLError
from urllib.error import HTTPError

from crontab import CronTab

from _datetime_utils import get_system_timezone
from _datetime_utils import get_timezone_offset
from _datetime_utils import utcnow
from _exceptions import CronScheduleException
from _exceptions import EmptyUrlException


class HealthPing:
    """
    Object containing information for carrying out scheduled health pings.

    :param url: url to call
    :param method: http method to call url with
    :param headers: http headers to call url with
    :param body: body to call url with
    :param timezone: timezone to reference
    :param schedule: cron schedule for health pings
    :param retries: list containing seconds to retry on failed call
    :param pre_fire: function called before a scheduled health ping
    :param post_fire: function called after a scheduled health ping
    :param log_file: whether to store a history of scheduled pings
    :param debug: whether to run in debug mode
    """
    def __init__(self, url, method="GET", headers={}, body={}, timezone=get_system_timezone(),
                 schedule="0 * * * *", retries=[], pre_fire=None, post_fire=None, log_file=None,
                 debug=False):

        # url cannot be empty
        if url is None or not url or url.isspace():
            raise EmptyUrlException("URL cannot be empty!")

        # user parameters
        self.url = url
        self.method = method
        self.headers = headers
        self.body = body
        self.timezone = timezone
        self.schedule = schedule
        self.retries = retries
        self.pre_fire = pre_fire
        self.post_fire = post_fire
        self.log_file = log_file
        self.debug = debug

        # ping result
        self.result = None

        # internal use
        self.__timezone_offset = get_timezone_offset(self.timezone)
        self.__timer = None
        self.__retry_count = 0
        self.__stopped_flag = True
        self.__logger = self._setup_logger()
        self.__next_execution_time = None

    def start(self):
        """
        Begins running a health ping schedule.
        """
        if self.__timer is not None:
            if self.__logger:
                self.__logger.info("HealthPing schedule already running!")
            return
        self.__stopped_flag = False
        self._create_timer(self._get_seconds_to_next_job())
        if self.__logger:
            self.__logger.info("HealthPing schedule started!")

    def stop(self):
        """
        Stops existing health ping schedule.
        """
        if self.__timer is None:
            if self.__logger:
                self.__logger.info("No HealthPing schedule running!")
            return

        self.__timer.cancel()
        self.__timer = None
        self.__next_execution_time = None
        self.__stopped_flag = True
        if self.__logger:
            self.__logger.info("HealthPing schedule stopped!")

    def fire(self, is_schedule=False):
        """
        Fires a single health ping call and retries if necessary.
        """
        current_time = utcnow() + timedelta(seconds=self.__timezone_offset)
        if self.__logger:
            self.__logger.info("HealthPing job executed at: {} ({})".format(current_time,
                                                                            self.timezone))

        if self.pre_fire is not None:
            self.pre_fire()

        is_retry = False
        try:
            request = urllib.request.Request(self.url, data=self.body, headers=self.headers,
                                             method=self.method)
            with urllib.request.urlopen(request) as response:
                self.result = PingResult(success=True, data=response.read().decode('utf-8'))
            self.__retry_count = 0
        except (URLError, HTTPError, ValueError) as e:
            self.result = PingResult(success=False, data=e)
            is_retry = (
                self.__retry_count < len(self.retries) and
                self.retries[self.__retry_count] <= self._get_seconds_to_next_job()
            )
        finally:
            if self.post_fire:
                self.post_fire()

            seconds_to_next_run = (
                self.retries[self.__retry_count] if is_retry else
                self._get_seconds_to_next_job()
            )
            self.__retry_count = self.__retry_count + 1 if is_retry else 0

            if is_schedule:
                self._create_timer(seconds_to_next_run)

    def next_time(self):
        """
        Retrieves the next time that a ping is fired.
        """
        return self.__next_execution_time

    def _get_seconds_to_next_job(self):
        """
        Retrieves the number of seconds to the next scheduled run.

        :return: number of seconds till the next schedule run.
        """
        try:
            current_time = utcnow() + timedelta(seconds=self.__timezone_offset)
            return CronTab(self.schedule).next(current_time, default_utc=False)
        except ValueError as e:
            raise CronScheduleException(e)

    def _create_timer(self, seconds_to_next_run):
        """
        Creates a timer that will run the next execution.

        :param seconds_to_next_run: number of seconds till the next run
        """
        if self.__stopped_flag:
            return

        new_timer = threading.Timer(seconds_to_next_run, self.fire, args=(True,))
        new_timer.daemon = True
        try:
            new_timer.start()
        # catches RuntimeError from python >= 3.12
        except RuntimeError:
            self.stop()
        current_timer, self.__timer = self.__timer, new_timer

        if current_timer is not None:
            current_timer.cancel()

        current_time = utcnow() + timedelta(seconds=self.__timezone_offset)
        next_time = current_time + timedelta(seconds=seconds_to_next_run)
        self.__next_execution_time = next_time

        if self.__logger:
            self.__logger.info("Current Time: {} ({})".format(current_time, self.timezone))
            self.__logger.info("Next Time: {} ({})".format(next_time, self.timezone))

    def _setup_logger(self):
        """
        Creates a logger to output information.

        :return: logger to log output
        """
        if not self.debug and not self.log_file:
            return None

        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        if self.debug:
            console_handler = logging.StreamHandler()
            console_handler.setFormatter(formatter)
            logger.addHandler(console_handler)

        if self.log_file:
            log_dir = os.path.dirname(self.log_file)
            os.makedirs(log_dir, exist_ok=True)
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(formatter)
            logger.addHandler(file_handler)

        return logger


class PingResult():
    """
    Ping result containing success state and response/error data.

    :param success: boolean indicating whether ping was successful
    :param data: response if ping was successful, else error
    """
    def __init__(self, success, data):
        self.success = success
        self.data = data
