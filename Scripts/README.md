# Python scripts

loadTIPNR.py takes the original table/spreadsheet from
the Tyndale Individualised Proper Names with all References (TIPNR),
loads, cross-checks, and transforms the data fields,
and writes them into JSON (and some XML)
data files for easier use in most programming environments.

loadTheograpicBibleData.py takes the nine (exported) csv tables
from the Viz.Bible dataset,
and loads, cross-checks, and transforms the data fields,
and writes them into JSON (and some XML)
data files for easier use in most programming environments.

## Lists

As we normalise the loaded data, we convert
things like strings of comma separated references
to list objects.

## Table keys

Note that we add our own new keys to the data.
For example, for people, if there's only one,
we call him "Fred". If there's three,
at load time we initially call them "Fred, Fred2, Fred3"
and later normalise that to "Fred1, Fred2, Fred3".
Then if Fred3 is the more well-known one,
we change that to "Fred1, Fred2, Fred".
This means that the human can link to "Joshua" who
followed "Moses", without having to worry
about any other minor Moses or Joshua characters.
(Of course, it creates other complications
for the computer walking through a set of names.)
We then create an index to map the original
keys to our new keys.

## Book and verse references

The Tyndale data uses USFM bookcodes and
the Theographic data uses OSIS.
We convert them all to our own BOS books
codes (always three characters, always UPPERCASE,
always start with a letter).
We often use BBB to refer to these books codes.

For verse references, we use BBB_C:V,
cf. say OSIS Bk.C.V.
(This makes 7:5 more uniquely recognised by a RegEx
than 7.5 which could also be a floating point number.)
