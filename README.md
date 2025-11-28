# Lineage system hierarchy definitions for SILO

In order to enable hierarchical wildcard search for lineage systems (e.g. to select all lineages descendant from mpox clade IIb lineage B.1), SILO needs to know the full lineage tree structure.

This repository contains those definitions for viruses supported by Pathoplexus that have hierarchical lineage systems.

The expected file format is documented here: <https://github.com/GenSpectrum/LAPIS-SILO/blob/main/documentation/lineage_definitions.md>

## Contributing

When making changes to lineage definitions, please ensure that:

- You use the short organism name as used in Pathoplexus urls
- You name each lineage file `lineage.yaml` and put it in a folder with the timestamp of the corresponding Nextclade release. That's because lineage definitions may change over time. The timestamp ensures we can easily track which Nextclade release a lineage definition corresponds to.
- Before you remove or modify a file here, ensure it is not used on Pathoplexus (and Loculus) anymore. We currently reference these definitions in:
  - Pathoplexus values.yaml under `.lineageSystemDefinitions`: <https://github.com/pathoplexus/pathoplexus/blob/main/loculus_values/values.yaml>
  - Loculus values.yaml under `.lineageSystemDefinitions`: <https://github.com/loculus-project/loculus/blob/main/kubernetes/loculus/values.yaml>
- For multi-segmented/multi-pathogen organisms, add an extra folder level for the segment/pathogen short name under the organism, e.g. `cchf/S/2025-09-12--03-01-02Z/lineage.yaml`

It's possible that new Nextclade releases don't change the lineage definitions - in that case we don't need to add a new folder.

Repo layout:

```txt
definitions/
  <organism_short_name>/
    <nextclade_release_timestamp>/
      lineage.yaml
  <multi_segmented_organism_short_name>/
    <segment_or_pathogen_short_name>/
      <nextclade_release_timestamp>/
        lineage.yaml
```
