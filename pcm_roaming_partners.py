#!/bin/env python
import billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Roaming Partners'
_desc = 'Report of setup in billing for network operators'

#-----------------------------------------------------------------------
# Support functions
#-----------------------------------------------------------------------
def getCountryItems(db) :

    sql = """

    select unique rc1.abbreviation as "Country", rc1.description as "Country English"  
    from reference_code rc1, derived_attribute_array daa1
    where rc1.reference_type_id = 4100044 -- country
    and daa1.derived_attribute_id = 4200183 --dH3G_NE_NetworkPrefix
    and daa1.result2_value = rc1.reference_code
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

# Get request parameters

db = br.getConnection(br.getBranchAlias())

countryList = getCountryItems(db)
roam_country = rep.getParam('roam_country') or ''
mcc_mnc = rep.getParam('mcc_mnc') or ''
nngt_start = rep.getParam('nngt_start') or ''
nngt_end = rep.getParam('nngt_end') or ''
tadig = rep.getParam('tadig') or ''

# Report form
form = br.form(action=module_name, method='get')

form.select(name = 'roam_country', label = 'Roaming Country Name (English)', items = countryList, default=roam_country)
form.input(name = 'mcc_mnc', label = 'MCC MNC Code', type='text', default = mcc_mnc)
form.input(name = 'tadig', label = 'TADIG Code', type='text', default = tadig)
form.input(name = 'nngt_start', label = 'NNGT range start', type='text', default = nngt_start)
form.input(name = 'nngt_end', label = 'NNGT range end', type='text', default = nngt_end)

form.input(type="submit", default = 'Submit')
form.render()


# Report

if (countryList.get(roam_country)) : 

    print("<h1> Swedish Setup </h1>")

    # Construct SQL
    sql = """
    select rc1.abbreviation as "Operator",
     rc1.reference_code as "MCC MNC", 
     rc1.code_label as "TADIG",
     rc3.abbreviation as "Network Id", 
'[link|'||  rc4.abbreviation  ||'|pcm_roaming_charges.py?market=SE&roam_country=' ||  rc4.abbreviation ||']' "Country",
--     rc4.abbreviation as "Country",
     rc5.abbreviation as "Postpaid To", 
     rc6.abbreviation as "Network Region", 
     rc7.abbreviation as "Postpaid From",
     rc8.abbreviation as "Data Location"
     from reference_code rc1,
     reference_code rc3,
     reference_code rc4,
     reference_code rc5,
     reference_code rc6,
     reference_code rc7,
     reference_code rc8,
     derived_attribute_array daa1
     where rc1.reference_type_id = 3200001
     and rc3.reference_type_id = 4100130
     and rc4.reference_type_id = 4100044
     and rc5.reference_type_id = 4200183
     and rc6.reference_type_id = 4100045
     and rc7.reference_type_id = 4200183
     and rc8.reference_type_id = 4200183
     and daa1.derived_attribute_id = 4200183
     and rc1.reference_code = daa1.index1_value
     and rc3.reference_code = daa1.result1_value
     and rc4.reference_code = daa1.result2_value
     and rc5.reference_code = daa1.result3_value
     and rc6.reference_code = daa1.result4_value
     and rc7.reference_code = daa1.result5_value
     and rc8.reference_code = daa1.result6_value
     and rc4.abbreviation like '%s%%'
     order by 2
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)
    
    print("<h1> Danish Setup </h1>")

    # Construct SQL
    sql = """
    select rc1.abbreviation as "Operator",
     rc1.reference_code as "MCC MNC", 
     rc1.code_label as "TADIG",
     rc3.abbreviation as "Network Id", 
--     rc4.abbreviation as "Country",
'[link|'||  rc4.abbreviation  ||'|pcm_roaming_charges.py?market=DK&roam_country=' ||  rc4.abbreviation ||']' "Country",
     rc5.abbreviation as "Postpaid To", 
     rc6.abbreviation as "Network Region", 
     rc7.abbreviation as "Postpaid From",
     rc8.abbreviation as "Data Location"
     from reference_code rc1,
     reference_code rc3,
     reference_code rc4,
     reference_code rc5,
     reference_code rc6,
     reference_code rc7,
     reference_code rc8,
     derived_attribute_array daa1
     where rc1.reference_type_id = 13000031
     and rc3.reference_type_id = 4100130
     and rc4.reference_type_id = 4100044
     and rc5.reference_type_id = 4200183
     and rc6.reference_type_id = 4100045
     and rc7.reference_type_id = 4200183
     and rc8.reference_type_id = 4200183
     and daa1.derived_attribute_id = 13000075
     and rc1.reference_code = daa1.index1_value
     and rc3.reference_code = daa1.result1_value
     and rc4.reference_code = daa1.result2_value
     and rc5.reference_code = daa1.result3_value
     and rc6.reference_code = daa1.result4_value
     and rc7.reference_code = daa1.result5_value
     and rc8.reference_code = daa1.result6_value
     and rc4.abbreviation like '%s%%'
     order by 2
    """ % (roam_country)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)    
    

