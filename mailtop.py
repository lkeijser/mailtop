#!/usr/bin/env python
"""

    Small script that will parse a (postfix) maillog file
    and produce a top10 of:
    - mail from
    - mail to
    - delay
    - smtp codes
    - deferred reasons

    L.S. Keijser <keijser@stone-it.com>

"""
import operator
from optparse import OptionParser
import os
import re
import sys


# see if we can import prettytable
try:
    from prettytable import PrettyTable
    pretty_tables = True
except:
    # alas ..
    print "Pssh, if you'd install python-prettytable, the output would look alot nicer!"
    pretty_tables = False

# populate parser
parser = OptionParser(usage="%prog -f <mail logfile>")
parser.add_option("-f",
        action="store",
        type="string",
        dest="logfile",
        help="Logfile name")
parser.add_option("-e",
        action="store_true",
        dest="example",
        help="Display an example logfile line with columns separated")
parser.add_option("-D", "--debug",
        action="count",
        dest="debug",
        help="enable debugging output")
parser.add_option("-i", "--ignore-id",
        action="store_true",
        dest="ignoreid",
        help="Ignore Postfix mail ID (mails with the same ID are \
        counted seperately")
parser.add_option("-t", "--top",
        action="store",
        type="string",
        dest="topcount",
        help="Produce a top TOPCOUNT instead of 10 (default)")
parser.add_option("-v", "--verbose",
        action="store_true",
        dest="verbose",
        help="Be more verbose")

# parse cmd line options
(options, args) = parser.parse_args()


# our logfile from optionparser
logfile = options.logfile
debug = options.debug
ignoreid = options.ignoreid
topcount = options.topcount
showexample = options.example
verbose = options.verbose

# all SMTP reply codes
smtp_reply_codes = {'200': '(nonstandard success response, see rfc876)', '211': 'System status, or system help reply', '214': 'Help message', '220': '<domain> Service ready', '221': '<domain> Service closing transmission channel', '250': 'Requested mail action okay, completed', '251': 'User not local; will forward to <forward-path>', '252': 'Cannot VRFY user, but will accept message and attempt delivery', '354': 'Start mail input; end with <CRLF>.<CRLF>', '421': '<domain> Service not available, closing transmission channel', '450': 'Requested mail action not taken: mailbox unavailable', '451': 'Requested action aborted: local error in processing', '452': 'Requested action not taken: insufficient system storage', '500': 'Syntax error, command unrecognised', '501': 'Syntax error in parameters or arguments', '502': 'Command not implemented', '503': 'Bad sequence of commands', '504': 'Command parameter not implemented', '521': '<domain> does not accept mail (see rfc1846)', '530': 'Access denied (???a Sendmailism)', '550': 'Requested action not taken: mailbox unavailable', '551': 'User not local; please try <forward-path>', '552': 'Requested mail action aborted: exceeded storage allocation', '553': 'Requested action not taken: mailbox name not allowed', '554': 'Transaction failed'}


if debug:
    print "Debug mode enabled."

def run():
    """ check for all args """
    if options.logfile is None:
        parser.print_help()
        sys.exit()

    # check if file exists
    if os.path.exists(logfile):
        print "Parsing logfile %s" % logfile
        main()
    else:
        print "Error: file %s doesn't exist!" % logfile
        sys.exit()


def readFile(filename):
    """ read a file into the buffer and return it """
    f = open(filename, 'r')
    lines = f.readlines()
    f.close()
    return lines

