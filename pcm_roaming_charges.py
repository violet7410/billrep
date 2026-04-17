#!/bin/env python
import billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Roaming Pricing'
_desc = 'Report of roaming charges'

#-----------------------------------------------------------------------
# Support functions
#-----------------------------------------------------------------------

def getCountryItems(db) :

    sql = """
    select rc1.abbreviation as "Country", rc1.description as "Country English"
    from reference_code rc1
    where rc1.reference_type_id = 4100044 
    and rc1.abbreviation not like '%Special%' 
    and rc1.abbreviation not like '%RLH%'
    order by 2
    """  

    cur = db.cursor()
    cur.execute(sql)

    items = {}
    for (roam_country, description) in cur:
        items[roam_country] = description

    cur.close()

    return items

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

db = br.getConnection(br.getBranchAlias())

# Get request parameters

roam_country = rep.getParam('roam_country') 
marketList  = { 'SE' : "Swedish Roaming Charges", 'DK' : 'Danish Roaming Charges'}

roam_country = rep.getParam('roam_country') or ''
market = rep.getParam('market') or ''

# Get release code list and environment list
countryList = getCountryItems(db)

# Report form
form = br.form(action=module_name, method='get')
form.select(name = 'market', label = 'Swedish or Danish Charges', items = marketList, default = market)
form.select(name = 'roam_country', label = 'Roaming Country Name (English)', items = countryList, default=roam_country)
form.input(type="submit", default = 'Submit')
form.render()


# Report

