#!/usr/bin/env python3
"""
Logging module for Hackatune application
"""
import logging
import os
from datetime import datetime

# Create logs directory if it doesn't exist
LOGS_DIR = "logs"
if not os.path.exists(LOGS_DIR):
    os.makedirs(LOGS_DIR)

# Create logger
logger = logging.getLogger("Hackatune")
logger.setLevel(logging.DEBUG)

# Create console handler (INFO level)
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)

# Create file handler (DEBUG level) with timestamp
log_file = os.path.join(LOGS_DIR, f"hackatune_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
file_handler = logging.FileHandler(log_file)
file_handler.setLevel(logging.DEBUG)

# Create formatter
formatter = logging.Formatter(
    fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Add formatter to handlers
console_handler.setFormatter(formatter)
file_handler.setFormatter(formatter)

# Add handlers to logger
logger.addHandler(console_handler)
logger.addHandler(file_handler)

# Export logger
__all__ = ['logger', 'LOGS_DIR']
