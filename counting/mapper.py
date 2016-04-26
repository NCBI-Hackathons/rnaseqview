from contextlib import closing
import subprocess
import logging

import do

logger = logging.getLogger("Main")

def g37_map(out_fn):
    url_map = "http://ftp.ncbi.nlm.nih.gov/genomes/Homo_sapiens/ARCHIVE/ANNOTATION_RELEASE.105/Assembled_chromosomes/chr_accessions_GRCh37.p13"
    url_ann = "http://ftp.ncbi.nlm.nih.gov/genomes/Homo_sapiens/ARCHIVE/ANNOTATION_RELEASE.105/GFF/ref_GRCh37.p13_top_level.gff3.gz"
    g_map(url_map, url_ann, out_fn)

def g38_map(out_fn):
    url_map = "http://ftp.ncbi.nlm.nih.gov/genomes/Homo_sapiens/Assembled_chromosomes/chr_accessions_GRCh38.p2"
    url_ann = "http://ftp.ncbi.nlm.nih.gov/genomes/Homo_sapiens/GFF/ref_GRCh38.p2_top_level.gff3.gz"
    g_map(url_map, url_ann, out_fn)

def g_map(url_map, url_ann, out_fn):
    cl = ("wget -q -O - {url_map}").format(**locals())
    cl = cl.split(" ")
    proc = subprocess.Popen(cl, stdout=subprocess.PIPE)
    d_map = {}
    with closing(proc.stdout) as stdout:
        for line in iter(stdout.readline,''):
            cols = line.split("\t")
	    d_map[cols[1]] = cols[0]
    cl = ("wget -q -O tmp.gz {url_ann}").format(**locals()).split(" ")
    do.run(cl)
    cl = ["zcat" ,"tmp.gz"]
    proc = subprocess.Popen(cl,stdout=subprocess.PIPE)
    logger.info("Creating GTF file %s" % out_fn)
    with closing(proc.stdout) as stdout:
	with open(out_fn, "w") as out_h:
	    for line in iter(stdout.readline,''):
	        cols = line.strip().split("\t")
	        if line.startswith("#") or cols[2] == "region":
		    continue
		if cols[0] in d_map:
	            cols[0] = d_map[cols[0]]
		    # cols[8] = cols[8].replace("=", " ")
 	            print >>out_h, "\t".join(cols)
