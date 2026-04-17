#!/bin/env python
import billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Product Checking'
_desc = 'Check for billing product setup'

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
product_id = rep.getParam('product_id') or ''

# Report form
form = br.form(action=module_name, method='get')
form.input(name = 'product_id', label = 'Product ID', type='text', default = product_id)
form.input(type="submit", default = 'Submit')
form.render()


# Report
if (product_id) :

    # Get SVTrunk db connection
    db = br.getConnection(br.getBranchAlias())

    print("<h1>Product Name and possible Campaign information and Consume Data </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (SELECT  to_char(ph.product_id) as "Product ID",
        ph.product_name,
        daa.result1_value GLOBAL_START_DATE,
        daa.result2_value GLOBAL_END_DATE,
        daa.result3_value CAMPAIGN_START_DATE,
        daa.result4_value VALIDITY_PERIOD,
        rc.abbreviation VALIDITY_UNIT,
        daa.result6_value CAMPAIGN_END_DATE,
        daa2.result1_value CONSUME_SHARED_DATA,
        fu_class.abbreviation FU_CLASS,
        rc2.abbreviation SPLIT_CATEGORY
        FROM product_history ph, derived_attribute_array daa, reference_code rc, derived_attribute_array daa2, derived_attribute_array daa3, reference_code rc2, reference_code fu_class
        WHERE daa.derived_attribute_id(+) = 4100565
        AND daa2.derived_attribute_id(+) = 16001328
        AND daa3.derived_attribute_id(+) = 14001284
        AND rc.reference_type_id(+) = 4100049
        AND rc2.reference_type_id(+) = 14000811
        AND fu_class.reference_type_id(+) = 23000634
        AND daa.index1_value(+) = ph.product_id
        AND daa2.index1_value(+) = ph.product_id
        AND daa3.index1_value(+) = ph.product_id
        AND rc.reference_code(+) = daa.result5_value
        AND rc2.reference_code(+) = daa3.result1_value
        AND fu_class.reference_code(+) = daa2.RESULT2_VALUE
        AND ph.product_id in (%s)
    ) t
    """ % (product_id)

    #print(sql)
    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h1>Product Tariffs </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (SELECT ph.product_id,
         ph.product_name,
         th.tariff_name
         FROM product_tariff pt, tariff_history th, product_history ph
         WHERE ph.product_id IN (%s)
         AND pt.tariff_id = th.tariff_id
         AND pt.product_id = ph.product_id 
         ORDER BY ph.product_id, th.tariff_name
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)


    print("<h1>Activation </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (SELECT ph.product_id,
        ph.product_name,
        daa1.result1_value ACTIVATION_FEE,
        gl.gl_code_name GL_CODE,
        rc_fu.abbreviation FU_CATEGORY,
        daa1.result6_value FU_AMOUNT,
        rc_uc.abbreviation USAGE_CATEGORY,
        daa1.result8_value FM_CATEGORY,
        daa1.result9_value FM_AMOUNT,
        daa2.result1_value INVOICE_TEXT,
        daa1.result3_value NUC_Activation_INVOICE_TEXT
        FROM derived_attribute_array daa1, product_history ph, gl_code_history gl, reference_code rc_fu, reference_code rc_uc, reference_code rc_fm, derived_attribute_array daa2
        WHERE ph.product_id IN (%s) AND mod(mod(mod(mod(daa1.index2_value,582000000),572000000),152000000),142000000)+12000000 = ph.product_id
        AND daa1.derived_attribute_id = 3100084 --dH3G_NUC_Activation_Chg
        AND daa2.derived_attribute_id = 4200210 --dH3G_Inv_PackageProductsAlias 
        AND rc_fu.reference_type_id(+) = 1000023
        AND daa1.result5_value = rc_fu.reference_code(+)
        AND rc_uc.reference_type_id(+) = 4100110
        AND daa1.result7_value = rc_uc.reference_code(+)
        AND rc_fm.reference_type_id(+) = 14000088
        AND daa1.result8_value = rc_fm.reference_code(+)
        AND daa1.result4_value = gl.gl_code_id
        AND to_char(ph.product_id) = daa2.index1_value(+)
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h1>Recurring Charges including Footnotes and Sort Codes and Tax Class </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (SELECT ph.product_id, ph.product_name, daa1.result1_value RECURRING_FEE, gl.gl_code_name GL_CODE,
        rc_fu.abbreviation FU_CATEGORY, daa1.result6_value FU_AMOUNT, rc_uc.abbreviation USAGE_CATEGORY,
        daa1.result10_value INVOICE_FEE, daa2.result1_value INVOICE_TEXT, daa3.result1_value FOOTNOTE, daa4.result1_value SORTCODE, tax_class.abbreviation TAX_CLASS 
        FROM derived_attribute_array daa1, product_history ph, gl_code_history gl, reference_code rc_fu,
        reference_code rc_uc, derived_attribute_array daa2, derived_attribute_array daa3, derived_attribute_array daa4, derived_attribute_array daa5, reference_code tax_class
        WHERE ph.product_id IN (%s) AND mod(mod(mod(mod(daa1.index2_value,582000000),572000000),152000000),142000000)+12000000 = ph.product_id
        AND daa1.derived_attribute_id = 3100144 --dH3G_NUC_RecurChg
        AND daa2.derived_attribute_id(+) = 4200210 --dH3G_Inv_PackageProductsAlias
        AND daa3.derived_attribute_id(+) = 14000801 --dHi3G_Inv_Footnote
        AND daa4.derived_attribute_id(+) = 13000313 --dHi3G_ProductSortCodes
        AND daa5.derived_attribute_id(+) =  12100069  --dHi3G_TAX_ServiceTaxClass_Mapping       
        AND rc_fu.reference_type_id(+) = 1000023
        AND daa1.result5_value = rc_fu.reference_code(+)
        AND rc_uc.reference_type_id(+) = 4100110
        AND daa1.result7_value = rc_uc.reference_code(+)
        AND tax_class.reference_type_id(+) = 12100029
        AND daa5.result1_value = tax_class.reference_code(+)       
        AND daa1.result4_value = gl.gl_code_id
        AND daa2.index1_value(+) = ph.product_id
        AND daa3.index3_value(+) = ph.product_id
        AND daa4.index1_value(+) = ph.product_id
        AND daa5.index3_value(+) = ph.product_id    
    ) t
    """ % (product_id)


    cur = br.query(db, sql)
    rep.showCursor(cur)
    
    print("<h1>Invoice Footnotes,Sort Codes,Tax Class and FunctNr Count </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (SELECT ph.product_id, ph.product_name, 
        daa2.result1_value INVOICE_TEXT, daa3.result1_value FOOTNOTE, daa4.result1_value SORTCODE, tax_class.abbreviation TAX_CLASS , daa6.result1_value  COUNT
        FROM product_history ph, derived_attribute_array daa2, derived_attribute_array daa3, derived_attribute_array daa4, derived_attribute_array daa5, derived_attribute_array daa6,reference_code tax_class
        WHERE 1=1
        AND daa2.derived_attribute_id(+) = 4200210 --dH3G_Inv_PackageProductsAlias
        AND daa3.derived_attribute_id(+) = 14000801 --dHi3G_Inv_Footnote
        AND daa4.derived_attribute_id(+) = 13000313 --dHi3G_ProductSortCodes
        AND daa5.derived_attribute_id(+) =  12100069  --dHi3G_TAX_ServiceTaxClass_Mapping 
        AND daa6.derived_attribute_id(+) =  50124157   -- dHi3G_RC_DSC_Prods_Count 
        AND tax_class.reference_type_id(+) = 12100029 -- TAX RT
        AND daa5.result1_value = tax_class.reference_code(+)       
        AND daa2.index1_value(+) = ph.product_id
        AND daa3.index3_value(+) = ph.product_id
        AND daa4.index1_value(+) = ph.product_id
        AND daa5.index3_value(+) = ph.product_id  
        AND daa6.index1_value(+) = ph.product_id  
        AND ph.product_id IN (%s) 
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)



    print("<h1>Discounts </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (SELECT ph1.product_name as "DISCOUNT_PRODUCT_ID", ph2.product_name as  "COMP_PRODUCT_ID" , rc1.abbreviation as "USAGE_CATEGORY",
       rc2.abbreviation as "DISCOUNT", daa2.result2_value as "PERCENTAGE", daa2.result3_value as "FIXED_AMOUNT", daa2.result5_value as "INVOICE_TEXT" , gl.gl_code_name as "GL_CODE"
       FROM derived_attribute_array daa1, derived_attribute_array daa2, product_history ph1, product_history ph2,
       reference_code rc1, reference_code rc2, gl_code_history gl
       WHERE daa1.derived_attribute_id = 16001081 --dHi3G_DSC_MRCDiscounts
       AND daa2.derived_attribute_id = 4100131 --dH3G_DSC_Global
       AND rc1.reference_type_id = 4100110 --H3G_NE_USAGE_CATEGORY
       AND rc2.reference_type_id = 4100104 --H3G_DISCOUNTS
       AND daa1.index1_value in (%s)
       AND daa1.index1_value = ph1.product_id
       AND daa1.index2_value = ph2.product_id
       AND daa1.index3_value = rc1.reference_code
       AND daa1.result1_value = rc2.reference_code
       AND daa2.index1_value = daa1.result1_value
       AND daa2.result6_value = gl.gl_code_id
       UNION
       SELECT ph1.product_name as "DISCOUNT_PRODUCT_ID", 'ANY', rc1.abbreviation as "USAGE_CATEGORY",
       rc2.abbreviation  as "DISCOUNT", daa2.result2_value as "PERCENTAGE", daa2.result3_value as "FIXED_AMOUNT", daa2.result5_value as "INVOICE_TEXT" , gl.gl_code_name as "GL_CODE"
       FROM derived_attribute_array daa1, derived_attribute_array daa2, product_history ph1,
       reference_code rc1, reference_code rc2, gl_code_history gl
       WHERE daa1.derived_attribute_id = 16001081 --dHi3G_DSC_MRCDiscounts
       AND daa2.derived_attribute_id = 4100131 --dH3G_DSC_Global
       AND rc1.reference_type_id = 4100110 --H3G_NE_USAGE_CATEGORY
       AND rc2.reference_type_id = 4100104 --H3G_DISCOUNTS
       AND daa1.index1_value in  (%s)
       AND daa1.index1_value = ph1.product_id
       AND daa1.index2_value = '-1'
       AND daa1.index3_value = rc1.reference_code
       AND daa1.result1_value = rc2.reference_code
       AND daa2.index1_value = daa1.result1_value
       AND daa2.result6_value = gl.gl_code_id
       UNION
       SELECT ph1.product_name as "DISCOUNT_PRODUCT_ID", ph2.product_name as  "COMP_PRODUCT_ID" , rc1.abbreviation as "USAGE_CATEGORY",
       rc2.abbreviation  as "DISCOUNT", daa2.result2_value as "PERCENTAGE", daa2.result3_value as "FIXED_AMOUNT", daa2.result5_value as "INVOICE_TEXT" , gl.gl_code_name as "GL_CODE"
       FROM derived_attribute_array daa1, derived_attribute_array daa2, product_history ph1, product_history ph2,
       reference_code rc1, reference_code rc2, gl_code_history gl
       WHERE daa1.derived_attribute_id = 4100135 --dH3G_DSC_Volume
       AND daa2.derived_attribute_id = 4100131 --dH3G_DSC_Global
       AND rc1.reference_type_id = 4100110 --H3G_NE_USAGE_CATEGORY
       AND rc2.reference_type_id = 4100104 --H3G_DISCOUNTS
       AND daa1.index5_value in (%s)
       AND daa1.index5_value = ph1.product_id
       AND daa1.index2_value = ph2.product_id
       AND daa1.index1_value = rc1.reference_code
       AND daa1.result1_value = rc2.reference_code
       AND daa2.index1_value = daa1.result1_value
       AND daa2.result6_value = gl.gl_code_id
       UNION
       SELECT ph1.product_name as "DISCOUNT_PRODUCT_ID", 'ANY', rc1.abbreviation as "USAGE_CATEGORY",
       rc2.abbreviation  as "DISCOUNT", daa2.result2_value as "PERCENTAGE", daa2.result3_value as "FIXED_AMOUNT", daa2.result5_value as "INVOICE_TEXT" , gl.gl_code_name as "GL_CODE"
       FROM derived_attribute_array daa1, derived_attribute_array daa2, product_history ph1,
       reference_code rc1, reference_code rc2, gl_code_history gl
       WHERE daa1.derived_attribute_id = 4100135 --dH3G_DSC_Volume 
       AND daa2.derived_attribute_id = 4100131 --dH3G_DSC_Global
       AND rc1.reference_type_id = 4100110 --H3G_NE_USAGE_CATEGORY
       AND rc2.reference_type_id = 4100104 --H3G_DISCOUNTS
       AND daa1.index5_value in (%s)
       AND daa1.index5_value = ph1.product_id
       AND daa1.index2_value = '-1'
       AND daa1.index1_value = rc1.reference_code
       AND daa1.result1_value = rc2.reference_code
       AND daa2.index1_value = daa1.result1_value
       AND daa2.result6_value = gl.gl_code_id
       ORDER BY 1, 2, 4, 5
    ) t
    """ % (product_id,product_id,product_id,product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)


    print("<h1>Free Units & Free Money Coverage </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (SELECT ph.product_id "Product ID", 
        ph.product_name "Product Name", 
        rc_uc.abbreviation "Usage Category", 
        rc_fu.abbreviation "FU/FM Type"
        FROM derived_attribute_array daa_fu, reference_code rc_uc, product_history ph, reference_code rc_fu
        WHERE daa_fu.derived_attribute_id = 3100000 --dH3G_FU_Type
        AND rc_uc.reference_type_id = 4100110 --H3G_NE_USAGE_CATEGORY
        AND rc_fu.reference_type_id = 3100000 --H3G FU Type
        AND daa_fu.index1_value = rc_uc.reference_code
        AND daa_fu.result1_value = rc_fu.reference_code
        AND daa_fu.index3_value = ph.product_id
        AND ph.product_id in  (%s)
        UNION
        SELECT ph.product_id "Product ID",
        ph.product_name "Product Name",
        rc_uc.abbreviation "Usage Category",
        rc_fm.abbreviation "FU/FM Type"
        FROM derived_attribute_array daa_fm, reference_code rc_uc, product_history ph, reference_code rc_fm
        WHERE daa_fm.derived_attribute_id = 14000276 --dH3G_FM_Type
        AND rc_uc.reference_type_id = 4100110 --H3G_NE_USAGE_CATEGORY
        AND rc_fm.reference_type_id = 14000085 --H3G FM Type
        AND daa_fm.index1_value = rc_uc.reference_code
        AND daa_fm.result1_value = rc_fm.reference_code
        AND daa_fm.index3_value = ph.product_id
        AND ph.product_id in  (%s)
        ORDER BY 1,3
    ) t
    """ % (product_id,product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)


    print("<h1>Rating </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (select unique rc1.abbreviation as "USAGE_CATEGORY",
        ph.product_name as "PRODUCT_NAME",
        daa2.index2_value as "PRODUCT_ID",
        daa1.result1_value as "PRIO",
        daa1.result9_value as "CHG_DA",
        rc2.abbreviation as "EVENT_TYPE",
        rc3.abbreviation as "EVENT_SUBTYPE",
        daa2.result1_value as "ONETIME",
        daa2.result4_value as "MULTIPLIER",
        daa2.result5_value as "DEB_INTERVAL",
        daa2.result10_value as "FU_ONETIME"
        from derived_attribute_array daa1,
        derived_attribute_array daa2,
        derived_attribute_array daa3,
        reference_code rc1,
        reference_code rc2,
        reference_code rc3,
        product_history ph,
        derived_attribute_history dah
        where daa1.derived_attribute_id = 4100166 --Prod_Eligibility
        and daa2.derived_attribute_id = dah.derived_attribute_id --Rating Table
        and sysdate between daa2.effective_start_date and daa2.effective_end_date  
        and daa3.derived_attribute_id in (4200186,50003587,4200291,4200294,4200325,15000821,16001863,4200326,4200233,4200234,13000259,
        14001888,15000959,50043733,50003589,13000381,13000260,50124013,15000822,15000716,15000717,
        15001142,17010362,16000245,12100170,14001887,16001965,12100045,50043732,50003590,12100041,
        12100277,12100278,50124012,50124014,13000382,17010361,17010440,16000244) -- Event Rules Tables
        and rc1.reference_type_id = 4100110 --USAGE_CATEGORY
        and rc2.reference_type_id = 4100006 --Event Type
        and rc3.reference_type_id = 4100057 --Event SubType
        and daa1.index2_value in (%s) --PRODUCT_ID
        and daa1.index1_value = to_char(rc1.reference_code)
        and daa1.index2_value = to_char(ph.product_id)
        and daa1.result9_value = substr(dah.derived_attribute_name,0,length(daa1.result9_value))
        and (daa2.index2_value = daa1.index2_value or daa2.index2_value = '-1')
        and daa2.index3_value = to_char(rc2.reference_code)
        and daa2.index4_value = to_char(rc3.reference_code)
        and daa3.result1_value = daa2.index3_value
        and daa3.result2_value = daa2.index4_value
        and daa3.result3_value = daa1.index1_value
        order by rc1.abbreviation, rc2.abbreviation, rc3.abbreviation, to_number(daa1.result1_value) asc, daa2.index2_value desc
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h1>Quarterly Invoicing </h1>")

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (select qi_da.index1_value as "Monthly_Prod_ID",ph1.product_name as "Monthly_Prod_Name", 
        qi_da.result1_value as "Quarterly_Prod_ID", ph2.product_name as "Quarterly_Prod_Name"
        from derived_attribute_array qi_da, product_history ph1, product_history ph2
        where qi_da.derived_attribute_id = 16001543 
        and ph1.product_id = qi_da.index1_value
        and ph2.product_id = qi_da.result1_value
        and ph1.product_id in (%s) -- search made by Monthly product ID
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)

    # Construct SQL
    sql = """
    select rownum no, t.*
    from (select qi_da.index1_value as "Monthly_Prod_ID",ph1.product_name as "Monthly_Prod_Name", 
        qi_da.result1_value as "Quarterly_Prod_ID", ph2.product_name as "Quarterly_Prod_Name"
        from derived_attribute_array qi_da, product_history ph1, product_history ph2
        where qi_da.derived_attribute_id = 16001543 
        and ph1.product_id = qi_da.index1_value
        and ph2.product_id = qi_da.result1_value
        and ph2.product_id in (%s) -- search made by Quarterly product ID
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h1>Fair Usage </h1>")


    # Construct SQL
    sql = """
    select rownum no, t.*
    from (select unique to_number(daa2.result1_value)/(1024*1024*1024) as "FUL_GB", daa2.index2_value as "Usage_Product", ph1.product_name as "Usage_Product_Name", daa1.index2_value as "RC_Product", ph2.product_name as "RC_Product_Name" 
        from derived_attribute_array daa1, derived_attribute_array daa2, reference_code rc1, product_history ph1, product_history ph2
        where daa1.derived_attribute_id = 50135887
        and daa2.derived_attribute_id = 50123974
        and rc1.reference_type_id = 23123591
        and ph1.product_id = daa2.index2_value
        and ph2.product_id = daa1.index2_value
        and daa1.index1_value = rc1.abbreviation
        and daa2.index1_value = rc1.reference_code
        and daa2.index2_value in (%s) -- search made by Usage product ID
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)


    # Construct SQL
    sql = """
    select rownum no, t.*
    from (select unique to_number(daa2.result1_value)/(1024*1024*1024) as "FUL_GB", daa2.index2_value as "Usage_Product", ph1.product_name as "Usage_Product_Name", daa1.index2_value as "RC_Product", ph2.product_name as "RC_Product_Name" 
        from derived_attribute_array daa1, derived_attribute_array daa2, reference_code rc1, product_history ph1, product_history ph2
        where daa1.derived_attribute_id = 50135887
        and daa2.derived_attribute_id = 50123974
        and rc1.reference_type_id = 23123591
        and ph1.product_id = daa2.index2_value
        and ph2.product_id = daa1.index2_value
        and daa1.index1_value = rc1.abbreviation
        and daa2.index1_value = rc1.reference_code
        and daa1.index2_value in (%s) -- search made by RC product ID
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)

    print("<h1>Final Bill Tax Class Mapping </h1>")


    # Construct SQL
    sql = """
    select rownum no, t.*
    from (select ph.product_id, ph.product_name, tax_class.abbreviation as "Tax Class" ,tax_da.result2_value as "Charge Tax Rate"
        from derived_attribute_array tax_da, reference_code tax_class, product_history ph
        where tax_da.derived_attribute_id = 16002265
        and tax_class.reference_type_id(+) = 12100029
        and tax_da.result1_value = tax_class.reference_code(+)  
        and ph.product_id = tax_da.index1_value
        and ph.product_id in (%s) 
    ) t
    """ % (product_id)

    cur = br.query(db, sql)
    rep.showCursor(cur)


    cur.close()
    db.close()
    



rep.htmlEnd()





