# Bible person/place/event/time-period database ideas

After becoming familiar with and analysing three different datasets,
the folder contains our ongoing attempt to consider if one dataset
could potentially combine the datafields and be useful to
all three sets of users.

The other thing that's not always considered is how English-centric the dataset is.
Of course, there are also other languages in the world
who are interested in Bible datasets.
On the other hand, we cannot bloat the datasets with some 10,000
different languages and/or Bible translations.

We don't object to using English as a meta-language,
since it is indeed the major world trade language,
and also since many users don't necessarily read the
original languages (mostly Hebrew and Koine Greek).
However, this is a world-wide endeavour and
we do have to consider how datasets from
other Bible translations might be able to be included.
(This is often a major failing of Biblical datasets --
failing to consider minority users.)

That's why we consider it important to create a
quality dataset with sensible fixed keys
so that other languages (and various translations)
can easily be linked to the dataset.

Perhaps it's not unreasonable to use the corrected 1769
King James Bible (KJB) as the meta-Bible
in the dataset???

Versification differences don't seem to be addressed in
these datasets (need to double-check what Glyssen does),
but does need to be addressed in the longer term.

We have not yet attempted to actually combine the data because
the available dataset that we find the most interesting and useful is
known to be obsolete, and there's a possibility that at least parts of the improved
and updated dataset could made available later in 2022???

So we will merely start here by listing the useful columns in the
Theographic Bible Data and then seeing if we can drop unnecessary
columns that can be trivially derived again,
plus what other useful information might be added
for other uses and for other languages/translations.

## Major classifications

This section is based on the idea of using
a single letter to represent major classes.

- B/C/V: already commonly used for book/chapter/verse
- S & M: for Strongs numbers and word morphologies
- P/G/T: for people (see People.md)
- D: for deities, God, satan
- A: for angelic beings (what about demons?)
- L: for locations/places (see Locations.md)
- O: for objects (like Solomon's temple)
- E: for events
- W: for when -- year or date or time
- F: for facts/dictionary (if required)
- Unused: (11) H I J K N Q R U X Y Z

## Biblical dating

It's clear that the author of the Theographical Bible Data
believes that dates can be derived from the OT and NT genealogies
(placed alongside corollations with non-Biblical historical sources).
This goes all the way back to the creation of Adam on Day Six
(as per Genesis 1 and Exodus 20:11) some 6,000 or so years ago.
This current writer also believes the Biblical accounts to
be historically reliable.

Of course, sceptics of the Bible might consider this
as some kind of super-spiritual naivety.
That is no surprise as they might typically believe
that the universe created itself and then eventually
an ancient ape evolved into a human,
or that we were reincarnated from some previous life form.

However, we are also aware that many also claim
major gaps in the Biblical record, or even claim
that Darwinian-type evolution fits within the Biblical time-scale.
These people are, of course, free to ignore any of the
database dates that they disagree with.
