#!/bin/env python
import billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'CM Maintenance Schedules'
_desc = 'Configuration Manager Maintenance Schedules Report'

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
reportDate  = rep.getParam('reportDate')
environment = rep.getParam('environment')

if (not environment) :
    environment = br.getBranchAlias()

# Default report date if not specified (current_date() - 1 days)
if (not reportDate) :
    reportDate = br.now().strftime("%Y-%m-%d")

# Environment List
envList = br.getActiveServerList()

# Report form
form = br.form(action=module_name, method='get')
form.input(type='date', name='reportDate', label='Report Date', default=reportDate)
form.select(name='environment', label='Environment', items=envList, default=environment)
form.input(type="submit", default='View Report')
form.render()


# Report
if (environment) :

    # Get DB connection
    db = br.getConnection(environment)

    # get projectCode
    cur = db.cursor()

    sql = """
    select rownum no
    , t.*
    from (
        select t.schedule_id
        , t.schedule_type_name
        , t.schedule_name
        , t.schedule_status schd_status
        , t.general_1
        , t.last_task_id
        , tq3.scheduled_start_date last_run
        , rc.abbreviation last_status
        , decode(tq3.task_status_code, 3, null, (select to_char(max(scheduled_start_date), 'yyyy-mm-dd hh24:mi:ss') from task_queue tq where tq.task_queue_id < t.last_task_id and tq.schedule_id = t.schedule_id and tq.task_status_code = 3)) last_success
        , t.next_task_id
        , tq4.scheduled_start_date next_run
        from (
            select 
            s.schedule_id
            , st.schedule_type_name
            , s.schedule_name
            , rc.abbreviation schedule_status
            , s.general_1 
            , max(tq1.task_queue_id) last_task_id
            , min(tq2.task_queue_id) next_task_id
            , s.description
            from schedule_type st, schedule s, task_queue tq1, task_queue tq2, reference_code rc
            where 1 = 1 
            and s.schedule_name like 'CM%'
            and st.schedule_type_id = s.schedule_type_id
            and s.schedule_id = tq1.schedule_id(+)
            and tq1.scheduled_start_date(+) <= to_date('{date}', 'yyyy-mm-dd')
            and s.schedule_id = tq2.schedule_id(+)
            and tq2.scheduled_start_date(+) > to_date('{date}', 'yyyy-mm-dd')
            and s.schedule_status_code = rc.reference_code
            and rc.reference_type_id = (select reference_type_id from reference_type where type_label = 'SCHEDULE_STATUS')
            group by st.schedule_type_name
            , s.schedule_id
            , s.schedule_name
            , s.description
            , s.general_1
            , rc.abbreviation
        ) t, task_queue tq3, task_queue tq4, reference_code rc
        where t.last_task_id = tq3.task_queue_id(+)
        and t.next_task_id = tq4.task_queue_id(+)
        and tq3.task_status_code = rc.reference_code
        and rc.reference_type_id(+) = 585 /* TASK_STATUS */
        order by t.schedule_type_name, t.general_1
    ) t 
    """.format(date=reportDate)
    cur = br.query(db, sql)
    rep.showCursor(cur)
    cur.close()
    db.close()

rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: cmschedule.py,v $
# Revision 1.2  2023/08/25 14:15:08  xchavon
# envList from br.getActiveServerList()
#
# Revision 1.1  2023/08/21 12:43:01  xchavon
# Initial report
#
#-----------------------------------------------------------------------
