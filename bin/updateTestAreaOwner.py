#!/bin/env python
#------------------------------------------------------------------------------
#
#   File:       updateTestAreaOwner.py
#   Created:    02-02-2021
#   Creator:    xchavon
#   Location:   Sweden
#   $Revision: 1.7 $
#   $Id: updateTestAreaOwner.py,v 1.7 2023/04/17 08:19:25 xadaton Exp $
#
#------------------------------------------------------------------------------
#
# USAGE:
#   updateTestAreaOwner.py
#
# DESCRIPTION:
#   Update test area onwer on svbt, trunk, nr
#
# EXIT STATUS:
#   0       - Succeeded
#   1       - Error (+ Description)
#   2       - Usage
#------------------------------------------------------------------------------
import billrep as br
import datetime
import os



#------------------------------------------------------------------------------
# Support functions
#------------------------------------------------------------------------------
def getAreaOwner(db) :
    sql = """
    select test_area_name, test_area_owner
    from dev_test.test_area
    --where test_area_owner is not null
    """
    cursor = br.query(db, sql)

    areaOwner = {}
    for row in cursor :
        if row[1] is None :
            print("  <WARN> Test area '%s' is not defined owner" % (row[0]))
        else :
            areaOwner[row[0]] = row[1]
    
    cursor.close()
    
    return areaOwner

def updateAreaOwner(db, areaOwner) :
    sql = """
    update dev_test.test_area
    set test_area_owner = :owner
    where test_area_name = :area
    """
    cursor = db.cursor()

    for areaName, owner in areaOwner.items() :
        cursor.execute(sql, area=areaName, owner=owner)

    cursor.close()
    db.commit()
    return

def now():
    return datetime.datetime.now()


#------------------------------------------------------------------------------
# Main code
#------------------------------------------------------------------------------
if not br.isBranchEnv(os.uname()[1]):
    print("<ERROR> This script is designed to be executed in SVBranch only")
else :
    srcEnv = 'svbranch'
    db = br.getConnection(srcEnv)
    print("%s - Getting test area owner from %s" % (now(), srcEnv.upper()))
    areaOwner = getAreaOwner(db)
    db.close()

    # get datasource list
    ds = br.getDBServers()
    activeServers = br.getActiveServers()


    print(os.uname())

    # update area owner only for active servers
    for s in activeServers :
        if s != srcEnv :
            print("%s - Updating area owner for %s - %s" % (now(), s.upper(), ds[s]))
            db = br.getConnection(s)
            updateAreaOwner(db, areaOwner)
            db.close()










#------------------------------------------------------------------------------
# REVISION HISTORY :
# $Log: updateTestAreaOwner.py,v $
# Revision 1.7  2023/04/17 08:19:25  xadaton
# Changed svbranch11 to svbranch
#
# Revision 1.6  2023/03/16 09:23:08  xchavon
# Fix typo
#
# Revision 1.5  2023/03/16 09:18:39  xchavon
# Allows script to be executed only in SVBranch
#
# Revision 1.4  2022/08/02 14:44:52  xchavon
# Change DB to SVBranch11
#
# Revision 1.3  2022/01/16 04:57:21  xchavon
# Update owner only for active servers
#
# Revision 1.2  2021/10/20 12:22:38  punkalong001
# update shebang to python3
#
# Revision 1.1  2021/02/02 22:49:53  xchavon
# Initial script
#
#------------------------------------------------------------------------------