if (market == "SE"  and countryList.get(roam_country)) :

    print("<h1> Swedish Roaming Pricing </h1>")

    print("<h3> Roaming Data </h3>")

    sql = """
    select unique daa3.index2_value as "Product ID" , 
     ph.product_name as "Product Name", 
     daa3.result4_value as "Price Per MB", 
     daa3.result5_value as "Debiting Interval",
     --rc.abbreviation as "Event Subtype",
     rc1.abbreviation as " From Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc, reference_code rc1
     where daa1.derived_attribute_id = 4200183 --dH3G_NE_NetworkPrefix
     and daa2.derived_attribute_id = 17010361 -- dHi3G_NE_PS_RoamingEventRules
     and daa3.derived_attribute_id = 13000212 -- dHi3G_RAT_Data_OB_Roaming_Chg
     and rc.reference_type_id = 4100057 -- event subtype 
     and rc1.reference_type_id = 4100044 -- country
     and daa1.result6_value = daa2.index2_value
     and (daa1.result2_value = daa2.index3_value or daa2.index3_value = '-1') 
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and (daa2.index3_value = rc1.reference_code or daa2.index3_value = '-1') 
     and daa3.index2_value = ph.product_id(+)
     and daa2.index1_value = '-1'
     and daa3.index4_value = rc.reference_code
     and daa1.result2_value = rc1.reference_code
     and (daa3.index7_value = daa1.index1_value or daa3.index7_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     --and daa1.index1_value like '23' -- mcc mnc 
     and rc1.abbreviation like '%s%%'
     order by 3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h3> Roaming MMS </h3>")
    
    sql = """
    select unique daa3.index2_value as "Product ID", 
     ph.product_name as "Product Name", 
     daa3.result1_value as "Price Per Message", 
     daa3.result4_value as "Price Per MB", 
     daa3.result5_value as "Debiting Interval",
     --rc.abbreviation as "Event Subtype",
     rc1.abbreviation as "From Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc, reference_code rc1
     where daa1.derived_attribute_id = 4200183 --dH3G_NE_NetworkPrefix
     and daa2.derived_attribute_id = 17010361 -- dHi3G_NE_PS_RoamingEventRules
     and daa3.derived_attribute_id = 13000213  -- dHi3G_RAT_Message_OB_Roaming_Chg 
     and rc.reference_type_id = 4100057 -- event subtype 
     and rc1.reference_type_id = 4100044 -- country
     and daa1.result6_value = daa2.index2_value
     and (daa1.result2_value = daa2.index3_value or daa2.index3_value = '-1') 
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and (daa2.index3_value = rc1.reference_code or daa2.index3_value = '-1') 
     and daa3.index2_value = ph.product_id(+) 
     and daa2.index1_value in (12,13) -- nobrmmsorg, nobrmmster
     and daa3.index4_value = rc.reference_code
     and daa1.result2_value = rc1.reference_code
     and (daa3.index7_value = daa1.index1_value or daa3.index7_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc1.abbreviation like '%s%%'
     order by 3,4
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)
    
    print("<h3> Roaming SMS </h3>")
    
    sql = """
    select unique daa3.index2_value as "Product ID", 
     ph.product_name as "Product Name", 
     daa3.result1_value as "Price Per Message", 
     rc1.abbreviation as "From Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc1
     where daa1.derived_attribute_id = 4200183
     and daa2.derived_attribute_id = 15000821
     and daa3.derived_attribute_id = 13000213
     and rc1.reference_type_id = 4100044 -- country
     and daa1.result3_value = daa2.index1_value
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and daa3.index2_value = ph.product_id(+)
     and daa1.result2_value = rc1.reference_code 
     and (daa3.index7_value = daa1.index1_value or daa3.index7_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc1.abbreviation like '%s%%'
     order by 3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)    
    
    print("<h3> Roaming Voice Originating </h3>")     
    
    sql = """
    select unique daa3.index2_value as "Product ID", 
     ph.product_name as "Product Name", 
     daa3.result1_value as "Start up Fee", 
     daa3.result4_value as "Price per Minute", 
     daa3.result5_value as "Debiting Interval", 
     rc1.abbreviation  as "Usage Type", 
     rc3.abbreviation as "From Country", 
     rc2.abbreviation as "To Destination"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc1, reference_code rc2, reference_code rc3
     where daa1.derived_attribute_id = 4200183 --dH3G_NE_NetworkPrefix
     and daa2.derived_attribute_id = 14001887 --dHi3G_NE_CS_IOBR_EventRules 
     and daa3.derived_attribute_id = 13000192 --dHi3G_RAT_Voice_OB_Roaming_Chg 
     and rc1.reference_type_id = 4100133 --H3G_NE_RECORD_CALLTYPE
     and rc2.reference_type_id = 4200183 --H3G_NE_LOCATION_GROUP
     and rc3.reference_type_id = 4100044 -- country
     and daa2.index3_value = rc1.reference_code
     and daa2.index2_value = rc2.reference_code
     and daa1.result5_value = daa2.index1_value
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and daa1.result2_value = rc3.reference_code 
     and daa3.index2_value = ph.product_id(+)
     and (daa3.index6_value = daa1.index1_value or daa3.index6_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc1.abbreviation like 'Telephony' -- voice only 
     and rc3.abbreviation like '%s%%'
     order by 8,4
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)
    
    print("<h3> Roaming Voice Terminating </h3>")  
  
    sql = """
    select unique daa3.index2_value as "Product ID", 
     ph.product_name as "Product Name", 
     daa3.result4_value as "Price per Minute", 
     daa3.result5_value as "Debiting Interval", 
     rc.abbreviation as "Usage Type", 
     rc1.abbreviation as "Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc,  reference_code rc1
     where daa1.derived_attribute_id = 4200183 --dH3G_NE_NetworkPrefix
     and daa2.derived_attribute_id = 12100045    --dHi3G_NE_CS_OBRoamEventRules
     and daa3.derived_attribute_id = 13000192    --dHi3G_RAT_Voice_OB_Roaming_Chg
     and rc.reference_type_id = 4100133 --H3G_NE_RECORD_CALLTYPE
     and rc1.reference_type_id = 4100044 -- country
     and daa2.index2_value = rc.reference_code   
     and daa1.result3_value = daa2.index1_value  
     and daa2.result1_value = daa3.index3_value  
     and daa2.result2_value = daa3.index4_value 
     and daa3.index2_value = ph.product_id(+)  
     and daa1.result2_value = rc1.reference_code 
     and (daa3.index6_value = daa1.index1_value or daa3.index6_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc.abbreviation like 'Telephony'
     and rc1.abbreviation like '%s%%'
     order by 5,3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)
   
    print("<h3> 3Global Pricing for International calls and IOBR MTC calls </h3>")
    
    sql = """
    select unique ph.product_name as "Product Name", 
     rc1.abbreviation as "Call Type", 
     rc2.abbreviation as "Destination", 
     daa3.result1_value as "Connection Fee", 
     daa3.result4_value as "Price per Min", 
     daa3.result5_value as "Debiting Interval"
     from derived_attribute_array daa3, derived_attribute_array daa2, derived_attribute_array daa1, reference_code rc1, reference_code rc2, product_history ph, reference_code rc3
     where daa1.derived_attribute_id = 4200183
     and daa2.derived_attribute_id = 4100033 
     and daa3.derived_attribute_id = 15000758
     and rc1.reference_type_id = 4100006
     and rc2.reference_type_id = 4100045
     and rc3.reference_type_id = 4100044 -- country
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and daa1.result2_value = daa2.result5_value
     and daa2.result6_value = daa3.index5_value
     and rc1.reference_code = daa3.index3_value
     and rc2.reference_code = daa3.index5_value
     and daa3.index2_value = ph.product_id(+)
     and daa1.result2_value = rc3.reference_code
     and rc3.abbreviation like '%s%%'
     order by 2,3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)   

 
