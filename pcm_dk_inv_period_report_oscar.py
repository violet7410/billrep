#!/bin/env python
import lib.billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Invoicing Period Report'
_desc = 'All DK products found with current date between start_date or end_date are shown on this report. The datasource is Oscar.'

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
invoice_period = rep.getParam('invoice_period') 

# Set default 
if (not invoice_period) : invoice_period = "all_inv_periods"

# Get db connection
db = br.getConnection('oscar_bt','oscar_stage/oscar_stage')

# Get invoice period list
invoice_period_list  = { 'all_inv_periods' : "All Invoicing Periods", 'monthly_inv_period' : "Only Monthly", 'monthly_qi_inv_period' : 'Monthly and Quarterly'}

# Report form
form = br.form(action=module_name, method='get')
form.select(name = 'invoice_period', label = 'Invoice Period', items = invoice_period_list, default = invoice_period)
form.input(type="submit", default = 'List products')
form.render()


# Report

if (invoice_period == "monthly_inv_period") :

    # Construct SQL
     
    sql = """
     select rownum "No.", t.*
     from 
      (select ci.external_id1 as "Product_ID", ci.label as "Product Name" , 
       case when ci.business_consumer like 'B' then 'Business' 
       when ci.business_consumer like 'C' then 'Consumer' 
       when ci.business_consumer like 'A' then 'All' 
       end "Bus_Con",
       case when ci.voice_broadband like 'S' then 'Switch' 
       when ci.voice_broadband like 'V' then 'Voice'
       when ci.voice_broadband like 'B' then 'ISP' 
       when ci.voice_broadband like 'VB' then 'Voice and ISP' 
       when ci.voice_broadband like 'H' then 'Hardware'  
       when ci.voice_broadband like 'O' then 'Other'  
       when ci.voice_broadband like 'A' then 'All'  
       end "Voice_ISP",
       case when ci.eligible_invoicing_period like 'M' then 'Monthly' 
       when ci.eligible_invoicing_period like 'A' then 'Monthly and Quarterly' 
       end "Invoicing_Period"
       from cat_item ci 
       where 1=1 
       and ci.external_id2 = 'COM04' -- Denmark
       and ci.business_consumer not like 'C' -- Not Consumer, only Business can be enabled for Quarterly invoicing 
       and ci.external_id1 not like 'A%'
       and ci.external_id1 not like 'R%'
       and ci.external_id1 not like 'F%'
       and ci.external_id1 not like 'DOC%'
       and ci.external_id1 not like 'PRO%'
       and ci.external_id1 not like 'EX%'
       and ci.external_id1 not like 'S4%'  
       and ci.external_id1 not like 'L%'  
       and ci.external_id1 not like 'ZZZZZ'
       and ci.start_date not like '2099%' -- exclude not started 
       and ci.eligible_invoicing_period = 'M'  
       order by start_date desc      
      ) t
    """
    cur = br.query(db, sql)
    rep.showCursor(cur)

elif (invoice_period == "monthly_qi_inv_period") : 

    # Construct SQL
     
    sql = """
     select rownum "No.", t.*
     from 
      (select ci.external_id1 as "Product_ID", ci.label as "Product Name" , 
       case when ci.business_consumer like 'B' then 'Business' 
       when ci.business_consumer like 'C' then 'Consumer' 
       when ci.business_consumer like 'A' then 'All' 
       end "Bus_Con",
       case when ci.voice_broadband like 'S' then 'Switch' 
       when ci.voice_broadband like 'V' then 'Voice'
       when ci.voice_broadband like 'B' then 'ISP' 
       when ci.voice_broadband like 'VB' then 'Voice and ISP' 
       when ci.voice_broadband like 'H' then 'Hardware'  
       when ci.voice_broadband like 'O' then 'Other'  
       when ci.voice_broadband like 'A' then 'All'  
       end "Voice_ISP",
       case when ci.eligible_invoicing_period like 'M' then 'Monthly' 
       when ci.eligible_invoicing_period like 'A' then 'Monthly and Quarterly' 
       end "Invoicing_Period"
       from cat_item ci 
       where 1=1 
       and ci.external_id2 = 'COM04' -- Denmark
       and ci.business_consumer not like 'C' -- Not Consumer, only Business can be enabled for Quarterly invoicing 
       and ci.external_id1 not like 'A%'
       and ci.external_id1 not like 'R%'
       and ci.external_id1 not like 'F%'
       and ci.external_id1 not like 'DOC%'
       and ci.external_id1 not like 'PRO%'
       and ci.external_id1 not like 'EX%'
       and ci.external_id1 not like 'S4%'  
       and ci.external_id1 not like 'L%'  
       and ci.external_id1 not like 'ZZZZZ'
       and ci.start_date not like '2099%' -- exclude not started 
       and ci.eligible_invoicing_period = 'A'  
       order by start_date desc      
      ) t
    """
    cur = br.query(db, sql)
    rep.showCursor(cur)

else : 

    # Construct SQL
     
    sql = """
     select rownum "No.", t.*
     from 
       (select ci.external_id1 as "Product_ID", ci.label as "Product Name" , 
       case when ci.business_consumer like 'B' then 'Business' 
       when ci.business_consumer like 'C' then 'Consumer' 
       when ci.business_consumer like 'A' then 'All' 
       end "Bus_Con",
       case when ci.voice_broadband like 'S' then 'Switch' 
       when ci.voice_broadband like 'V' then 'Voice'
       when ci.voice_broadband like 'B' then 'ISP' 
       when ci.voice_broadband like 'VB' then 'Voice and ISP' 
       when ci.voice_broadband like 'H' then 'Hardware'  
       when ci.voice_broadband like 'O' then 'Other'  
       when ci.voice_broadband like 'A' then 'All'  
       end "Voice_ISP",
       case when ci.eligible_invoicing_period like 'M' then 'Monthly' 
       when ci.eligible_invoicing_period like 'A' then 'Monthly and Quarterly' 
       end "Invoicing_Period"
       from cat_item ci 
       where 1=1 
       and ci.external_id2 = 'COM04' -- Denmark
       and ci.business_consumer not like 'C' -- Not Consumer, only Business can be enabled for Quarterly invoicing 
       and ci.external_id1 not like 'A%'
       and ci.external_id1 not like 'R%'
       and ci.external_id1 not like 'F%'
       and ci.external_id1 not like 'DOC%'
       and ci.external_id1 not like 'PRO%'
       and ci.external_id1 not like 'EX%'
       and ci.external_id1 not like 'S4%' -- service products
       and ci.external_id1 not like 'L%'  
       and ci.external_id1 not like 'ZZZZZ'
       and ci.start_date not like '2099%' -- exclude not started 
       order by start_date desc       
      ) t
    """

    cur = br.query(db, sql)
    rep.showCursor(cur)

db.close()
rep.htmlEnd()





