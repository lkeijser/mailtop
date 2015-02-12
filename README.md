# mailtop

Mailtop is a small script that will parse a (postfix) maillog file and produce a top 10 of:
    
* mail from
* mail to
* delay
* smtp codes
* deferred reasons

# usage

```
$ ./mailtop.py --help
Usage: mailtop.py -f <mail logfile>

Options:
  -h, --help            show this help message and exit
  -f LOGFILE            Logfile name
  -e                    Display an example logfile line with columns separated
  -D, --debug           enable debugging output
  -i, --ignore-id       Ignore Postfix mail ID (mails with the same ID are
                        counted seperately
  -t TOPCOUNT, --top=TOPCOUNT
                        Produce a top TOPCOUNT instead of 10 (default)
  -v, --verbose         Be more verbose
```
