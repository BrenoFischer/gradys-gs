import logging
from datetime import datetime

class Logger():
  def __init__(self, logging_for='uav_simulator'):
    time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = "./LOGS_sim/"

    log_file = path + f'{logging_for}-{time_now}.log'
    self.logger_except = self.setup_logger('log_exception', log_file, '%(lineno)d: %(asctime)s %(message)s', level=logging.ERROR)
    self.logger_info = self.setup_logger('log_info', log_file, '%(asctime)s: %(message)s', level=logging.INFO)


  def setup_logger(self, name, log_file, my_format, level=logging.INFO):
    formatter = logging.Formatter(my_format)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    lo = logging.getLogger(name)
    lo.setLevel(level)
    lo.addHandler(handler)

    return lo

  def log_info(self, source=None, data=''):
    if self.logger_info != None:
      if source != None:
        self.logger_info.info(f'{source}: {data};')
      else:
        self.logger_info.info(f'{data}')

  def log_except(self):
    if self.logger_except != None:
      self.logger_except.exception('')
