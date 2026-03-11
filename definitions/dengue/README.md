# Dengue Lineage Definitions

This repo includes lineage definition files generated from the [v-gen-lab nextclade datasets](https://github.com/nextstrain/nextclade_data/tree/master/data/community/v-gen-lab/dengue) for each dengue subtype and also for all merged dengue subtypes. 

To create dengue lineage definition yaml files for a newer dataset, you can run the python script using:

```
python -m venv venv
source venv/bin/activate
pip install pandas requests
python scripts/generate_denv_lineage_files.py --dataset-tag <tag>
```