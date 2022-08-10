# People database

## Original datasets

TIPNR refers to all of their names and aliases in the original languages.
This is done by having an embedded list of names with various
derivations of Strongs numbers and also English translations.
(Of course, most of those translations are identical.)

Theographic Bible Data has twenty people-groups in a separate file
with lists of their known members.
This includes the tribes of Israel, but not other tribes/clans.
The *people* DB (almost 3,800 entries) has the following headings:

- personLookup -- rename to key?
- status: (for development)
- personID: number -- remove???
- displayTitle: too English-translation-centric -- remove from here
- name
- surname
- alsoCalled
- isProperName: (for development)
- ambiguous: (for development)
- Disambiguation (temp): (for development)
- gender: "Male" or "Female"
- occupations: seems unused so far
- birthYear
- minYear
- deathYear
- maxYear
- birthPlace
- deathPlace
- memberOf: could be one of the twenty people-groups
- eastons: maybe put in a list of outsideLinks, incl. Strongs links, etc.
- dictText: could maybe be "briefDescription" ???
- events
- eventGroups
- verseCount: (superfluous -- just count the next list)
- verses: does this include pronomial references???
- mother
- father
- partners
- children
- siblings
- halfSiblingsSameMother
- halfSiblingsSameFather
- chaptersWritten: Why chapters (and not verse ranges)??? Would this be covered by *narrated* below?
- alphaGroup: first letter of name? Why included?
- slug: (for development???)
- modified: (for development)

## Major classifications

This section is based on the idea of using
a single letter to represent major data subsets.
For people, we would recommend **three** divisions
(most of the existing datasets only distinguish two):

- P: individual persons
- G: groups of two to say thousands of people --
these can be temporary/informal groups, e.g., *the two lepers*
or more formal groups like *the twelve disciples* or *the Pharisees*.
- T: complete tribes/kingdoms/nations, e.g., *the tribe of Judah* or
*the people of Moab* or *the Assyrians* or *Gentiles*.

So *the Assyrian army* would be **G** not **T**.
*Israel* might be a **P** and a **T** in different places
(as well as also being a location in other places).

Note: we also propose the following:

- D: for deities, God, satan
- A: for angelic beings (what about demons?)

so they would be in a different database table/file -- not mixed in here with people/humans.

## Verse references

We would suggest splitting into four groups.
The TIPNR used *significance* for this, e.g., *named*.
We suggest using the following (in the given priority order):

- spoke: e.g., Peter (or he) said...
- named: i.e., mentioned by name,
e.g., "Peter went to the temple".
- implied: i.e., pronominal (but a shorter word),
e.g., "Then he went to the temple."
- narrated: e.g., most of Acts narrated by Luke.

We suggest using verse ranges rather than every reference
to prevent bloat in the data files,
e.g., Matthew 5:47-6:3 instead of Matthew 5:47, Matthew 5:48, Matthew 6:1, Matthew 6:2, Matthew 6:3.
This requires supporting code functions to both enumerate all verses in a range,
and to determine if a certain verse is in a range.

Obviously this is dependent on versification schemes.
We recommend either the original Hebrew & Greek versification schemes
or possibly the KJB versification scheme to be our standard (to be investigated further).
Obviously versification mapping will be required when dealing with various translations,
but that's true in the real/wider world no matter what our reference scheme is.

## Suggested fields and structure

No spaces in the keys, so any spaces are replaced by underlines.

### People table

- key: metaname, e.g., Adam, Joshua2, John_the_Baptist,
or prefixed with P if tables are combined, so PAdam, PJoshua2
- names: list
  - type: Hebrew, Greek, alias
  - name:
- gender: 'M' or 'F'
- occupations
- birthYear
- minYear
- deathYear
- maxYear
- birthPlace
- deathPlace
- memberOf: list of G or T groups
- links: dict/map
  - type: Strongs, Easton
  - linkKey
- dictText: could maybe be "briefDescription" ???
- events
- eventGroups
- verseReferences: list (of verse ranges)
  - type: spoke/named/implied/narrated
  - verse range
- mother
- father
- partners: list
- children: list
- siblings: list
- halfSiblingsSameMother: list
- halfSiblingsSameFather: list

### Groups table

- key: metaname, e.g., two_lepers, 5,000, or prefixed with G if tables are combined, so Gtwo_lepers, G5,000
- names: list
  - type: Hebrew, Greek, alias
  - name:
- gender: 'M' or 'F' or 'B' (both) for a mixed group
- members: list of people
- membersAreComplete: True or False
- memberOf: list of T groups
- links: dict/map
  - type: Strongs, Easton
  - linkKey
- dictText: could maybe be "briefDescription" ???
- events
- eventGroups
- verseReferences: list (of verse ranges)
  - type: spoke/named/implied/narrated
  - verse range

### Tribes/Kingdoms/Nations table

- key: metaname, e.g., Moabites, Gentiles, or children_of_Israel,
or prefixed with T if tables are combined, so TMoabites, TGentiles
- names: list
  - type: Hebrew, Greek, alias
  - name:
- members: list of people
- links: dict/map
  - type: Strongs, Easton
  - linkKey
- dictText: could maybe be "briefDescription" ???
- events
- eventGroups
- verseReferences: list (of verse ranges)
  - type: spoke/named/implied/narrated
  - verse range

### Language sets

The above tables connect to the original language words
along with some English "metadata".
However, we also want to connect with specific Bible translations
in various languages.

We use the IETF 2-3-character language codes,
followed by underline and the Bible abbreviation
to name these sets,
e.g., en_WEB or en_NASB95 or hi_NHV.

- key: refers to a person, group, or tribe key above
- names: list
  - type: OT, NT
  - name:
