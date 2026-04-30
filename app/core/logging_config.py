# logging config file for handle loggings in this project
import logging
import sys

def setup_logging():
    # format to show in terminal time-name-level-message
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=logging.INFO, 
        format = log_format,
        handlers=[
            logging.StreamHandler(sys.stdout),      # output in terminal 
            logging.FileHandler("app.log")          # save app.log file
        ],
        force=True
    )

def get_logger(name:str):

    return logging.getLogger(name)