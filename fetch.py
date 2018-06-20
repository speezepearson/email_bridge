import argparse
import base64
import email
import glob
import imaplib
import json
import logging
import os
import re

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
parser.add_argument('--imap-hostname', default='imap.gmail.com')
parser.add_argument('--imap-port', type=int, default=993)
parser.add_argument('-v', '--verbose', action='store_true')
parser.add_argument('username')
parser.add_argument('start_uid', type=int, default=1)

def mime2json(msg):
  return {
    'headers': dict(msg.items()),
    'type': msg.get_content_type(),
    'payload': [mime2json(sub) for sub in msg.get_payload()] if msg.is_multipart() else msg.get_payload()
  }

if __name__ == '__main__':
  args = parser.parse_args()
  if args.verbose:
    logging.basicConfig(level=logging.DEBUG)
  if 'IMAP_PASSWORD' not in os.environ:
    raise RuntimeError('IMAP_PASSWORD environment variable is not set')
  password = os.environ['IMAP_PASSWORD']

  logger.debug('creating IMAP client')
  with imaplib.IMAP4_SSL(args.imap_hostname, args.imap_port) as server:
    logger.debug('logging in as %s', args.username)
    server.login(args.username, password)
    logger.debug('selecting inbox')
    server.select('INBOX')

    logger.debug('asking for messages')
    result, data = server.uid('search', None, '(UID {}:*)'.format(args.start_uid))

    uids = [int(word) for word in data[0].split()]
    logger.info('found %d messages', len(uids))
    for uid in uids:
      if uid < args.start_uid:
        continue
      logger.debug('fetching message %d', uid)
      result, data = server.uid('fetch', str(uid), '(RFC822)')  # fetch entire message
      msg = email.message_from_string(data[0][1].decode())

      payload_dict = mime2json(msg)
      payload_dict['uid'] = uid
      print(json.dumps(payload_dict))
