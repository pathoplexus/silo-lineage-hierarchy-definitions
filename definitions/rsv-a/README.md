# RSV-A Lineage Definitions

This repo includes lineage definition files generated from the [rsv-lineages nextclade datasets](https://github.com/rsv-lineages/lineage-designation-A) for rsv-a.

To create a rsv-a lineage definition yaml files for a newer dataset, you can run the python script using:

```
python -m venv venv
source venv/bin/activate
pip install pyyaml
python scripts/generate_hierarchy.py --organism rsv-a --lineage-definition-repo https://github.com/rsv-lineages/lineage-designation-A.git --lineage-definition-path lineages --dataset-tag <tag> 
```