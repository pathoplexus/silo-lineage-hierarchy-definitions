# Influenza A Lineage Definitions

This repo includes lineage definition files generated from the [influenza-clade-nomenclature](https://github.com/influenza-clade-nomenclature) for influenza A H3N2 and H1N1pdm as used in the current nextclade datasets.

To create an influenza A lineage definition yaml files for a newer dataset, you can run the python script using:

```
python -m venv venv
source venv/bin/activate
pip install pyyaml
python scripts/generate_hierarchy.py --output-dir definitions/flu --organism H1N1pdm_NA --lineage-definition-repo https://github.com/influenza-clade-nomenclature/seasonal_A-H1N1pdm_NA.git --lineage-definition-path subclades --dataset-tag 2026-03-04--12-40-26Z --add-default-lineages
python scripts/generate_hierarchy.py --output-dir definitions/flu --organism H1N1pdm_HA --lineage-definition-repo https://github.com/influenza-clade-nomenclature/seasonal_A-H1N1pdm_HA.git --lineage-definition-path subclades --dataset-tag 2026-03-04--12-40-26Z --add-default-lineages
python scripts/generate_hierarchy.py --output-dir definitions/flu --organism H3N2_HA --lineage-definition-repo https://github.com/influenza-clade-nomenclature/seasonal_A-H3N2_HA.git --lineage-definition-path subclades --dataset-tag 2026-03-04--12-40-26Z --add-default-lineages
python scripts/generate_hierarchy.py --output-dir definitions/flu --organism H3N2_NA --lineage-definition-repo https://github.com/influenza-clade-nomenclature/seasonal_A-H3N2_NA.git --lineage-definition-path subclades --dataset-tag 2026-03-04--12-40-26Z --add-default-lineages
```

For H5N1 I use a custom script to parse the tree.json inside the nextclade dataset and create a lineage definition yaml.

I download the tree.json first and then run the script using :

```
curl -L -o tree.json \
https://raw.githubusercontent.com/nextstrain/nextclade_data/master/data/community/moncla-lab/iav-h5/ha/all-clades/tree.json
python scripts/extract_clade_hierarchy.py --output-dir definitions/flu/H5 --tree tree.json --dataset-tag 2026-03-04--12-40-26Z
```