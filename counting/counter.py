import os
import sys
import logging
import subprocess
from contextlib import closing
import xml.etree.ElementTree
from collections import defaultdict
import HTSeq

import do
import mapper

from argparse import ArgumentParser

'''
HOWTO:
 python counter.py --inp SRRXXXXX --out SRRXXXX_counts
TODOs: 
    * detect if paired or single end protocol
'''

logger = logging.getLogger("Main")

def _get_size(gtf):
    """based on http://seqanswers.com/forums/showthread.php?t=4914"""
    gff_file = HTSeq.GFF_Reader( gtf, end_included=True )

    transcripts= {}
    data = defaultdict(dict)
    gene = defaultdict()
    for feature in gff_file:
        if feature.type == "exon":
            transcript_id = feature.attr['ID']
  	    gene[transcript_id] = feature.attr['gene']
            if transcript_id not in transcripts:
                transcripts[ transcript_id ] = list()
            transcripts[ transcript_id ].append( feature )
      
    for transcript_id in sorted( transcripts ):      
        transcript_length = 0
        for exon in transcripts[ transcript_id ]:
            transcript_length += exon.iv.length + 1
  	data[gene[transcript_id]].update({transcript_id: transcript_length})

    for g in data.keys():
	d = data[g]
        for w in sorted(d, key=d.get, reverse=True):
            data[g] = d[w]
            break
    return data


def get_counts(fn_in, gtf, out):
    """Get counts using htseq-count script"""
    if fn_in.endswith("bam") or fn_in.endswith("sam"):
        cmd = "samtools sort -n -O sam {fn_in} -o /dev/stdout | awk '$7==\"=\"' | htseq-count -s no -i gene - {gtf} > {out}"
    elif fn_in.startswith("SRR"):
        cmd = "sam-dump {fn_in} | samtools sort -n -O sam - -o /dev/stdout | awk '$7==\"=\"' | htseq-count -s no -i gene - {gtf} > {out}"
    else:
	raise ValueError("Sample or ID doesn't sound familiar %s" % fn_in)
	
    logger.info(cmd.format(**locals()))
    if not os.path.exists(out):
        do.run(cmd.format(**locals()), log_stdout=True)
    return out

def normalize(counts, gtf):
    """Divide total counts by largest transcript in gene"""
    size = _get_size(gtf)
    out = os.path.basename(counts).replace(".tsv", "_norm.tsv")
    with open(out, "w") as out_h:
	with open(counts) as in_h:
    	    for line in in_h:
                cols = line.strip().split("\t")
                if cols[0] in size:
	    	    rk = float(cols[1])/float(size[cols[0]])*1000
                    print >>out_h, "%s\t%s" % (cols[0], rk)
    return out

def _get_gtf(version):
    """Download GTF if it doesn't exists or return file if GTF given """
    file_out = "%s.gtf" % version
    gz_out = "%s.gz" % file_out
    if os.path.exists(version):
        return version
    if os.path.exists(file_out):
        return file_out
    if version == "GRCh37":
    	mapper.g37_map(file_out)
        # url = "ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_19/gencode.v19.annotation.gtf.gz"
    elif version == "GRCh38":
    	mapper.g37_map(file_out)
        # url = "ftp://ftp.sanger.ac.uk/pub/gencode/Gencode_human/release_24/gencode.v24.annotation.gtf.gz"
    else:
        raise ValueError("Species not supported %s" % version)
    cmd = "wget -O {gz_out} {url} && gunzip {gz_out} && sed -i 's/^chr//' {file_out}"
    if not os.path.exists(file_out):
        do.run(cmd.format(**locals()), log_stdout=True)
    return file_out

def _check_samples(sra_id):
    """Get sample information to check assembly version that will means is aligned """
    if not sra_id.startswith("SRR") or sra_id.endswith("sam"): # need better way to check if sam file or not
	return None
    cl = ("wget -q -O {sra_id} 'http://trace.ncbi.nlm.nih.gov/Traces/sra/sra.cgi?save=efetch&db=sra&rettype=sampleinfo&term={sra_id}'").format(**locals())
    if not os.path.exists(sra_id):
        do.run(cl)
     
    from xml.dom import minidom
    xmldoc = minidom.parse(sra_id)
    itemlist = xmldoc.getElementsByTagName('RUN')
    for s in itemlist:
	if s.attributes["accession"].value == sra_id:
           return s.attributes['assembly'].value
    raise ValueError("Sample not aligned.")

def _set_log():
    """Set logging system to stdout """
    logger = logging.getLogger()
    logger.setLevel(logging.NOTSET)

    logging_handler_out = logging.StreamHandler(sys.stdout)
    logging_handler_out.setLevel(logging.INFO)
    logger.addHandler(logging_handler_out)
    return logger

if __name__ == "__main__":
    description = ("Count gene expression from SRA accession number of SAM/BAM file.")

    parser = ArgumentParser(description="Merge fastq or bam files")
    parser.add_argument("--inp", required=True, help="SRA id or bam file")
    parser.add_argument("--gtf", required=False, help="GTF file")
    parser.add_argument("--out", required=True, help="output dir")
    args = parser.parse_args()
    logger = _set_log()
    gtf = _check_samples(args.inp)
    if not gtf:
	gtf = args.gtf
    if not gtf:
        raise ValueError("Sample without aligment information or none GTF given.")
    logger.info("Using this annotation %s" % gtf)
    if not args.gtf:
        gtf = _get_gtf(gtf)
    elif not os.path.exists(args.gtf):
	logger.info("Assuming version instead of gtf file")
	gtf = _get_gtf(args.gtf)
    logger.info("Using this file annotation %s" % gtf)
    out_fn = get_counts(args.inp, gtf,"%s.tsv" % args.out)
    out_fn = normalize(out_fn, gtf)
    logger.info("Normalized file stored at %s" % out_fn)

