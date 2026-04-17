#!/bin/env python
import lib.billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Topups Report'
_desc = 'All topups found with current date between start_date or end_date are shown on this report. The datasource is Oscar.'

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
country = rep.getParam('country') 

# Set default country
if (not country) : country = "SE"

# Get db connection
#db = br.getConnection('oscar_bt','oscar_stage/oscar_stage')
db = br.getConnection('pcmtool','pcmtool/p3mtoo1')

# Get country list
countryList     = { 'SE' : "SE Topups", 'DK' : 'DK Topups'}

# Report form
form = br.form(action=module_name, method='get')
form.select(name = 'country', label = 'Country', items = countryList, default = country)
form.input(type="submit", default = 'View Topups')
form.render()


# Report

if (country == "SE") :

    # Construct SQL
     
    sql = """
     select rownum "No.", t.*
     from 
      (
       SELECT  external_label AS NAME, external_id1 AS ID, decode (business_consumer,'B','Business','C','Consumer') as Customer_Type,
       decode(voice_broadband, 'V' ,'Voice' ,'B','ISP') as Subscription_Type, cat1.value AS billing_topup, cat2.value as VAT, cat4.value as Price_ex_VAT, cat3.value as Price_incl_VAT, --description,
       case when cat1.value like '%RLH%' then '3Like Home' 
       when cat1.value not like '%RLH%' then 'N/A' end "RLH",
       case when external_id2 =  'COM04' and cat1.value like '%BL%' then 'Block TopUp' 
       when external_id2 =  'COM04' and cat1.value like '%BW%' then 'Bandwidth Limited' 
       when external_id2 =  'COM04' and cat1.value like '%RDP%' then 'N/A'  
       when external_id2 =  'COM04' and cat1.value like '%PASS%' then 'N/A'
       when external_id2 =  'COM04' and cat1.value like '%FCA%' then 'N/A' 
       when external_id2 =  'COM03' and cat1.value like '%Co%' then 'Block TopUp' 
       when external_id2 =  'COM03' and cat1.value like '%Bus%' then 'Bandwidth Limited' 
       when external_id2 =  'COM03' and cat1.value like '%RDP%' then 'N/A'  
       when external_id2 =  'COM03' and cat1.value like '%PASS%' then 'N/A'
       when external_id2 =  'COM03' and cat1.value like '%FCA%' then 'N/A' 
       end "Free Units Msg",
       case when cat1.value like '%NS%' then 'NonShared' 
       when cat1.value like '%RDP%' then 'N/A'     
       when cat1.value like '%PASS%' then 'N/A'
       when cat1.value like '%FCA%' then 'N/A'
       when cat1.value like '%_S%' then 'Shared' 
       when cat1.value like '%Sh%' then 'Shared'
       end "Free Units Shared"
       FROM  cat_item@oscarread,  cat_item_attribute@oscarread cat1,  cat_item_attribute@oscarread cat2, cat_item_attribute@oscarread cat3,  cat_item_attribute@oscarread cat4
       WHERE external_id1 LIKE 'PT%'
       AND external_id2 like '%03%'
       -- AND business_consumer = 'B'
       AND SYSDATE BETWEEN start_date AND end_date
       and id = cat1.item_id
       and cat1.attr_id = 93710
       and id = cat2.item_id
       and cat2.attr_id = 95110
       and id = cat3.item_id
       and cat3.attr_id = 93610
       and id = cat4.item_id
       and cat4.attr_id = 1079451
       order by 3,4,9,11,10
      ) t
    """
    #print(sql)
    cur = br.query(db, sql)
    rep.showCursor(cur)

else : 

    # Construct SQL
     
    sql = """
     select rownum "No.", t.*
     from 
      (SELECT  external_label AS NAME, external_id1 AS ID, decode (business_consumer,'B','Business','C','Consumer') as Customer_Type,
       decode(voice_broadband, 'V' ,'Voice' ,'B','ISP') as Subscription_Type, cat1.value AS billing_topup, cat2.value as VAT, cat4.value as Price_ex_VAT, cat3.value as Price_incl_VAT, --description,
       case when cat1.value like '%RLH%' then '3Like Home' 
       when cat1.value not like '%RLH%' then 'N/A' end "RLH",
       case when external_id2 =  'COM04' and cat1.value like '%BL%' then 'Block TopUp' 
       when external_id2 =  'COM04' and cat1.value like '%BW%' then 'Bandwidth Limited' 
       when external_id2 =  'COM04' and cat1.value like '%RDP%' then 'N/A'  
       when external_id2 =  'COM04' and cat1.value like '%PASS%' then 'N/A'
       when external_id2 =  'COM04' and cat1.value like '%FCA%' then 'N/A' 
       when external_id2 =  'COM03' and cat1.value like '%Co%' then 'Block TopUp' 
       when external_id2 =  'COM03' and cat1.value like '%Bus%' then 'Bandwidth Limited' 
       when external_id2 =  'COM03' and cat1.value like '%RDP%' then 'N/A'  
       when external_id2 =  'COM03' and cat1.value like '%PASS%' then 'N/A'
       when external_id2 =  'COM03' and cat1.value like '%FCA%' then 'N/A' 
       end "Free Units Msg",
       case when cat1.value like '%NS%' then 'NonShared' 
       when cat1.value like '%RDP%' then 'N/A'     
       when cat1.value like '%PASS%' then 'N/A'
       when cat1.value like '%FCA%' then 'N/A'
       when cat1.value like '%_S%' then 'Shared' 
       when cat1.value like '%Sh%' then 'Shared'
       end "Free Units Shared"
       FROM  cat_item@oscarread,  cat_item_attribute@oscarread cat1,  cat_item_attribute@oscarread cat2, cat_item_attribute@oscarread cat3,  cat_item_attribute@oscarread cat4
       WHERE external_id1 LIKE 'PT%'
       AND external_id2 like '%04%'
       -- AND business_consumer = 'B'
       AND SYSDATE BETWEEN start_date AND end_date
       and id = cat1.item_id
       and cat1.attr_id = 93710
       and id = cat2.item_id
       and cat2.attr_id = 95110
       and id = cat3.item_id
       and cat3.attr_id = 93610
       and id = cat4.item_id
       and cat4.attr_id = 1079451
       order by 3,4,9,11,10
      ) t
    """
    #print(sql)
    cur = br.query(db, sql)
    rep.showCursor(cur)

db.close()
rep.htmlEnd()