elif (market == "DK"  and countryList.get(roam_country)) :

    print("<h1> Danish Roaming Pricing </h1>")

    print("<h3> Roaming Data </h3>")
    
    sql = """
    select unique daa3.index2_value as "Product ID" , 
     ph.product_name as "Product Name", 
     daa3.result4_value as "Price Per MB", 
     daa3.result5_value as "Debiting Interval",
     --rc.abbreviation as "Event Subtype",
     rc1.abbreviation as " From Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc, reference_code rc1
     where daa1.derived_attribute_id = 13000075 --dHi3G_DK_NE_NetworkPrefix
     and daa2.derived_attribute_id = 17010362 -- dHi3G_DK_NE_PS_RoamingEventRules
     and daa3.derived_attribute_id = 13000254 -- dHi3G_DK_RAT_Data_OB_Roaming_Chg
     and rc.reference_type_id = 4100057 -- event subtype 
     and rc1.reference_type_id = 4100044 -- country
     and daa1.result6_value = daa2.index2_value
     and (daa1.result2_value = daa2.index3_value or daa2.index3_value = '-1') 
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and (daa2.index3_value = rc1.reference_code or daa2.index3_value = '-1') 
     and daa3.index2_value = ph.product_id(+)
     and daa2.index1_value = '-1'
     and daa3.index4_value = rc.reference_code
     and daa1.result2_value = rc1.reference_code
     and (daa3.index7_value = daa1.index1_value or daa3.index7_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc1.abbreviation like '%s%%'
     order by 3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h3> Roaming MMS </h3>")

    sql = """
    select unique daa3.index2_value as "Product ID" , 
     ph.product_name as "Product Name", 
     daa3.result1_value as "Price Per Message", 
     daa3.result4_value as "Price Per MB", 
     daa3.result5_value as "Debiting Interval",
     --rc.abbreviation as "Event Subtype",
     rc1.abbreviation as "From Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc, reference_code rc1
     where daa1.derived_attribute_id = 13000075 --dHi3G_DK_NE_NetworkPrefix
     and daa2.derived_attribute_id = 17010362 -- dHi3G_DK_NE_PS_RoamingEventRules
     and daa3.derived_attribute_id = 13000255 -- dHi3G_DK_RAT_Message_OB_Roaming_Chg
     and rc.reference_type_id = 4100057 -- event subtype 
     and rc1.reference_type_id = 4100044 -- country
     and daa1.result6_value = daa2.index2_value
     and (daa1.result2_value = daa2.index3_value or daa2.index3_value = '-1') 
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and (daa2.index3_value = rc1.reference_code or daa2.index3_value = '-1') 
     and daa3.index2_value = ph.product_id(+)
     and daa2.index1_value in (12,13) 
     and daa3.index4_value = rc.reference_code
     and daa1.result2_value = rc1.reference_code
     and (daa3.index7_value = daa1.index1_value or daa3.index7_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc1.abbreviation like '%s%%'
     order by 3,4
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)

    
    print("<h3> Roaming SMS </h3>")
    
    sql = """
    select unique daa3.index2_value as "Product ID", 
     ph.product_name as "Product Name", 
     daa3.result1_value as "Price Per Message", 
     rc1.abbreviation as "From Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc1
     where daa1.derived_attribute_id = 13000075
     and daa2.derived_attribute_id = 15000822
     and daa3.derived_attribute_id = 13000255
     and rc1.reference_type_id = 4100044 -- country
     and daa1.result3_value = daa2.index1_value
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and daa3.index2_value = ph.product_id(+)
     and daa1.result2_value = rc1.reference_code 
     and (daa3.index7_value = daa1.index1_value or daa3.index7_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc1.abbreviation like '%s%%'
     order by 3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)    
    
    print("<h3> Roaming Voice Originating </h3>")
    
    sql = """
    select unique daa3.index2_value as "Product ID", 
     ph.product_name as "Product Name", 
     daa3.result1_value as "Start up Fee", 
     daa3.result4_value as "Price per Minute", 
     daa3.result5_value as "Debiting Interval",
     rc1.abbreviation  as "Usage Type", 
     rc3.abbreviation as "From Country", 
     rc2.abbreviation as "To Destination"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc1, reference_code rc2, reference_code rc3
     where daa1.derived_attribute_id = 13000075 --dHi3G_DK_NE_NetworkPrefix
     and daa2.derived_attribute_id = 14001888 --dHi3G_DK_NE_CS_IOBR_EventRules 
     and daa3.derived_attribute_id = 13000253 --dHi3G_DK_RAT_Voice_OB_Roaming_Chg 
     and rc1.reference_type_id = 4100133 --H3G_NE_RECORD_CALLTYPE
     and rc2.reference_type_id = 4200183 --H3G_NE_LOCATION_GROUP
     and rc3.reference_type_id = 4100044 -- country
     and daa2.index3_value = rc1.reference_code
     and daa2.index2_value = rc2.reference_code
     and daa1.result5_value = daa2.index1_value
     and daa2.result1_value = daa3.index3_value
     and daa2.result2_value = daa3.index4_value
     and daa1.result2_value = rc3.reference_code 
     and daa3.index2_value = ph.product_id(+)
     and (daa3.index6_value = daa1.index1_value or daa3.index6_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc1.abbreviation like 'Telephony' -- voice only 
     and rc3.abbreviation like  '%s%%'
     order by 8,4
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)
    
    print("<h3> Roaming Voice Terminating </h3>")
  
    sql = """
    select unique daa3.index2_value as "Product ID", 
     ph.product_name as "Product Name", 
     daa3.result4_value as "Price per Minute", 
     daa3.result5_value as "Debiting Interval", 
     rc.abbreviation as "Usage Type", 
     rc1.abbreviation as "Country"
     from derived_attribute_array daa1, derived_attribute_array daa2, derived_attribute_array daa3, product_history ph, reference_code rc,  reference_code rc1
     where daa1.derived_attribute_id = 13000075   --dHi3G_DK_NE_NetworkPrefix
     and daa2.derived_attribute_id = 15000959    --dHi3G_DK_NE_CS_OBRoamEventRules
     and daa3.derived_attribute_id = 13000253    --dHi3G_DK_RAT_Voice_OB_Roaming_Chg
     and rc.reference_type_id = 4100133 --H3G_NE_RECORD_CALLTYPE
     and rc1.reference_type_id = 4100044 -- country
     and daa2.index2_value = rc.reference_code   
     and daa1.result3_value = daa2.index1_value  
     and daa2.result1_value = daa3.index3_value  
     and daa2.result2_value = daa3.index4_value 
     and daa3.index2_value = ph.product_id(+)  
     and daa1.result2_value = rc1.reference_code 
     and (daa3.index6_value = daa1.index1_value or daa3.index6_value = '-1')
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and rc.abbreviation like 'Telephony'
     and rc1.abbreviation like '%s%%'
     order by 5,3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h3> 3Global Pricing for International calls and IOBR MTC calls </h3>")

    sql = """
    select unique ph.product_name as "Product Name", 
     rc1.abbreviation as "Call Type", 
     rc2.abbreviation as "Destination", 
     daa3.result1_value as "Connection Fee", 
     daa3.result4_value as "Price per Min", 
     daa3.result5_value as "Debiting Interval"
     from derived_attribute_array daa3, derived_attribute_array daa2, derived_attribute_array daa1, reference_code rc1, reference_code rc2, product_history ph, reference_code rc3
     where daa1.derived_attribute_id = 13000075 --dHi3G_DK_NE_NetworkPrefix
     and daa2.derived_attribute_id = 13000072 --dHi3G_DK_NE_NumberRegion
     and daa3.derived_attribute_id = 15000759 --dHi3G_DK_RAT_3Global_Chg
     and rc1.reference_type_id = 4100006 --H3G_NE_EVENT_TYPE
     and rc2.reference_type_id = 4100045 --H3G_NE_REGIONS
     and rc3.reference_type_id = 4100044 -- country
     and sysdate between daa3.effective_start_date and daa3.effective_end_date
     and daa1.result2_value = daa2.result5_value
     and daa2.result6_value = daa3.index5_value
     and rc1.reference_code = daa3.index3_value
     and rc2.reference_code = daa3.index5_value
     and daa3.index2_value = ph.product_id(+)
     and daa1.result2_value = rc3.reference_code
     and rc3.abbreviation like '%s%%'
     order by 2,3
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)

    cur.close()
    db.close()

else : 

    print("<h3> Please select roaming country </h3>")

 
rep.htmlEnd()










