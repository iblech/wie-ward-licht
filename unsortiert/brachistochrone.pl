#!/usr/bin/perl

use warnings;
use strict;

my $C = 100;
my $g = 9.81;

my $y = 1;

my $dt = $ARGV[0] || 0.01;

for(my $x = 0;; $x += $dt) {
    print "$x\t$y\n";
    my $dy = sqrt($C/(2*$g*$y) - 1);
    $y += $dt * $dy;
}
