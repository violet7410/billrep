#!/bin/env python
import cgi, cgitb, inspect, os, datetime, string, random, html, re, socket
import treservers
import macro 
import cx_Oracle

#------------------------------------------------------------------------------------------
# Classes
#------------------------------------------------------------------------------------------
class report :
   
    title  = None
    name   = None
    desc   = None
    params = {}
    startTime  = None
    finishTime = None

    

    def __init__(self, name = 'Untitled Report', description = None):
        # Set context type
        print("Content-Type: text/html; charset=UTF-8\r\n")

        # Debugging : Print error on browser
        cgitb.enable(display=1)

        self.title = 'Billing Report - %s' % (name)
        self.name  = name
        self.desc  = description
        self.startTime = datetime.datetime.now()

        # Handling for form parameters
        form = cgi.FieldStorage()
        for k in form.keys() :
            self.params[k] = form.getvalue(k)

    def getReportName(self):
        filename = inspect.stack()[-1][1]
        return os.path.splitext(fileBasename(filename))[0]

    def getParam(self, name) :
        return self.params.get(name)

    def setParam(self, name, value) :
        self.params[name] = value
    
    def printParam(self):
        print(self.params)


    def htmlStart(self, js = [], css = []) :
        html = """
<!DOCTYPE html>
<html>
<header>
    <title>{title}</title>
    <meta http-equiv="content-type" content="text/html" charset="UTF-8" />
    
"""
        # Add default css if file exists
        if os.path.exists('css/default.css') :
            html += "\t<link rel=\"stylesheet\" href=\"css/default.css\"/>\n"

        # Add bootstrap css if exists
        # if os.path.exists('css/bootstrap.css') :
        #     html += "\t<link rel=\"stylesheet\" href=\"css/bootstrap.css\"/>\n"

        # Add default global js if file exists
        if os.path.exists('js/default.js') :
            html += "\t<script type=\"text/javascript\" src=\"js/default.js\"></script>\n"
        
        # Add addtional css
        for f in css :
            html += "\t<link rel='stylesheet' href='css/%s'/>\n" % f
        
        # Add default java script
        defaultJS = self.getReportName() + '.js'
        if os.path.exists('js/' + defaultJS) :
            html += "\t<script src='js/%s'></script>\n" % (defaultJS)

        # Add addtional js
        for f in js :
            html += "\t<script src='js/%s'></script>\n" % f
        
        # Add remaining header
        html += """\
</header>
<body>
<div class='pageHeader'>
<div class='reportName'>{reportName}</div>
<div class='reportDescription'>{description}</div>
</div>
<div class='pageBody'>
"""
        print(html.strip().format(title=self.title, reportName=self.name, description=self.desc))

        return 1

    def htmlEnd(self) :
        self.finishTime = datetime.datetime.now()
        html = """\
<div class='pageFooter'>Generating time %s</div>
</div>
</body>
</html>
        """
        elapsedTime = self.finishTime - self.startTime
        #print(html.strip() % ((elapsedTime.minutes * 60) + elapsedTime.seconds + elapsedTime.microseconds/ 1000000))
        print(html.strip() % (elapsedTime))

    
    def showCursor(self, dbCursor, decorator={}):
        if checkDbCursor(dbCursor) :

            tableId = randomId(10)
            print("<table border=1 class=\"reportAlt\" id=\"%s\">" % (tableId))

            # print header
            print("<tr class='header'>")
            dataTypes   = []
            columnNames = []
            i = 0
            for col in dbCursor.description : 
                columnNames.append(col[0])
                dataTypes.append(col[1])

                isNumber = 0
                
                if col[1].name == 'DB_TYPE_NUMBER' :
                    isNumber = 1
                

                print("\t<th><a class=\"tabSort\" href=\"javascript:;\" onClick=\"sortTable(\'%s\', %s, %s)\">%s</a></th>" % (tableId, i, isNumber, col[0]))

                i = i + 1
            print("</tr>")

            # print row
            i = 0
            for row in dbCursor :
                
                # difference color every alternate row
                # style = 'row1'
                # if i % 2 == 1 :
                #     style = 'row2'
                # print("<tr class='%s table'>" % style)
                print("<tr>")

                colIdx = 0    
                for col in row :
                    # Determine data type
                    colType = dataTypes[colIdx]
                    colName = columnNames[colIdx]
                    style = 'leftAlign'  # Default align left

                    if colName in decorator :
                        # Customize style is detected
                        if 'style' in decorator[colName] :
                            style = decorator[colName]['style']
                    else :
                        # style derived by data type
                        if cx_Oracle.version != '6.3' :
                            if (colType.name == 'DB_TYPE_NUMBER'):
                                style = 'rightAlign'
                        else :
                            if (colType.__name__ == 'NUMBER'):
                                style = 'rightAlign'

                    print("\t<td class=\"%s\">%s</td>" % (style, printValue(col)))
                    colIdx += 1
                    # if type(value) is str :
                    #     print("<td>%s</td>" % (html.escape(value)))
                    # else :    
                    #     print("<td>%s</td>" % (value))
                print("</tr>")
                i+=1
                    
            print("</table>")
        else :
            print("<div style='color : red'>Data not found!!</div>")

    def printError(self, message) :
        print("<div style='color : red'>%s</div>" % (message))

        
