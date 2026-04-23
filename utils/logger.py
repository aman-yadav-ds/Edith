import logging
import os
from datetime import datetime

def setup_logger():
    # 1. Ensure the logs directory exists at the root of your project
    log_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "logs")
    os.makedirs(log_dir, exist_ok=True)

    # 2. Create a unique filename for the current run based on the timestamp
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    log_file = os.path.join(log_dir, f"edith_run_{timestamp}.log")

    # 3. Initialize the logger
    logger = logging.getLogger("EdithLogger")
    logger.setLevel(logging.DEBUG)  # Capture everything from DEBUG level and up

    # 4. Create a FileHandler to write to the file (No StreamHandler = clean terminal)
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)

    # 5. Define the format of the logs
    formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(filename)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)

    # 6. Add the handler to the logger
    # We clear existing handlers first to prevent duplicate logs if imported multiple times
    if logger.hasHandlers():
        logger.handlers.clear()
        
    logger.addHandler(file_handler)
    
    # Prevent logs from bubbling up to the root logger and accidentally printing
    logger.propagate = False

    return logger

# Create a global instance that you can import anywhere
edith_logger = setup_logger()