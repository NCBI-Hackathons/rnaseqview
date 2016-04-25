import os
import sys

import do

from argparse import ArgumentParser


def get_counts(fn_in, gtf, out):
    if fn_in.endswith("bam") or fn_in.endswith("sam"):
        cmd = "samtools view {fn_in} | htseq-count -i gene_name - {gtf} > {out}"
    do.run(cmd.format(**locals()))

def get_position(gtf, out):
    seen = set()
    with open(out, "w") as out_h:
        with open(gtf) as in_h:
            for line in in_h:
                cols = line.split("\t")
                gene_id = [f.strip().split(" ")[1].replace("\"", "") for f in line.split("\t")[8].split(";") if f.strip().startswith("gene_id")]
                if cols[2] in ["gene", "transcript", "CDS"] and gene_id[0] not in seen:
                    print >>out_h, "%s\t%s\t%s\t%s" % (cols[0], gene_id[0], cols[3], cols[4])
                    seen.add(gene_id[0])

if __name__ == "__main__":
    description = ("Merge multiple files from the same sample to be compatible with bcbio BAM/FASTQ input files")

    parser = ArgumentParser(description="Merge fastq or bam files")
    parser.add_argument("--inp", required=True, help="SRA id or bam file")
    parser.add_argument("--gtf", required=True, help="GTF file")
    parser.add_argument("--out", required=True, help="output dir")
    args = parser.parse_args()
    get_counts(args.inp, args.gtf,"%s.tsv" % args.out)
    get_position(args.gtf, "%s_pos.tsv" % args.out)

