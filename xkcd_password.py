#!/usr/bin/env python3
# SPDX-License-Identifier: MIT-0
#
# Reference #1: https://docs.python.org/3/library/secrets.html#secrets.choice
# Reference #2: https://xkcd.com/936/
# Reference #3: https://www.eff.org/deeplinks/2016/07/new-wordlists-random-passphrases

import argparse
import secrets
import sys
import math

DEFAULT_WORDLIST = 'dict/eff_large_wordlist.txt'
DEFAULT_PASSWORD_LEN = 4

##------------------------------------------------------------------------------
def _strict_positive_int(value):
    try:
        ivalue = int(value)
        if ivalue <= 0: raise ValueError
    except ValueError:
        raise argparse.ArgumentTypeError("invalid strict positive int value: '%s'" % value)
    return ivalue

def parse_args():
    parser = argparse.ArgumentParser(description="""
A password generator inspired by XKCD #936 and EFF Diceware wordlist
""")

    parser.add_argument("NUM_WORDS", type=_strict_positive_int, nargs='?',
                        default=DEFAULT_PASSWORD_LEN,
                        help="number of words to generate (default: %s)"
                            % DEFAULT_PASSWORD_LEN)
    parser.add_argument("-f", "--wordlist",
                        default=DEFAULT_WORDLIST,
                        help="Diceware or UNIX wordlist to use (default: %s)" % DEFAULT_WORDLIST)
    parser.add_argument("-b", "--brief", action="store_true",
                        help="do not output password metric")
    return parser.parse_args()

##------------------------------------------------------------------------------
def load(path):
    ## Accept:
    ##  - Diceware format /^[1-6]+\s+\w+$/
    ##  - UNIX words format /^\w+$/
    with open(path) as f:
        words = []
        for line in f:
            tokens = line.strip().split()
            word = tokens[1] if len(tokens) == 2 else tokens[0]
            words.append(word)
    return words

##------------------------------------------------------------------------------
def validate(words):
    from collections import Counter
    wc = Counter(words)
    if len(words) != len(wc):
        duped = []
        for word, count in wc.items():
            if count > 1: duped.append(word)
        sys.stderr.write("ERROR: duped word detected: %s\n" % ', '.join(duped))
        sys.exit(1)

##------------------------------------------------------------------------------
if __name__ == '__main__':
    args = parse_args()
    (wordlist, num_words) = (args.wordlist, args.NUM_WORDS)
    words = load(wordlist)
    validate(words)

    entropy     = math.log(len(words))/math.log(2)
    pw_entropy  = num_words * entropy
    password    = ' '.join(secrets.choice(words) for i in range(num_words))

    if args.brief:
        print(password)
    else:
        print('''
Dictionary  : %s
Dict Len    : %10d (word)
Entropy     : %10.2f (bit/word)
Pw Len      : %10d (word)
            : %10d (char)
Pw Entropy  : %10.2f (bit)
Password    : %s
''' % (wordlist, len(words), entropy, num_words, len(password), pw_entropy, password))
