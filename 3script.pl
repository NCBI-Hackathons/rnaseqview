#!/usr/bin/perl
use strict;
use warnings;
=begin comment
author bupton
Im trying to turn a .tsv into a filtered .txt
This is an in-work file that Im just uploading to git so other people can see what Im doing
but its not doing what I want.
=end comment
=cut

#Declare variables, because I might like Perl, but I'm not a savage
my $fhIn = undef;
my $fhOut = undef;
#my $clIntake = shift @ARGV;
#	if (defined $clIntake && $clIntake ne '') {
#    	my $inputFile = $clIntake;
#}else{
my $inputFile = "./GSE40705_Pancreas_gene.txt"; #Should shift argv rather than hard code
#}
my $outputFile = "./filterOutput.txt"; #Give user option to name file?
my $errOut = "./errorLog.txt";
my $count = 0; #Counting iterations to append line number
#my $first = shift @argv;

#Prepare file handles
open $fhIn, '<', $inputFile or die "Sorry, I couldn't open '$inputFile': $!\n";
open $fhOut, '>', $outputFile or die "Sorry, I couldn't create another file here\n";

while (my $row = <$fhIn>){
        if($row =~ /^[\d]/){
                $row =~ /([\S]+)\t(\S*)\t(\S*)\t(\S*)\t(\S*)/;
                if ($1 ne ""){
                print $fhOut "\[$count\]\t\[$3,$4,$5\]\n";}
		$count++;
        }
}
close $fhIn or die "Input close failed.";
close $fhOut or die "Output close failed";
