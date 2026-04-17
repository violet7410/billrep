#!/bin/env python

import billrep as br
import datetime

#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'Nightly Regression Test Result By Area'
_desc = 'Regression test result by test area'

#-----------------------------------------------------------------------
# Support functions
#-----------------------------------------------------------------------
def genReRunCommand(taskId, testStartDate, areaName, cursor) :
  cmd = None

  if (cursor.rowcount > 0) :
    cursor.scroll(mode='first')
    # Set row format to dictionary
    cursor.rowfactory = lambda *args: dict(zip([d[0] for d in cur.description], args))

    scripts = []
    for row in cursor :
      if row['Failed'] > 0 :
        scripts.append(row['Test Script'].split("|")[1])

    
    if len(scripts) > 0 :
      cmd = "run_regress %s '%s' -test_area %s:%s" % (taskId, testStartDate.strftime('%d-%m-%Y %H:%M:%S'), areaName, ','.join(scripts))
    
  return cmd

def genCompareLink(activeServers, apacheServers) :
    compareLinks = []
    linkStr = "'[link|{alias}|http://{host}/attool/'||ta.test_area_parent||'/'||substr(ts.test_suite_name, 1, instr(ts.test_suite_name,'.', -1) -1)||'_results_'||to_char(tr.test_run_start_date, 'yyyymmdd') || '.html]'"
    for alias in activeServers :
        compareLinks.append(linkStr.format(alias=alias.upper(), host=apacheServers.get(alias)))
    return  " ||', '|| \n".join(compareLinks)

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)
rep.htmlStart()

# Get request parameters
reportDate  = rep.getParam('reportDate')
environment = rep.getParam('environment')
testArea    = rep.getParam('testArea')
errorOnly   = rep.getParam('errorOnly')

# Default report date if not specified (current_date() - 1 days)
if (not reportDate) :
    reportDate = (br.now() - datetime.timedelta(days=1)).strftime("%d-%m-%Y")

# Environment List
envList = br.getActiveServerList() 

# Apache server list
apacheHosts = br.getApacheServers()

# Report form
form = br.form(action=module_name, method='get')
form.input(type='date', name='reportDate', label='Report Date', default=reportDate)
form.select(name='environment', label='Environment', items=envList, default=environment)
form.input(name='testArea', label='Test Area', default=testArea)
form.select(name='errorOnly', label='Error Only', items={'1' : 'Yes', '0' : 'No'}, default=errorOnly)
form.input(type="submit", default='View Report')
form.render()

