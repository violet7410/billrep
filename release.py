#!/bin/env python
import billrep as br


#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'Bill-IT/PCM Release Report'
_desc = 'Report what are tickets included in the specified release'

#-----------------------------------------------------------------------
# Support functions
#-----------------------------------------------------------------------
def getReleaseItems(env, db) :

    projectCode = 'HI3G V8 BRANCH'

    if (environment == "NR") :
        projectCode = 'HI3G V8 TRUNK'

    sql = """
    select release_code, release_code || ' - ' || substr(description, 1, decode(instr(description, ','), 0, length(description), instr(description, ',') - 1)) release_name
    from relgen.rg_project p, relgen.rg_release r
    where p.project_id = r.project_id
    and p.project_code = '%s'
    and r.release_date > SYSDATE - (365*3)
    order by release_id desc
""" % (projectCode)

    cur = db.cursor()
    cur.execute(sql)

    items = {}
    for (releaseCode, description) in cur:
        items[releaseCode] = description

    cur.close()

    return items

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
environment = rep.getParam('environment')
releaseCode = rep.getParam('releaseCode')
developer   = rep.getParam('developer')


# Set default environment
if (not environment) : environment = "BT"

# Get SVTrunk db connection
db = br.getConnection(br.getTrunkAlias())

# Get release code list and environment list
releaseList = getReleaseItems(environment, db)
envList     = { 'BT' : "BT Release", 'NR' : 'NR Release'}

# Report form
form = br.form(action=module_name, method='get')
form.select(name = 'environment', label = 'Environment', items = envList, default = environment)
form.select(name = 'releaseCode', label = 'Release', items = releaseList, default=releaseCode)
form.input(name = 'developer', label = 'Developer', default = developer)
form.input(type="submit", default = 'View Release')
form.render()


# Report
if (releaseCode and releaseList.get(releaseCode)) :

    print("<h1>%s</h1>" % releaseCode)

    if (environment == "BT") :
        tableName   = 'customer_query@svbranch cq, atlanta_operator@svbranch op1, atlanta_operator@svbranch op2'
        columnName  = '"NR Retrofitted"'
    else :
        tableName   = 'customer_query cq, atlanta_operator op1, atlanta_operator op2'
        columnName  = '"BT Dropped"'

    whereClause = ""
    if (developer) :
        whereClause = "and op1.operator_full_name = '%s'" % (developer)

    # Construct SQL
    url = 'ticketdetail.py?ticket_no='
    sql = """
    select rownum "No.", t.*
    from 
    (
        select 
        '[link|'||rgs.ticket_no||'|{url}'||rgs.ticket_no||']' "Ticket No."
        , cq.general_1 "Requirement No."
        , cq.general_2 "Description"
        , op1.operator_full_name "Developer"
        , to_char(rgs.date_last_modified, 'dd-mm-yyyy hh24:mi:ss') "Last Modified"
        , decode(tt.release_id, null, 'No', 'Yes') {column}
        from {table}, rg_ticket_summary rgt, rg_soc rgs, rg_release rgr, rg_project rgp, rg_soc tt, reference_code rc
        where rgr.release_code = '{release}'
        and rgt.ticket_no = cq.general_3(+)
        and rgt.ticket_no = rgs.ticket_no(+)
        and rgs.release_id = rgr.release_id(+)
        and rgs.project_id = rgp.project_id(+)
        and cq.general_6 = op1.atlanta_operator_id(+)
        and cq.general_5 = op2.atlanta_operator_id(+)
        and cq.general_4 = rc.reference_code(+)
        and rc.reference_type_id(+) = 23000515 -- DCUT_PROCESS_STEP " 
        and cq.general_7 = tt.ticket_no(+)
        {whereclause}
        ORDER BY rgs.date_last_modified desc, rgs.ticket_no
    ) t
    """.format(column=columnName, table=tableName, release=releaseCode, url=url, whereclause=whereClause)

    #print(sql)
    cur = br.query(db, sql)
    rep.showCursor(cur)

db.close()
rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: release.py,v $
# Revision 1.9  2024/03/13 09:58:08  xchavon
# Added search by developer
#
# Revision 1.8  2023/03/21 15:57:33  xchavon
# Remove hardcode Branch/Trunk envs
#
# Revision 1.7  2022/07/13 13:47:11  xchavon
# Update link to Trunk v11
#
# Revision 1.6  2022/01/13 21:08:45  xchavon
# Update shebang
#
# Revision 1.5  2021/11/04 12:19:01  punkalong001
# check-in for svbranch
#
# Revision 1.4  2021/02/01 18:29:30  xchavon
# Support macro
#
# Revision 1.3  2021/01/29 18:03:28  xchavon
# Change report name
#
# Revision 1.2  2021/01/29 17:54:48  xchavon
# Update web template
#
# Revision 1.1  2021/01/25 22:08:52  xchavon
# Initial billrep
#
#-----------------------------------------------------------------------

