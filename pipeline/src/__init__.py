import logging

# set logging settings
log = logging.getLogger(__name__)
log.setLevel(logging.INFO)

FORMAT = '%(asctime)s - %(threadName)s - %(levelname)s - %(message)s'
logging.basicConfig(format=FORMAT)
logger = logging.getLogger(__name__)