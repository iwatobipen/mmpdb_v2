import glob
import sys
import subprocess
import os

inputdir = "./chembl29/chunkfiles/*.csv"
outputdir = "./chembl29/chunk_fragments"

files = glob.glob(inputdir)

for f in files:
    subprocess.call(['mmpdb', 'fragment',
                              '--min-heavies-per-const-frag', '5',
                              '--min-heavies-total-const-frag', '10',
                              '--max-heavies','50',
                              '--max-rotatable-bonds','15',
                              '--delimiter', 'comma',
                              f,
                              '--output', os.path.join(outputdir, f.split('/')[-1].replace('.csv','.fragments'))
                              ])


