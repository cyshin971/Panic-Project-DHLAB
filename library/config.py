import logging

# ----------------------
# Logging Configuration
# ----------------------
"""
LOG_FORMAT elements:
%(asctime)s - The time when the log message was created
%(levelname)s - The log level (e.g., DEBUG, INFO, WARNING, ERROR, CRITICAL)
%(filename)s - The filename where the log message was generated
%(funcName)s - The function name where the log message was generated
%(lineno)d - The line number in the source code where the log message was generated
%(message)s - The log message
%(name)s - The name of the logger
%(threadName)s - The name of the thread where the log message was generated

Log Levels:
DEBUG - Detailed information, typically of interest only when diagnosing problems.
INFO - Confirmation that things are working as expected.
WARNING - An indication that something unexpected happened, or indicative of some problem in the near future (e.g., ‘disk space low’). The software is still working as expected.
ERROR - Due to a more serious problem, the software has not been able to perform some function.
CRITICAL - A very serious error, indicating that the program itself may be unable to continue running.
"""
LOG_FORMAT = "%(levelname)s - (%(filename)s) %(funcName)s: %(message)s"
LOG_LEVEL = logging.DEBUG  # Default INFO (Change to DEBUG if needed)

logging.basicConfig(level=LOG_LEVEL, format=LOG_FORMAT)