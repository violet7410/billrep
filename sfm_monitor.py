#!/bin/env python
import billrep as br
import datetime
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'Scheduled Function Monitor'
_desc = 'Scheduled function summary report'

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
category    = rep.getParam('category')
subCategory = rep.getParam('subCategory')
funcName    = rep.getParam('funcName')
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
form.input(name = 'category', label = 'Category', default=category)
form.input(name = 'subCategory', label = 'Sub Category', default=subCategory)
form.input(name = 'funcName', label = 'Function Name', default=funcName)
form.input(name = 'whereClause', label = 'Where Clause', default=whereClause)
form.input(type="submit", default = 'View Report')
form.render()


# Report
if (reportDate and environment) :

    print("<h1>Scheduled Functions Summary Report</h1>")
    
    whereCategory    = ""
    whereSubCategory = ""
    whereFuncName    = ""
    whereGeneric     = ""
    if (category) : 
        whereCategory = "and c.abbreviation like '%s'" % category
    
    if (subCategory) : 
        whereSubCategory = "and sc.abbreviation like '%s'" % subCategory
    
    if (funcName) :
        whereFuncName = "and sf.function_name like '%s'" % funcName
    
    if (whereClause) : 
        whereGeneric = "and %s" % whereClause


    # Default URL to detail page
    #url = "sfm_detail_report.py?reportDate={reportDate}&environment={environment}&funcName={funcName}&interfaceNr=1&statusCode=4"
    url = "sfm_detail_report.py?reportDate={reportDate}&environment={environment}".format(reportDate=reportDate, environment=environment)

    sql = """
    select rownum "No", t.*
    from (
        select /*+ index(sf, I_SCHEDULED_FUNCTION_SCHEDULED)*/
        c.abbreviation                                     "Category"
        , sc.abbreviation                                  "Sub Category"
        , decode(sf.interface_nr, 1, sf.function_name, sf.function_name||' ('||sf.interface_nr||')') "Function Name"
        --, sf.function_name                                 "Function Name"
        --, sf.interface_nr                                  "Interface Nr."
        , count(*)                                         "Count"
        , round(sum(elapsed_time))                         "Elapsed Time (Sec)"
        , round(decode(greatest(count(*), 0), count(*), sum(elapsed_time)/count(*), 0),3) "Avg. (Sec)"
        , '[link|' || sum(decode(status_code, 1, 1, 0)) || '|{url}&funcName=' || replace(sf.function_name, '&', '%26') ||'&interfaceNr='|| sf.interface_nr||'&statusCode=1'||']' "Pending"
        , '[link|' || sum(decode(status_code, 2, 1, 0)) || '|{url}&funcName=' || replace(sf.function_name, '&', '%26') ||'&interfaceNr='|| sf.interface_nr||'&statusCode=2'||']' "Running"
        , sum(decode(status_code, 3, 1, 0))                "Success"
        , '[link|' || sum(decode(status_code, 4, 1, 0)) || '|{url}&funcName=' || replace(sf.function_name, '&', '%26') ||'&interfaceNr='|| sf.interface_nr||'&statusCode=4'||']' "Failure"
        , '[link|' || sum(decode(status_code, 5, 1, 0)) || '|{url}&funcName=' || replace(sf.function_name, '&', '%26') ||'&interfaceNr='|| sf.interface_nr||'&statusCode=5'||']' "Attempting"
        
        from scheduled_function sf
        , reference_code c
        , reference_code sc
        where sf.scheduled_start_date between to_date('{reportDate}', 'yyyy-mm-dd hh24:mi:ss') and to_date('{reportDate} 23:59:59', 'yyyy-mm-dd hh24:mi:ss') /* input date */
        and sf.category_code = c.reference_code(+)
        and c.reference_type_id(+) = 716 -- SCHEDULED_FUNC_CATEGORY
        and sf.sub_category_code = sc.reference_code(+)
        and sc.reference_type_id(+) = 717 -- SCHEDULED_FUNC_SUB_CATEGORY
        {whereCategory}
        {whereSubCategory}
        {whereFuncName}
        {whereGeneric}
        group by
        c.abbreviation
        , sc.abbreviation
        , sc.reference_type_id
        , sf.function_name
        , sf.interface_nr
        order by 1, 3
    ) t
    where 1 = 1
    """.format(reportDate=reportDate, 
               whereCategory=whereCategory, 
               whereSubCategory=whereSubCategory, 
               whereFuncName=whereFuncName,
               whereGeneric=whereGeneric,
               url=url)

    # Get SVTrunk db connection
    db = br.getConnection(environment)
    #print(sql)
    cur = br.query(db, sql)

    # Custom decoration
    decoration = {}
    decoration["Pending"]    = {"style" : 'rightAlign'} 
    decoration["Failure"]    = {"style" : 'rightAlign'} 
    decoration["Running"]    = {"style" : 'rightAlign'} 
    decoration["Attempting"] = {"style" : 'rightAlign'} 
    rep.showCursor(cur, decoration)

    # Close cursor and DB connection
    cur.close()
    db.close()
else :
    rep.printError("Report date or Environment not deifned")
    

rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: sfm_monitor.py,v $
# Revision 1.6  2023/04/04 11:45:42  xchavon
# Update report name
#
# Revision 1.5  2023/04/04 11:45:18  xchavon
# Update report name
#
# Revision 1.4  2023/03/27 09:07:06  xchavon
# Added where clause field
#
# Revision 1.3  2023/03/21 15:54:06  xchavon
# Add link on Running column
#
# Revision 1.2  2023/03/08 12:38:12  xchavon
# - Add link to sfm_detail_report.py
#
# Revision 1.1  2023/03/08 08:51:07  xchavon
# Initial sfm_monitor.py
#
#-----------------------------------------------------------------------