def main():
    """ main function """

    # read logfile
    lines = readFile(logfile)
    total_lines = len(lines)

    if showexample:
        print "Displaying the first maillog line:"
        example_line = lines[0].split(' ')
        el = 0
        print "\ncol:\tvalue:\n"
        for part in example_line:
            print "%s:\t%s" % (el, part)
            el += 1
        sys.exit()

    print "Analyzing %s lines:" % total_lines

    # initialize lists (actually they're dictionaries)
    list_mailfrom = {}
    list_mailto = {}
    list_mailcode = {}
    list_mailsize = {}
    list_maildelay = {}
    list_maildefer = {}

    # progress bar counter (up 1, each iteration)
    p = 0
    # parse logfile
    for line in lines:
        # display funky progressbar
        point = total_lines / 100
        inc = total_lines / 20
        try:
            if p % point == 0:
                outputbar = "\r[" + "=" * (p / inc) +  \
                        " " * ((total_lines - p)/ inc) + "] "
                # ugly fix for missing whitespace
                if len(outputbar) == 23:
                    outputbar = "\r[" + "=" * (p / inc) +  \
                            " " * ((total_lines - p)/ inc) + " ] "
                outputperc = str(p / point) + "%"
                sys.stdout.write(outputbar + outputperc)
                sys.stdout.flush()
        except ZeroDivisionError as e:
            if debug:
                print "Sorry, logfile probably too small for progressbar"
                print "Error: %s" % e
        if debug:
            print "DEBUG: line: %s" % line
        # try to grab mail_from
        try:
            m = re.search(r'from=\<(.*)\>,', line).group(1)
            if m != "":
                mailfrom = m
            else:
                mailfrom = 'UNKNOWN'
            if mailfrom in list_mailfrom:
                list_mailfrom[mailfrom] = int(list_mailfrom[mailfrom]) + 1
            else:
                list_mailfrom[mailfrom] = 1
            if verbose:
                print "[TEST] found from_addr: %s" % mailfrom
        except:
            pass
        # try to grab mail_to
        try:
            m = re.search(r'to=\<(.*)\>,', line).group(1)
            if m != "":
                mailto = m
            else:
                mailto = 'UNKNOWN'
            if mailto in list_mailto:
                list_mailto[mailto] = int(list_mailto[mailto]) + 1
            else:
                list_mailto[mailto] = 1
            if verbose:
                print "[TEST] found to_addr: %s" % mailto
        except:
            pass
        # try to grab mail_size
        try:
            m = re.search(r'size=(\d+),', line).group(1)
            if m != "":
                mailsize = m
            list_mailsize[mailfrom] = int(mailsize)
            if verbose:
                print "[TEST] found mail_size: %s" % mailsize
        except:
            pass
        # try to grab mail_delay
        try:
            m = re.search(r'delay=(\d+),', line).group(1)
            if m != "":
                maildelay = m
            if maildelay in list_maildelay:
                list_maildelay[maildelay] = int(list_maildelay[maildelay]) + 1
            else:
                list_maildelay[maildelay] = 1
            if verbose:
                print "[TEST] found mail_delay: %s" % maildelay
        except:
            pass
        # try to grab mail_code (errors only)
        try:
            m = re.search(r'said: (\d+) ', line).group(1)
            if m != "":
                mailcode = m
            if mailcode in list_mailcode:
                list_mailcode[mailcode] = int(list_mailcode[mailcode]) + 1
            else:
                list_mailcode[mailcode] = 1
            if verbose:
                print "[TEST] found mail_code: %s" % mailcode
        except:
            pass
        # try to grab deferred mails
        try:
            m = re.search(r'status=deferred (.*)', line).group(1)
            if m != "":
                maildefer = m
            if maildefer in list_maildefer:
                list_maildefer[maildefer] = int(list_maildefer[maildefer]) + 1
            else:
                list_maildefer[maildefer] = 1
            if verbose:
                print "[TEST] found mail deferred: %s" % maildefer
        except:
            pass

        # up progressbar counter by 1
        p += 1



    # empty line, for greater power!
    print "\n"

    # produce grand total stats
    print "Total unique mail_from:\t%s" % len(list_mailfrom)
    print "Total unique mail_to:\t%s" % len(list_mailto)
    print "Total unique errors:\t%s" % len(list_mailcode)

    if not topcount:
        sorted_mailfrom = sorted(list_mailfrom.iteritems(),
                key=operator.itemgetter(1), reverse=True)[:10]
        sorted_mailto = sorted(list_mailto.iteritems(),
                key=operator.itemgetter(1), reverse=True)[:10]
        sorted_mailcode = sorted(list_mailcode.iteritems(),
                key=operator.itemgetter(1), reverse=True)[:10]
        sorted_mailsize = sorted(list_mailsize.items(),
                key=operator.itemgetter(1), reverse=True)[:10]
        sorted_maildefer = sorted(list_maildefer.items(),
                key=operator.itemgetter(1), reverse=True)[:10]
    else:
        tc = int(topcount)
        sorted_mailfrom = sorted(list_mailfrom.iteritems(),
                key=operator.itemgetter(1), reverse=True)[:tc]
        sorted_mailto = sorted(list_mailto.iteritems(),
                key=operator.itemgetter(1), reverse=True)[:tc]
        sorted_mailcode = sorted(list_mailcode.iteritems(),
                key=operator.itemgetter(1), reverse=True)[:tc]
        sorted_maildefer = sorted(list_maildefer.iteritems(),
                key=operator.itemgetter(1), reverse=True)[:tc]

    # produce grand total top X for mailfrom
    if not topcount:
        print "\nTOP 10 Mail From"
    else:
        print "\nTOP %s Mail From" % topcount
    if pretty_tables:
        table = PrettyTable(["Count", "Address"])
        table.align["Address"] = "l"
        table.padding_width = 1
    else:
        print "\nCount\tAddress\n"
    for k, v in sorted_mailfrom:
        if pretty_tables:
            table.add_row([v, k])
        else:
            print "%s\t%s" % (v, k)
    if pretty_tables:
        print table

    # produce grand total top X for mailto
    if not topcount:
        print "\nTOP 10 Mail To"
    else:
        print "\nTOP %s Mail To" % topcount
    if pretty_tables:
        table = PrettyTable(["Count", "Address"])
        table.align["Address"] = "l"
        table.padding_width = 1
    else:
        print "\nCount\tAddress\n"
    for k, v in sorted_mailto:
        if pretty_tables:
            table.add_row([v, k])
        else:
            print "%s\t%s" % (v, k)
    if pretty_tables:
        print table

    # produce grand total top X for mailcode
    if not topcount:
        print "\nTOP 10 SMTP error codes"
    else:
        print "\nTOP %s SMTP error codes" % topcount
    if pretty_tables:
        table = PrettyTable(["Count", "Code"])
        table.align["Code"] = "l"
        table.padding_width = 1
    else:
        print "\nCount\tCode\n"
    for k, v in sorted_mailcode:
        if pretty_tables:
            table.add_row([v, k + " (" + smtp_reply_codes[k] + ")"])
        else:
            print "%s\t%s (%s)" % (v, k, smtp_reply_codes[k])
    if pretty_tables:
        print table

    # produce grand total top X for mailsize
    if not topcount:
        print "\nTOP 10 Biggest mails"
    else:
        print "\nTOP %s SMTP error codes" % topcount
    if pretty_tables:
        table = PrettyTable(["Size", "Mail From"])
        table.align["Mail From"] = "l"
        table.padding_width = 1
    else:
        print "\nSize\t\tMail From\n"
    for k, v in sorted_mailsize:
        if pretty_tables:
            table.add_row([v, k])
        else:
            print "%s\t%s" % (v, k)
    if pretty_tables:
        print table

    # produce grand total top X for maildefer
    if not topcount:
        print "\nTOP 10 Mail deferred"
    else:
        print "\nTOP %s Mail deferred" % topcount
    if pretty_tables:
        table = PrettyTable(["Count", "Reason"])
        table.align["Reason"] = "l"
        table.padding_width = 1
    else:
        print "\nCount\tCode\n"
    for k, v in sorted_maildefer:
        if pretty_tables:
            table.add_row([v, k[1:-1]])
        else:
            print "%s\t%s" % (v, k[1:-1])
    if pretty_tables:
        print table


if __name__ == '__main__':
    run()
