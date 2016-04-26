
### DEPS

read `deps.txt` to know the tools needed to run. 
You can install all of them from the `bioconda` channel if you have an enviroment running.

An easy way to install conda:

```
  wget http://repo.continuum.io/miniconda/Miniconda-latest-Linux-x86_64.sh
  bash Miniconda-latest-Linux-x86_64.sh -b -p ~/install
```

### HOW TO

`counter.py` script helps to get gene expression stored in ncbi. 

Use `python counter.py` to know how to use it. It accepts SAM/BAM files or SRA accession numbers like `SRR562646`. 

`python $PATH/counter.py --inp SRR562645 --out SRR562645_counts`

This will connect to NCBI and gets the genome reference used for the alignment. In case, there is no alignment information,
it will stop. It will download the gene annotation from NCBI, only GRCh37 and GRCh38 are supported right now.

As well you can use it like: 

`python $PATH/counter.py --inp SRR562645.bam --out SRR562645_counts --gtf GTF_file`

and will use the given GTF to create the count data. GTF needs to have `ID` and `gene` in the attributes field.

### OUTPUTS

It creates 2 outputs: 

* `*.tsv`: with absolute read counts per gene
* `*_norm.tsv`: with counts/kb per gene
