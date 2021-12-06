import logging
from datetime import datetime

class Logger():
  def __init__(self, logging_for='post'):
    time_now = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
    path = "./connections/LOGS/"

    log_file_name_exc = path + f'exceptions/{logging_for}-{time_now}.log'
    self.logger_except = self.setup_logger('log_exception', log_file_name_exc, '%(lineno)d: %(asctime)s %(message)s', level=logging.ERROR)

    log_file_name_info = path + f'info/{logging_for}-{time_now}.log'
    self.logger_info = self.setup_logger('log_info', log_file_name_info, '%(asctime)s; %(message)s', level=logging.INFO)


  def setup_logger(self, name, log_file, my_format, level=logging.INFO):
    formatter = logging.Formatter(my_format)
    handler = logging.FileHandler(log_file)
    handler.setFormatter(formatter)

    lo = logging.getLogger(name)
    lo.setLevel(level)
    lo.addHandler(handler)

    return lo

  def log_info(self, data, source, code_origin):
    if self.logger_info != None:
      self.logger_info.info(f'{source}; {code_origin}; {data}')

  def log_except(self):
    if self.logger_except != None:
      self.logger_except.exception('')