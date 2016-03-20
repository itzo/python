#!/usr/bin/env python

# author:       itzo <me@itzo.org>
# version:      1.0
# description:  Check the status of a payout address against the Driveshare API data.
#               Send an email with the current status of the instance(s). 
# comments:     Less Secure Apps must be enabled in the sender's Google account.
#               See: https://www.google.com/settings/security/lesssecureapps

import urllib
import json
import smtplib
import argparse
from getpass import getpass

def get_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument('recipients',
        help='The recipient email addresses (space delimited).',
        nargs='+'
    )
    parser.add_argument('-u', '--user',
        help='The sender\'s Gmail username or email address. The username@gmail.com will be used as the Friendly From header of the email.',
    )
    parser.add_argument('-p', '--pwfile',
        help='File containing the password for Gmail username (optional). If a file is not provided the user will be asked to enter a password.',
    )
    parser.add_argument('-a', '--address',
        help='The user\'s SJCX payout address to check the status of.',
    )
    parser.add_argument('-d', '--debug',
        action='store_true',
        help='Enable debugging for the SMTP server interaction.'
    )

    return parser


# parse arguments
def parse_args():
    parser = get_parser()
    args = parser.parse_args()
    # gmail user/pw and payout address are required
    if args.user is None:
        args.user = raw_input('Gmail username: ')
    if args.pwfile is None:
        args.pwfile = getpass()
    else:
        pwfile = open(args.pwfile, 'r')
        args.pwfile = file.read(pwfile)
    if args.address is None:
        args.address = raw_input('Payout address: ')
    return args


# create the actual email message
def create_message(args,body):
    FROM    = args.user
    TO      = ','.join(args.recipients)
    SUBJECT = "Driveshare Status Report"
    TEXT    = body
    msg     = """From: %s\nTo: %s\nSubject: %s\n\n%s""" % (FROM, TO, SUBJECT, TEXT)
    return msg


# create the body of the email to be sent
def create_body(args):
    url = 'http://status.driveshare.org/api/online/json'

    # capture the data into an object
    json_obj = urllib.urlopen(url)
    data = json.load(json_obj)

    # grab our payout address
    count = 0
    body = ""
    for item in data['farmers']:
        if item['payout_addr'] == args.address:
            body += str(item['btc_addr'])+" "+str(item['height'])+" "+str(item['last_seen'])+"sec\n"
            count += 1
    body += "\n"+str(count)+" instances found."
    return body


# send the email
def send_email(args,msg):
    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.set_debuglevel(args.debug)
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(args.user, args.pwfile)
        server.sendmail(args.user, args.recipients, msg)
        print "Message sent to '%s'." % args.recipients
        server.close()
    except smtplib.SMTPAuthenticationError as e:
        print "Unable to send message: %s" % e


# main function
def main():
    args = parse_args()
    body = create_body(args)
    msg = create_message(args,body)
    send_email(args,msg)

if __name__ == "__main__":
    main()
