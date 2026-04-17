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
peoplesoft_name_id = rep.getParam('peoplesoft_name_id')


# Report form
form = br.form(action=module_name, method='get')
form.input(name = 'peoplesoft_name_id', label = 'Peoplesoft Product ID or Name', type='text', default = peoplesoft_name_id)
form.input(type="submit", default = 'Submit')
form.render()

print("<h1> Peoplesoft Details </h1>")

db = br.getConnection('psoft','psoft08/hutch08')

sql = """
   SELECT '[link|'|| ppi.product_id  ||'|pcm_product_checking_oscar.py?peoplesoft_id=' || ppi.product_id ||']' "Product ID",
   --SELECT ppi.product_id as "Product ID",
   ppi.Descr as "Product",
   DECODE (ppi.setid,
   'COM03', 'Sweden',
   'COM04', 'Denmark',
            'Unknown') "Country",
   DECODE (ppi.orderable,
   'A', 'Business and Consumer',
   'B', 'Business',
   'C', 'Consumer',
        'Unknown') "Customer Type",
   ppi.prod_category as "Product Category",
   ppa.attribute_value as "Report Category",
   'N/A' as "Tariff Usage",
   'N/A' as "Tariff Type",
   ppi.prod_field_c6 AS LTE,
   ppa4.attribute_value as "FUL EU Data",
   --ppi.model_nbr  as "Billing Product ID"
   '[link|'|| ppi.model_nbr  ||'|pcm_product_checking_billing.py?product_id=' || ppi.model_nbr ||']' "Billing Product ID"
   FROM   ps_prod_item ppi, ps_prod_attr ppa, ps_prod_attr ppa4
   WHERE  (upper(ppi.descr) Like  upper('%%%s%%')  OR ppi.product_id like '%%%s%%')
   AND ppi.model_nbr <> ' '
   AND ppi.prod_category NOT IN ('MW_TARIFF_PLAN','TARIFF_PLAN','RET_NORMAL','NSW_TARIFF_PLAN')
   and ppi.product_id = ppa.product_id(+)
   and ppi.product_id = ppa4.product_id(+)
   and ppa.attribute_id(+) = 'REPORT_CAT'
   and ppa4.attribute_id(+) = 'FUL_EU_DATA'
   UNION
   SELECT '[link|'|| ppi.product_id  ||'|pcm_product_checking_oscar.py?peoplesoft_id=' || ppi.product_id ||']' "Product ID",
   ---SELECT ppi.product_id as "Product ID",
   ppi.Descr as "Product",
   DECODE (ppi.setid,
   'COM03', 'Sweden',
   'COM04', 'Denmark',
            'Unknown') "Country",
   DECODE (ppi.orderable,
   'A', 'Business and Consumer',
   'B', 'Business',
   'C', 'Consumer',
        'Unknown') "Customer Type",
   ppi.prod_category as "Product Category",
   ppa.attribute_value as "Report Category",
   'N/A' as "Tariff Usage",
   'N/A' as "Tariff Type",
   ppi.prod_field_c6 AS LTE,
   ppa4.attribute_value as "FUL EU Data",
   'N/A' as "Billing Product ID"
   FROM   ps_prod_item ppi, ps_prod_attr ppa, ps_prod_attr ppa4
   WHERE  (upper(ppi.descr) Like upper('%%%s%%') OR ppi.product_id like '%%%s%%')
   AND ppi.model_nbr = ' '
   AND ppi.prod_category NOT IN ('MW_TARIFF_PLAN','TARIFF_PLAN','RET_NORMAL','NSW_TARIFF_PLAN','RET_POTT')
   and ppi.product_id = ppa.product_id(+)
   and ppi.product_id = ppa4.product_id(+)
   and ppa.attribute_id(+) = 'REPORT_CAT'
   and ppa4.attribute_id(+) = 'FUL_EU_DATA'
   UNION
   SELECT '[link|'|| ppi.product_id  ||'|pcm_product_checking_oscar.py?peoplesoft_id=' || ppi.product_id ||']' "Product ID",
   ---SELECT  ppi.product_id as "Product ID",
   PPI.Descr as "Product",
   DECODE (PPI.setid,
   'COM03', 'Sweden',
   'COM04', 'Denmark',
            'Unknown') "Country",
   DECODE (PPI.orderable,
   'A', 'Business and Consumer',
   'B', 'Business',
   'C', 'Consumer',
        'Unknown') "Customer Type",
   PPI.prod_category as "Product Category",
   'N/A' as "Report Category",
   PPA2.attribute_value as "Tariff Usage",
   PPA3.attribute_value as "Tariff Type",
   ppi.prod_field_c6 AS LTE,
   ppa4.attribute_value as "FUL EU Data",
   '[link|'|| LISTAGG(PPA.attribute_value, ',') WITHIN GROUP (ORDER BY PPA.attribute_value) ||'|pcm_product_checking_billing.py?product_id='|| LISTAGG(PPA.attribute_value, ',') WITHIN GROUP (ORDER BY PPA.attribute_value) ||']' "Billing Product ID"
   FROM   ps_prod_item PPI, ps_prod_attr PPA, ps_prod_attr ppa4, ps_prod_attr PPA2, ps_prod_attr PPA3
   WHERE PPI.product_id = PPA.product_id
   AND PPI.product_id = PPA2.product_id(+)
   AND PPI.product_id = PPA3.product_id(+)
   and ppi.product_id = ppa4.product_id(+)
   AND PPA2.attribute_id(+) = 'TARIFF_USAGE'
   AND PPA3.attribute_id(+) = 'TARIFF_TYPE'
   AND (upper(PPI.descr) Like  upper('%%%s%%')  OR ppi.product_id like '%%%s%%')
   AND PPI.model_nbr <> ' '
   AND PPI.prod_category in ('MW_TARIFF_PLAN','TARIFF_PLAN','RET_NORMAL','NSW_TARIFF_PLAN','RET_POTT')
   AND (PPA.attribute_id = PPA.attribute_value OR PPA.attribute_id = 'REMAINDER_RC')
   AND length(PPA.attribute_value) = 8
   and ppa4.attribute_id(+) = 'FUL_EU_DATA'
   GROUP BY PPI.product_id, PPI.Descr, PPI.setid, PPI.orderable, PPI.prod_category, PPA2.attribute_value, PPA3.attribute_value, ppi.prod_field_c6, PPA4.attribute_value
   ORDER BY 1 
""" % (peoplesoft_name_id,peoplesoft_name_id,peoplesoft_name_id,peoplesoft_name_id,peoplesoft_name_id,peoplesoft_name_id)

cur = br.query(db, sql)
rep.showCursor(cur)

db.close()

rep.htmlEnd()

