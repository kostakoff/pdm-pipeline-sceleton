#!/usr/bin/env python

import sys
import os

# load PEP 582 libraryes
_PATH = "/__pypackages__/3.8/lib"
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + _PATH)

# load deps
import getopt
import yaml
import json
import uuid

from src import logger
from src.utils import CmdExecutor

def init_pipeline():

    logger.info("Python pipeline initialization start")
    with open('./onboarding.yaml', 'r') as read_yaml: 
        onboarding = yaml.load(read_yaml, Loader=yaml.FullLoader)


    logger.info("Python pipeline initialization done")

# help
def print_help():
    help_str = """Possible functions:
    Init pipeline metadata:
    python pipeline.py --init

    Show this page:
    python pipeline.py --help
    """
    print(help_str)

# main 
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "hu:t:i:o:", ["init", "help", "backup_truststore", "update_truststore", "fetch_certificates"])
        
    except getopt.GetoptError:
        logger.error("Wrong options")
        print_help()
        sys.exit(2)
    for opt, arg in opts:
        if opt == '--help':
            print_help()
            sys.exit()
        elif opt == '--init':
            init_pipeline()

if __name__ == "__main__":
    main(sys.argv[1:])
