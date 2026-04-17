#!/bin/env python
import billrep as br

#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM GL report for all Swedish products'
_desc = 'Overview of GL codes for all products/addons/discounts/topups/priceplans '

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

prodid = rep.getParam('prodid') or ''
prodname = rep.getParam('prodname') or ''
glcode = rep.getParam('glcode') or ''

show_all = rep.getParam('show_all') or ''

# Report form
form = br.form(action=module_name, method='get')

form.input(name = 'prodid', label = 'Product ID', type='text', default = show_all)
form.input(name = 'prodname', label = 'Product Name', type='text', default = show_all)
form.input(name = 'glcode', label = 'GL Code', type='text', default = show_all)

form.input(type="submit", default = 'Search')
form.input(type="submit", default = 'Display all products')

form.render()

print ("<p> This report is fetching data from billing, peoplesoft and oscar. </p> ")


db = br.getConnection('pcmtool','pcmtool/p3mtoo1')

if (prodid != '') : 

     sql = """
     select * from gl_overview where "Country" = 'Sweden'
     and "Product ID" like '%%%s%%'
     """% (prodid) 

     cur = br.query(db, sql)
     rep.showCursor(cur)

elif (prodname != '') : 

     sql = """
     select * from gl_overview where "Country" = 'Sweden'
     and "Name" like '%%%s%%'
     """% (prodname)
 
     cur = br.query(db, sql)
     rep.showCursor(cur)

elif (glcode != '') :

     sql = """
     select * from gl_overview where "Country" = 'Sweden'
     and "GL Code" like '%%%s%%'
     """% (glcode)
 
     cur = br.query(db, sql)
     rep.showCursor(cur)

else : 

     sql = """
     select * from gl_overview where "Country" = 'Sweden'
     """
 
     cur = br.query(db, sql)
     rep.showCursor(cur)


rep.htmlEnd()











