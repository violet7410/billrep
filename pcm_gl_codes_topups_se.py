#!/bin/env python
import billrep as br

#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM GL report for topups'
_desc = 'Overview of GL codes for topups'

#-----------------------------------------------------------------------
# Support functions
#-----------------------------------------------------------------------
   
#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

print("<h1>Topups </h1>")

print("<p> This report is fetching data from billing and oscar. </p> ")
print("<p> It starts by gathering all topups found in oscar and it collects the gl codes from billing based on the asset type and event category from oscar .</p> ")

db = br.getConnection('pcmtool','pcmtool/p3mtoo1')

sql = """
select 
oscar."Voucher ID", 
oscar."Name", 
oscar."customer_type" as "Customer Type",
oscar."subscription_type" as "Subscription Type", 
oscar."price_ex_vat" as "Price ex Vat", 
oscar."price_incl_vat" as "Price incl Vat", 
oscar."vat" as "Vat", 
oscar."GL_AccountCode" as "GL Account Code",
oscar."GL_ProductService" as "GL Product Service",
oscar."GL_CustomerType" as "GL Customer Type",
oscar."GL_SpecCode" as "GL Spec Code",
billing."GL Code" as "Billing GL Code"
from 
(select  
external_id1 as "Voucher ID", 
external_label as "Name", 
decode (business_consumer,'B','Business','C','Consumer') as "customer_type",
decode(voice_broadband, 'V' ,'Voice' ,'B','ISP') as "subscription_type", 
cat1.value as "billing_topup", 
cat2.value as "vat", 
cat4.value as "price_ex_vat", 
cat3.value as "price_incl_vat", 
cat5.value as "asset_type",
cat6.value as "content_category",
cat7.value as "GL_SpecCode",
cat8.value as "GL_ProductService",
cat9.value as "GL_CustomerType",
cat10.value as "GL_AccountCode"
from  cat_item@oscarread, cat_item_attribute@oscarread cat1, cat_item_attribute@oscarread cat2, cat_item_attribute@oscarread cat3,  
cat_item_attribute@oscarread cat4, cat_item_attribute@oscarread cat5, cat_item_attribute@oscarread cat6, cat_item_attribute@oscarread cat7,
cat_item_attribute@oscarread cat8, cat_item_attribute@oscarread cat9, cat_item_attribute@oscarread cat10
where 1=1
and sysdate between start_date and end_date
AND external_id2 like '%03%' -- DK only
and id = cat1.item_id
and cat1.attr_id = 93710
and id = cat2.item_id
and cat2.attr_id = 95110
and id = cat3.item_id
and cat3.attr_id = 93610
and id = cat4.item_id
and cat4.attr_id = 1079451
and id = cat5.item_id
and cat5.attr_id = 95310 -- asset type
and id = cat6.item_id
and cat6.attr_id = 95210 -- cat
and id = cat7.item_id
and cat7.attr_id = 94010 --GL_SpecCode 	PP
and id = cat8.item_id
and cat8.attr_id = 93910 -- GL_ProductService  	499
and id = cat9.item_id
and cat9.attr_id = 94110 --GL_CustomerType 	VPO
and id = cat10.item_id
and cat10.attr_id = 93810 --GL_AccountCode  	3301
)oscar
left join 
(select rt_fullpath.abbreviation as "Asset Type",
rt_fullpath.reference_code as "Asset_Type",
rt_event_cat.reference_code as "Content_Category",
rt_event_cat.abbreviation as "Content Category",
rt_est.abbreviation as "Event Subtype",
gl_da.gl_code_name as "GL Code"
from derived_attribute_array@svbranch ct_callcat, derived_attribute_array@svbranch ct_evrules, derived_attribute_array@svbranch ct_chg_da, 
gl_code_history@svbranch gl_da, reference_code@svbranch rt_est,  reference_code@svbranch rt_fullpath,reference_code@svbranch rt_event_cat 
where 1=1
and ct_callcat.derived_attribute_id = 4200290 --dH3G_NE_CT_CallCategory
and ct_evrules.derived_attribute_id = 12100041 --dHi3G_NE_CT_EventRules_AP1
and ct_chg_da.derived_attribute_id = 12100073 --dHi3G_RAT_Content_PreChg 
and rt_est.reference_type_id = 4100057 --H3G_NE_EVENT_SUBTYPE
and rt_fullpath.reference_type_id = 4100132 --H3G_NE_RECORD_SUBTYPE
and rt_event_cat.reference_type_id = 4200285 --H3G_NE_CT_CATEGORY
and ct_callcat.result7_value = ct_evrules.index1_value --event category 
and ct_callcat.index2_value =  ct_evrules.index2_value -- product category 
and ct_chg_da.index4_value = ct_evrules.result2_value -- event subtype 
and gl_da.gl_code_id = ct_chg_da.result9_value
and rt_est.reference_code = ct_evrules.result2_value 
and rt_fullpath.reference_code = ct_callcat.index1_value 
and rt_event_cat.reference_code = ct_callcat.index2_value  
--and ct_callcat.index1_value like '490' -- asset type - full path 
--and ct_callcat.index2_value like '37000' -- content category (product category)
)billing
on oscar."asset_type" = billing."Asset_Type"
and oscar."content_category" = billing."Content_Category"
order by oscar."Name", oscar."customer_type", oscar."subscription_type"
""" 
cur = br.query(db, sql)
rep.showCursor(cur)


rep.htmlEnd()









