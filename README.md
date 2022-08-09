# Bible_speaker_identification

Reference data and algorithms for identifying speakers and quotations in Bible text

The Bible contains a range of direct and indirect speech, as well as quotations, narrator interrupts, implicit speech, etc.
It can be useful to have these text snippets tagged with identifiers in order to allow the following:

1. Calculating the number of speakers required for an audio or video production.
2. Printing scripts for assigning speakers for an audio or video production.
3. Automatically linking to biographical details or other information in a Bible app.
4. Advanced searching capabilities.
5. Alignment of texts in multiple languages for reference purposes, checking, and possible NLP applications.
6. Developing resources and tools to show relationships between biblical characters.

We plan to use this repository firstly as a home for discussion, and then hopefully for the following:

1. Manually curated quotation data for Bible books
2. Standard formats for the above, and for marking-up Bible data, e.g., USFM files.
3. Derived forms of the data as required, e.g., JSON or other compiled versions of the source data
4. Algorithms and or code for automatically parsing and tagging of Bible files.
5. Possibly some marked-up sample Bibles (open-licensed of course).

## Three data sets

We have three open-licensed data sets from other sources:

1. The TIPNR (Translators Individualised Proper Names with all References) STEPBible
data from Tyndale House, Cambridge. (Single spreadsheet.)
This more academic dataset is based on names in the original languages,
so an OT character mentioned in the NT
will likely have two (Hebrew and Greek) names as sub-entries.
2. The Theographic Bible Data from Viz.Bible. (Nine CSV tables exported from AirTables.)
This dataset has no references to original languages.
It seems to be designed for creating popular-level graphics.
3. The data sets extracted from the SIL Glyssen app --
a mixture of XML, TSV, and XLSX (MS-Excel) files.
This is designed for assigning parts to voice actors
for the creation of audio Bibles,
so this dataset also includes unnamed characters,
e.g., "Absalom's secret messengers".
Some characters also need to distinguish multiple voices
of differing ages, e.g., young shepherd boy David vs.
elderly King David near death.
There's no interest in computer-readable relationships between characters,
nor in places, events, etc. even though it's sometimes listed in their
Character IDs for human consumption.

## Our experiment

Partly just to gain familiarity with the datasets
and to get a feel for the pros and cons of each different way of doing things,
we have written scripts to load these datasets,
add our own little modifications, and output them as JSON.

Once that's completed, the next step would be to try to combine them
into a master set, and see how much we gain and how much we lose.
