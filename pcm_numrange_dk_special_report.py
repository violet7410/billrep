#!/bin/env python
import lib.billrep as br
#-----------------------------------------------------------------------
# Define report name and descriptions here
# This information is used by report portal page
#-----------------------------------------------------------------------
_name = 'PCM Number Prefix Report'
_desc = 'Report of all Danish Special Numbers. The datasource is Billing.'

#-----------------------------------------------------------------------
# Main code
#-----------------------------------------------------------------------
module_name = br.fileBasename(__file__)

rep = br.report(_name, _desc)

rep.htmlStart()

# Get request parameters

number_search = rep.getParam('number_search') or ''
show_all = rep.getParam('show_all') or ''

# Get db connection
db = br.getConnection(br.getBranchAlias())

# Report form
form = br.form(action=module_name, method='get')

form.input(name = 'number_search', label = 'Search Number Range', type='text', default = show_all)
form.input(type="submit", default = 'Search')
form.input(type="submit", default = 'Display all numbers')

form.render()

print("<h3> All charges are excluding VAT. </h3>") 

# Report

if (number_search == '') : 
      
       # Construct SQL to show all numbers
           
    sql = """
      select 
      num_chg."Number Region", 
      num_chg."Event Category", 
      num_chg."Event_Type",
      num_chg."Event_Sub_Type",
      num_chg."Usage Category",
      num_chg."Charge Per Call",
      num_chg."Charge Per Minute",
      substr (num_chg."GL Code",7,11) as "GL Code",
      case 
      when tax_da."Tax Class" like 'NOT APPLICABLE' then 'Not Applicable' 
      when tax_da."Tax Class" like 'NON TAXABLE SERVICES' then 'Non Taxable' 
      when tax_da."Tax Class" like 'INCLUDED_25PCT' then 'Included 25' 
      when tax_da."Tax Class" like '§7-SERVICES' then 'Standard 25' 
      when tax_da."Tax Class" is null then 'Standard 25' 
      end "Tax Class", 
      split_da."Split Category", 
      event_supplier_da."Event Supplier", 
      event_supplier_da."Charge Method" 
      from 
      (select daa_num_reg.index1_value as "Number Region", 
      rc_event_cat.abbreviation as "Event Category", 
      rc_event_type.abbreviation as "Event_Type",
      rc_event_subtype.abbreviation as "Event_Sub_Type",
      rc_uc.abbreviation as "Usage Category",
      daa_chg.result1_value as "Charge Per Call",
      daa_chg.result4_value as "Charge Per Minute",
      gl_code.gl_code_name as "GL Code",
      daa_chg.index2_value as "Product"
      from derived_attribute_array daa_num_reg, derived_attribute_array daa_ev_rules, derived_attribute_array daa_chg, gl_code_history gl_code,
      reference_code rc_event_cat, reference_code rc_event_type, reference_code rc_event_subtype, reference_code rc_uc 
      where 1=1 
      and sysdate between daa_chg.effective_start_date and daa_chg.effective_end_date
      and daa_num_reg.derived_attribute_id = 13000072 -- dHi3G_DK_NE_NumberRegion
      and daa_ev_rules.derived_attribute_id = 13000259 -- dHi3G_DK_NE_CS_EventRules
      and daa_chg.derived_attribute_id = 13000153 -- dHi3G_DK_RAT_VoiceSpec_Chg
      and rc_event_cat.reference_type_id =  4200201 -- H3G_NE_EVENT_CATEGORY
      and rc_event_type.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_event_subtype.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_uc.reference_type_id =  4100110  --  H3G_NE_USAGE_CATEGORY
      and daa_num_reg.result4_value = daa_ev_rules.index1_value -- location group 
      and daa_ev_rules.index3_value = 1 -- Voice Event Category
      and daa_chg.index3_value = daa_ev_rules.result1_value -- event type 
      and daa_chg.index4_value = daa_ev_rules.result2_value -- event subtype
      and gl_code.gl_code_id = daa_chg.result9_value
      and rc_event_cat.reference_code = daa_ev_rules.index3_value 
      and rc_event_type.reference_code = daa_ev_rules.result1_value 
      and rc_event_subtype.reference_code = daa_ev_rules.result2_value 
      and rc_uc.reference_code = daa_ev_rules.result3_value 
      and gl_code.gl_code_id = daa_chg.result9_value
      and daa_chg.index2_value = '-1' -- Any
      union
      select daa_spec_numb.index1_value as "Number_Region" , 
      rc_event_cat.abbreviation as "Event Category",
      rc_event_type.abbreviation as "Event_Type",
      rc_event_subtype.abbreviation as "Event_Sub_Type",
      rc_uc.abbreviation as "Usage Category",
      daa_chg.result1_value as "Charge Per Call",
      daa_chg.result4_value as "Charge Per Minute",
      gl_code.gl_code_name as "GL Code",
      daa_chg.index2_value as "Product"
      from derived_attribute_array daa_spec_numb, derived_attribute_array daa_ev_rules, derived_attribute_array daa_chg, gl_code_history gl_code,
      reference_code rc_event_cat, reference_code rc_event_type, reference_code rc_event_subtype, reference_code rc_uc 
      where 1=1
      and sysdate between daa_chg.effective_start_date and daa_chg.effective_end_date
      and daa_spec_numb.derived_attribute_id = 13000074 -- dHi3G_DK_NE_SpecialNumbers
      and daa_ev_rules.derived_attribute_id = 13000259 -- dHi3G_DK_NE_CS_EventRules
      and daa_chg.derived_attribute_id = 13000153 -- dHi3G_DK_RAT_VoiceSpec_Chg
      and rc_event_cat.reference_type_id =  4200201 --H3G_NE_EVENT_CATEGORY
      and rc_event_type.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_event_subtype.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_uc.reference_type_id =  4100110  --  H3G_NE_USAGE_CATEGORY
      and daa_spec_numb.result1_value = daa_ev_rules.index1_value -- location group 
      and daa_ev_rules.index3_value = 1 -- Voice Event Category
      and daa_chg.index3_value = daa_ev_rules.result1_value -- event type 
      and daa_chg.index4_value = daa_ev_rules.result2_value -- event subtype
      and gl_code.gl_code_id = daa_chg.result9_value
      and rc_event_cat.reference_code = daa_ev_rules.index3_value 
      and rc_event_type.reference_code = daa_ev_rules.result1_value 
      and rc_event_subtype.reference_code = daa_ev_rules.result2_value 
      and rc_uc.reference_code = daa_ev_rules.result3_value 
      and gl_code.gl_code_id = daa_chg.result9_value
      and daa_chg.index2_value = '-1' -- Any
      ) num_chg
      left join
      (select rc_est.abbreviation as "Event_Sub_Type", rc_et.abbreviation as "Event_Type", rc_tax.abbreviation as "Tax Class"
      from derived_attribute_array tax_da, reference_code rc_tax, reference_code rc_est, reference_code rc_et
      where tax_da.derived_attribute_id = 12100069 -- dHi3G_TAX_ServiceTaxClass_Mapping
      and rc_tax.reference_type_id = 12100029 --Hi3G_SERVICE_TAX_CLASS
      and rc_est.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_et.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_tax.reference_code = tax_da.result1_value
      and rc_est.reference_code = tax_da.index2_value
      and rc_et.reference_code = tax_da.index1_value
      and tax_da.index4_value = 3936 -- DK 
      ) tax_da 
      on num_chg."Event_Sub_Type" = tax_da."Event_Sub_Type"
      and num_chg."Event_Type" = tax_da."Event_Type"
      left join 
      (
      select split_uc_rt.abbreviation as "UsageCat" , split_cat_rt.abbreviation as "Split Category"
      from derived_attribute_array split_uc_daa, reference_code split_cat_rt, reference_code split_uc_rt
      where split_uc_daa.derived_attribute_id = 14001306 --- dHi3G_3Split_UsageCategory   
      and split_cat_rt.reference_type_id = 14000811 -- HI3G_FENIX_CATEGORY
      and split_uc_rt.reference_type_id =  4100110  --  H3G_NE_USAGE_CATEGORY
      and split_uc_rt.code_label = split_uc_daa.index1_value
      and split_cat_rt.reference_code = split_uc_daa.result1_value 
      ) split_da
      on split_da."UsageCat" = num_chg."Usage Category"
      left join 
      (
      select rc_est.abbreviation as "Event_Sub_Type", rc_et.abbreviation as "Event_Type", rc_sc.abbreviation as "Event Supplier" , rc_chg_met.abbreviation as "Charge Method" 
      from derived_attribute_array ev_sup , reference_code rc_est, reference_code rc_et, reference_code rc_sc, reference_code rc_chg_met
      where ev_sup.derived_attribute_id = 14001405 ---dHi3G_3PS_EventSupplier 
      and ev_sup.index3_value = 3936 -- DK 
      and rc_est.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_et.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_sc.reference_type_id =  4100081 -- H3G_SALES_CHANNELS
      and rc_chg_met.reference_type_id  = 14000871 --HI3G_DUAL_CHARGING_METHOD
      and rc_est.reference_code = ev_sup.index2_value
      and rc_et.reference_code = ev_sup.index1_value
      and rc_sc.reference_code = ev_sup.result1_value
      and rc_chg_met.reference_code = ev_sup.result2_value
      ) event_supplier_da
      on event_supplier_da."Event_Sub_Type" = num_chg."Event_Sub_Type"
      order by 3,4,1    
    """
    cur = br.query(db, sql)
    rep.showCursor(cur)

