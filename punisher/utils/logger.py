import os
import imp
import logging
import time
import traceback

import punisher.config as cfg
from punisher.clients import ses_client


def retry_hdlr(details):
    print(traceback.format_exc())
    print("Backing off {wait:0.1f} seconds afters {tries} tries "
           "calling function {target} with args {args} and kwargs "
           "{kwargs}".format(**details))

def giveup_hdlr(details):
    msg = ("Stop retrying afters {tries} attempts "
           "calling function {target} with args {args} and kwargs "
           "{kwargs} \n".format(**details))
    msg += traceback.format_exc()
    print(msg)
    ses_client.send_error_email(to_email=cfg.ADMIN_EMAIL, msg=msg)

def get_logger(fpath='',
               logger_name='output',
               ch_log_level=logging.ERROR,
               fh_log_level=logging.INFO):
    logging.shutdown()
    imp.reload(logging)
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)

    # Console Handler
    if ch_log_level:
        ch = logging.StreamHandler()
        ch.setLevel(ch_log_level)
        ch.setFormatter(logging.Formatter('%(message)s'))
        logger.addHandler(ch)

    # File Handler
    if fh_log_level:
        fh = logging.FileHandler(os.path.join(fpath,logger_name+'.log'))
        fh.setLevel(fh_log_level)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        fh.setFormatter(formatter)
        logger.addHandler(fh)

    return logger

def get_time_msg(start_time):
    time_elapsed = time.time() - start_time
    msg = 'Time {:.1f}m {:.2f}s'.format(
        time_elapsed // 60, time_elapsed % 60)
    return msg
