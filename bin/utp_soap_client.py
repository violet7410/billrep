#!/bin/env python
#--------------------------------------------------------------------------- #
# File: utp_soap_client.py
# $Revision: 1.7 $
# $Id: utp_soap_client.py,v 1.7 2022/04/15 10:17:35 xadaton Exp $
# $Source: /svw/svbranch/admin/repository/attool/billrep/bin/utp_soap_client.py,v $
#--------------------------------------------------------------------------- #

import os
import sys
import argparse
import socket
import re
import html
import requests
import json

from requests import Session
from zeep.transports import Transport
from zeep import Client
from lxml import etree


def get_wsdl_endpoint(soap_serv):
    '''Returns the endpoint of the SOAP service'''
    soap_serv_dict = { 'inbound': ('http',  'tresoap',  'Inbound'),
                       'gdpr'   : ('https', 'tresoaps', 'gdpr'),
                       'ussd'   : ('http',  'tresoap',  'ussd' ) }
    fqdn = socket.getfqdn()
    proto, serv_pfx, endpt_pfx = soap_serv_dict.get(soap_serv, ('http', 'tresoap', 'Inbound'))
    sock_serv_name = serv_pfx + os.getenv('ATA_SERVICE_SUFFIX')
    port = socket.getservbyname(sock_serv_name, 'tcp')
    endpoint = f'{proto}://{fqdn}:{port}/services/{endpt_pfx}?wsdl'
    return endpoint


def get_pem_file(basename):
    '''Returns a pathname of the pem file given the basename'''
    for dir in [ 'ATA_DATA_SERVER_CONFIG', 'ATAI_REL_SERVER_CONFIG' ]:
        pathname = os.path.join(os.getenv(dir), basename)
        if os.path.exists(pathname):
            return pathname
    return None

def build_param_dict(param):
    '''Returns a dictionary for the -p parameters'''
    param_dict = dict()
    if param:
        for p in param:
            k, v = p.split('=')
            
            ''' for multi-level params, Example: DonationParam/DonationDisplayName=InvoiceText1 '''
            if k.find('/')>0:
                ''' for multi-level params '''
                k1, k2 = k.split('/')
                if k1 in param_dict:
                    if type(param_dict[k1]) is dict:
                        if len(param_dict[k1]) == 0:
                            param_dict[k1] = {k2:v}
                        else:
                            tmpdict = param_dict[k1].copy()
                            newdict = {k2:v}
                            param_dict[k1] = {**tmpdict, **newdict}
                    else:
                        if param_dict[k1] is None:
                            param_dict[k1] = {k2:v}
                        else:
                            sys.exit('the parameter with key '+ k1 + ' is already exists with non dictionary value')
                else:
                    param_dict[k1] = {k2:v}
            else:
                ''' for single-level params '''
                param_dict[k] = v
    return param_dict


def extract_soap_envelope(data):
    '''Returns the SOAP Envelope in data'''
    spos = data.find('<soapenv:Envelope')
    if spos >= 0:
        data = data[spos:]
    epos = data.rfind('</soapenv:Envelope>')
    if epos >= 0:
        data = data[0:epos + len('</soapenv:Envelope>')]
    return data


def debug_key_value(key, value):
    '''Prints out key-value for debugging'''
    if args.debug:
        print(f'[{key}]\n{value}\n')


def print_key_value(key, value):
    '''Prints out key-value, with support for ETH output mode'''
    value = value.strip()
    if args.eth:
        key = html.escape(key)
        value = html.escape(value)
        print(f'<b>[{key}]</b><pre>{value}</pre>')
    else:
        print(f'[{key}]\n{value}\n')


def print_value(value):
    '''Prints out value, with support for ETH output mode'''
    value = value.strip()
    if args.eth:
        value = html.escape(value)
        print(f'<pre>{value}</pre>')
    else:
        print(value)


def replace_placeholders(s, param_dict):
    '''Replaces placeholders in s according to the param_dict'''
    for k, v in param_dict.items():
        s = s.replace(k, v)
    return s


def load_file_with_replacement(filepath, param_dict):
    '''Returns the content of file specified by filepath,
       subject to placeholder replacement specified by param_dict'''
    with open(filepath) as fh:
        data = fh.read()
    data = replace_placeholders(data, param_dict)
    return data


