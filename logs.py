import logging


def setup_log():
  log = logging.getLogger('mon')
  log.setLevel(logging.DEBUG)

  sh = logging.StreamHandler()
  sh.setLevel(logging.DEBUG)
  sh.setFormatter(logging.Formatter(
      '%(asctime)s %(name)s %(levelname)s %(message)s'
      ))
  log.addHandler(sh)

  fh = logging.FileHandler('dendnet.log')
  fh.setLevel(logging.INFO)
  fh.setFormatter(logging.Formatter('%(asctime)s %(message)s'))
  log.addHandler(fh)

  return log

