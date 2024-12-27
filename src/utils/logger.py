import logging
import sys
from pathlib import Path
from typing import Optional


def setup_logger(
        name: str,
        log_file: Optional[str] = None,
        level: int = logging.INFO
) -> logging.Logger:
    """
    Set up a logger with console and optional file output.
    
    Args:
        name (str): Logger name
        log_file (str, optional): Path to log file
        level (int): Logging level
        
    Returns:
        logging.Logger: Configured logger instance
    """
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Prevent duplicate handlers
    if logger.handlers:
        return logger

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(detailed_formatter)
    logger.addHandler(console_handler)

    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(str(log_path.absolute()))
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

    return logger