elif (mcc_mnc) :

    print("<h1> Swedish Setup </h1>")

    # Construct SQL
    sql = """
    select rc1.abbreviation as "Operator",
     rc1.reference_code as "MCC MNC", 
     rc1.code_label as "TADIG",
     rc3.abbreviation as "Network Id", 
     '[link|'||  rc4.abbreviation  ||'|pcm_roaming_charges.py?market=SE&roam_country=' ||  rc4.abbreviation ||']' "Country",
     rc5.abbreviation as "Postpaid To", 
     rc6.abbreviation as "Network Region", 
     rc7.abbreviation as "Postpaid From",
     rc8.abbreviation as "Data Location"
     from reference_code rc1,
     reference_code rc3,
     reference_code rc4,
     reference_code rc5,
     reference_code rc6,
     reference_code rc7,
     reference_code rc8,
     derived_attribute_array daa1
     where rc1.reference_type_id = 3200001
     and rc3.reference_type_id = 4100130
     and rc4.reference_type_id = 4100044
     and rc5.reference_type_id = 4200183
     and rc6.reference_type_id = 4100045
     and rc7.reference_type_id = 4200183
     and rc8.reference_type_id = 4200183
     and daa1.derived_attribute_id = 4200183
     and rc1.reference_code = daa1.index1_value
     and rc3.reference_code = daa1.result1_value
     and rc4.reference_code = daa1.result2_value
     and rc5.reference_code = daa1.result3_value
     and rc6.reference_code = daa1.result4_value
     and rc7.reference_code = daa1.result5_value
     and rc8.reference_code = daa1.result6_value
     and rc1.reference_code like '%s%%'
     order by 2
    """ % (mcc_mnc)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)


    print("<h2> Sweden - Terminating Numbers in this country by best lookup </h2>")

    sql = """
    select unique daa.index1_value as "Number range", rc.abbreviation as "Type of Number"
     from derived_attribute_array daa, reference_code rc
     where daa.derived_attribute_id = 4100033
     and rc.reference_type_id = 4100045
     and daa.result6_value = rc.reference_code
     and daa.result5_value in
     (select unique result2_value
     from derived_attribute_array
     where derived_attribute_id = 4200183
     and index1_value like '%s%%')
     order by 1
    """ % (mcc_mnc)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)

    
    print("<h1> Danish Setup </h1>")

    sql = """
    select rc1.abbreviation as "Operator",
     rc1.reference_code as "MCC MNC", 
     rc1.code_label as "TADIG",
     rc3.abbreviation as "Network Id", 
     '[link|'||  rc4.abbreviation  ||'|pcm_roaming_charges.py?market=DK&roam_country=' ||  rc4.abbreviation ||']' "Country", 
     rc5.abbreviation as "Postpaid To", 
     rc6.abbreviation as "Network Region", 
     rc7.abbreviation as "Postpaid From",
     rc8.abbreviation as "Data Location"
     from reference_code rc1,
     reference_code rc3,
     reference_code rc4,
     reference_code rc5,
     reference_code rc6,
     reference_code rc7,
     reference_code rc8,
     derived_attribute_array daa1
     where rc1.reference_type_id = 13000031
     and rc3.reference_type_id = 4100130
     and rc4.reference_type_id = 4100044
     and rc5.reference_type_id = 4200183
     and rc6.reference_type_id = 4100045
     and rc7.reference_type_id = 4200183
     and rc8.reference_type_id = 4200183
     and daa1.derived_attribute_id = 13000075
     and rc1.reference_code = daa1.index1_value
     and rc3.reference_code = daa1.result1_value
     and rc4.reference_code = daa1.result2_value
     and rc5.reference_code = daa1.result3_value
     and rc6.reference_code = daa1.result4_value
     and rc7.reference_code = daa1.result5_value
     and rc8.reference_code = daa1.result6_value
     and rc1.reference_code like '%s%%'
     order by 2
    """ % (mcc_mnc)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)    



    print("<h2> Denmark - Terminating Numbers in this country by best lookup </h2>")

    sql = """
    select unique daa.index1_value as "Number range", rc.abbreviation as "Type of Number"
     from derived_attribute_array daa, reference_code rc
     where daa.derived_attribute_id = 13000072
     and rc.reference_type_id = 4100045
     and daa.result6_value = rc.reference_code
     and daa.result5_value in
     (select unique result2_value
     from derived_attribute_array
     where derived_attribute_id = 13000075
     and index1_value like '%s%%')
     order by 1
    """ % (mcc_mnc)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)
    
    print("<h1> NNGT Ranges </h1>")

    # Construct SQL
    sql = """
    select result1_value MCC_MNC, index1_value RANGE_START, index2_value RANGE_END, rc.abbreviation TIMEZONE, daa.description DESCRIPTION
     from derived_attribute_array daa, reference_code rc
     where daa.derived_attribute_id = 16002042 -- dHi3G_MSC_GT_To_MCC_MNC
     and rc.reference_type_id = 23000954 --Time Zone
     and daa.result2_value = rc.reference_code
     and daa.result1_value like '%s%%'
     order by 1, 2
    """ % (mcc_mnc)

    cur = br.query(db, sql)
    rep.showCursor(cur)



