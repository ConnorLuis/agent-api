import logging
import sys

def setup_logging() -> None:
    """
    Configure application logging.

    Current format:
        timestamp | level | logger | message
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )