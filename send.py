import argparse
import logging
import os
import smtplib
import sys

if sys.version_info[0]<3:
    # python2:
    from email.MIMEText import MIMEText
else:
    # python3
    from email.mime.text import MIMEText

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--smtp-hostname', default='smtp.gmail.com')
parser.add_argument('--smtp-port', type=int, default=587)
parser.add_argument('--send-as')
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('--subject')
parser.add_argument('username')
parser.add_argument('recipient')

if __name__ == '__main__':
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
  if 'SMTP_PASSWORD' not in os.environ:
    raise RuntimeError('SMTP_PASSWORD environment variable is not set')
  password = os.environ['SMTP_PASSWORD']
  send_as = args.send_as if (args.send_as is not None) else '{}@gmail.com'.format(args.username)
  logger.debug('creating SMTP client')
  with smtplib.SMTP_SSL(args.smtp_hostname) as client:
    logger.debug('logging in as %s', args.username)
    client.login(args.username, password)
    message = MIMEText(sys.stdin.read())
    message['Subject'] = args.subject if (args.subject is not None) else ''
    logger.debug('sending from %s to %s:\n%s', send_as, args.recipient, message.as_string())
    client.sendmail(send_as, args.recipient, message.as_string())
    logger.debug('sent message')
  logger.debug('closed SMTP client')
