#!/bin/env python
"""getxml.py - Retrieve invoice contents as XML or PDF"""

import os,sys
import logging
import argparse
import cx_Oracle
import subprocess
import re
import socket
import time
import lxml.etree as ET

def collect_inv_from_file(filename):
    """Collect invoice ids/numbers from a file specified by filename"""
    try:
        with open(filename, 'r') as f:
            lines = [ line.rstrip() for line in f ]
        return lines
    except IOError as e:
        print('I/O error {0}: {1}: {2}'.format(e.errno, e.strerror, filename))


def collect_inv_from_account(con, acc):
    """Collect latest invoice from an account"""
    try:
        sql = '''select i.invoice_id, i.last_modified, i.effective_date, i.customer_invoice_str
                 from invoice i
                 where (   i.account_id = to_number(:ACC)
                        or i.account_id = (select account_id from account where account_name = :ACC)
                 ) and i.image_generated_ind_code = 1
                 order by i.last_modified desc'''
        cur = con.cursor()
        cur.execute(sql, { 'ACC': acc })
        row = cur.fetchone()
        if row:
            return [ row[0] ]
    except cx_Oracle.DatabaseError as e:
        err = e.args[0]
        print('DatabaseError {0}: {1}'.format(err.code, err.message))


def collect_inv_from_where(con, where):
    """Collect invoice ids from a where clause on the invoice table"""
    try:
        sql = 'select i.invoice_id from invoice i where (' + where + ')'
        cur = con.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        cur.close()
        return [ row[0] for row in rows ]
    except cx_Oracle.DatabaseError as e:
        err = e.args[0]
        print('DatabaseError {0}: {1}'.format(err.code, err.message))


def inv_nr_to_id(con, nr):
    """Convert an invoice number to id"""
    try:
        sql = 'select invoice_id from invoice where customer_invoice_str = :INV'
        if not hasattr(inv_nr_to_id, 'cur'):
            inv_nr_to_id.cur = con.cursor()
        inv_nr_to_id.cur.execute(sql, { 'INV': nr })
        row = inv_nr_to_id.cur.fetchone()
        return row[0] if row else None
    except cx_Oracle.DatabaseError as e:
        err = e.args[0]
        print('DatabaseError {0}: {1}'.format(err.code, err.message))


def inv_to_id(con, nr):
    """Verify an invoice id"""
    try:
        sql = 'select invoice_id from invoice where invoice_id = :INV'
        if not hasattr(inv_to_id, 'cur'):
            inv_to_id.cur = con.cursor()
        inv_to_id.cur.execute(sql, { 'INV': nr })
        row = inv_to_id.cur.fetchone()
        return row[0] if row else None
    except cx_Oracle.DatabaseError as e:
        err = e.args[0]
        print('DatabaseError {0}: {1}'.format(err.code, err.message))


def convert_inv_to_id(con, inv_list):
    """Convert a list of invoice ids/numbers to invoice ids"""

    # Convert invoice to invoice_id
    inv_ids = []
    for x in inv_list:
        if args.invid:
            # Confirm invoice id
            inv_id = inv_to_id(con, x)
        else:
            # Try to look up first as an invoice number
            # then as an invoice id
            inv_id = inv_nr_to_id(con, x)
            if not inv_id:
                inv_id = inv_to_id(con, x)

        if inv_id:
            inv_ids.append(inv_id)

    return inv_ids


def get_inv_info(con, inv_id):
    """Retrieve (invoice_id, invoice_number, filename) for an invoice identified by its invoice id"""

    try:
        sql = '''select iv.invoice_id
                    , iv.customer_invoice_str
                    , iv.invoice_type_id
                    , ac.account_name
                    , nvl(substr(iv.general_9, 1, instr(iv.general_9, '|')-1), to_char(iv.issue_date, 'yyyymmdd')) issue_date
                from invoice iv, account ac
                where iv.invoice_id = :INV
                and iv.account_id = ac.account_id'''

        # Use function attribute as a static variable
        # to cache a cusror
        if not hasattr(get_inv_info, 'cur'):
            get_inv_info.cur = con.cursor()

        get_inv_info.cur.execute(sql, { 'INV': inv_id })
        row = get_inv_info.cur.fetchone()

        # filename = <account_nr>_<issue_date>_<invoice_id>.xml
        filename = row[3] + '_' + row[4] + '_' + str(row[0]) + '.xml'

        return (row[0], row[1], filename)

    except cx_Oracle.DatabaseError as e:
        err = e.args[0]
        print('DatabaseError {0}: {1}'.format(err.code, err.message))


