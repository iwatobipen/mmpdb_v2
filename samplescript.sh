mmpdb fragment --min-heavies-per-const-frag 5 --min-heavies-total-const-frag 10 --max-heavies 50 --max-rotatable-bonds 15 chembl29_30k.smi --output chembl29_30k.fragments.gz
mmpdb index --max-variable-heavies 12 --output chembl29_30k.mmpdb chembl29_30k.fragments.gz


python mmpdblib/fragmentFileToCoreBasedFragmentFile.py --fragment_folder chembl29/chunk_fragments/ --max_lim 100000000

time mmpdb index --max-variable-heavies 10 0.txt -o chembl29.mmpdb

time python mmpdblib/convert_mmpdb_to_flatFile.py --mmpdb chembl29.mmpdb --output_file chembl29_flat.csv