elif (nngt_start) : 

    print("<h1>NNGT Ranges search by NNGT start range </h1>")

    # Construct SQL
    sql = """
    select result1_value MCC_MNC, index1_value RANGE_START, index2_value RANGE_END, rc.abbreviation TIMEZONE, daa.description DESCRIPTION
     from derived_attribute_array daa, reference_code rc
     where daa.derived_attribute_id = 16002042 -- dHi3G_MSC_GT_To_MCC_MNC
     and rc.reference_type_id = 23000954 --Time Zone
     and daa.result2_value = rc.reference_code
     and daa.index1_value like '%s%%'
     order by 1, 2
    """ % (nngt_start)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)
    
elif (nngt_end) : 

    print("<h1>NNGT Ranges search by NNGT end range </h1>")

    # Construct SQL
    sql = """
    select result1_value MCC_MNC, index1_value RANGE_START, index2_value RANGE_END, rc.abbreviation TIMEZONE, daa.description DESCRIPTION
     from derived_attribute_array daa, reference_code rc
     where daa.derived_attribute_id = 16002042 -- dHi3G_MSC_GT_To_MCC_MNC
     and rc.reference_type_id = 23000954 --Time Zone
     and daa.result2_value = rc.reference_code
     and daa.index2_value like '%s%%'
     order by 1, 2
    """ % (nngt_end)
    
    cur = br.query(db, sql)
    rep.showCursor(cur)


elif (tadig) : 

   print("<h1> Swedish Setup </h1>")

    # Construct SQL
   sql = """
    select rc1.abbreviation as "Operator",
     rc1.reference_code as "MCC MNC", 
     rc1.code_label as "TADIG",
     rc3.abbreviation as "Network Id", 
     '[link|'||  rc4.abbreviation  ||'|pcm_roaming_charges.py?market=SE&roam_country=' ||  rc4.abbreviation ||']' "Country",
     rc5.abbreviation as "Postpaid To", 
     rc6.abbreviation as "Network Region", 
     rc7.abbreviation as "Postpaid From",
     rc8.abbreviation as "Data Location"
     from reference_code rc1,
     reference_code rc3,
     reference_code rc4,
     reference_code rc5,
     reference_code rc6,
     reference_code rc7,
     reference_code rc8,
     derived_attribute_array daa1
     where rc1.reference_type_id = 3200001
     and rc3.reference_type_id = 4100130
     and rc4.reference_type_id = 4100044
     and rc5.reference_type_id = 4200183
     and rc6.reference_type_id = 4100045
     and rc7.reference_type_id = 4200183
     and rc8.reference_type_id = 4200183
     and daa1.derived_attribute_id = 4200183
     and rc1.reference_code = daa1.index1_value
     and rc3.reference_code = daa1.result1_value
     and rc4.reference_code = daa1.result2_value
     and rc5.reference_code = daa1.result3_value
     and rc6.reference_code = daa1.result4_value
     and rc7.reference_code = daa1.result5_value
     and rc8.reference_code = daa1.result6_value
     and rc1.code_label like '%s%%'
     order by 2
    """ % (tadig)
    
   cur = br.query(db, sql)
   rep.showCursor(cur)

    
   print("<h1> Danish Setup </h1>")

   sql = """
    select rc1.abbreviation as "Operator",
     rc1.reference_code as "MCC MNC", 
     rc1.code_label as "TADIG",
     rc3.abbreviation as "Network Id", 
     '[link|'||  rc4.abbreviation  ||'|pcm_roaming_charges.py?market=DK&roam_country=' ||  rc4.abbreviation ||']' "Country", 
     rc5.abbreviation as "Postpaid To", 
     rc6.abbreviation as "Network Region", 
     rc7.abbreviation as "Postpaid From",
     rc8.abbreviation as "Data Location"
     from reference_code rc1,
     reference_code rc3,
     reference_code rc4,
     reference_code rc5,
     reference_code rc6,
     reference_code rc7,
     reference_code rc8,
     derived_attribute_array daa1
     where rc1.reference_type_id = 13000031
     and rc3.reference_type_id = 4100130
     and rc4.reference_type_id = 4100044
     and rc5.reference_type_id = 4200183
     and rc6.reference_type_id = 4100045
     and rc7.reference_type_id = 4200183
     and rc8.reference_type_id = 4200183
     and daa1.derived_attribute_id = 13000075
     and rc1.reference_code = daa1.index1_value
     and rc3.reference_code = daa1.result1_value
     and rc4.reference_code = daa1.result2_value
     and rc5.reference_code = daa1.result3_value
     and rc6.reference_code = daa1.result4_value
     and rc7.reference_code = daa1.result5_value
     and rc8.reference_code = daa1.result6_value
     and rc1.code_label like '%s%%'
     order by 2
    """ % (tadig)
    
   cur = br.query(db, sql)
   rep.showCursor(cur)    


   cur.close()
   db.close()    
 
rep.htmlEnd()










