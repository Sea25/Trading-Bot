import logging
import sys

def setup_logging():
    """Configure logging to file and console"""
    
    # Create logger
    logger = logging.getLogger('trading_bot')
    logger.setLevel(logging.DEBUG)
    
    # File handler (detailed)
    file_handler = logging.FileHandler('trading_bot.log')
    file_handler.setLevel(logging.DEBUG)
    file_format = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_format)
    
    # Console handler (important info only)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_format = logging.Formatter('%(message)s')
    console_handler.setFormatter(console_format)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger