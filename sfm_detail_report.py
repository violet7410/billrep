#!/bin/env python
import billrep as br
import datetime
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'SFM detail report'
_desc = 'Scheduled function detail report'

#-----------------------------------------------------------------------
# Support functions
#-----------------------------------------------------------------------
   

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
reportDate  = rep.getParam('reportDate')
environment = rep.getParam('environment')
funcName    = rep.getParam('funcName')
interfaceNr = rep.getParam('interfaceNr')
statusCode  = rep.getParam('statusCode')
whereClause = rep.getParam('whereClause')



# Default report date if not specified (current_date() - 1 days)
if (not reportDate) :
    reportDate = (br.now() - datetime.timedelta(days=0)).strftime("%Y-%m-%d")

# Default environment is 1st server in activeServers
if (not environment) :
    environment = br.getActiveServers()[0]

# Get env list from getActiveServerList()
envList = br.getActiveServerList()  

# Report form
form = br.form(action=module_name, method='get')
form.input(type='date', name = 'reportDate', label = 'Report Date', default = reportDate)
form.select(name = 'environment', label = 'Environment', items = envList, default = environment)
form.input(name = 'funcName', label = 'Function Name', default=funcName)
form.input(name = 'interfaceNr', label = 'Interface Nr.', default=interfaceNr)
form.input(name = 'statusCode', label = 'Status Code', default=statusCode)
form.input(name = 'whereClause', label = 'Where Clause', default=whereClause)
form.input(type="submit", default = 'View Report')
form.render()


# Report
if (funcName or interfaceNr or statusCode or whereClause) :

    print("<h1>Scheduled Functions Detail Report (%s)</h1>" % funcName)
    
    whereFuncName    = ""
    whereInterfaceNr = ""
    whereStatusCode  = ""
    whereGeneric     = ""
    
    if (funcName) :
        whereFuncName = "and sf.function_name like '%s'" % funcName
    
    if (interfaceNr) :
        whereInterfaceNr = "and sf.interface_nr = %s" % interfaceNr
    
    if (statusCode) :
        whereStatusCode = "and sf.status_code = %s" % statusCode

    if (whereClause) : 
        whereGeneric = "and %s" % whereClause


    sql = """
    select /*+ index(sf, I_SCHEDULED_FUNCTION_SCHEDULED)*/
    rownum no
    , sf.scheduled_function_id            "SF Id"
    , sf.last_modified                    "Last Modified"
    , sf.scheduled_start_date             "Scheduled Start"
    , sf.original_scheduled_start_date    "Ori. Scheduled Start"
    , sf.status_code || ' - ' ||rc2.abbreviation   "Status"
    , sf.retry_count                      "Retry Cnt."
    , sf.original_retry_count             "Ori. Retry Cnt."
    , sf.start_date                       "Start Date"
    , sf.elapsed_time                     "Elapsed (ms)"
    , sf.evaluation_count                 "Eval Cnt."
    , rc.abbreviation                     "Entity Code"
    , sf.entity_id                        "Entity Id"
    , sf.last_error_message_id            "Last Error Id"
    , sf.last_error_message               "Last Error Msg"
    from scheduled_function sf
    , reference_code rc
    , reference_code rc2
    where 1 = 1
    and sf.scheduled_start_date between to_date('{reportDate}', 'yyyy-mm-dd hh24:mi:ss') and to_date('{reportDate} 23:59:59', 'yyyy-mm-dd hh24:mi:ss') /* input date */
    and sf.entity_code = rc.reference_code(+)
    and rc.reference_type_id(+) = 723 /* SCHEDULED_FUNC_ENTITY */
    and sf.status_code = rc2.reference_code(+)
    and rc2.reference_type_id(+) = 718 /* SCHEDULED_FUNCTION_STATUS */

    {whereFuncName}
    {whereInterfaceNr}
    {whereStatusCode}
    {whereGeneric}
    """.format(reportDate=reportDate,
               whereFuncName=whereFuncName,
               whereInterfaceNr=whereInterfaceNr,
               whereStatusCode=whereStatusCode,
               whereGeneric=whereGeneric)

    # Get SVTrunk db connection
    db = br.getConnection(environment)
    #print(sql)
    cur = br.query(db, sql)
    rep.showCursor(cur)

    # Close cursor and DB connection
    cur.close()
    db.close()
else :
    rep.printError("Function Name or Status Code or where clause must be specified")
    

rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: sfm_detail_report.py,v $
# Revision 1.4  2023/04/05 11:18:49  xchavon
# Update report name
#
# Revision 1.3  2023/03/27 09:07:06  xchavon
# Added where clause field
#
# Revision 1.2  2023/03/08 12:56:55  xchavon
# Update report column names
#
# Revision 1.1  2023/03/08 12:37:41  xchavon
# - Add new report
#
# Revision 1.1  2023/03/08 08:51:07  xchavon
# Initial sfm_monitor.py
#
#-----------------------------------------------------------------------





