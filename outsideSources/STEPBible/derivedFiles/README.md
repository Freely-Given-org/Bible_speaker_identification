# STEPBible TIPNR derived files

None of the other files in this folder have been hand-created.
They are all produced from their original table/spreadsheet
by a script for convenience of those wanting to use the data.

Any errors in these files will need to be fixed either in the
original table, or in the _loadTIPNR.py_ conversion script.

If you require a slightly different format or pivot of the data,
feel free to contact us and we might be able to help.

## Notes

When multiple people or places have the same name, e.g., _Joshua_,
we label them _Joshua1_, _Joshua2_, etc.
However, if one of the characters is mentioned more often than the others,
we remove that suffix for convenience, so we could end up with _Joshua1_, _Joshua_, _Joshua3_, etc.
Although that has its own inconsistencies, in general
we expect this to be shorter and more helpful to humans than the TIPNR
format using "Name@firstReference".

We also prefix names with 'P' for person, 'Q' for persons/group,
'L' for locations, and 'D' for deities/gods. So the above examples
would end up as _PJoshua1_, _PJoshua_, _PJoshua3_, etc.

Currently all the "Others" are marked with 'D'
even though they're not all deities/gods.
Improving this is work for further investigation.

Prefixing the IDs like that enables us to combine their three datasets
(otherwise a person and a place with the same name would clash)
into the various "...All..." derived files.

There may also be the mid_People.json, mid_Places.json, and mid_Others.json
files produced by the converter script but not checked into GitHub
as they're not of particular use except for debugging.
