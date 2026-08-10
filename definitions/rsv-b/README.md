# RSV-B Lineage Definitions

This repo includes lineage definition files generated from the [rsv-lineages nextclade datasets](https://github.com/rsv-lineages/lineage-designation-B) for rsv-b.

To create a rsv-b lineage definition yaml files for a newer dataset, you can run the python script using:

```
python -m venv venv
source venv/bin/activate
pip install pyyaml
python scripts/generate_hierarchy.py --organism rsv-b --lineage-definition-repo https://github.com/rsv-lineages/lineage-designation-B.git --lineage-definition-path lineages --dataset-tag <tag> 
```