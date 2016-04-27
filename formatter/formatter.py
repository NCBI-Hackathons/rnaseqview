#!/usr/bin/env python

import sys
import csv
import json
from scipy import stats
from argparse import ArgumentParser

parser = ArgumentParser(description="create formatted json for ideogram viewer")
parser.add_argument("--type", required=True, help="Type gse or srr")
parser.add_argument("--lookup", required=False, help="Looktable file for gene annotations")
parser.add_argument("--inp", required=True, help="input file")
parser.add_argument("--out", required=True, help="output json")
args = parser.parse_args()

genetype_code = {'mRNA': 1, 
                 'ncRNA': 2, 
                 'misc_RNA' : 3, 
                 'precursor_RNA' : 4,
                 'tRNA' : 5,
                 'rRNA' : 6
}

lookup = {}
with open(args.lookup, 'r') as csvfile:
    genereader = csv.reader(csvfile, delimiter='\t')
    for row in genereader:
      gene = row[0]
      chro = row[1]
      start = row[2]
      end = row[3]
      genetype = genetype_code.get(row[4], 7)
      lookup[gene] = "%s %s %s %d" % (chro, start, end, genetype)

json_dict = {}
json_dict['keys'] =  ["name", "start", "length", "expression-level", "gene-type"]
chromosome_list = []
for i in range(0,24):
    chromosome_list.append([]) 

chromosome = {}
annots_list = []
score_list = []
json_dict_chromsome = {}

with open(args.inp, 'r') as csvfile:
    genereader = csv.reader(csvfile, delimiter='\t')
    for row in genereader:
        annot = []
        if args.type == 'gse' :
            gene = row[2]
            expression_level = row[3]
        elif args.type == 'srr':
            gene = row[0]
            expression_level = row[1]
        else:
            sys.stderr.write("Unknown input type. Must be either gse or srr\n")
            sys.exit(1)

        annot.append(gene)
        dlookup = lookup.get(gene)
        if dlookup is None:
           continue
        genelookup = dlookup.split(" ")
        chro = genelookup[0]
        start = int(genelookup[1])
        annot.append(start)
        end = int(genelookup[2]) - start
        annot.append(end)
        score_list.append(float(expression_level))
        annot.append(float(expression_level))
        genetype = int(genelookup[3])
        annot.append(genetype)
        chromosome['annots'] = annot
        if chro == 'X': 
           chromosome_index = 22
        elif chro == 'Y':
           chromosome_index = 23
        else:
           chromosome_index = int(chro) - 1

        chromosome_list[chromosome_index].append(annot)


for list in chromosome_list:
    for annotation in list:
        percentile = stats.percentileofscore(score_list, annotation[3], 'strict')
        annotation[3] = 1 + int(percentile/16)

    chromosome = str(chromosome_list.index(list) + 1)
    if chromosome == "23":
	chromosome = 'X'
    if chromosome == "24":
	chromosome = 'Y'
   
    json_dict_chromosome = {'chr': chromosome, 'annots': list}
    annots_list.append(json_dict_chromosome)

json_dict['annots'] = annots_list

f = open(args.out, 'w')
f.write("%s\n"%json.dumps(json_dict))
