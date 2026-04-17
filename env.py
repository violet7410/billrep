#!/bin/env python
import os, sys, cx_Oracle

print("Content-type: text/html\n")

# Get python location
stream = os.popen('which python')
output = stream.read()

print("python %s<br/>" % (sys.version))
print("%s<br/>" % output)
print("cx_Oracle %s<br/>" % cx_Oracle.version)
for k, v in sorted(os.environ.items()) :
    print("%s = %s<br/>" % (k, v))