def get_inv_blob(con, inv_id):
    """Retrieve invoice contents from the database"""

    try:
        sql = '''select invoice_contents
                from invoice_contents
                where invoice_id = :INV
                order by seqnr'''

        # Use function attribute as a static variable
        # to cache a cusror
        if not hasattr(get_inv_blob, 'cur'):
            get_inv_blob.cur = con.cursor()

        get_inv_blob.cur.execute(sql, { 'INV': inv_id })
        (blob,) = get_inv_blob.cur.fetchone()
        return blob.read()

    except cx_Oracle.DatabaseError as e:
        err = e.args[0]
        print('DatabaseError {0}: {1}'.format(err.code, err.message))
    except TypeError as e:
        # This exception is thrown by get_inv_blob.cur.fetchone()
        # if the invoice_content blob has been purged
        print('invoice contents for invoice id {0} is not available'.format(inv_id))


def write_blob(filename, inv_blob):
    """Write an invoice content blob to a file and gunzip the file"""
    filename += '.gz'
    try:
        with open(filename, 'wb') as f:
            f.write(inv_blob)
        subprocess.check_call(['gunzip', '-f', filename])
    except IOError as e:
        print('I/O error {0}: {1}: {2}'.format(e.errno, e.strerror, filename))


def convert_inv_xml(infile, outfile, filename):
    """Convert an invoice XML to Streamserve format"""
    cust_type = 'SE'
    account_nr = ''
    issue_date = ''
    inv_nr = ''
    for line in infile:
        if re.search(r'<\?xml |<Billrun>|</Billrun>', line):
            continue
        elif re.search(r'<Cust_Acct_Type>', line):
            if re.search(r'\bDK\b', line):
                cust_type = 'DK'
        elif re.search(r'<Cust_Output_Method>', line):
            line = '<Cust_Output_Method><![CDATA[PDFOUT]]></Cust_Output_Method>\r\n'
        elif re.search(r'<Inv_Vat_Spec>', line) and args.vat:
            line = '<Inv_Vat_Spec><![CDATA[Yes]]></Inv_Vat_Spec>\r\n'
        elif re.search(r'<Inv_Sum_Det>', line) and args.cdr:
            line = '<Inv_Sum_Det><![CDATA[Yes]]></Inv_Sum_Det>\r\n'
        elif args.xml:
            if re.search(r'<Cust_Account_Nr>', line):
                logging.debug(line)
                m = re.search(r'\[CDATA\[(\d+)\]\]', line)
                if m:
                    account_nr = m.group(1)
            if re.search(r'<Inv_Issue_Date>', line):
                logging.debug(line)
                m = re.search(r'\[CDATA\[(\d+)[.-](\d+)[.-](\d+)\]\]', line)
                if m:
                    if len(m.group(1)) == 4:
                        # Inv_Issue_Date is yyyy-mm-dd
                        issue_date = m.group(1) + m.group(2) + m.group(3)
                    else:
                        # Inv_Issue_Date is dd.mm.yyyy
                        issue_date = m.group(3) + m.group(2) + m.group(1)
            if re.search(r'<Invoice_Number>', line):
                logging.debug(line)
                m = re.search(r'\[CDATA\[(\d+)\]\]', line)
                if m:
                    inv_nr = m.group(1)

        outfile.write(line)

    # If the xml filename begins with 3SE or 3DK, we assume that
    # the filename is in correct streamserve format, other we try
    # to generate filename based on information in the XML
    #
    if re.match(r'3(DK|SE)', filename):
        (root, ext) = os.path.splitext(filename)
        ss_filename = root + '_ss' + ext
    elif account_nr and issue_date and inv_nr:
        ss_filename = '3' + cust_type + '_' + account_nr + '_' + issue_date + '_' + inv_nr + '.xml'
    else:
        ss_filename = '3' + cust_type + '_' + filename

    logging.debug('convert_inv_xml> ss_filename=%s', ss_filename)
    return ss_filename