def extract_namespace(data):
    '''Extract namespace specification from data'''
    xmlns_pfx = 'xmlns="'
    spos = data.find(xmlns_pfx)
    if spos > 0:
        data = data[spos+len(xmlns_pfx):]
    else:
        '''If doesnot match with xmlns= then 2nd try with trefault namespace'''
        xmlns_pfx = 'xmlns:trefault="'
        spos = data.find(xmlns_pfx)
        if spos > 0:
            data = data[spos+len(xmlns_pfx):]
    
    epos = data.find('"')
    if epos >= 0:
        data = data[0:epos]
    return data

def recursive_dict(element):
    # Convert element to dict recursively
    return element.tag.split('}')[-1], dict(map(recursive_dict, element)) or element.text.replace('\n','')
 
def eval_xpath(elem, xpath):
    '''Evaluates xpath against elem'''
    # Extract the response body
    elem = elem.find('{http://schemas.xmlsoap.org/soap/envelope/}Body')
    body_text = etree.tostring(elem, pretty_print=True).decode()
    debug_key_value('ResponseBody', body_text)
    # Extract the namespace used for the response
    namespace = extract_namespace(body_text)
    # Evaluate the xpath expression on the response body.
    # Each element in the response must be referred to in the XPath expression
    # with the ns namespace prefix, e.g. ns:CustomerLabel
    result = ''
    edict = {'RESULT':{}}
    for et in elem.xpath(xpath, namespaces={'ns': namespace}):
        if args.json:
            etlist = recursive_dict(et)
            
            if type(etlist[1]) is dict:
                newdict = etlist[1]
            else:
                newdict = {etlist[0]:etlist[1]}
            tmpdict = edict['RESULT'].copy()
            edict['RESULT'] = {**tmpdict, **newdict}
        else:
            if etree.iselement(et):
                for elem in et.iter():
                    result += str(elem.text) + '\n'
            elif et is not None:
                result += str(et) + '\n'
    
    if args.json:
        result = str(json.dumps(edict)) + '\n'

    return result.strip()



def utp_soap_client():
    '''A SOAP client for Regression Testing'''
    # Derive the URL for the WSDL endpoint
    if args.url:
        endpoint = args.url
    else:
        endpoint = get_wsdl_endpoint(args.service)
    debug_key_value('Endpoint', endpoint)

    if args.wsdl:
        os.system(f'python -mzeep --no-verify {endpoint}')
        sys.exit(os.EX_OK)
    elif not args.api:
        print('No --api option specified', file=sys.stderr)
        sys.exit(os.EX_USAGE)

    if args.verbose:
        print('Service Name : ', args.service)
        print('API Name     : ', args.api)
        print('Endpoint     : ', endpoint)
        print('Parameters   : ', args.param)
        print('-' * 80)

    # Create the zeep client
    if endpoint.startswith('https'):
        # For HTTPS, we need a PEM file to validate the connection
        pem_file = get_pem_file('tresoap.pem')
        if pem_file is None:
            raise ValueError('Could not location tresoap.pem')
        session = Session()
        session.verify = pem_file
        transport = Transport(session=session)
        client = Client(endpoint, transport=transport)
    else:
        client = Client(endpoint)

    # Construct the param dictionary 
    param_dict = build_param_dict(args.param)
    #debug_key_value('Parameters', param_dict)

    if args.template:
        # Load the SOAP request from template and perform substitions
        req_txt = load_file_with_replacement(args.template, param_dict)
        debug_key_value('Request', req_txt)
        # Send the request via requests
        url = client.wsdl.location
        debug_key_value('URL', url)
        headers = { 'Content-Type': 'txt/xml', 'SOAPAction': args.api }
        resp = requests.post(url, headers=headers, data=req_txt)
    else:
        # Create the SOAP request from the param dictionary
        req = client.create_message(client.service, args.api, **param_dict)
        req_txt = etree.tostring(req, pretty_print=True).decode()
        debug_key_value('Request', req_txt)
        # Send the request via zeep and request a raw response
        with client.settings(raw_response=True):
            resp = client.service[args.api](**param_dict)

    # Save response text to outfile
    if args.outfile:
        with open(args.outfile, 'w') as f:
            print(resp.text, file=f, end='')

    # Handle status code
    status_code = resp.status_code
    debug_key_value('HTTP Status', str(status_code))

    # Handle response message
    if resp.content is not None:
        resp_soap = extract_soap_envelope(resp.content.decode())
        debug_key_value('Envelope', resp_soap)
        resp_elem = etree.fromstring(resp_soap)
        resp_txt = etree.tostring(resp_elem, pretty_print=True).decode()
        debug_key_value('Response', resp_txt)

    # Handle XPath expression
    if args.xpath and resp_elem is not None:
        xpath_result = eval_xpath(resp_elem, args.xpath)

    # Generate output
    if args.verbose:
        print_key_value('HTTP Status', str(status_code))
        print_key_value('Request', req_txt)
    if not args.xpath or args.verbose:
        print_key_value('Response', resp_txt)
    if args.xpath:
        print(xpath_result.strip(), end='')

    sys.exit(os.EX_OK)


