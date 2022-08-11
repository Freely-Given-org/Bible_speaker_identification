# Periods database

## Original datasets

Only the Theographic Bible Data set has periods.
The *periods* DB (250 entries) has the following headings:

- yearNum: e.g., "-4003" or "30"
- formattedYear: e.g., "4003 BC" or "AD 30"
- era: seems to be unused
- isoYear: e.g., "-4002" or "30"
- BC-AD: 'BC': 221, 'AD': 29
- peopleBorn: list -- can be derived from People.db
- peopleDied: list -- can be derived from People.db
- events: list -- can be derived from People.db
- booksWritten: list -- can be derived???
- modified: (for development)

## Suggested fields and structure

Can everything above not be derived from the other tables
or from other fields within each entry???

If we do need a table, the key will be prefixed with W (for "when")
if they are combined into other tables.