def convert_to_ss_xml(filename):
    """Convert an invoice XML to Streamserve format and return the name
       of the temporary file containing the Streamserve XML"""

    tmpfile = filename + '.tmp'
    with open(filename, 'r') as infile:
        with open(tmpfile, 'w') as outfile:
            outfile.write('<?xml version="1.0" encoding="ISO-8859-1"?>\r\n')
            outfile.write('<Billrun>\r\n')
            ss_filename = convert_inv_xml(infile, outfile, filename)
            outfile.write('</Billrun>\r\n')

    # Rename tmpfile to a filename expected by Streamserve
    os.rename(tmpfile, ss_filename)

    return ss_filename


def get_xml_revision(filename):
    """Get country and XML_Revision"""
    with open(filename, 'r') as infile:
        for line in infile:
            m = re.search(r'<Fin_Doc XML_Revision=\'([\d.]+)\'>', line)
            if m:
                xml_rev = m.group(1)
            m = re.search(r'<H3GInfo Swe_Owning_Company_Code=\'(\d+)\'.* XML_Revision=\'([\d.]+)\'', line)
            if m:
                country = m.group(1)
                xml_rev = m.group(2)
                return ( country, xml_rev )
            m = re.search(r'<H3GInfo Swe_Owning_Company_Code=\'(\d+)\'', line)
            if m:
                country = m.group(1)
                return ( country, xml_rev )
    return ( '3917', '1.0' )


def get_streamserve_hostport(layout):
    """Determine the streamserve ssh host and port number for the environment"""

    # renderer:  env_name => [ streamserve_hostpost, exstream_hostport ]
    renderer = { 'SX_NR': [ # Streamserve/Extream NR
                              ('appadm@x12227azz.nextrel.tre.se', 22),
                              ('appadm@x18197azz.nextrel.tre.se', 22) ],
                 'SX_BT': [ # Streamserve/Extream BT
                              ('appadm@x12230tzz.testaccess.net', 22),
                              ('appadm@x18161tzz.test.tre.se', 22) ],
                 'SX_TN': [ # Streamserve BT via Tunnel/Extream BT
                              ('appadm@localhost', 53022),
                              ('appadm@x18161tzz.test.tre.se', 22) ],
                 'SX_NA': [ # Streamserve/Extream Not Available
                              ('NA', 0),
                              ('NA', 0) ]
                      }
    hostport_dict = { 'x13363azz': renderer['SX_NR'],   # PERF
                      'x13221azz': renderer['SX_NR'],   # NR
                      'x13213tzz': renderer['SX_BT'],   # BT
                      'x13144dzz': renderer['SX_TN'],   # TRUNK
                      'x13205dzz': renderer['SX_TN'],   # BRANCH
                      'x18177dzz': renderer['SX_BT'],   # SANDBOX SV11
                      'x18291dzz': renderer['SX_BT'],   # BRANCH SV11
                      'x18293tzz': renderer['SX_BT'],   # BT SV11
                      'x18292dzz': renderer['SX_NR'],   # Trunk SV11
                      'x18294azz': renderer['SX_NR'],   # NR SV11
                      'x18416aaz': renderer['SX_NR'],   # PERF SV11
                      'NA'       : renderer['SX_NA']    # Not available
                    }
    hostname = socket.gethostname().split('.')[0]
    hostport = hostport_dict.get(hostname, hostport_dict['NA'])
    if layout == 'exstream':
        return hostport[1]
    else:   # streamserve
        return hostport[0]


def get_streamserve_dirs(filename, layout):
    """Determine the streamserve input and output directories"""

    country = filename[1:3].lower()
    cdir = country

    if args.old:
        ss_base = '/opt/streamserve/qnas'
    else:
        if layout == 'exstream':
            ss_base = '/opt/exstream/qnas/exstream'
            cdir = country + 'st'
        else:
            ss_base = '/opt/streamserve/qnas'

    dirs = ['in', 'out']
    return [os.path.join(ss_base, cdir, d) for d in dirs]


def get_filename_wildcard(filename):
    """Return a wildcard that can be used to identify the invoice PDF"""
    m = re.search(r'^(...)_(\d+)_(\d+)_(\d+)', filename)
    if m:
        return m.group(1) + '*' + m.group(2) + '*' + m.group(3) + '*' + m.group(4) + '*'
    m = re.search(r'^(...)_(\d+)_(\d+)', filename)
    if m:
        return m.group(1) + '*' + m.group(2) + '*' + m.group(3) + '*'
    return filename


