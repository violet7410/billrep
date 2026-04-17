#!/bin/env python
import billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'Retrofit Ticket'
_desc = 'Tool generate command for retrofitting'

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
branchTicket = rep.getParam('branchTicket') or ''
trunkTicket  = rep.getParam('trunkTicket') or ''
entityType   = rep.getParam('entityType') or ''

# Report form
form = br.form(action=module_name, method='get')
form.input(type="number", name='branchTicket', label='Ticket No. (Branch)', default=branchTicket, mandatory=True)
form.input(type="number", name='trunkTicket', label='Ticket No. (Trunk)', default=trunkTicket)
form.input(type="text", name='entityType', label='Entity Type', default=entityType)
form.input(type="submit", default='Submit')
form.render()

# Report
if (branchTicket) :
    # Get SVTrunk db connection
    db = br.getConnection(br.getTrunkAlias())

    # Get ticket information

    sql = """
    select r.release_code "Release Code", 
    s.ticket_no "Ticket No", 
    rc2.abbreviation "Status (Branch)",
    s.created_by "Creator", 
    ts.short_problem_summary "Description", 
    q.general_3 "Retrofit Ticket No",
    rc1.abbreviation "Status (Trunk)"
    from rg_project p, rg_release r, rg_soc s, rg_ticket_summary ts, customer_query q
    , customer_query@svbranch bq, reference_code rc1, reference_code rc2
    where s.ticket_no = %s
    and s.ticket_no = ts.ticket_no
    and s.release_id = r.release_id(+)
    and r.project_id = p.project_id(+)
    and p.project_code(+) = 'HI3G V8 BRANCH' -- Make sure ticket is checked-in against Branch project
    and s.ticket_no = q.general_7
    AND s.ticket_no = bq.general_3(+)
    AND q.general_4 = rc1.reference_code(+)
    AND rc1.reference_type_id(+) = 23000515 /* DCUT_PROCESS_STEP */
    AND bq.general_4 = rc2.reference_code(+)
    AND rc2.reference_type_id(+) = 23000515 /* DCUT_PROCESS_STEP */
    """ % (branchTicket)
    
    cur = br.query(db, sql)

    if br.checkDbCursor(cur) :

        # Print ticket Detail
        print("<h2>Ticket Detail</h2>")
        rep.showCursor(cur)

        
        # Set trunkTicket if not specified.
        if not trunkTicket :
            # Reset corsor
            cur.scroll(mode='first')
            row = cur.fetchone()
            trunkTicket = row[5]


        print("<h2>Retrofit Command</h2>")

        # Construct eccs where clause
        entityType = "AND entity_type like '%s'" % entityType if entityType else ''
        
        
        #/* mergetotrunk commands for configuration requiring merging from uat to siu */
        sql = """
        select rownum      "No."
        , b.relgen_ticket  "Ticket No"
        , b.entity_class   "Entity Class"
        , b.entity_type    "Entity Type"
        , b.entity_type_id "Entity Id"
        , b.entity_name    "Entity Name"
        , b.max_revision   "Branch Version"
        , t.max_revision   "Trunk Version"
        , b.command        "Command"
        , '[clipboard|copy|' || b.command ||']' "."
        from (
            /* ticket from branch */
            SELECT 
                CASE WHEN entity_type = 'Installation Script Extension' THEN 1
                    WHEN entity_type = 'Reference Type'           THEN 10
                    WHEN entity_type = 'Attribute Type'           THEN 20
                    WHEN entity_type = 'Entity Validation'        THEN 30
                    WHEN entity_type = 'Configuration Item Type'  THEN 40
                    WHEN entity_type = 'Derived Attribute Definition' THEN 50
                    WHEN entity_type = 'Subtotal'                 THEN 60
                    WHEN entity_type = 'Function'                 THEN 70
                    WHEN entity_type = 'Service Type'             THEN 80
                    WHEN entity_type = 'Derived Attribute Table'  THEN 200
                    WHEN entity_type = 'configuration_items'      THEN 800
                    WHEN entity_type = 'tables'                   THEN 900
                END         as priority 
            , relgen_ticket, entity_class, entity_type, entity_type_id, entity_name, max_revision
            , decode(egroup, 'eccs', command || ' ' || merge_ticket || ' ' || max(new_switch) || ' ' || entity_type_alias || ' ' || entity_type_id || ' ' || max_revision || ' ''' || entity_name || ''''
                            , 'system_method', command || ' ' || merge_ticket || ' ' || entity_type_alias || ' ' || ' ''' || entity_name || '''' || ' ' || '''' || max_revision || ''''
                            , 'install_script', command) command
            FROM (
                SELECT et.entity_class
                    , decode(egroup, 'eccs', re.ent_property1
                                , 'system_method', ent_property1
                                , et.entity_class) entity_type
                    , CASE WHEN egroup = 'eccs'           THEN daa.result1_value
                            WHEN egroup = 'system_method'  THEN 'SystemMethods'
                            WHEN egroup = 'install_script' THEN 'Install Script Extension'
                    END  as entity_type_alias
                    , CASE WHEN egroup = 'eccs'           THEN 'movetotrunk'
                            WHEN egroup = 'system_method'  THEN CONCAT('cd $ATAI_SRC/', CONCAT(re.ENT_PROPERTY1, '; movetotrunk'))
                            ELSE /* add entry manually to relgen. Run this statement in your own schema in DEV1B */
                                'EXECUTE RELGEN.RG.CREATE_ENTITY(' || ( SELECT soc_id FROM RG_SOC where ticket_no = {trunkTicket}  )
                                || ',' || et.ENTITY_TYPE_ID || ','''   || ENT_PROPERTY1 || ''',''' || ENT_PROPERTY2
                                || ''',''' || ENT_PROPERTY3 || ''',''' || ENT_PROPERTY4 || ''',''' || ENT_PROPERTY5
                                || ''',''' || ENT_PROPERTY6 || ''',''' || ENT_PROPERTY7 || ''',''' || ENT_PROPERTY8
                                || ''',''' || ENT_PROPERTY9 || ''',''' || ENT_PROPERTY10 || ''');'
                        END                                                            as command
                    , {trunkTicket}                                                   as merge_ticket   /* the ticket number you want to retrofit your changes to */
                    , DECODE(re.ent_property4,'1.1.2.1', '-n', '')                    as new_switch

                    , decode(egroup, 'eccs', re.ent_property3) entity_type_id
                        
                    , CASE WHEN egroup = 'eccs'           THEN re.ent_property4
                        WHEN egroup = 'system_method'  THEN re.ent_property3
                    END                                                            "Revision"
                    , CASE WHEN egroup = 'eccs'           THEN re.ent_property2
                            WHEN egroup = 'system_method'  THEN re.ent_property2
                        END                                                            as entity_name
                    /*, '; # Relgen Ticket '                                            as EndComment */
                    , ts.TICKET_NO                                                    as relgen_ticket
                    , CASE WHEN egroup not in ('eccs', 'system_method')
                            THEN 'prop1=' || re.ent_property1 || ', ' ||
                                'prop2=' || re.ent_property2 || ', ' ||
                                'prop3=' || re.ent_property3 || ', ' ||
                                'prop4=' || re.ent_property4 || ', ' ||
                                'prop5=' || re.ent_property5
                        END                                                             as Properties
                    , re.entity_id                                                     as EntityId
                    , egroup                                                           as egroup
                    , (CASE WHEN egroup = 'eccs'          THEN (SELECT ent_property4 FROM RG_ENTITY WHERE entity_id = (select max(entity_id) from RG_ENTITY e2 where e2.soc_id = re.soc_id and e2.ent_property1 = re.ent_property1 and e2.ent_property3 = re.ent_property3))
                            WHEN egroup = 'system_method' THEN (SELECT ent_property3 FROM RG_ENTITY WHERE entity_id = (select max(entity_id) from RG_ENTITY e2 where e2.soc_id = re.soc_id and e2.ent_property1 = re.ent_property1 and e2.ent_property2 = re.ent_property2))
                        END )                                                          as max_revision
                        
                FROM RG_RELEASE rel,
                    RG_SOC s,
                    RG_ENTITY re,
                    RG_ENTITY_TYPE et,
                    RG_TICKET_SUMMARY ts,
                    RG_PROJECT p,
                    DERIVED_ATTRIBUTE_ARRAY daa,
                        ( SELECT entity_type_id, entity_class, entity_action
                        , CASE WHEN entity_type_id in (19, 20, 21, 22, 24) then 'eccs'
                                WHEN entity_type_id in (11, 12, 13, 15)     then 'install_script'
                                WHEN entity_type_id in (7, 8)               then 'system_method'
                                WHEN entity_type_id in (1, 2, 3, 4, 5, 6)   then 'db_config'
                                ELSE 'other'
                            END egroup
                        FROM RG_ENTITY_TYPE ) eg
                WHERE et.entity_type_id = re.entity_type_id
                AND s.release_id      = rel.release_id(+)
                AND re.soc_id         = s.soc_id
                AND s.ticket_no       = ts.ticket_no
                AND et.entity_type_id = eg.entity_type_id
                AND p.project_id      = s.project_id
                AND re.ent_property1  = daa.index1_value (+) and daa.derived_attribute_id (+)= 16001822 /* dev_util.ddcut_eccs_entitymapping */
                AND sysdate between daa.effective_start_date (+) and daa.effective_end_date (+)
                AND ts.ticket_no      = {branchTicket}  /* can be comment out to include all the tickets */
            ) WHERE 1 = 1
            {entityType}
            GROUP BY command, merge_ticket, entity_type_alias, entity_type, entity_type_id, max_revision, entity_name, relgen_ticket, properties, egroup, entity_class
            ORDER BY 1, entity_type, entity_name
        )b, (
            /* Retrofitted ticket from trunk */
            select ticket_no, entity_class, entity_type, entity_type_id, entity_name, max_revision
            from (
                select s.ticket_no  
                , et.entity_class
                , decode(et.entity_class, 'ECCS Config', ent_property1
                                        , 'System Method', ent_property1
                                        , entity_class) entity_type
                , decode(et.entity_class, 'ECCS Config', ent_property3) entity_type_id
                , decode(et.entity_class, 'ECCS Config', ent_property2
                                        , 'System Method', ent_property2) entity_name
                , CASE WHEN entity_class = 'ECCS Config'   THEN (SELECT ent_property4 FROM RG_ENTITY WHERE entity_id = (select max(entity_id) from RG_ENTITY e2 where e2.soc_id = e.soc_id and e2.ent_property1 = e.ent_property1 and e2.ent_property3 = e.ent_property3))
                    WHEN entity_class = 'System Method' THEN (SELECT ent_property3 FROM RG_ENTITY WHERE entity_id = (select max(entity_id) from RG_ENTITY e2 where e2.soc_id = e.soc_id and e2.ent_property1 = e.ent_property1 and e2.ent_property2 = e.ent_property2))
                END max_revision
                , ent_property1
                from rg_soc s, rg_entity e, rg_entity_type et
                where s.ticket_no = {trunkTicket} 
                and s.soc_id = e.soc_id
                and e.entity_type_id = et.entity_type_id
            )
            group by ticket_no, entity_class, entity_type, entity_type_id, entity_name, max_revision
            order by 2, 3,4
        ) t
        where b.entity_class = t.entity_class(+)
        and b.entity_type = t.entity_type(+)
        and b.entity_name = t.entity_name(+)
        """.format(branchTicket=branchTicket, trunkTicket=trunkTicket, entityType=entityType)

        # print(sql)
        # print("<br/><br/>")
        # print(entityType)
        
        # Show report
        cur = br.query(db, sql)
        rep.showCursor(cur)

    cur.close()
    db.close()
    

rep.htmlEnd()
#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: retrofit_ticket.py,v $
# Revision 1.8  2023/07/03 09:53:41  xchavon
# Add ticket status
#
# Revision 1.7  2023/04/11 09:44:42  xchavon
# Remove condition on b.entity_type_id
#
# Revision 1.6  2023/03/21 15:57:33  xchavon
# Remove hardcode Branch/Trunk envs
#
# Revision 1.5  2023/01/13 09:42:11  xchavon
# Fix display issue for same function name difference interfaces
#
# Revision 1.4  2022/07/29 11:09:58  xchavon
# Change DB setting to svtrunk11
#
# Revision 1.3  2022/01/13 21:08:45  xchavon
# Update shebang
#
# Revision 1.2  2021/11/04 12:22:28  punkalong001
# make sure the shebang is using python3
#
# Revision 1.1  2021/02/10 09:16:20  xchavon
# Added
#
# Revision 1.1  2021/01/25 22:08:52  xchavon
# Initial billrep
#
#-----------------------------------------------------------------------





