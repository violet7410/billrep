#!/bin/env perl
print "Content-type: text/html\n\n";

printf("%s<br/>", `perl -V`);
printf("%s<br/>", `which perl`);

foreach (sort keys %ENV) {
    printf("%s = %s<br>\n", $_, $ENV{$_});
}