if reportDate and environment :

    # Get DB connection
    db = br.getConnection(environment)

    # Get test run info
    taskId = None
    testStartDate = None
    cur = br.query(db, "select test_run_task_id, test_run_start_date from test_run where test_run_start_date between to_date('{date} 00:00:00', 'yyyy-mm-dd hh24:mi:ss') and to_date('{date} 23:59:59', 'yyyy-mm-dd hh24:mi:ss')".format(date=reportDate))
    if cur :
      row = cur.fetchone()
      if row != None :
        (taskId, testStartDate) = row

    
    # Get active server list
    activeServers = br.getActiveServers()
    #print(activeServers)

    # Generate compare link
    compareLinkStr = genCompareLink(activeServers, apacheHosts)

    # Query report
    testAreaWherClause  = "and ta.test_area_name like '%s'" % (testArea) if testArea is not None else ''

    #""" +  "||', '||".join(compareLinks) """ as "Comparison" """ + """
    
    sql = """
    select rownum as "No", t.*
    from (
      select 
        ta.test_area_name as "Test Area"
      , '[link|' || ts.test_suite_name || '|http://{host}/attool/'|| ta.test_area_parent||'/'||substr(ts.test_suite_name, 1, instr(ts.test_suite_name,'.', -1) -1) || '_results_' || to_char(tr.test_run_start_date, 'yyyymmdd') || '.html]' as "Test Script"
      , '[link|script|http://{host}/attool/'|| ta.test_area_parent||'/'||ts.test_suite_name||']'||', '||
        '[link|regress|http://{host}/attool/'|| ta.test_area_parent||'/'||substr(ts.test_suite_name, 1, instr(ts.test_suite_name,'.', -1) -1) || '.regress]' ||', '||
        '[link|error|http://{host}/attool/'|| ta.test_area_parent||'/'||substr(ts.test_suite_name, 1, instr(ts.test_suite_name,'.', -1) -1) || '.error]' as "Output Files"
      , {compareLink} as "Comparison"
      , sum(decode(trs.test_result_status, 'TEST_PASSED', 1, 0)) as "Passed"
      , sum(decode(trs.test_result_status, 'TEST_PASSED', 0, 1)) as "Failed"
      , to_char(min(trs.test_result_date), 'hh24:mi:ss') as "Start Date"
      , round((max(trs.test_result_date) - min(trs.test_result_date)) * (24*60*60)) as "Elapsed Second"
      , '[clipboard|copy|run_regress ' || tr.test_run_task_id || ' "' || to_char(tr.test_run_start_date, 'dd-mm-yyyy hh24:mi:ss') || '" -skip_sysprep -test_area ' || ta.test_area_name||':'||ts.test_suite_name || ']'  as "."
      from dev_test.test_run tr
      , dev_test.test_result trs
      , dev_test.test_case tc
      , dev_test.test_suite ts
      , dev_test.test_area ta
      where tr.test_run_id = (
          select max(test_run_id)
          from dev_test.test_run
          where test_run_start_date between to_date('{date} 00:00:00', 'yyyy-mm-dd hh24:mi:ss') and to_date('{date} 23:59:59', 'yyyy-mm-dd hh24:mi:ss')
      )
      and tr.test_run_id = trs.test_run_id
      and trs.test_case_id = tc.test_case_id
      and tc.test_suite_id = ts.test_suite_id
      and ts.test_area_id = ta.test_area_id
      {area}
      group by tr.test_run_id
      , trunc(test_run_start_date)
      , tr.test_run_task_id
      , ta.test_area_name
      , ts.test_suite_name
      , tr.test_run_start_date
      , ta.test_area_parent
      having sum(decode(trs.test_result_status, 'TEST_PASSED', 0, 1)) >= {errorOnly}
      order by 2, 3
    ) t
    """.format(date=reportDate, area=testAreaWherClause, host=apacheHosts.get(environment), errorOnly=errorOnly, compareLink=compareLinkStr)
    #print(sql)

    cur = br.query(db, sql)
    rep.showCursor(cur)

    # print re-run command for this area if applicable.
    if testArea :
      sql = "select dev_test.dev_util.RerunCommand(to_date(nvl('{reportDate}', to_char(sysdate, 'yyyy-mm-dd')), 'yyyy-mm-dd'), '{testArea}') from dual".format(reportDate=reportDate, testArea=testArea)
      cur = br.query(db, sql)
      row = cur.fetchone()

      if row[0] :

        print("<br/>")
        print(br.printValue("[clipboard|Copy re-run command for error scripts in this area|%s]" % (row[0])))
        print("<br/><br/>")

    cur.close()
    db.close()
   
rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: regression_result_by_area.py,v $
# Revision 1.12  2023/08/25 14:14:27  xchavon
# EnvList from br.getActiveServerList()
#
# Revision 1.11  2022/01/16 05:30:33  xchavon
# Add -skip_sysprep for re-run command
#
# Revision 1.9  2022/01/13 08:21:17  xchavon
# Fix shebang
#
# Revision 1.8  2022/01/11 11:44:14  xadaton
# Add SV11 branch
#
# Revision 1.7  2021/10/17 20:42:53  xadaton
# change python to python3
#
# Revision 1.6  2021/10/17 19:40:56  xadaton
# Add SV11 sandbox
#
# Revision 1.5  2021/04/20 09:04:15  xchavon
# Fix error when no result for the specified area
#
# Revision 1.4  2021/02/02 22:50:25  xchavon
# Add macro clipboard
#
# Revision 1.3  2021/02/01 18:29:30  xchavon
# Support macro
#
# Revision 1.2  2021/01/29 17:54:48  xchavon
# Update web template
#
# Revision 1.1  2021/01/25 22:08:52  xchavon
# Initial billrep
#
#-----------------------------------------------------------------------
