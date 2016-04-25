import os
import sys
import logging

import do

from argparse import ArgumentParser

'''
TODOs: 
    * detect if paired or single end protocol
    * get genome version: supported 37 and 38 for now
    all those probably through http query to sra.cgi
    wget -O SRP005601_metadata.csv 'http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db=sra&rettype=runinfo&term=SRP005601'
'''

def get_counts(fn_in, gtf, out):
    if fn_in.endswith("bam") or fn_in.endswith("sam"):
        cmd = "samtools sort -n -O sam {fn_in} -o /dev/stdout | awk '$7==\"=\"' | htseq-count -i gene_name - {gtf} > {out}"
    do.run(cmd.format(**locals()), log_stdout=True)

def get_position(gtf, out):
    seen = set()
    with open(out, "w") as out_h:
        with open(gtf) as in_h:
            for line in in_h:
                cols = line.split("\t")
                gene_id = [f.strip().split(" ")[1].replace("\"", "") for f in line.split("\t")[8].split(";") if f.strip().startswith("gene_name")]
                if cols[2] in ["gene", "transcript", "CDS"] and gene_id[0] not in seen:
                    print >>out_h, "%s\t%s\t%s\t%s" % (cols[0], gene_id[0], cols[3], cols[4])
                    seen.add(gene_id[0])

def _get_gtf(version):
    if version == "GRCh37":
        url = "ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz"
    elif version == "GRCh38":
        url = "ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_24/gencode.v24.annotation.gtf.gz"

    file_out = "%s.gtf" % version
    gz_out = "%s.gz" % file_out
    cmd = "wget -O {gz_out} {url} && gunzip {gz_out} && sed -i 's/^chr//' {file_out}"
    if not os.path.exists(file_out):
        do.run(cmd.format(**locals()), log_stdout=True)
    return file_out

def _set_log():
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    logging_handler_out = logging.StreamHandler(sys.stdout)
    logging_handler_out.setLevel(logging.INFO)
    logger.addHandler(logging_handler_out)


if __name__ == "__main__":
    description = ("Merge multiple files from the same sample to be compatible with bcbio BAM/FASTQ input files")

    parser = ArgumentParser(description="Merge fastq or bam files")
    parser.add_argument("--inp", required=True, help="SRA id or bam file")
    parser.add_argument("--gtf", required=True, help="GTF file")
    parser.add_argument("--out", required=True, help="output dir")
    args = parser.parse_args()
    _set_log()
    gtf = _get_gtf(args.gtf)
    get_counts(args.inp, gtf,"%s.tsv" % args.out)
    get_position(gtf, "%s_pos.tsv" % args.out)

