#!/usr/bin/env python3
# SPDX-License-Identifier: MIT-0
#
# This password generator is inspired by NES Snake's Revenge (SR) video game.
# The SR was published in 1990 by Ultra Software Corporation.
#
# The original SR password charset (35 symbols):
#
#   !! !  ?  .  '  #  %
#   0  1  2  3  4  5  6  7  8  9
#   B  D  G  H  J  K  L  M  N  P
#   Q  R  T  V  W  X  Y  Z
#
# The modified password charset (32 symbols) to reduce transcription errors:
#
#   ?  .  *  #  %
#   0  1  2  3  4  5  6  7  8  9
#   C  D  F  H  J  K  L  M  N  P
#   Q  R  T  V  W  X  Y
#
# Symbol and lowercase variation (32 symbols) for easier typing:
#
#   .  /  -  +  =
#   0  1  2  3  4  5  6  7  8  9
#   a  b  c  d  e  f  i  m  n  r
#   s  u  v  w  x  y  z
#
# A password of 16 symbols would provides 80 bits entropy,
# and can be easily written as four groups of four characters on a post-it note.
#
#   >>> math.log(32**16)/math.log(2)
#   80.0
#

import argparse
import math
import secrets
import sys
from enum import Enum

DEFAULT_PASSWORD_LEN = 4
CHARS_PER_WORD = 4

# Reference: https://stackoverflow.com/questions/43968006/support-for-enum-arguments-in-argparse
# Reference (base32): https://datatracker.ietf.org/doc/html/rfc4648#page-10
# Reference (base58): https://en.wikipedia.org/wiki/Binary-to-text_encoding#Base58
# Reference (zbase32): https://philzimmermann.com/docs/human-oriented-base-32-encoding.txt
# Rererence (bech32): https://github.com/bitcoin/bips/blob/master/bip-0173.mediawiki#bech32
class Charset(Enum):
    default = "?.*#%0123456789CDFHJKLMNPQRTVWXY"
    symlow  = "./-+=0123456789abcdefgikrsuvwxyz"
    alpha   = "".join(map(chr, range(ord('a'), ord('z')+1)))
    ALPHA   = "".join(map(chr, range(ord('A'), ord('Z')+1)))
    digit   = "".join(map(chr, range(ord('0'), ord('9')+1)))
    alphanum= alpha + digit
    xdigit  = digit + "abcdef"
    Alpha   = ALPHA + alpha
    AlphaNum= Alpha + digit
    base32  = alpha + "234567"
    base58  = AlphaNum.translate(str.maketrans({'O':None, '0':None, 'I':None, 'l':None}))
    zbase32 = alphanum.translate(str.maketrans({'0':None, 'l':None, 'v':None, '2':None}))
    bech32  = alphanum.translate(str.maketrans({'1':None, 'b':None, 'i':None, '0':None}))

    def __str__(self):
        return self.name

    @staticmethod
    def from_string(s):
        try:
            return Charset[s]
        except KeyError:
            raise ValueError()

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
A password generator inspired by NES Snake's Revenge video game
""")
    parser.add_argument("NUM_WORDS", type=_strict_positive_int, nargs='?',
                        default=DEFAULT_PASSWORD_LEN,
                        help="number of words to generate (default: %s)"
                            % DEFAULT_PASSWORD_LEN)
    parser.add_argument("-b", "--brief", action="store_true",
                        help="do not output password metric")
    parser.add_argument("-c", "--charset",
                        type=Charset.from_string, choices=list(Charset),
                        default=Charset.default,
                        help="charset to use")
    return parser.parse_args()

##------------------------------------------------------------------------------
def gen_word(charset):
    return "".join(secrets.choice(charset) for x in range(CHARS_PER_WORD))

##------------------------------------------------------------------------------
if __name__ == '__main__':
    args = parse_args()
    num_words = args.NUM_WORDS
    charset = args.charset.value

    entropy_per_char = math.log(len(charset))/math.log(2)
    entropy_per_word = entropy_per_char * CHARS_PER_WORD

    pw_entropy = entropy_per_word * num_words
    password = " ".join(gen_word(charset) for x in range(num_words))

    if args.brief:
        print(password)
    else:
        print('''
Charset     : %s
            : %10d (char)
Entropy     : %10.2f (bit/char)
            : %10.2f (bit/word)
Pw Len      : %10d (word)
            : %10d (char)
Pw Entropy  : %10.2f (bit)
Password    : %s
''' % (charset, len(charset),
       entropy_per_char, entropy_per_word,
       num_words, len(password),
       pw_entropy,
       password))