# Class handling form
class form :
    id = None
    action = None
    method = None
    inputs = []

    def __init__(self, action, method, id=None):
        # default id if not specified
        if (not id) : id = randomId(10)
        
        self.action = action
        self.method = method
        self.id     = id
    
    def input(self, name = None, label = '', default = None, id = None, type = 'text', mandatory=False) :
        if default is None :  default = ''
        if id is None : id = name

        mandatoryHtml = ''
        style = ''
        if mandatory:
            mandatoryHtml = "required" #<q class='mandatoryField'>*</q>"
            style = 'mandatoryField'

        html = """\
    <tr>
        <td class='rightAlign'>%s</td>
        <td><input type='%s' id='%s' name='%s' value='%s' %s %s></td>
    </tr>
        """ % (label, type, id, name, default, mandatoryHtml, style)
        self.inputs.append(html)

    def select(self, name, label, items = {}, default = None, id = None):
        html = """\
    <tr>
        <td class='rightAlign'>%s</td>
        <td>
            <select id='%s' name='%s'>\n""" % (label, id, name)
               

        # if default value doesn't match any item in item,
        # add 1 blank item
        if (not items.get(default)) :
            html += "\t\t\t\t<option></option>\n"
        
        for k, v in items.items():
            selected = ''
            if default == k :
                selected = 'selected'

            html += "\t\t\t\t<option value='%s' %s>%s</option>\n" % (k, selected, v)

        html += "\t\t\t</select>\n"
        html += "\t\t</td>"
        self.inputs.append(html)

    def render(self):
        print("<form id='%s' action='%s' method='%s'>" % (self.id, self.action, self.method))
        print("<table border=0 class='form'>")
        for x in self.inputs :
            print(x)
        print("</table>")
        print("</form><br/>")
        return


        
#------------------------------------------------------------------------------------------
# Support functions
#------------------------------------------------------------------------------------------
def printValue(value):
    if value is None :
        value = '' # do not print None on html
    else :
        # Escape special characters
        if type(value) is str :
            if re.match(r'^\[.*\|.*\]$', value) :
                # link pattern [.*|.*] found
                m = re.findall(r'\[(.*?)\]', value)
                macros = []
                for i in m:
                    params = i.split('|')
                    #macros.append("<a href='%s'>%s</a>" % (url, text))
                    macros.append(macro.processMacro(params))
                
                if len(macros) > 0 : value = ', '.join(macros)
            else :
                value = html.escape(value)
    return value

def checkDbCursor(cursor) :
    cursor.fetchone()
    if cursor.rowcount > 0 :
        cursor.scroll(mode='first')
        return 1
    else :
        return 0

def fileBasename(fullname):
    return os.path.basename(fullname)

def randomId(length) :
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def now() :
    return datetime.datetime.now()

def getConnection(dsname = '', user = None):
    # Set default user if not specified
    if (not user):
        user = 'dev_test/dev_test1'

    # Get dsn configuration
    instance = treservers.dbServers.get(dsname.lower())
    if (not instance):
        raise(Exception("Data source name '%s' not found" % (dsname)))

    # Construct connection string format <user/pass>@<host><port><service name>
    conStr = "%s@%s:%s/%s" % (user, instance.get('host'), instance.get('port'), instance.get('service'))
    #print(conStr)
    #return cx_Oracle.connect(conStr, encoding="UTF-8")
    #return cx_Oracle.connect(conStr, encoding="WINDOWS-1255")
    return cx_Oracle.connect(conStr)

def getApacheServers() :
    return treservers.apacheServers

