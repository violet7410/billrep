#!/bin/env python

import billrep as br
import datetime, re
from multiprocessing.pool import ThreadPool
import math

#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'Nightly Regression Comparison Report'
_desc = 'Compare result of regression test from all envrionments'

#-----------------------------------------------------------------------
# Support functions
#-----------------------------------------------------------------------
def getAreaOwner(db):
    cur = db.cursor()
    cur.execute("select test_area_name, nvl(test_area_owner, 'N/A') test_area_owner from dev_test.test_area")

    areaOwner = {}
    for area, owner in cur :
        areaOwner[area] = owner

    return areaOwner
        

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)
rep.htmlStart()

# Get request parameters
reportDate = rep.getParam('reportDate')
areaOwner  = rep.getParam('areaOwner')
testArea   = rep.getParam('testArea')

# Default report date if not specified (current_date() - 1 days)
if (not reportDate) :
    reportDate = (br.now() - datetime.timedelta(days=1)).strftime("%Y-%m-%d")

# Report form
form = br.form(action=module_name, method='get')
form.input(type='date', name = 'reportDate', label = 'Report Date', default = reportDate)
form.input(name = 'areaOwner', label = 'Area Owner', default=areaOwner)
form.input(name = 'testArea', label = 'Test Area', default=testArea)
form.input(type="submit", default = 'View Report')
form.render()

if (reportDate) :

    areaOwner = "AND ta.test_area_owner like '%s'" % (areaOwner) if areaOwner is not None else ''
    testArea = "AND ta.test_area_name like '%s'" % (testArea) if testArea  is not None else ''

    sql = """
    SELECT 
       trun.test_run_task_id,
       trun.test_run_start_date start_date,
       trun.test_run_end_date end_date,
       ta.test_area_name AS TEST_AREA,
       ta.test_area_owner,
       min(tres.test_result_date) test_area_start_date,
       max(tres.test_result_date) test_area_end_date,
       sum(decode(test_result_status, 'TEST_PASSED', 1, 0)) PASSED,
       sum(decode(test_result_status, 'TEST_FAILED', 1, 0)) FAILED
  FROM dev_test.test_area ta,
       dev_test.test_suite ts,
       dev_test.test_case tc,
       dev_test.test_result tres,
       dev_test.test_run trun
 WHERE trun.test_run_id = (
     SELECT MAX(test_run_id) 
     FROM dev_test.test_run
     WHERE test_run_start_date between to_date('{date} 00:00:00', 'yyyy-mm-dd hh24:mi:ss') and to_date('{date} 23:59:59', 'yyyy-mm-dd hh24:mi:ss')
    )
   AND tres.test_run_id = trun.test_run_id
   AND tc.test_case_id = tres.test_case_id
   AND ts.test_suite_id = tc.test_suite_id
   AND ta.test_area_id = ts.test_area_id
   {owner}
   {area}
GROUP BY trun.test_run_task_id, ta.test_area_name, ta.test_area_owner, trun.test_run_start_date, trun.test_run_end_date
    """.format(date=reportDate, owner=areaOwner, area=testArea)

    #------------------------------------------------------------------
    # Define data source list
    # all datasources are configured in lib/treservers.py
    #------------------------------------------------------------------
    # [Update 13 Jan 2022]
    # No longer need to make host list here. 
    # Active servers are configred in treservers.py
    #------------------------------------------------------------------
    dataSourceList = br.getActiveServers()
    #print(dataSourceList)
    
    # Set thread
    pool = ThreadPool(processes=4)

    # Get DB connections
    connections = {}
    areaOwner = {}
    okDataSource = []

    for ds in dataSourceList:
        try :
            connections[ds] = br.getConnection(ds)
            # Get test area owner from Branch DB
            if (ds == br.getBranchAlias()) :
                areaOwner = getAreaOwner(connections.get(ds))

            # Add OK connection
            okDataSource.append(ds)
        except Exception as e:
            msg = str(e) + " hence, '%s' data source is removed" % (ds)
            rep.printError(msg)

    # Overwrite dataSourceList with okDataSource
    # so that all bad data source were removed.
    dataSourceList = okDataSource

    # Execute sql in thread
    threads = {}
    for ds in dataSourceList:
        threads[ds] = pool.apply_async(br.query, (connections.get(ds), sql, 1))

    # Get result from all threads
    cursors = {}
    for ds in dataSourceList:
        cursors[ds] = threads[ds].get()
        #print("%s - %s : done<br/>" % (datetime.datetime.now(), ds))

    #-----------------------------#
    # All queries are done here!! #
    #-----------------------------#

    # Grouping result by report group/area/datasource
    result = {}
    overall = {}

    # Billing report constant 
    billReportGroupName = "Billing Regression Test Results"
    
    for ds in dataSourceList:
        cur = cursors.get(ds)
        #cur.scroll(mode="first")
        i = 0
        for row in cursors.get(ds):

            if i == 0 :
                # Get Overall performance
                if not ds in overall : overall[ds] = {}
                
                excutedDate = row.get('START_DATE')

                overall[ds]['TEST_RUN_TASK_ID'] = row.get('TEST_RUN_TASK_ID')
                overall[ds]['PASSED']      = 0
                overall[ds]['FAILED']      = 0
                # Initial start/end date (will be update later)
                overall[ds]['START_DATE']  = row.get('START_DATE')#excutedDate + datetime.timedelta(days=5)
                overall[ds]['END_DATE']    = row.get('END_DATE')#excutedDate - datetime.timedelta(days=5)

            testArea = row.get('TEST_AREA')
            
            # Identify report group by area name
            if re.match('^KNOWN_ISSUE.*', testArea) :
                reportGroup = 'Known Issues'
            elif re.match('^PCM.*', testArea) :
                reportGroup = 'PCM Regression Test Results'
            elif re.match('^CUST_MGMT.*', testArea) :
                reportGroup = 'Customer Management Regression Test Results'
            elif (re.match('^DonationServiceAPI', testArea) or
                  re.match('^GL_Billed', testArea) or
                  re.match('^payments', testArea) or
                  re.match('^treatment_collection', testArea)) :
                # Add this separate group for miscellaneous or sundry tests that are not managed by Bill-IT
                reportGroup = 'Miscellaneous / Sundry Regression Test Results'
            else : 
                reportGroup = billReportGroupName
            
            # Initial dict key for the first time
            if not reportGroup in result : result[reportGroup] = {}
            if not testArea in result[reportGroup] : result[reportGroup][testArea] = {}
            
            # Assign value
            result[reportGroup][testArea][ds] = row

            # Get min/max test_result date
            # areaStartDate = row.get('TEST_AREA_START_DATE')
            # areaEndDate   = row.get('TEST_AREA_END_DATE')

            # if areaStartDate < overall[ds]['START_DATE'] : overall[ds]['START_DATE'] = areaStartDate
            # if areaEndDate   > overall[ds]['END_DATE']   : overall[ds]['END_DATE']   = areaEndDate


            # Accumulate overall status
            overall[ds]['PASSED'] += row.get('PASSED')
            overall[ds]['FAILED'] += row.get('FAILED')

            i += 1

    #print(result)
    #print(overall)

    #---------------------------#
    # Show link to Kibana       #
    #---------------------------#
    print('''Regression Statistics: 
        [<a href="http://x18292dzz.test.tre.se:51093/s/billing/app/dashboards#/view/b8c0d8f0-e038-11ed-b3bf-6df1ea00e3ad?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-14d%2Cto%3Anow))" 
            target="kibana_regress">Percent Over Time</a>]
        [<a href="http://x18292dzz.test.tre.se:51093/s/billing/app/dashboards#/view/c5dac750-df5f-11ed-b3bf-6df1ea00e3ad?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-14d%2Cto%3Anow))" 
            target="kibana_regress">Failure Analysis</a>]
        [<a href="http://x18292dzz.test.tre.se:51093/s/billing/app/dashboards#/view/9d61b710-df83-11ed-b3bf-6df1ea00e3ad?_g=(filters%3A!()%2CrefreshInterval%3A(pause%3A!t%2Cvalue%3A0)%2Ctime%3A(from%3Anow-14d%2Cto%3Anow))" 
            target="kibana_regress">Failure by Test Script</a>]
        [<a href="regression_fail_report.py" target="failure_report">Failure Report</a>]
        <br><br>''')

    #---------------------------#
    # Print report result here  #
    #---------------------------#
    for reportGroup, testAreas in sorted(result.items()):
        print("<h1>%s</h1>" % reportGroup)

        colHeader = ['Test Area', 'Owner'] + [ds for ds in dataSourceList] + ['Env Consistency']
    
        # Table header
        print("<table border=1 class=\"regressResult\">")
        print("<tr class='tableHeader1'>")
        for col in colHeader:
            if col in dataSourceList :
                print("\t<th>%s</th>" % (col.upper()))
            else :
                print("\t<th>%s</th>" % (col))
        print("</tr>")

        # Add overall performance
        # Print this header only for reportGroup = 'Billing Regression Test Result'
        if reportGroup == billReportGroupName:
            print("<tr class='tableHeader2'>")
            for col in colHeader :
                if col in dataSourceList :
                    if col in overall:
                        passed = overall.get(col).get('PASSED')
                        failed = overall.get(col).get('FAILED')
                        total  = passed + failed
                        # Calculate overall performance
                        #perf = "%.2f%%" % ((passed/total) * 100) if total > 0  else '0.00%'
                        # always round down so it show 100.00% only when all green
                        perf = "%.2f%%" % (math.floor((passed/total) * 10000)/100.0) if total > 0  else '0.00%'
                        startDate = overall.get(col).get('START_DATE').strftime("%d-%m-%Y %H:%M") if overall.get(col).get('START_DATE') else ''
                        endDate = overall.get(col).get('END_DATE').strftime("%d-%m-%Y %H:%M") if overall.get(col).get('END_DATE') else ''
                        overAllHtml = """\
                            <b>Task Id :</b> {testRunId}<br/>
                            <b>Performance :</b> {performance}<br/>
                            <b>Start Date :</b> {startDate}<br/>
                            <b>End Date :</b> {endDate}<br/>\
                            """.format(testRunId=overall.get(col).get('TEST_RUN_TASK_ID'), startDate=startDate, endDate=endDate, performance=perf)
                        print("\t<th>%s\n\t</th>" % (overAllHtml))
                    else :
                        print("\t<th/>")
                else :
                    print("\t<th/>")
            print("</tr>")

        # Print test area details
        j = 0
        for testArea, result in sorted(testAreas.items()):

            html = "<tr>\n"
            html += "\t<td>%s</td>\n" % testArea
            html += "\t<td>%s</td>\n" % (areaOwner.get(testArea) or 'N/A')
            
            isConsistent = True
            i = 0
            prevTotal = 0
            for ds in dataSourceList:
                row = result.get(ds)
                #print(row)
                total = 0

                # construnc link to next detail pages
                url = "regression_result_by_area.py?environment=%s&reportDate=%s&testArea=%s&errorOnly=1" % (ds, reportDate, testArea)

                if row :
                    # print(row)
                    # print("<br/>")
                    passed    = row.get('PASSED')
                    failed    = row.get('FAILED')
                    total     = passed + failed
                    pct       = (passed/total) * 100
                    areaStart = row.get('TEST_AREA_START_DATE')
                    areaEnd   = row.get('TEST_AREA_END_DATE')

                    if (pct == 100):
                        style = "green"
                    elif (pct > 95) :
                        style = "orange"
                    else :
                        style = "red"
                    
                    hint = ''
                    if failed > 0 : hint += "Failed : %d<br/>" % (failed)
                    hint += "Start : %s<br/>" % areaStart.strftime("%d-%m-%Y %H:%M:%S")
                    hint += "End : %s<br/>" % areaEnd.strftime("%d-%m-%Y %H:%M:%S")
                    hint += "Elapsed : %s" % (areaEnd - areaStart)

                    
                    # Add hint for failed number
                    html += "\t<td class='%s'><div class='tooltip'><a href='%s' target='resultByArea'>%.2f%% of %d</a><span class='tooltiptext'>%s</span></div></td>\n" % (style, url, pct, total, hint)
                else :
                    html += "<td/>\n"


                # Check consistency
                if i > 0  and isConsistent  and total != prevTotal :
                    isConsistent = False
                else :
                    prevTotal = total

                i+=1

            # Add consistency column
            if (isConsistent) :
                isConsistent = 'Consistent'
                style = 'green'
            else :
                isConsistent = 'Inconsistent'
                style = 'red'
            html += "\t<td class='%s'>%s</td>\n" % (style, isConsistent)

            html += "</tr>"
            print(html)
            j += 1
        
        print("</table><br/>")
        # End report group
    
    # close connection.
    for ds in dataSourceList:
        cursors[ds].close()
        connections[ds].close()

    pool.close()

rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: regression_result.py,v $
# Revision 1.21  2024/03/20 09:19:25  xchavon
# Add back env overall info
#
# Revision 1.20  2024/02/14 08:55:00  xdamols
# Move payments tests to miscellaneous group
#
# Revision 1.19  2024/02/05 11:38:53  xdamols
# Add a separate group for miscellaneous or sundry tests that are not managed by Bill-IT
#
# Revision 1.18  2023/06/16 16:06:55  xchavon
# update CSS
#
# Revision 1.17  2023/06/15 14:23:18  xchavon
# Update css
#
# Revision 1.16  2023/04/26 08:28:41  punkalong001
# add link to failure statistics in Kibana and the failure report page
#
# Revision 1.15  2023/04/21 08:35:48  punkalong001
# round down performance to show 100.00% only when all green
#
# Revision 1.14  2023/04/14 08:59:26  xchavon
# Fix typo
#
# Revision 1.13  2023/03/21 15:57:33  xchavon
# Remove hardcode Branch/Trunk envs
#
# Revision 1.12  2023/03/21 14:22:44  xchavon
# Remove hardcode for Branch env
#
# Revision 1.11  2022/01/13 21:08:24  xchavon
# Introduce new seeting activeServers
#
# Revision 1.10  2022/01/11 11:27:38  xadaton
# Add svbranch11
#
# Revision 1.9  2021/10/17 20:42:29  xadaton
# change python to python3
#
# Revision 1.8  2021/10/17 19:40:03  xadaton
# Add SV11 sandbox
#
# Revision 1.7  2021/04/27 13:14:54  xchavon
# Print actual error message when connection failed
#
# Revision 1.5  2021/02/01 18:29:30  xchavon
# Support macro
#
# Revision 1.3  2021/01/29 18:10:41  xchavon
# Update report name
#
# Revision 1.2  2021/01/29 17:54:48  xchavon
# Update web template
#
# Revision 1.1  2021/01/25 22:08:52  xchavon
# Initial billrep
#
#-----------------------------------------------------------------------

