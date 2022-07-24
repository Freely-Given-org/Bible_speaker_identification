# STEPBible TIPNR - Tyndale Individualised Proper Names with all References

The original copy of this file came from https://github.com/STEPBible/STEPBible-Data.
Any errors in the data should be submitted back to this source.
If you wish to have a copy of the source table/spreadsheet,
we recommend that you find the original at the above link
as our copy might be out-of-date.

Last downloaded: 2022-07-20

The original file was released under a CC-BY 4.0 license.

This copy is simply included here so we can easily monitor
exactly which data the JSON and other files were derived from.
It you are aware that our copy has become outdated,
please contact us.

We would like to express grateful thanks to Tyndale House (Cambridge)
for this work, and especially to David Instone-Brewer and others
that contributed to make their work available under an open licence.

Any work or effort that has been contributed by Freely-Given.org
processing the Tyndale House TIPNR is freely gifted to the world,
i.e, our curation work is released into the public domain.
(Please note that that does not at all imply that the
licence conditions of the original content creators no longer apply.)

## Notes

- Our first extraction had 3,140 persons, 1,020 places, and 114 "other" --
a total of 4,274 major entries (although many of those have multiple "name" subentries)
- The TIPNR dataset makes no attempt to assign text to narrators
- Nor does it assign text to multiple speakers, i.e., if Peter and John replied to Jesus, there's no group representing just those two speakers, or the twelve disciples as a group
- There's no attempt to determine voice age, e.g., young Jesus vs adult Jesus which would be needed for an audio Bible
- This dataset does not have tribes as separate entries, i.e, Levites are under the person Levi and Samaritans are under the place Samaria, Gentiles are in "other"
- Objects (like the temple) which are not capitalised in English are not included
- There's no time period information
- Not sure of the reason for having both the description and summaryDescription fields yet?

## Format

For a dataset that we thought was used in the STEPBible software,
there's a lot of inconsistencies and obvious human errors throughout
the data. Perhaps it's never been checked before by a software script?
If we're able to make contact with the authors,
we have a number of questions to ask about various marks in the format,
as well as a number of corrections to submit.

Meanwhile, we made an attempt to correct many of the apparent errors
in the rather pedantic loading script.