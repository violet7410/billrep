#!/bin/env python
import lib.billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Product Checking'
_desc = 'Product setup in Psoft, Oscar and Billing.'

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
peoplesoft_id = rep.getParam('peoplesoft_id')


# Report form
form = br.form(action=module_name, method='get')
form.input(name = 'peoplesoft_id', label = 'Product', type='text', default = peoplesoft_id)
form.input(type="submit", default = 'Submit')
form.render()

print("<h1> Oscar Details </h1>")

db = br.getConnection('oscar_bt','oscar_stage/oscar_stage')

sql = """
  --- select ci.external_id1 as "PS_ID",
  SELECT '[link|'|| ci.external_id1  ||'|pcm_product_checking_psoft.py?peoplesoft_name_id=' || ci.external_id1 ||']' "PS_ID",
    ci.label as "PRODUCT_NAME",
    ci.external_label as  "CONTRACT_TEXT",
    ci.postpaid_prepaid as  "POSTPAID_PREPAID",
    ci.business_consumer as "CUSTOMER_TYPE",
    ci.voice_broadband as "SUBSCRIPTION_TYPE",
    cav1.value as  "UI_GROUP",
    cav2.value as "CONTRACT_CATEGORY",
    cav3.value as "COVERAGE_TYPE"
    from cat_item ci, cat_item_attribute cia1, cat_item_attribute cia2, cat_item_attribute cia3, cat_attribute_value cav1, cat_attribute_value cav2, cat_attribute_value cav3
    where ci.id = cia1.item_id(+)
    and cia1.attr_id(+) = 43310
    and cia1.value_id = cav1.id(+)
    and ci.id = cia2.item_id(+)
    and cia2.attr_id(+) = 296711
    and cia2.value_id = cav2.id(+)
    and ci.id = cia3.item_id(+)
    and cia3.attr_id(+) = 10855051
    and cia3.value_id = cav3.id(+)    
    and ci.external_id1 in ('%s')
"""  % (peoplesoft_id)

cur = br.query(db, sql)
rep.showCursor(cur)

db.close()
rep.htmlEnd()
