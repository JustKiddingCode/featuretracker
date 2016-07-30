#! /usr/bin/env python3

BASE_DIR = "/opt/featuretracker/"
BASE_DIR = ""

SENDMAIL_COMMAND = "/usr/sbin/sendmail"
SENDMAIL_OPTS = ["-t", "-oi"]

SENDMAIL_COMMAND = "/bin/cat"
SENDMAIL_OPTS = []

SENDMAIL = [SENDMAIL_COMMAND] + SENDMAIL_OPTS

EMAIL_FROM = "Featuretracker <featuretracker@fsmi.uka.de>"
