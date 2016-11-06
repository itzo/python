## driveshare-check.py
Check the status of a payout address against the Driveshare API data. Send an email with the current status of the instance(s). Less Secure Apps must be enabled in the user's Google account to be able to send email from this script.
See: [Google Less Secure Apps](https://www.google.com/settings/security/lesssecureapps "Google Less Secure Apps")

Some examples:

Using a password file with no prompts. This is useful for automated processes such as adding a cronjob to run this check and email you occasionally. TODO: alert if instance goes down, otherwise email status report only once a week.
```
$ ./driveshare-check.py your@email.address -a <payout address> -u <gmail user> -p <secret file>
Message sent to '['your@email.address']'.
```
Interactive run with no arguments passed on the command line
```
$ ./driveshare-check.py your@email.address
Gmail username: <gmail user>
Password: <gmail password>
Payout address: <payout address>
Message sent to '['your@email.address']'.
```
Detailed help menu
```
$ ./driveshare-check.py -h
usage: driveshare-check.py [-h] [-u USER] [-p PWFILE] [-a ADDRESS] [-d]
                           recipients [recipients ...]

positional arguments:
  recipients            The recipient email addresses (space delimited).

optional arguments:
  -h, --help            show this help message and exit
  -u USER, --user USER  The sender's Gmail username or email address. The
                        username@gmail.com will be used as the Friendly From
                        header of the email.
  -p PWFILE, --pwfile PWFILE
                        File containing the password for Gmail username
                        (optional). If a file is not provided the user will be
                        asked to enter a password.
  -a ADDRESS, --address ADDRESS
                        The user's SJCX payout address to check the status of.
  -d, --debug           Enable debugging for the SMTP server interaction.
```

### Automated checks

Doing an automated check can be done via a cron job that runs the script with your payout address, user, and email. Here's one way to do it:

1) Clone the repository
```
mkdir -p ~/git && cd ~/git
git clone https://github.com/itzo/python.git driveshare_check
```
2) Add your gmail user's password here and make sure only you can read the file
```
vim $HOME/git/driveshare_check/.x
chmod 600 $HOME/git/driveshare_check/.x
```
3) Finally create the cron entry. The below example will run twice a day - at midnight and noon.
```
RECIPIENTS="your@email.address"
PAYOUT_ADDR="your SJCX payout address"
GMAIL_USER="your gmail username"
MYPWFILE="$HOME/git/driveshare_check/.x"

printf "#Script to check if Storj instances are up and send a report\nMAILTO=''\n0 0,12 * * * $USER $HOME/git/driveshare_check/driveshare-check.py $RECIPIENTS -a $PAYOUT_ADDR -u $GMAIL_USER -p $MYPWFILE >> /tmp/driveshare_check.log 2>&1\n" > ~/git/driveshare_check/cron.tmp
sudo cp ~/git/driveshare_check/cron.tmp /etc/cron.d/driveshare_check
```
If you're not receiving the email check the log file for errors. You should be seeing something like this:
```
cat /tmp/driveshare_check.log
2016-03-20 01:39:02.626560 - message sent to '['your@email.address']'.
```


---
