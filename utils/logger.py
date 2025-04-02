#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

""" Logger configuration for GenMedia Arena """
from curses import ERR
import logging
from termios import VERASE

class LogLevel:
    """Enum for log levels"""
    OFF = 0
    ON = 1
    WARNING = 2
    ERROR = 3
    _names = {
        0: "OFF",
        1: "ON",
        2: "WARNING",
        3: "ERROR"
    }

    def __repr__(self):
        return self._names.get(self, "UNKNOWN")
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(message)s",
    datefmt="%H:%M:%S",)

def log(message: str, level: LogLevel = LogLevel.ON):
    """Log a message at the specified level."""
    if level == LogLevel.OFF:
        return  # Do not log if level is OFF
    if level == LogLevel.ON:
        logging.info(message)
    elif level == LogLevel.WARNING:
        logging.warning(message)
    elif level == LogLevel.ERROR:
        logging.error(message)
    else:
        raise ValueError("Invalid log level specified. Use LogLevel.ON or LogLevel.OFF.")