#!/bin/env python
import billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'Comparison Report'
_desc = 'Compare result of regression test from all envrionments'

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
ticket_no = rep.getParam('ticket_no') or ''
where_clause = rep.getParam('where_clause') or ''

# Report form
form = br.form(action=module_name, method='get')
form.input(name = 'ticket_no', label = 'Ticket No', type='number', default = ticket_no)
form.input(name = 'where_clause', label = 'Where clause', default = where_clause)
form.input(type="submit", default = 'Submit')
form.render()


# Report
if (ticket_no) :

    # Get SVTrunk db connection
    db = br.getConnection(br.getTrunkAlias())

    # get projectCode
    cur = db.cursor()
    
    cur.execute("select upper(project_code) project_code from rg_ticket_summary rgt where ticket_no = %s" % ticket_no)
    projectCode = cur.fetchone()[0]

    # Determine table to be use
    if (projectCode is None) :
        raise(Exception('Ticket %s not found' % ticket_no))
    elif (projectCode == 'HI3G V8 TRUNK') :
        tableName = 'customer_query cq, atlanta_operator op1, atlanta_operator op2'
        env = 'NR'
    else :
        tableName = 'customer_query@svbranch cq, atlanta_operator@svbranch op1, atlanta_operator@svbranch op2'
        env = 'BT'

    print("<h1>Ticket Summary : %s</h1>" % ticket_no)

    url1 = 'release.py'
    url2 = 'ticketdetail.py'
    sql = """
    select rgp.project_name
    , decode(rgr.release_code, null, rgr.release_code, '[link|'||rgr.release_code||'|{url1}?releaseCode='||rgr.release_code||'&environment={env}]') release_code
    , rgs.ticket_no
    , cq.general_1 requirement_no
    , cq.general_2 description
    , rc.abbreviation status
    , op1.operator_full_name developer
    , op2.operator_full_name responsible
    , '[link|'||cq.general_7||'|{url2}?ticket_no='||cq.general_7||']' retrofit_id
    from rg_ticket_summary rgt, rg_soc rgs, rg_release rgr, rg_project rgp, reference_code rc, {table}
    where rgt.ticket_no = '{ticket}'
    and rgt.ticket_no = cq.general_3(+)
    and rgt.ticket_no = rgs.ticket_no(+)
    and rgs.release_id = rgr.release_id(+)
    and rgs.project_id = rgp.project_id(+)
    and cq.general_6 = op1.atlanta_operator_id(+)
    and cq.general_5 = op2.atlanta_operator_id(+)
    and cq.general_4 = rc.reference_code(+)
    and rc.reference_type_id = 23000515 -- DCUT_PROCESS_STEP 
    """.format(table=tableName, ticket=ticket_no, url1=url1, url2=url2, env=env)
    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h1>Ticket Details</h1>")

    # Construct SQL
    if (where_clause) :
        where_clause = "and " + where_clause
    else :
        where_clause = "and 1 = 1"

    sql = """
    select rownum no, t.*
    from (
        select ret.entity_class, ret.entity_action
        , rge.ent_property1
        , rge.ent_property2
        , rge.ent_property3
        , rge.ent_property4
        , rge.ent_property5
        from rg_soc rgs, rg_entity rge, rg_entity_type ret
        where rgs.ticket_no = '%s'
        and rgs.soc_id = rge.soc_id
        and rge.entity_type_id = ret.entity_type_id
        %s
        order by 3, 5, 6
    ) t
    """ % (ticket_no, where_clause)

    #print(sql)
    cur = br.query(db, sql)
    rep.showCursor(cur)

    cur.close()
    db.close()
    

rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: ticketdetail.py,v $
# Revision 1.6  2023/06/27 08:53:08  xchavon
# Fix typo
#
# Revision 1.5  2023/03/21 15:57:33  xchavon
# Remove hardcode Branch/Trunk envs
#
# Revision 1.4  2022/07/19 14:12:47  xchavon
# Update to SVTrunk11
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





