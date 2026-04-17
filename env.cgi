#!/bin/env perl
print "Content-type: text/html\n\n";


printf("%s<br/>", `perl -V`);


$text = `id`;
print $text."<br/>\n";

foreach (sort keys %ENV) {
    printf("%s = %s<br>\n", $_, $ENV{$_});
}





