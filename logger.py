import logging

logger = logging.getLogger('choco')

s_handler = logging.StreamHandler()
f_handler = logging.FileHandler('log.log')

fmt = logging.Formatter('%(asctime)s: %(levelname)s: %(message)s', datefmt='%d-%b-%y %H:%M:%S')
s_handler.setFormatter(fmt)
f_handler.setFormatter(fmt)

logger.addHandler(s_handler)
logger.addHandler(f_handler)