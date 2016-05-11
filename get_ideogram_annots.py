import sys
import os
import subprocess
import json
from scipy import stats
from argparse import ArgumentParser

parser = ArgumentParser(description="Get Ideogram.js annotations for an SRR")
parser.add_argument("--acc", required=True, help="SRR accession")
args = parser.parse_args()

acc = args.acc
out = acc + "_counts"

os.chdir("counting")

subprocess.call(["python", "counter.py", "--inp", acc, "--out", out])

os.chdir("../formatter")
subprocess.call([
    "python", "formatter.py", "--type", "srr", "--lookup", "gene_lookup_GRCh37.tsv", 
    "--inp", "../counting/" + out + "_norm.tsv", "--out", acc + ".json"
])

