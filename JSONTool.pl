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
my $inputFile = "./GSE40705_Pancreas_gene.txt"; #Should shift argv rather than hard code
my $compareFile = "./gene_lookup.txt";
my $outputFile = "./filterOutput.txt"; #Give user option to name file?
my $errOut = "./errorLog.txt";
my $count = 1; #Counting iterations to append line number
my @gene; #the array containing the JSON data
my %dataSet; #the hash to hold every row of data
my $temp; #debug

#Prepare file handles
open $fhIn, '<', $inputFile or die "Sorry, I couldn't open '$inputFile': $!\n";
open $fhOut, '>', $outputFile or die "Sorry, I couldn't create another file here\n";

while (my $row = <$fhIn>){
        if($row =~ /^[\d]/){
                $row =~ /([\S]+)\t(\S*)\t(\S*)\t(\S*)\t(\S*)/;
                if ($1 ne ""){#just checking to be sure I caught a valid line
		my $cluster = $1; #creating these variables in a loop is inefficient, but clarifies the code
		my $isoForms = $2; #These variables are holding the values under the actual name in the table that Im reading in.
		my $geneSymbol = $3;
		my $rnaSeh = $4;
		my $riboZero = $5;
		my @gene = ("$count", "$cluster", "$isoForms", "$geneSymbol", "$rnaSeh", "$riboZero"); #storing unused data for clarity
#		print $fhOut "\[$gene[0]\]\t$gene[3]\t$gene[4]\t$gene[5]\n";
#		$dataSet{$geneSymbol}[0] = "$count";
#		$dataSet{$geneSymbol}[1] = "$cluster";
#		$dataSet{$geneSymbol}[2] = "$isoForms";
		$dataSet{$geneSymbol}[0] = "$geneSymbol";
		$dataSet{$geneSymbol}[3] = "$rnaSeh";
		$dataSet{$geneSymbol}[4] = "$riboZero";
		}
		$count++; #only relevant to first file
        }
}
#print "$dataSet{MIR1276}[0]"; #debug
close $fhIn or die "Input close failed."; #now that ive built the hash, close to keep them from getting mixed up with stray inputs
open $fhIn, '<', $compareFile or die "Sorry, I couldn't open '$compareFile': $!\n";
while (my $row = <$fhIn>){
	if($row =~ /^Symbol/){#catch the first line of this file and do nothing
	}elsif($row =~ /^\w/){
		$row =~ /(\w+)\s(\w+)\s(\d*)\s(\d*)/;
		if ( length $4 ){
		#print $fhOut "$1, $2, $3, $4\n";#debug
		$temp = $1;
		$dataSet{$geneSymbol}[1] = "$3";
		$dataSet{$geneSymbol}[2] = "$4";
#		print "$dataSet{$1}[0]";#debug
		}
	}
}
print "$dataSet{MIR1276}[0]" . "\t$dataSet{MIR1276}[1]" . "\t$dataSet{MIR1276}[2]" . "\t$dataSet{MIR1276}[3]" . "\t$dataSet{MIR1276}[4]";
print $temp;
close $fhIn or die "Input close failed.";
close $fhOut or die "Output close failed";