def remote_ls(host, port, path, filename):
    """Execute ls remotely.
       Note that the components of path and filename cannot contain spaces"""
    pathname = os.path.join(path, filename)
    logging.debug('remote_ls> pathname=%s', pathname)
    logging.debug('remote_ls> /usr/bin/ssh -p=%d %s /bin/ls %s', port, host, pathname)
    proc = subprocess.Popen(['/usr/bin/ssh', '-p', str(port), host, '/bin/ls ' + pathname],
                            stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    output = proc.communicate()
    return (proc.poll(), output[0].rstrip().decode('utf-8'))


def remote_rm(host, port, path, filename):
    """Execute rm -f remotely.
       Note that the components of path and filename cannot contain spaces"""
    pathname = os.path.join(path, filename)
    logging.debug('remote_rm> pathname=%s', pathname)
    return subprocess.call(['/usr/bin/ssh', '-p', str(port), host, '/bin/rm -f ' + pathname])


def remote_put(host, port, path, filename):
    remote_pathname = host + ':' + path
    logging.debug('remote_put> filename=%s, remote_pathname=%s', filename, remote_pathname)
    logging.debug('remote_put> /usr/bin/scp -q -P %d %s %s', port, filename, remote_pathname)
    return subprocess.call(['/usr/bin/scp', '-q', '-P', str(port), filename, remote_pathname])


def remote_get(host, port, path, filename):
    remote_pathname = host + ':' + os.path.join(path, filename)
    logging.debug('remote_get> remote_pathname=%s', remote_pathname)
    logging.debug('remote_get> /usr/bin/scp -q -P %d %s .', port, remote_pathname)
    return subprocess.call(['/usr/bin/scp', '-q', '-P', str(port), remote_pathname, '.'])


def get_pdf_from_ss(filename):
    """Delivery the invoice XML to Streamserve for processing and retrieve
       the resulting PDF"""
    logging.debug('get_pdf_from_ss> xml=%s', filename)

    (country, xml_rev) = get_xml_revision(filename)
    layout = 'exstream'
    logging.debug('get_pdf_from_ss> country=%s, xml_rev=%s, layout=%s', country, xml_rev, layout)

    (host, port) = get_streamserve_hostport(layout)
    logging.debug('get_pdf_from_ss> host=%s, port=%d', host, port)
    if not host:
        print('Streamserve is not available')
        return

    (indir, outdir) = get_streamserve_dirs(filename, layout)
    logging.debug('get_pdf_from_ss> indir=%s, outdir=%s', indir, outdir)

    wildcard = get_filename_wildcard(filename)
    logging.debug('get_pdf_from_ss> wildcard=%s', wildcard)

    # Ensure there are no left-over files from previous runs
    remote_rm(host, port, outdir, wildcard)

    # After sending the XML to the streamserve input directory,
    # we poll the streamserve output directory for a file matching
    # the output PDF wildcard name.  If such a file is found, we
    # retrieve the PDF with a get.
    # Currently, we wait up to 30 seconds before timing out.
    remote_put(host, port, indir, filename)
    max_tries = 60
    ntries = 0
    while True:
        (rv, pdf_pathname) = remote_ls(host, port, outdir, wildcard)
        if rv == 0:
            # A file matching the output PDF wildcard is found
            pdf_basename = os.path.basename(pdf_pathname)
            logging.debug('get_pdf_from_ss: Getting PDF %s', pdf_basename)
            remote_get(host, port, outdir, pdf_basename)
            # If there has been previous retries, print out a newline
            # on stderr to end the line of dots before print out
            # the name of the PDF file
            if ntries > 1: print('', file=sys.stderr)
            print('PDF:', pdf_basename)
            return pdf_basename
        else:
            ntries += 1

        # Print out a line of dots on stderr while waiting for Streamserve
        if ntries < max_tries:
            print('.', end='', file=sys.stderr)
            time.sleep(1)
        else:
            print('Timed out waiting for Streamserve')
            return


def generate_pdf(xml_filename):
    """Generate PDF from XML with Streamserve"""

    if args.nopdf:
        return

    # Convert XML to streamserve format and then obtain the PDF from Streamserve
    ss_filename = convert_to_ss_xml(xml_filename)
    logging.debug('generate_pdf> ss_filename=%s', ss_filename)
    pdf_filename = get_pdf_from_ss(ss_filename)
    logging.debug('generate_pdf> pdf_filename=%s', pdf_filename)

    # Remove the temporary streamserve XML if we not not in debug mode
    if not args.debug:
        os.remove(ss_filename)


def eval_print_et_expr(filename):
    """Evaluate an ElementTree expression specified as the argument to
       the --et option, on the XML contained in filename, and print out
       the result"""

    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag != 'Fin_Doc':
        root = root.find('Fin_Doc')
    if root.tag != 'Fin_Doc':
        print('Unable to locate Fin_Doc element in XML')
        return
    et = eval(args.et)
    if ET.iselement(et):
        # Print out the result as is without adding trailing newline
        print(ET.tostring(et), end='')
    elif et is not None:
        print(str(et))
    else:
        print('<None>')


def eval_print_xpath_elem_text(filename):
    """Evaluate an XPath expression specified as the argument to the
       --xp option, on the XML contained in filename, and print out
       the associated element text"""

    tree = ET.parse(filename)
    root = tree.getroot()
    if root.tag != 'Fin_Doc':
        root = root.find('Fin_Doc')
    if root.tag != 'Fin_Doc':
        print('Unable to locate Fin_Doc element in XML')
        return

    for et in root.xpath(args.xp):
        if ET.iselement(et):
            for elem in et.iter():
                print(elem.text)
        elif et is not None:
            print(str(et))
        else:
            print('<None>')


def get_invoice(con, inv_id):
    """Retrieve the contents of one invoice"""

    (inv_id, inv_nr, filename) = get_inv_info(con, inv_id)
    logging.debug('get_invoice> inv_id=%d, inv_nr=%s, filename=%s', inv_id, inv_nr, filename)

    inv_blob = get_inv_blob(con, inv_id)
    if not inv_blob:
        logging.debug('get_invoice> blob not found')
        return

    write_blob(filename, inv_blob)

    if args.et:
        eval_print_et_expr(filename)
        # Remove the XML since we are only interested in the ElementTree evaluation
        os.remove(filename)
    elif args.xp:
        eval_print_xpath_elem_text(filename)
        # Remove the XML since we are only interested in the XPath evaluation
        os.remove(filename)
    else:
        # Generate PDF and keep the invoice XML
        print('XML:', filename)
        generate_pdf(filename)


def getxml(con):
    """Retrieve invoice contents as specified by the command"""

    if args.where:
        # Collect invoice_ids from where clause
        inv_ids = collect_inv_from_where(con, args.where)

    else:
        if args.acc:
            # Collect latest invoice from account
            inv_ids = collect_inv_from_account(con, args.acc)
        elif args.file:
            # Collect invs from file
            inv_list = collect_inv_from_file(args.file)
            inv_ids = convert_inv_to_id(con, inv_list)
        else:
            # Collect invs from command line
            inv_list = args.inv
            inv_ids = convert_inv_to_id(con, inv_list)

    logging.debug('getxml> invoice_ids: %s', inv_ids)
    for id in inv_ids:
        get_invoice(con, id)


def getxml_db():
    """Open a database connection and then call getxml"""
    con = None
    try:
        userpass = args.userpass if args.userpass else os.environ['ATADBACONNECT']
        with cx_Oracle.connect(userpass) as con:
            getxml(con)

    except cx_Oracle.DatabaseError as e:
        err = e.args[0]
        print('DatabaseError {0}: {1}'.format(err.code, err.message))
    except Exception as e:
        logging.exception('Exception in getxml')


def process_xml_files():
    """Process XML files specified on the command line"""
    for f in args.inv:
        if args.et:
            eval_print_et_expr(f)
        elif args.xp:
            eval_print_xpath_elem_text(f)
        else:
            generate_pdf(f)


def main():
    examples = '''\
examples:
  To retrieve the invoice XML and PDF by invoice number:
    getxml.py 5123927120

  To retrieve the invoice XML only by invoice number:
    getxml.py --nopdf 5123927120

  To retrieve the invoice XML and PDF by invoice Id:
    getxml.py -i 16217052

  To retrieve the invoice XML and PDF of the latest invoice on an account
    getxml.py -a 2217084439

  To generate the invoice PDF from the invoice XML:
    getxml.py --xml 3SE_10000010067_20160717_16217052.xml

  To print the text associated with elements identified by an XPath expression on the invoice XML:
    getxml.py --xp ".//InvoiceInfo/Inv_Issue_Date" 16685110
    getxml.py --xp ".//InvoiceInfo/ST[@USAGE_CATEGORY='InvoiceUsageTotal']/ST_ST/Swe_ST_ST_Amt_w_VAT" 16685110
    getxml.py --xp ".//Prod_Dt[Prod_Name='Fri Tale - 3Deling']/PkPr_Dt_Chrg[PkPr_Dt_Chrg_NewUpdated='NewAdvance']/Swe_PkPr_Dt_Chrg_Amt_w_VAT" --xml 3DK_2209990304_20161217_16685110.xml

  To evaluate an elementtree expression on the invoice XML:
    getxml.py --et "root.findall('.//Acct_OO_Dt')[0].find('Acct_OO_Dt_Name')" 5123927120

'''
    parser = argparse.ArgumentParser(
                formatter_class=argparse.RawDescriptionHelpFormatter,
                description='Retrieve invoice contents as XML or PDF',
                epilog=examples)
    parser.add_argument('-u', '--userpass', metavar='userpass',  help='username/password')
    parser.add_argument('-d', '--debug',    action='store_true', help='debug mode')
    parser.add_argument('-i', '--invid',    action='store_true', help='invoice id specified')
    parser.add_argument('-f', '--file',     metavar='filename',  help='file with invoice ids/numbers')
    parser.add_argument('-a', '--acc',      metavar='account',   help='latest invoice on an account')
    parser.add_argument('-w', '--where',    metavar='where',     help='where clause on invoice (alias i)')
    parser.add_argument('-x', '--xml',      action='store_true', help='invoice XML as input')
    parser.add_argument('-n', '--nopdf',    action='store_true', help='do not generate invoice pdf')
    parser.add_argument('-v', '--vat',      action='store_true', help='include VAT specification')
    parser.add_argument('-c', '--cdr',      action='store_true', help='include call detail records')
    parser.add_argument('-p', '--xp',       metavar="xpath",     help='print element text identified by XPath expression')
    parser.add_argument('-e', '--et',       metavar='expr',      help='evaluate and print elementtree expression on Fin_Doc')
    parser.add_argument('-o', '--old',      action='store_true', help='old DK invoice layout')
    parser.add_argument('inv', nargs='*', help='invoice id or invoice number')

    global args
    args = parser.parse_args()

    # Set logging level to DEBUG when call with -d option
    log_level = logging.DEBUG if args.debug else logging.INFO
    logging.basicConfig(level=log_level)

    logging.debug('main> args=%s', args)

    # One of -f, -w, and inv must be provided
    if not args.file and not args.acc and not args.where and not args.inv:
        parser.print_help()
        sys.exit(2)

    # Detect xml file as input
    if len(args.inv) > 0 and re.search(r'\.xml$', args.inv[0], re.IGNORECASE):
        args.xml = True

    if args.xml:
        process_xml_files()
    else:
        # Retrieve XML from database
        getxml_db()


if __name__ == '__main__':
    main()

#------------------------------------------------------------------------------
# CHANGE LOG
#
# 2016-05-23  A.Tong
#   * Initial version
#
# 2016-06-17  A.Tong
#   * Improved XML handling
#
# 2016-06-28  A.Tong
#   * Detect XML input
#
# 2016-07-04  A.Tong
#   * Handle exception when the invoice_content blob is not available
#   * Generate pdf by default; Added --nopdf option
#
# 2016-07-19  A.Tong
#   * Added --et option to evaluate and print elementtree expression
#
# 2016-12-17  A.Tong
#   * Added --xp option to evaluate and print texts associated with an xpath expression
#
# 2017-03-28  A.Tong
#   * Added --old option for old DK invoice layout
#
# 2017-04-13  A.Tong
#   * Replaced ElementTree by lxml
#
# 2021-05-04  A.Tong
#   * Add support for exstream
#------------------------------------------------------------------------------
