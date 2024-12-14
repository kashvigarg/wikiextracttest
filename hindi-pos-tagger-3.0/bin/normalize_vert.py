#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
#from remove_extra_vowels import normalise
from normalize_bojar_lrec_2010 import normalise

for line in sys.stdin:
    if line[0]=="<":
        print(line.strip())
        continue
    line= line.strip("\n")
    nword= normalise(line).encode("utf-8")
    print("%s" %(nword))
