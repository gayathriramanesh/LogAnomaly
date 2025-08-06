import logging
import os

#Setup a logger for each service
def getLogger(service_name: str) -> logging.Logger:
    """
    Returns a logger for the given service name.
    The logger will log to a file named after the service in the logs directory.
    """
    logger = logging.getLogger(service_name)
    logger.setLevel(logging.INFO)
    # Ensure the logs directory exists
    if not logger.handlers:
        os.makedirs('logs', exist_ok=True)
        # Create a file handler
        log_file = os.path.join('logs', f'{service_name}.log')
        file_handler = logging.FileHandler(log_file)

        # Create a formatter and set it for the handler
        formatter = logging.Formatter(
            '{"timestamp": "%(asctime)s", "level": "%(levelname)s", "message": "%(message)s"}'
        )
        file_handler.setFormatter(formatter)

        # Add the handler to the logger
        logger.addHandler(file_handler)

    return logger