def query(db, sql, returnDictionary = 0):
    #print("%s - %s@%s :start<br/>" % (datetime.datetime.now(), db.username, db.dsn))
    cur = db.cursor()
    cur.execute(sql)

    if (returnDictionary):
        cur.rowfactory = lambda *args: dict(zip([d[0] for d in cur.description], args))

    #print("%s - %s@%s :end<br/>" % (datetime.datetime.now(), db.username, db.dsn))
    return cur

# def getDBList():
#     envs = {}
#     for k,v in treservers.dbServers.items():
#         envs[k] = v.get('desc')
#     return envs

def getDBServers():
    envs = {}
    for k,v in treservers.dbServers.items():
        envs[k] = v.get('desc')
    return envs

def isBranchEnv(hostname):
    # Check if hostname is SVBranch or not.
    rs = 0
    if (hostname in treservers.BranchEnv) :
        rs = 1
    return rs

def isTrunkEnv(hostname):
    # Check if hostname is SVBranch or not.
    rs = 0
    if (hostname in treservers.TrunkEnv) :
        rs = 1
    return rs

def getHostnameByAlias(hostAlias):
    rs = None
    if hostAlias in treservers.apacheServers.keys() :
        rs = treservers.apacheServers[hostAlias]
    else :
        raise(Exception("Alias '%s' not found" % (hostAlias)))
    return rs

def getHostname():
    return socket.gethostname().split('.')[0]

def getActiveServers():
    if isBranchEnv(getHostname()):
        # Running on SV11 Branch
        return treservers.activeServers
    else:
        # Non-standard setup
        return ['sandbox', 'svbranch', 'svbt', 'svtrunk', 'svnr']

def getBranchAlias():
    Alias = ""
    for alias, host in treservers.apacheServers.items():
        # if hostname matches with hostname in BranchEnv, we assume that it's Branch environment.
        if host in treservers.BranchEnv :
            Alias = alias
            break
    return Alias

def getTrunkAlias():
    Alias = ""
    for alias, host in treservers.apacheServers.items():
        # if hostname matches with hostname in TrunkEnv, we assume that it's Trunk environment.
        if host in treservers.TrunkEnv :
            Alias = alias
            break
    return Alias

def getActiveServerList():
    env = {}
    activeServe = getActiveServers()
    dbServe = getDBServers()

    for name in activeServe :
        env[name] = dbServe[name]

    return env

#-----------------------------------------------------------------------
# Revision History
#-----------------------------------------------------------------------
# $Log: billrep.py,v $
# Revision 1.20  2023/06/15 14:23:02  xchavon
# Update css
#
# Revision 1.19  2023/04/26 14:23:58  xchavon
# Support sort table
#
# Revision 1.18  2023/03/30 13:41:25  xchavon
# - Add isTrunkEnv()
# - Change way to identify Branch & Trunk env
#
# Revision 1.17  2023/03/21 15:59:02  xchavon
# Add getBranchAlias(), getTrunkAlias()
#
# Revision 1.16  2023/03/21 15:17:16  xchavon
# Removed SV10 envs
#
# Revision 1.15  2023/03/21 14:23:55  xchavon
# Added getHostnameByAlias()
#
# Revision 1.14  2023/03/16 09:18:59  xchavon
# Added isBranchEnv()
#
# Revision 1.13  2023/03/08 12:35:45  xchavon
# - Support decoration on showCursor()
# - Add getActiveServerList()
#
# Revision 1.12  2022/09/13 13:39:57  xadaton
# Change how activeServers are derived
#
# Revision 1.11  2022/04/04 20:02:31  xadaton
# Change shebang for python
#
# Revision 1.10  2022/03/31 15:05:57  xadaton
# Replace getenv('HOST') by gethostname
#
# Revision 1.9  2022/03/31 13:55:53  xadaton
# Put in a temporary fix to getActiveServers so that it returns a different
# list when run on SV11 branch
#
# Revision 1.8  2022/01/13 21:14:03  xchavon
# Update shebang
#
# Revision 1.7  2021/10/20 12:24:33  punkalong001
# update shebang to python3
#
# Revision 1.6  2021/04/27 13:15:42  xchavon
# Add printError()
#
# Revision 1.5  2021/02/02 22:50:31  xchavon
# Add macro clipboard
#
# Revision 1.4  2021/02/01 18:29:37  xchavon
# Support macro
#
# Revision 1.2  2021/01/29 17:54:58  xchavon
# Update web template
#
# Revision 1.1  2021/01/25 22:09:03  xchavon
# Initial billrep
#
#-----------------------------------------------------------------------
        