if __name__ == '__main__':
    examples = '''
Examples:
    To call GetFreeUnits on MSISDN:
        utp_soap_client.py -a GetFreeUnits -p Msisdn='00461780000110'

    To call GetFreeUnits on MSISDN on EFFECTIVE_DATE:
        utp_soap_client.py -a GetFreeUnits  -p Msisdn='00461780000110' -p EffectiveDate='2021-11-01T00:00:00'

    To call an Inbound SOAP service based on a request template with variable substition:
        utp_soap_client.py -t soap_tmpl_GetFreeUnits -p MSISDN='00461780000110'

    To call GetFreeUnits on an MSISDN and evaluate an XPath expression on the response:
    (elements in the response must be referenced with the namespace ns:)
        utp_soap_client.py -a GetFreeUnits -p Msisdn='00461780000110' -x '//ns:CustomerLabel'

    To call GetFreeUnits on an MSISDN to retrieve the AllocationId of all FU allocations of main category 107:
        utp_soap_client.py -a GetFreeUnits -p Msisdn='00467790031027' -x //ns:FuFm[ns:MainUsageCategory=107]/ns:AllocationId

    To call the USSD api of the ussd SOAP service to retrieve the account balance of a subscription: 
        utp_soap_client.py -a USSD -s ussd -p ServiceName='467790031010' -p USSDString='*133#' -x '//ns:ResponseMessage' 

    To call the GetAccessToken API of the gdpr SOAP service:
        utp_soap_client.py -a GetAccessToken -s gdpr -p ClientId=singleview -p ClientSecret=wwgXysexR1Xhr2zwrDmlFm1BdrfE1k5l -p Requester=UTP

    To call the USSD api of the ussd SOAP service using a request template with parameter substitution
    and saving the response text in an output file:
        utp_soap_client.py -a USSD -s ussd -t request_template.xml -p MSISDN=00461780000110 -o resp_text.out
    '''
    parser = argparse.ArgumentParser(
                description='UTP SOAP Client',
                formatter_class=argparse.RawDescriptionHelpFormatter,
                epilog=examples)
    parser.add_argument('-a', '--api', help='SOAP API to invoke')
    parser.add_argument('-p', '--param', action='append', help='Parameter(s) as name=value pair(s)')
    parser.add_argument('-s', '--service', default='inbound', help='SOAP service (defaults to inbound)')
    parser.add_argument('-t', '--template', help='File containing template for SOAP request')
    parser.add_argument('-x', '--xpath', help='Return element text specified by XPath expression')
    parser.add_argument('-u', '--url', help='URL of the SOAP WSDL')
    parser.add_argument('-e', '--eth', action='store_true', help='Format output for ETH')
    parser.add_argument('-o', '--outfile', help='Save response text to file')
    parser.add_argument('-w', '--wsdl', action='store_true', help='Print wsdl')
    parser.add_argument('-j', '--json', action='store_true', help='Return out in JSON format')
    parser.add_argument('-v', '--verbose', action='store_true', help='Verbose mode: print request and status code')
    parser.add_argument('-d', '--debug', action='store_true', help='Debug mode')

    global args
    args = parser.parse_args()
    debug_key_value('Arguments', args)
    utp_soap_client()


#----------------------------------------------------------------------------
# $Log: utp_soap_client.py,v $
# Revision 1.7  2022/04/15 10:17:35  xadaton
# Changed python3 to python
#
# Revision 1.6  2022/04/04 19:57:46  xadaton
# Change shebang back to python
#
# Revision 1.5  2021/12/02 16:00:31  punkalong001
# add option --json
# support return multiple values when using XPATH in json format
# support up to 2 levels hash parameters
#
# Revision 1.4  2021/11/26 00:36:59  xadaton
# Fix issue with xpath result
#
# Revision 1.3  2021/11/25 11:06:04  xadaton
# Improved handling of PEM file and HTTPS; do not set the exit status based on http status
#
# Revision 1.2  2021/11/10 11:09:13  xadaton
# Handle case where script is called with no arguments
#
# Revision 1.1  2021/11/08 19:00:23  xadaton
# Add utp_soap_client.py to billrep/bin
#
#----------------------------------------------------------------------------

