#!/bin/env python
#--------------------------------------------------------------------------- #
# File: json2epm.py
# Created: 15-Jan-2021
# Creator: xchavon (Chatchai Vongpratoom)
# $Revision: 1.2 $
# $Id: json2epm.py,v 1.2 2022/04/04 19:59:19 xadaton Exp $
# $Source: /svw/svbranch/admin/repository/attool/billrep/bin/json2epm.py,v $
#--------------------------------------------------------------------------- #
# NAME:
# json2epm.py 
#
# UNIT TEST PLAN PURPOSE:
#   Parse json string to EPM evaluation string
#--------------------------------------------------------------------------- #

import json, re, sys
import argparse

moduleName = "json2epm.py"
version = sys.version_info[0]

def usage():
    usageStr = """
    Convert json string to Epm syntax for converting using eval()

    Usage : {moduleName} <json string>

    Example :

      {moduleName} '{{"name" : "testname", "age" : 27 }}'
    """

    print(usageStr.format(moduleName = moduleName))
    return 1


def isStrDate(str) :
    return re.search("^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$", str)


def castEpmType(v):
    s = None
    if (type(v) == int) :
        s = str(v)
    elif (type(v) == float) :
        s = str(v)
    elif (version == 3 and type(v) == str) :
        if (isStrDate(v)) :
            s = "to_date('%s', 'yyyy-mm-dd\"T\"hh:nn:ss')" % v
        else :
            # Add escape \ for special characters
            v = v.replace("\'", "\\'")
            s = "'%s'" % v
    elif (version == 2 and type(v) == unicode) :
        if (isStrDate(v)) :
            s = "to_date('%s', 'yyyy-mm-dd\"T\"hh:nn:ss')" % v
        else :
            # Add escape \ for special characters
            v = v.replace("\'", "\\'")
            s = "'%s'" % v
    return s

def dict2Epm(Dict):
    array = []
    for k, v in Dict.items():
        #print("%s => %s, %s" % (k, v, type(v)))

        if (type(v) == dict) :
            array.append("'%s', %s" % (k, dict2Epm(v)))
        elif (type(v) == list) :
            tmp = []
            for v2 in v :
                if (type(v2) == dict) :
                    tmp.append("%s" % (dict2Epm(v2)))
                elif (type(v2) == list) :
                    raise(Exception("Array of array is not supported"))
                else :
                    tmp.append(castEpmType(v2))
            
            array.append("'%s', [%s]" % (k, ", ".join(tmp)))
        else :
            array.append("'%s', %s" % (k, castEpmType(v)))

    return "hash([" + ", ".join(array) +"])"


def json2Dict(jsonStr):
    try :
        Dict = json.loads(jsonStr)
    except Exception as e :
        raise(Exception("Invalid json format : " + e.message))
    return Dict


#----------------------------------------------------------------------------
#  Main code
#----------------------------------------------------------------------------
# Process arguments
sample = """\
Example :

    {moduleName} '{{"name" : "testname", "age" : 27 }}'
""".format(**{'moduleName' : moduleName})
parser = argparse.ArgumentParser(description='Convert json string to Epm syntax for converting using eval()',
                                 formatter_class=argparse.RawTextHelpFormatter,
                                 epilog=sample)
parser.add_argument('-e', '--epm', action='store_true', help='Print only epm on output')
parser.add_argument('jsonStr')

args = None
if len(sys.argv) == 1 :
    parser.print_help()
    exit(1)
else :
    args = parser.parse_args()

# Convert json epm string
epmStr = dict2Epm(json2Dict(args.jsonStr))

if (args.epm) :
    print(epmStr)
else :
    print("[Json]\n%s\n" % (args.jsonStr))
    print("[Epm]\n%s" % (epmStr))

#----------------------------------------------------------------------------
# REVISION HISTORY
#----------------------------------------------------------------------------
# $Log: json2epm.py,v $
# Revision 1.2  2022/04/04 19:59:19  xadaton
# Change shebang for python
#
# Revision 1.1  2021/11/04 09:22:45  punkalong001
# moved from src/interfaces to be under attool as it is used by test framework only
#
# Revision 1.2.2.1  2021/11/02 09:56:57  xadaton
# Ticket 1058308: BIT-6083 Changed shebang to python3
#
# Revision 1.2  2021/02/10 09:52:01  xchavon
# Ticket 1057481: Moved revision 1.1.2.2 onto trunk.
#
# Revision 1.1.2.2  2021/02/09 17:17:07  xchavon
# Ticket 1057480: BIT-5515 New Restin adapter for EAI/TOM and Apis reponse message
#
#----------------------------------------------------------------------------
