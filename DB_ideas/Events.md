# Events database

Of course, the key or name of an event is rather arbitrary,
e.g., "Creation of the world" vs. "God creates everything"
or "Birth of Noah" vs. "The birth of Noah" vs. "Noah's birth".
So it's unlikely that two different people would agree
on the actual wording.
This doesn't make them useless for linking datasets,
but does mean that they won't always be what any particular person might expect or predict,
i.e., they may be less *discoverable*.

Event names may or may not correlate with typical section headings
in many Bible translations, although of course,
both the text and even the number of or placement of section headings
differ widely between different translations.

Also event names are more *English segments* (short phrases or clauses)
than just *English as metalanguage*.

## Original datasets

Only the Theographic Bible Data set has events.
The *events* DB (almost 400 entries) has the following headings:

- title: several words, e.g., "Birth of Noah"
- ID: number -- remove???
- startDate: e.g., starts at -4003, ends at 0060. May contain month and date, e.g., Paul speaks to Ephesian Elders: 0057-04-29
- duration: e.g., "1Y"
- rangeFlag: '': 385, 'checked': 6 (for development)
- predecessor: event
- lag: after predecessor
- Lag Type: '': 303, 'FS': 59, 'SS': 29 -- what do these mean?
- partOf: a bigger event
- verses:
- people (from verses):
- participants:
- places (from verses):
- locations:
- groups:
- notes:
- verseSort: 8-digit representation of first verse above
- modified: (for development)
- Sort Key: floating point representation of startDate???

Note that some keys are camelCase (like "startDate")
and some contain spaces (like "Lag Type").

## Suggested fields and structure

- key: several words, e.g., "Birth_of_Noah"
or prefixed with E if tables are combined, so EBirth_of_Noah
- startDate: e.g., starts at -4003, ends at 0060. May contain month and date, e.g., Paul speaks to Ephesian Elders: 0057-04-29
- duration: e.g., "1Y"
- predecessor: event
- lag: after predecessor
- Lag Type: '': 303, 'FS': 59, 'SS': 29 ???
- partOf: a bigger event
- verses:
- people (from verses):
- participants:
- places (from verses):
- locations:
- groups:
- comment:
