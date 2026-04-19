# Python CGI Web Report #

For billing team internal use only. 

## Installation ##
### 1. Environment Setup ###
* Http Server setup

```dnf install httpd```

### 2. httpd setup ###

1. Add directory to /etc/httpd/conf.d

```vi /etc/httpd/conf.d/billrep.conf```

then add following settings 

```
# Bill Reports CGI

Alias       /billrep/css "/svw/svbranch/imp/attool/billrep/css"
Alias       /billrep/js  "/svw/svbranch/imp/attool/billrep/js"
ScriptAlias /billrep     "/svw/svbranch/imp/attool/billrep"
<Directory "/svw/svbranch/imp/attool/billrep/">
    Options +ExecCGI
    AllowOverride None
    Require all granted
</Directory>

SetEnv BILL_REP_HOME /svw/svbranch/imp/attool/billrep
SetEnv PYTHONPATH    /svw/svbranch/imp/attool/billrep/lib
```

2. Restart httpd

```
systemctl restart httpd
```

