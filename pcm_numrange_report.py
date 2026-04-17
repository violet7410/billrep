#!/bin/env python
import lib.billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Number Prefix Report'
_desc = 'All number prefixes are shown on this report. The datasource is Billing.'

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters
country = rep.getParam('country') 
number_search = rep.getParam('number_search') or ''

show_all = rep.getParam('show_all') or ''

# Set default country
if (not country) : country = "DK"

# Get db connection
db = br.getConnection('pcmtool','pcmtool/p3mtoo1')

# Get country list
countryList     = { 'SE' : "SE Numbers", 'DK' : 'DK Numbers'}

# Report form
form = br.form(action=module_name, method='get')
form.select(name = 'country', label = 'Country', items = countryList, default = show_all)
form.input(name = 'number_search', label = 'Search Number Range', type='text', default = show_all)
form.input(type="submit", default = 'Search')
form.input(type="submit", default = 'View Numbers')
form.render()


# Report

if (country == "SE" and number_search != '') : 
    
    sql = """
    select * from num_region_se where numberregion like '%%%s%%'
    """% (number_search)

    cur = br.query(db, sql)
    rep.showCursor(cur)

elif (country == "SE" and number_search == '') :

    sql = """
    select * from num_region_se 
    """
     
    cur = br.query(db, sql)
    rep.showCursor(cur)

elif (country == "DK" and number_search != '') : 
    
    sql = """
    select * from num_region_dk where numberregion like '%%%s%%'
    """% (number_search)

    cur = br.query(db, sql)
    rep.showCursor(cur)

else :

    sql = """
    select * from num_region_dk
    """
     
    cur = br.query(db, sql)
    rep.showCursor(cur)


db.close()
rep.htmlEnd()


