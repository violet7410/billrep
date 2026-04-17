#!/bin/env python

#--------------------------------------------------------------------
# Database server list (Oracle)
#--------------------------------------------------------------------
# Format :
#
#   alias : {oracle settings}
#
# Note!! hostname alias should be sync with apache host alias below
#--------------------------------------------------------------------
dbServers = {
    'svbranch'   : { 'host' : 'dbsv11-1', 'port' : 1521, 'service' : 'SVDB01' , 'desc' : 'SVBranch environment'}
}

#--------------------------------------------------------------------
# Apache server list
#--------------------------------------------------------------------
# Format  :
#
#   alias : hostname[:port]
#
# Note!! hostname alias should be sync with db host alias
#--------------------------------------------------------------------
apacheServers = {
    'svbranch'   : 'sv11-1.home.pve'
}

#--------------------------------------------------------------------
# Active servers
#--------------------------------------------------------------------
# Select hostname to be reported on regression test result page.
#--------------------------------------------------------------------
activeServers = ['svbranch']

#--------------------------------------------------------------------
# Specify hostname that considered as Branch & Trunk env.
#--------------------------------------------------------------------
BranchEnv = ['sv11-1.home.pve', 'x18291dzz.home.pve', 'x18291dzz']
TrunkEnv  = ['sv11-1.home.pve', 'x18291dzz.home.pve', 'x18291dzz']
