# Locations database

We use the word *locations* rather than *places*,
because we use P for Person and L for Location.

## Original datasets

Glyssen app for producing audio Bibles has no interest
in locations, so only two of our three datasets have
location information.

The Theographic Bible Data has the following columns
for places:

- placeLookup: rename to key?
- status: (for development)
- displayTitle: too English-translation-centric -- remove from here
- ambiguous:
- duplicate_of:
- placeID: number -- remove???
- kjvName: } not a scalable solution
- esvName: }
- recogitoComments:
- featureType: 'Water': 38, 'Region': 102, 'City': 436, '': 554, 'Landmark': 52, 'Mountain': 44, 'Island': 11, 'Valley': 36, 'Path': 1
- featureSubType: 'River': 23, '': 1207, 'Gate': 17, 'Country': 11, 'Spring': 8, 'Well': 1, 'Garden': 2, 'Cave': 2, 'Tower': 3
- openBibleLat:
- openBibleLong:
- rootID: What is this???
- precision: '': 732, 'Rough': 348, 'Unlocated': 22, 'Related-Surrounding': 111, 'Related-Within': 57, 'Center': 2, 'Precise': 2
- aliases:
- comment:
- verses:
- verseCount: (superfluous -- just count the previous list)
- eastons:
- dictText:
- recogitoUri:
- recogitoLat:
- recogitoLon:
- peopleBorn: this could be derived from the People.db
- peopleDied: this could be derived from the People.db
- recogitoStatus:
- recogitoType:
- recogitoLabel:
- recogitoUID:
- booksWritten:
- eventsHere:
- eventGroups:
- hasBeenHere:
- latitude:
- longitude:
- alphaGroup: first letter of name? Why included?
- slug": (for development???)

## Suggested fields and structure

Want no spaces in the keys, so any spaces will be replaced by underlines.

### Locations table

- key: metaname, e.g., Nineveh, Bethlehem, Garden_of_Eden,
or prefixed with L if tables are combined, so LNineveh, LBethlehem
- ambiguous:
- duplicate_of:
- recogitoComments:
- featureType: 'Water': 38, 'Region': 102, 'City': 436, '': 554, 'Landmark': 52, 'Mountain': 44, 'Island': 11, 'Valley': 36, 'Path': 1
- featureSubType: 'River': 23, '': 1207, 'Gate': 17, 'Country': 11, 'Spring': 8, 'Well': 1, 'Garden': 2, 'Cave': 2, 'Tower': 3
- openBibleLat:
- openBibleLong:
- rootID: Is this required???
- precision: '': 732, 'Rough': 348, 'Unlocated': 22, 'Related-Surrounding': 111, 'Related-Within': 57, 'Center': 2, 'Precise': 2
- aliases:
- verses:
- links: dict/map
  - type: Strongs, Easton
  - linkKey
- dictText:
- recogitoUri:
- recogitoLat:
- recogitoLon:
- recogitoStatus:
- recogitoType:
- recogitoLabel:
- recogitoUID:
- booksWritten:
- eventsHere:
- eventGroups:
- hasBeenHere:
- latitude:
- longitude:
- comment:

### Language sets

The above tables connect to the original language words
along with some English "metadata".
However, we also want to connect with specific Bible translations
in various languages.

We use the IETF 2-3-character language codes,
followed by underline and the Bible abbreviation
to name these sets,
e.g., en_WEB or en_NASB95 or hi_NHV.

- key: refers to a location above
- names: list
  - type: OT, NT
  - name: do we also need displayName?
- dictText: could maybe be "briefDescription" ???
If missing or empty, the main text is used.
