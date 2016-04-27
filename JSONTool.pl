#!/usr/bin/perl
#use strict;
use warnings;
=begin comment
author bupton
This file is still broken, because hackathon, but the project moved on without it. Still, does do some good, fast parsing
and searches through files to match up data and turns it into a JSON format. I stopped right at the end, when it just needed
another layer of data structure, so it would be able to output a five position array of gene data, instead of one big string.
=end comment
=cut
use JSON; #Dependency: This needs a module installed from the CPAN

#Declare variables, because I might like Perl, but I'm not a savage
my $fhIn = undef;
my $fhOut = undef;
my $inputFile = "./GSE40705_Pancreas_gene.txt"; #Should shift argv rather than hard code
my $compareFile = "./gene_lookup_GRCh38.tsv";	#The input for the second file that needs to be compared to line up symbol with insertion
my $outputFile = "./filterOutput.txt"; 		#Give user option to name file?
my $errOut = "./errorLog.txt";			#error logs are only for people that make mistakes
my %dataSet; 					#the hash to hold every row of data
my %chrSet;  					#the hash that holds the compared data, keyed by chromosome
my @index;

#Prepare file handles
open $fhIn, '<', $inputFile or die "Sorry, I couldn't open '$inputFile': $!\n";
open $fhOut, '>', $outputFile or die "Sorry, I couldn't create another file here\n";

while (my $row = <$fhIn>){
        if($row =~ /^[\d]/){
                $row =~ /([\S]+)\t(\S*)\t(\S*)\t(\S*)\t(\S*)\t(\S*)/;
                if ($1 ne ""){		#just checking to be sure I caught a valid line
		my $cluster = $1; 	#creating these variables in a loop is inefficient, but clarifies the code
		my $isoForms = $2; 	#These variables are holding the values under the actual name in the table that Im reading in.
		my $geneSymbol = $3;
		my $rnaSeh = $4;
		my $riboZero = $5;
		my $total = $6;
#		$dataSet{$geneSymbol}[0] = "$count";    #unused data field
#		$dataSet{$geneSymbol}[1] = "$cluster";  #unused data field
#		$dataSet{$geneSymbol}[2] = "$isoForms"; #unused data field
		$dataSet{$geneSymbol}[0] = "$geneSymbol";
		$dataSet{$geneSymbol}[3] = "$rnaSeh";
		$dataSet{$geneSymbol}[4] = "$riboZero";
		}
        }
}
close $fhIn or die "Input close failed."; #now that ive built the hash, close to keep them from getting mixed up with stray inputs
open $fhIn, '<', $compareFile or die "Sorry, I couldn't open '$compareFile': $!\n";
while (my $row = <$fhIn>) #read line by line
{
	if($row =~ /^Symbol/)
	{	#catch the first line of this file and do nothing
	}elsif($row =~ /^\w/)
	{	#use a regex to parse the text and put it into separate variables, like an explode or split method
		$row =~ /(\w+)\t(\w+)\t(\d*)\t(\d*)/;
		if ( length $4 )
		{			#check to see if we have all five data fields populated, take no action if they aren't
		my $chromosome;
		my $geneSymbol = $1; 	#this is local and is not the same as earlier variable, but its the same data field
		$chromosome = "$2";  	#save the value to a local variable for clarity, not efficiency
		$dataSet{$geneSymbol}[1] = "$3"; #start
		$dataSet{$geneSymbol}[2] = "$4"; #length
		if (!exists $chrSet{$chromosome})
		{	 #identifies the hash to the chromosome name 1-19, x, y so we can identify all data to the owning chromosome
			$chrSet{$chromosome} = [];
		}
		my @annot; 		#create local variable to store all data associated with each line from both files
					# This pushes the set of data into the basic array, that can be formatted neatly for JSON output
		push (@annot, ($dataSet{$geneSymbol}[0], $dataSet{$geneSymbol}[1], $dataSet{$geneSymbol}[2], $dataSet{$geneSymbol}[3]));
		push (@annot, ($dataSet{$geneSymbol}[4]));
#		push (@index, (@annot)); #this is a key area to fix, the data structure isn't layered enough and needs another array
		push ($chrSet{$chromosome}, (@annot));
		}
	}
}
my $JSON;
$JSON = JSON->new->allow_nonref; 		#requires JSON module from CPAN archive
my $json_text = $JSON->encode( $chrSet{'1'} ); 	#this should iterate through each chromosome number, needs a for loop
print $fhOut "$json_text\n";
close $fhIn or die "Input close failed.";
close $fhOut or die "Output close failed";
