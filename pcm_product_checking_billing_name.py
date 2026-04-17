#!/bin/env python
import billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Product Checking'
_desc = 'Check for billing product setup using product name'

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
product_name = rep.getParam('product_name') or ''

# Report form
form = br.form(action=module_name, method='get')
form.input(name = 'product_name', label = 'Product Name', type='text', default = product_name)
form.input(type="submit", default = 'Submit')
form.render()


# Report
if (product_name) :

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
        AND ph.product_name like '%%%s%%'
    ) t
    """ % (product_name)

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
         WHERE ph.product_name like '%%%s%%'
         AND pt.tariff_id = th.tariff_id
         AND pt.product_id = ph.product_id 
         ORDER BY ph.product_id, th.tariff_name
    ) t
    """ % (product_name)

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
        daa2.result1_value INVOICE_TEXT
        FROM derived_attribute_array daa1, product_history ph, gl_code_history gl, reference_code rc_fu, reference_code rc_uc, reference_code rc_fm, derived_attribute_array daa2
        WHERE ph.product_name like '%%%s%%'
        AND mod(mod(mod(mod(daa1.index2_value,582000000),572000000),152000000),142000000)+12000000 = ph.product_id
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
    """ % (product_name)

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
        WHERE ph.product_name like '%%%s%%'
        AND mod(mod(mod(mod(daa1.index2_value,582000000),572000000),152000000),142000000)+12000000 = ph.product_id
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
    """ % (product_name)


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
        AND ph.product_name like '%%%s%%'
    ) t
    """ % (product_name)

    cur = br.query(db, sql)
    rep.showCursor(cur)



    print("<h1>Discounts </h1>")

  

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
        AND ph.product_name like '%%%s%%'
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
        AND ph.product_name like '%%%s%%'
        ORDER BY 1,3
    ) t
    """ % (product_name,product_name)

    cur = br.query(db, sql)
    rep.showCursor(cur)


    print("<h1>Rating </h1>")


    print("<h1>Quarterly Invoicing </h1>")


    print("<h1>Fair Usage </h1>")


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
        and ph.product_name like '%%%s%%'
    ) t
    """ % (product_name)

    cur = br.query(db, sql)
    rep.showCursor(cur)


    cur.close()
    db.close()
    



rep.htmlEnd()






