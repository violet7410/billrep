#!/bin/env python
import lib.billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Product Checking'
_desc = 'Product setup in Psoft searching by billing id as input'

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
billing_id = rep.getParam('billing_id')


# Report form
form = br.form(action=module_name, method='get')
form.input(name = 'billing_id', label = 'Billing Product ID', type='text', default = billing_id)
form.input(type="submit", default = 'Submit')
form.render()

print("<h1> Peoplesoft Details </h1>")

db = br.getConnection('psoft','psoft08/hutch08')

sql = """
select 
ppi.product_id as "Product ID",
ppi.Descr as "Product",
DECODE (ppi.setid,
'COM03', 'Sweden',
'COM04', 'Denmark',
         'Unknown') "Country",
ppi.prod_category, 
ppa.attribute_value "Billing Product ID"
from ps_prod_attr ppa, ps_prod_item ppi 
where ppa.PRODUCT_ID = ppi.PRODUCT_ID
and ppa.ATTRIBUTE_ID = ppa.ATTRIBUTE_VALUE
and ppa.ATTRIBUTE_VALUE like '%%%s%%'
--order by ppi.datetime_added desc 
union
select 
ppi.product_id as "Product ID",
ppi.Descr as "Product",
DECODE (ppi.setid,
'COM03', 'Sweden',
'COM04', 'Denmark',
         'Unknown') "Country",
ppi.prod_category, 
ppi.model_nbr "Billing Product ID"
from ps_prod_item ppi 
where ppi.model_nbr like '%%%s%%'
""" % (billing_id,billing_id)

cur = br.query(db, sql)
rep.showCursor(cur)

db.close()

rep.htmlEnd()


