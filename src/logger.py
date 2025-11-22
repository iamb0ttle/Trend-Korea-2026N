import logging
from rich.logging import RichHandler

# Global logging configuration
# Set level to CRITICAL to suppress noisy logs from external libraries (e.g., Selenium, urllib3).
logging.basicConfig(
    level="CRITICAL", 
    format="%(message)s",
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True)]
)

class AppLogger(logging.LoggerAdapter):
    """
    A custom logger adapter that prefixes log messages with a specific tag.

    This class wraps the standard logger to automatically prepend a prefix (e.g., [Module])
    to all log messages. It also ensures that logs from this instance are set to 
    the INFO level, overriding the global CRITICAL setting.

    Attributes:
        extra (dict): A dictionary containing the prefix information.
    """

    def __init__(self, prefix: str):
        """
        Initializes the AppLogger with a specific prefix.

        Args:
            prefix (str): The string tag to be prepended to every log message
                (e.g., "[BrowserClient]", "[Database]").
        """
        # Use a specific logger name 'rich' or 'App' to manage this stream
        logger = logging.getLogger("rich")

        # Explicitly set this logger's level to INFO to make it visible
        # despite the global configuration being set to CRITICAL.
        logger.setLevel(logging.INFO)
        
        super().__init__(logger, {"prefix": prefix})

    def process(self, msg, kwargs):
        """
        Processes the log message to inject the prefix.

        Overrides the LoggerAdapter.process method.

        Args:
            msg (str): The original log message.
            kwargs (dict): Keyword arguments passed to the logging call.

        Returns:
            tuple: A tuple containing the modified message string (with prefix)
                and the original keyword arguments.
        """
        return f"{self.extra['prefix']} {msg}", kwargs
  

def test_logger():
    """
    Demonstrates the functionality of the AppLogger class.

    This function initializes the logger with a "[TEST]" prefix and triggers
    info, warning, and exception logs to verify formatting, color output, 
    and traceback handling.
    """
    logger = AppLogger("[TEST]")
  
    logger.info("Info Log test")
    logger.warning("Warning Log test")
    
    try:
        1 / 0
    except Exception:
        # logger.exception automatically includes the stack trace
        logger.exception("When exception occurred, traceback will be printed.")


if __name__ == "__main__":
    test_logger()