else :

    # Construct SQL to search for specific number 
     
    sql = """
      select 
      num_chg."Number Region", 
      num_chg."Event Category", 
      num_chg."Event_Type",
      num_chg."Event_Sub_Type",
      num_chg."Usage Category",
      num_chg."Charge Per Call",
      num_chg."Charge Per Minute",
      substr (num_chg."GL Code",7,11) as "GL Code", 
      case 
      when tax_da."Tax Class" like 'NOT APPLICABLE' then 'Not Applicable' 
      when tax_da."Tax Class" like 'NON TAXABLE SERVICES' then 'Non Taxable' 
      when tax_da."Tax Class" like 'INCLUDED_25PCT' then 'Included 25' 
      when tax_da."Tax Class" like '§7-SERVICES' then 'Standard 25' 
      when tax_da."Tax Class" is null then 'Standard 25' 
      end "Tax Class", 
      split_da."Split Category", 
      event_supplier_da."Event Supplier", 
      event_supplier_da."Charge Method" 
      from 
      (select daa_num_reg.index1_value as "Number Region", 
      rc_event_cat.abbreviation as "Event Category", 
      rc_event_type.abbreviation as "Event_Type",
      rc_event_subtype.abbreviation as "Event_Sub_Type",
      rc_uc.abbreviation as "Usage Category",
      daa_chg.result1_value as "Charge Per Call",
      daa_chg.result4_value as "Charge Per Minute",
      gl_code.gl_code_name as "GL Code",
      daa_chg.index2_value as "Product"
      from derived_attribute_array daa_num_reg, derived_attribute_array daa_ev_rules, derived_attribute_array daa_chg, gl_code_history gl_code,
      reference_code rc_event_cat, reference_code rc_event_type, reference_code rc_event_subtype, reference_code rc_uc 
      where 1=1 
      and sysdate between daa_chg.effective_start_date and daa_chg.effective_end_date
      and daa_num_reg.derived_attribute_id = 13000072 -- dHi3G_DK_NE_NumberRegion
      and daa_ev_rules.derived_attribute_id = 13000259 -- dHi3G_DK_NE_CS_EventRules
      and daa_chg.derived_attribute_id = 13000153 -- dHi3G_DK_RAT_VoiceSpec_Chg
      and rc_event_cat.reference_type_id =  4200201 -- H3G_NE_EVENT_CATEGORY
      and rc_event_type.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_event_subtype.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_uc.reference_type_id =  4100110  --  H3G_NE_USAGE_CATEGORY
      and daa_num_reg.result4_value = daa_ev_rules.index1_value -- location group 
      and daa_ev_rules.index3_value = 1 -- Voice Event Category
      and daa_chg.index3_value = daa_ev_rules.result1_value -- event type 
      and daa_chg.index4_value = daa_ev_rules.result2_value -- event subtype
      and gl_code.gl_code_id = daa_chg.result9_value
      and rc_event_cat.reference_code = daa_ev_rules.index3_value 
      and rc_event_type.reference_code = daa_ev_rules.result1_value 
      and rc_event_subtype.reference_code = daa_ev_rules.result2_value 
      and rc_uc.reference_code = daa_ev_rules.result3_value 
      and gl_code.gl_code_id = daa_chg.result9_value
      and daa_chg.index2_value = '-1' -- Any
      and daa_num_reg.index1_value like  '%%%s%%'
      union
      select daa_spec_numb.index1_value as "Number_Region" , 
      rc_event_cat.abbreviation as "Event Category",
      rc_event_type.abbreviation as "Event_Type",
      rc_event_subtype.abbreviation as "Event_Sub_Type",
      rc_uc.abbreviation as "Usage Category",
      daa_chg.result1_value as "Charge Per Call",
      daa_chg.result4_value as "Charge Per Minute",
      gl_code.gl_code_name as "GL Code",
      daa_chg.index2_value as "Product"
      from derived_attribute_array daa_spec_numb, derived_attribute_array daa_ev_rules, derived_attribute_array daa_chg, gl_code_history gl_code,
      reference_code rc_event_cat, reference_code rc_event_type, reference_code rc_event_subtype, reference_code rc_uc 
      where 1=1
      and sysdate between daa_chg.effective_start_date and daa_chg.effective_end_date
      and daa_spec_numb.derived_attribute_id = 13000074 -- dHi3G_DK_NE_SpecialNumbers
      and daa_ev_rules.derived_attribute_id = 13000259 -- dHi3G_DK_NE_CS_EventRules
      and daa_chg.derived_attribute_id = 13000153 -- dHi3G_DK_RAT_VoiceSpec_Chg
      and rc_event_cat.reference_type_id =  4200201 --H3G_NE_EVENT_CATEGORY
      and rc_event_type.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_event_subtype.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_uc.reference_type_id =  4100110  --  H3G_NE_USAGE_CATEGORY
      and daa_spec_numb.result1_value = daa_ev_rules.index1_value -- location group 
      and daa_ev_rules.index3_value = 1 -- Voice Event Category
      and daa_chg.index3_value = daa_ev_rules.result1_value -- event type 
      and daa_chg.index4_value = daa_ev_rules.result2_value -- event subtype
      and gl_code.gl_code_id = daa_chg.result9_value
      and rc_event_cat.reference_code = daa_ev_rules.index3_value 
      and rc_event_type.reference_code = daa_ev_rules.result1_value 
      and rc_event_subtype.reference_code = daa_ev_rules.result2_value 
      and rc_uc.reference_code = daa_ev_rules.result3_value 
      and gl_code.gl_code_id = daa_chg.result9_value
      and daa_chg.index2_value = '-1' -- Any
      and daa_spec_numb.index1_value like  '%%%s%%'
      ) num_chg
      left join
      (select rc_est.abbreviation as "Event_Sub_Type", rc_et.abbreviation as "Event_Type", rc_tax.abbreviation as "Tax Class"
      from derived_attribute_array tax_da, reference_code rc_tax, reference_code rc_est, reference_code rc_et
      where tax_da.derived_attribute_id = 12100069 -- dHi3G_TAX_ServiceTaxClass_Mapping
      and rc_tax.reference_type_id = 12100029 --Hi3G_SERVICE_TAX_CLASS
      and rc_est.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_et.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_tax.reference_code = tax_da.result1_value
      and rc_est.reference_code = tax_da.index2_value
      and rc_et.reference_code = tax_da.index1_value
      and tax_da.index4_value = 3936 -- DK 
      ) tax_da 
      on num_chg."Event_Sub_Type" = tax_da."Event_Sub_Type"
      and num_chg."Event_Type" = tax_da."Event_Type"
      left join 
      (
      select split_uc_rt.abbreviation as "UsageCat" , split_cat_rt.abbreviation as "Split Category"
      from derived_attribute_array split_uc_daa, reference_code split_cat_rt, reference_code split_uc_rt
      where split_uc_daa.derived_attribute_id = 14001306 --- dHi3G_3Split_UsageCategory   
      and split_cat_rt.reference_type_id = 14000811 -- HI3G_FENIX_CATEGORY
      and split_uc_rt.reference_type_id =  4100110  --  H3G_NE_USAGE_CATEGORY
      and split_uc_rt.code_label = split_uc_daa.index1_value
      and split_cat_rt.reference_code = split_uc_daa.result1_value 
      ) split_da
      on split_da."UsageCat" = num_chg."Usage Category"
      left join 
      (
      select rc_est.abbreviation as "Event_Sub_Type", rc_et.abbreviation as "Event_Type", rc_sc.abbreviation as "Event Supplier" , rc_chg_met.abbreviation as "Charge Method" 
      from derived_attribute_array ev_sup , reference_code rc_est, reference_code rc_et, reference_code rc_sc, reference_code rc_chg_met
      where ev_sup.derived_attribute_id = 14001405 ---dHi3G_3PS_EventSupplier 
      and ev_sup.index3_value = 3936 -- DK 
      and rc_est.reference_type_id =  4100057 -- H3G_NE_EVENT_SUBTYPE
      and rc_et.reference_type_id =  4100006 -- H3G_NE_EVENT_TYPE
      and rc_sc.reference_type_id =  4100081 -- H3G_SALES_CHANNELS
      and rc_chg_met.reference_type_id  = 14000871 --HI3G_DUAL_CHARGING_METHOD
      and rc_est.reference_code = ev_sup.index2_value
      and rc_et.reference_code = ev_sup.index1_value
      and rc_sc.reference_code = ev_sup.result1_value
      and rc_chg_met.reference_code = ev_sup.result2_value
      ) event_supplier_da
      on event_supplier_da."Event_Sub_Type" = num_chg."Event_Sub_Type"
      order by 3,4,1
        """  % (number_search,number_search)
    cur = br.query(db, sql)
    rep.showCursor(cur)

db.close()
rep.htmlEnd()


