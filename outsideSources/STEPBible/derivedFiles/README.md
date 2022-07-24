# STEPBible TIPNR derived files

None of the files in this folder have been hand-created.
They are all produced from the original table/spreadsheet
by a script for convenience of those wanting to use the data.

Any errors in these files will need to be fixed either in the
original table, or in the _loadTIPNR.py_ conversion script.

If you require a slightly different format or pivot of the data,
feel free to contact us and we might be able to help.

## Notes

When multiple people or places have the same name, e.g., Joshua,
we label them Joshua1, Joshua2, etc.
However, if one of the characters is mentioned more often than the others,
we remove that suffix for convenience, so we could end up with Joshua1, Joshua, Joshua3, etc.
Although that has its own inconsistencies, in general
we expect this to be shorter and more helpful to humans than the TIPNR
format using "Name@firstReference".

We also prefix names with 'P' for person, 'Q' for persons/group,
'L' for locations, and 'D' for deities/gods. So the above examples
would end up as PJoshua1, PJoshua, PJoshua3, etc.