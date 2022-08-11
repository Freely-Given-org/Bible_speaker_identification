#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# loadTheographicBibleData.py
#
# Module handling "Theographic Bible Data" loading, cross-validating,
#   processing/adapting, converting, and resaving as JSON and/or XML.
#
# Copyright (C) 2022 Robert Hunt
# Author: Robert Hunt <Freely.Given.org+GitHub@gmail.com>
#
# License: CC0 1.0 Universal (CC0 1.0) Public Domain Dedication
#
#   This is a human-readable summary of the Legal Code
#
#   No Copyright
#
#   The person who associated a work with this deed has dedicated the work to the public domain
#       by waiving all of his or her rights to the work worldwide under copyright law,
#       including all related and neighboring rights, to the extent allowed by law.
#
#   You can copy, modify, distribute and perform the work, even for commercial purposes,
#       all without asking permission. See Other Information below.
#
#   Other Information
#
#   In no way are the patent or trademark rights of any person affected by CC0,
#       nor are the rights that other persons may have in the work or in how the work is used,
#       such as publicity or privacy rights.
#    Unless expressly stated otherwise, the person who associated a work with this deed makes no
#       warranties about the work, and disclaims liability for all uses of the work,
#       to the fullest extent permitted by applicable law.
#    When using or citing the work, you should not imply endorsement by the author or the affirmer.
#
#   You should have received a copy of the formal licence text
#   along with this program.  If not, see <https://CreativeCommons.org/publicdomain/zero/1.0/>.
#
"""
Module to load and process Viz.Bible "Theographic Bible Data" CSV files
        exported from their AirTables database
    and then to export various parts of the dataset in various formats,
        especially JSON and XML.
"""
from gettext import gettext as _
from collections import defaultdict
from csv import DictReader
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import date
import os
import logging
import json

import BibleOrgSysGlobals
from BibleOrgSysGlobals import fnPrint, vPrint, dPrint


LAST_MODIFIED_DATE = '2022-08-11' # by RJH
SHORT_PROGRAM_NAME = "loadTheographicBibleData"
PROGRAM_NAME = "Load Viz.Bible Theographic Bible Data exported CSV tables"
PROGRAM_VERSION = '0.23'
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False


SOURCE_DATA_LAST_DOWNLOADED_DATE_STRING = '2022-07-24'

PREFIX_OUR_IDS_FLAG = True

# Create a header to go in the data files
HEADER_DICT = { '__HEADERS__':
    {
    'conversion_software': programNameVersion,
    'conversion_software_last_modified_date': LAST_MODIFIED_DATE,
    'source_data_last_downloaded_date': SOURCE_DATA_LAST_DOWNLOADED_DATE_STRING,
    'conversion_date': str(date.today()),
    'conversion_format_version': '0.1'
    }
}

TheographicBibleData_INPUT_FOLDERPATH = Path(f'../outsideSources/TheographicBibleData/')
TheographicBibleData_OUTPUT_FOLDERPATH = TheographicBibleData_INPUT_FOLDERPATH.joinpath( 'derivedFiles/' )
TheographicBibleData_XML_OUTPUT_FILENAME = 'TheographicBibleData.xml'
TheographicBibleData_XML_OUTPUT_FILEPATH = TheographicBibleData_OUTPUT_FOLDERPATH.joinpath(TheographicBibleData_XML_OUTPUT_FILENAME)


OSIS_BOOK_ID_MAP = {
            1: 'Gen', 2: 'Exod', 3: 'Lev', 4: 'Num', 5: 'Deut',
            6: 'Josh', 7: 'Judg', 8: 'Ruth', 9: '1Sam', 10: '2Sam',
            11: '1Kgs', 12: '2Kgs', 13: '1Chr', 14: '2Chr', 15: 'Ezra', 16: 'Neh', 17: 'Esth', 18: 'Job',
            19: 'Ps', 20: 'Prov', 21: 'Eccl', 22: 'Song', 23: 'Isa', 24: 'Jer', 25: 'Lam',
            26: 'Ezek', 27: 'Dan', 28: 'Hos', 29: 'Joel', 30: 'Amos', 31: 'Obad',
            32: 'Jonah', 33: 'Mic', 34: 'Nah', 35: 'Hab', 36: 'Zeph', 37: 'Hag', 38: 'Zech', 39: 'Mal',
            40: 'Matt', 41: 'Mark', 42: 'Luke', 43: 'John', 44: 'Acts',
            45: 'Rom', 46: '1Cor', 47: '2Cor', 48: 'Gal', 49: 'Eph', 50: 'Phil', 51: 'Col',
            52: '1Thess', 53: '2Thess', 54: '1Tim', 55: '2Tim', 56: 'Titus', 57: 'Phlm',
            58: 'Heb', 59: 'Jas', 60: '1Pet', 61: '2Pet', 62: '1John', 63: '2John', 64: '3John', 65: 'Jude', 66: 'Rev'}
assert len(OSIS_BOOK_ID_MAP) == 66
BOS_BOOK_ID_MAP = {
            1: 'GEN', 2: 'EXO', 3: 'LEV', 4: 'NUM', 5: 'DEU',
            6: 'JOS', 7: 'JDG', 8: 'RUT', 9: 'SA1', 10: 'SA2',
            11: 'KI1', 12: 'KI2', 13: 'CH1', 14: 'CH2', 15: 'EZR', 16: 'NEH', 17: 'EST', 18: 'JOB',
            19: 'PSA', 20: 'PRO', 21: 'ECC', 22: 'SNG', 23: 'ISA', 24: 'JER', 25: 'LAM',
            26: 'EZK', 27: 'DAN', 28: 'HOS', 29: 'JOL', 30: 'AMO', 31: 'OBA',
            32: 'JNA', 33: 'MIC', 34: 'NAH', 35: 'HAB', 36: 'ZEP', 37: 'HAG', 38: 'ZEC', 39: 'MAL',
            40: 'MAT', 41: 'MRK', 42: 'LUK', 43: 'JHN', 44: 'ACT',
            45: 'ROM', 46: 'CO1', 47: 'CO2', 48: 'GAL', 49: 'EPH', 50: 'PHP', 51: 'COL', 52: 'TH1', 53: 'TH2', 54: '1TI', 55: '2TI', 56: 'TIT', 57: 'PHM',
            58: 'HEB', 59: 'JAS', 60: 'PE1', 61: 'PE2', 62: 'JN1', 63: 'JN2', 64: 'JN3', 65: 'JDE', 66: 'REV'}
assert len(BOS_BOOK_ID_MAP) == 66

# IDs are prefixed with these letters before being combined together into allDicts
PREFIX_MAP = { 'people':'P',
               'peopleGroups':'T', # Tribe/Kingdom/Nation
               'places':'L', # Location
               'events':'E',
            #    'periods':'W', # When
            #    'Easton':'F', # Facts
}

COLUMN_NAME_REPLACEMENT_MAP = {'personLookup':'TBDPersonLookup', 'personID':'TBDPersonNumber',
                               'placeLookup':'TBDPlaceLookup', 'placeID':'TBDPlaceNumber',
                               'ID':'TBDEventNumber'}



def main() -> None:
    """
    """
    BibleOrgSysGlobals.introduceProgram( __name__, programNameVersion, LAST_MODIFIED_DATE )

    if load_all_TheographicBibleData_data():
        # if clean_data():
            export_JSON('raw')
            # export_xml('raw')
            if add_FGids():
                rebuild_dictionaries('FGid')
                # if debuggingThisModule:
                export_JSON('mid')
                if normalise_data() and check_data():
                    rebuild_dictionaries('FGid')
                    export_JSON('normalised')
                    export_xml('normalised')
                    export_verse_index()
# end of loadTheographicBibleData.main


prefixed_our_IDs = False
books, chapters, verses = {}, {}, {}
people, peopleGroups, places = {}, {}, {}
periods, events, easton = {}, {}, {}
allEntries = {}
# NOTE: The following lists will be wrong if any of the above dict names are rebound to new/different objects
DB_LIST = ( ('books',books), ('chapters',chapters), ('verses',verses),
            ('people',people), ('peopleGroups',peopleGroups), ('places',places),
            ('periods',periods), ('events',events), ('Easton',easton) )
ALL_DB_LIST = ( ('books',books), ('chapters',chapters), ('verses',verses),
            ('people',people), ('peopleGroups',peopleGroups), ('places',places),
            ('periods',periods), ('events',events), ('Easton',easton),
            ('all',allEntries) )


def load_all_TheographicBibleData_data() -> bool:
    """
    This is quite quick.
    """
    fnPrint(debuggingThisModule, "load_all_TheographicBibleData_data()")
    vPrint('Quiet', debuggingThisModule, f"\nFinding TheographicBibleData CSV files from {TheographicBibleData_INPUT_FOLDERPATH}…")

    db_count = 0
    for name, db in DB_LIST:
        result = load_individual_TheographicBibleData_CSV_file(name)
        if result is not None:
            db['__COLUMN_HEADERS__'], db['dataList'] = result
            db_count += 1

    vPrint('Quiet', debuggingThisModule, f"{db_count:,} tables loaded from TheographicBibleData CSV files.")
    return True
# end of loadTheographicBibleData.load_all_TheographicBibleData_data()


def load_individual_TheographicBibleData_CSV_file(which:str) -> Tuple[List[str],List[Dict[str,str]]]:
    """
    We use the DictReader package for this.

    We return a list of column headers (strings)
    as well as the list of entries (dicts).
    """
    fnPrint(debuggingThisModule, "load_individual_TheographicBibleData_CSV_file()")

    csv_filename = f'{which.lower() if which=="Easton" else which}-Grid view.csv'
    try_filepath = TheographicBibleData_INPUT_FOLDERPATH.joinpath(csv_filename)
    tries = 1
    while not os.access(try_filepath, os.R_OK):
        tries += 1
        if tries > 4:
            logging.error(f"Unable to load {which} csv from {TheographicBibleData_INPUT_FOLDERPATH} {csv_filename}")
            return
        try_filepath = Path('../'*(tries-1)).joinpath(TheographicBibleData_INPUT_FOLDERPATH).joinpath(csv_filename)
        vPrint('Quiet', debuggingThisModule, f"  Trying to find TheographicBibleData {which} CSV file at {try_filepath}…")

    vPrint('Quiet', debuggingThisModule,
        f"  Loading TheographicBibleData {which} table from {try_filepath if BibleOrgSysGlobals.verbosityLevel > 2 else csv_filename}…")
    with open(try_filepath, 'rt', encoding='utf-8') as csv_file:
        csv_lines = csv_file.readlines()

    # Remove BOM
    if csv_lines[0].startswith("\ufeff"):
        vPrint('Quiet', debuggingThisModule, f"  Removing Byte Order Marker (BOM) from start of {which} CSV file…")
        csv_lines[0] = csv_lines[0][1:]

    # Get the headers before we start
    original_column_headers = [ header for header in csv_lines[0].strip().split(',') ]  # assumes no commas in headings
    dPrint('Info', debuggingThisModule, f"  Original column headers: ({len(original_column_headers)}): {original_column_headers}")

    # Read, check the number of columns, and summarise row contents all in one go
    dict_reader = DictReader(csv_lines)
    csv_rows = []
    genders = defaultdict(int)
    occupations = defaultdict(int)
    featureTypes, featureSubtypes = defaultdict(int), defaultdict(int)
    precisions = defaultdict(int)
    comments = defaultdict(int)
    rangeFlags = defaultdict(int)
    lagTypes = defaultdict(int)
    eras = defaultdict(int)
    bc_ad = defaultdict(int)
    # csv_column_counts = defaultdict(lambda: defaultdict(int))
    for n, row in enumerate(dict_reader):
        if len(row) != len(original_column_headers):
            logging.critical(f"Line {n} has {len(row)} column(s) instead of {len(original_column_headers)}")
        if 'gender' in row: genders[row['gender']] += 1
        if 'occupations' in row: occupations[row['occupations']] += 1
        if 'featureType' in row: featureTypes[row['featureType']] += 1
        if 'featureSubType' in row: featureSubtypes[row['featureSubType']] += 1
        if 'precision' in row: precisions[row['precision']] += 1
        if 'comment' in row: comments[row['comment']] += 1
        if 'rangeFlag' in row: rangeFlags[row['rangeFlag']] += 1
        if 'Lag Type' in row: lagTypes[row['Lag Type']] += 1
        if 'era' in row: eras[row['era']] += 1
        if 'BC-AD' in row: bc_ad[row['BC-AD']] += 1
        csv_rows.append(row)
    vPrint('Quiet', debuggingThisModule, f"  Loaded {len(csv_rows):,} '{which}' data rows.")
    if genders: vPrint('Normal', debuggingThisModule, f"    Genders: {str(genders).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if occupations: vPrint('Normal', debuggingThisModule, f"    Occupations: {str(occupations).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if featureTypes: vPrint('Normal', debuggingThisModule, f"    FeatureTypes: {str(featureTypes).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if featureSubtypes: vPrint('Normal', debuggingThisModule, f"    FeatureSubtypes: {str(featureSubtypes).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if precisions: vPrint('Normal', debuggingThisModule, f"    Precisions: {str(precisions).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if comments: vPrint('Normal', debuggingThisModule, f"    Comments: {str(comments).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if rangeFlags: vPrint('Normal', debuggingThisModule, f"    RangeFlags: {str(rangeFlags).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if lagTypes: vPrint('Normal', debuggingThisModule, f"    LagTypes: {str(lagTypes).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if eras: vPrint('Normal', debuggingThisModule, f"    Eras: {str(eras).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")
    if bc_ad: vPrint('Normal', debuggingThisModule, f"    BC/AD: {str(bc_ad).replace('''defaultdict(<class 'int'>, {''','').replace('})','')}")

    return original_column_headers, csv_rows
# end of loadTheographicBibleData.load_individual_TheographicBibleData_CSV_file()


def add_FGids() -> bool:
    """
    Take the raw data dict (containing __COLUMN_HEADERS__ and dataList lists),
        and add our Freely-Given ids,
        while at the same time converting the data from a list into a dict.
    """
    fnPrint(debuggingThisModule, "add_FGids()")
    vPrint('Quiet', debuggingThisModule, "\nAdding Freely-Given IDs to raw data…")

    for dict_name,the_dict in DB_LIST:
        assert len(the_dict) == 2 # '__COLUMN_HEADERS__' and 'dataList'
        column_header_list, data_row_list = the_dict['__COLUMN_HEADERS__'], the_dict['dataList']

        # Adjust and rename the list of column headers first
        # if dict_name in ('people','places'):
        column_header_list.insert(0, 'FGid')
        column_header_list = [COLUMN_NAME_REPLACEMENT_MAP[item] if item in COLUMN_NAME_REPLACEMENT_MAP else item
                                for item in column_header_list]

        new_data_dict = {}
        name_list = []
        for j1,entry_dict in enumerate(data_row_list):
            # dPrint('Info', debuggingThisModule, f"{dict_name} {j1} {len(entry_dict)}")
            new_entry_dict = {}
            for j2, (entry_key,entry_value) in enumerate(entry_dict.items()):
                # dPrint('Info', debuggingThisModule, f"{dict_name} {j1} {len(entry_dict)} {j2} {entry_key} {entry_value}")
                if entry_key in COLUMN_NAME_REPLACEMENT_MAP: # Rename the original keys as we go
                    entry_key = COLUMN_NAME_REPLACEMENT_MAP[entry_key]
                if j2 == 0: # Create an initial FGid
                    FGid = entry_value # Default to the first field/column in the original table
                    if dict_name == 'people':
                        assert entry_key == 'TBDPersonLookup' # but we won't use that
                        FGid = entry_dict['name'].replace(' ','_')
                        assert FGid
                        name_list.append(FGid)
                        if name_list.count(FGid) > 1:
                            FGid = f'{FGid}{name_list.count(FGid)}'
                    elif dict_name == 'places':
                        assert entry_key == 'TBDPlaceLookup' # but we won't use that
                        FGid = entry_dict['kjvName'].replace(' ','_')
                        assert FGid
                        name_list.append(FGid)
                        if name_list.count(FGid) > 1:
                            FGid = f'{FGid}{name_list.count(FGid)}'
                    elif entry_key == 'osisRef': # in Chapters, Verses
                        FGid = FGid.replace('.', '_', 1).replace('.', ':', 1) # There'll be nothing for the second replace to do in Chapters
                    elif entry_key in ('dictLookup','title','groupName'): # in Easton and Events and PeopleGroups
                        FGid = FGid.replace(' ', '_')
                    assert ' ' not in FGid # We want single tokens
                    assert FGid not in new_entry_dict # Don't want to be losing data
                    new_entry_dict['FGid'] = FGid
                new_entry_dict[entry_key] = entry_value
            new_data_dict[FGid] = new_entry_dict
        del the_dict['dataList']
        the_dict['__COLUMN_HEADERS__'] = column_header_list # which has been updated
        the_dict['dataDict'] = new_data_dict
    # vPrint('Quiet', debuggingThisModule, f"{db_count:,} tables loaded from TheographicBibleData CSV files.")
    return True
# end of loadTheographicBibleData.add_FGids()


# def clean_data() -> bool:
#     """
#     Many data entry errors and inconsistencies are already discovered/fixed in the parsing code.

#     This function removes leading and trailing whitespace, and doubled spaces,
#         removes the final semicolon from verse Reference lists, etc.

#     It also checks that we haven't accumulated empty strings and containers.

#     Note: it's not written recursively as situational awareness of the various dicts and lists
#             is also helpful to know (and the structure isn't THAT deep).
#     """
#     vPrint('Quiet', debuggingThisModule, "\nCleaning TheographicBibleData datasets…")

#     for dict_name,the_dict in DB_LIST:
#         vPrint('Normal', debuggingThisModule, f"  Cleaning {dict_name}…")
#         for mainKey, mainData in the_dict.items():
#             # dPrint('Quiet', debuggingThisModule, f"    {mainKey} ({len(mainData)}) {mainData}")
#             assert mainKey and mainData and mainKey!='>'
#             assert isinstance(mainKey, str) # a person/place/other id/name
#             assert mainKey.strip() == mainKey and '  ' not in mainKey # Don't want leading or trailing whitespace
#             if isinstance(mainData, str):
#                 assert mainData.strip() == mainData and '  ' not in mainData # Don't want leading or trailing whitespace
#             else: # dict
#                 for subKey, subData in mainData.items():
#                     # dPrint('Quiet', debuggingThisModule, f"    {mainKey=} {subKey=} ({len(subData)}) {subData=}")
#                     assert subKey and subData and subKey!='>'
#                     assert isinstance(subKey, str)
#                     assert subKey.strip() == subKey and '  ' not in subKey # Don't want leading or trailing whitespace
#                     if isinstance(subData, str):
#                         assert subData and subData!='>'
#                         if '  ' in subData:
#                             dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} '{subData}'")
#                             mainData[subKey] = subData = subData.replace('  ',' ')
#                         assert subData.strip() == subData and '  ' not in subData # Don't want leading or trailing whitespace
#                     else: # dict
#                         for sub2Key, sub2Data in subData.items():
#                             # dPrint('Quiet', debuggingThisModule, f"    {sub2Key} ({len(sub2Data)}) {sub2Data}")
#                             assert sub2Key and sub2Data
#                             assert isinstance(sub2Key, str) and sub2Key!='>'
#                             assert sub2Key.strip() == sub2Key and '  ' not in sub2Key # Don't want leading or trailing whitespace
#                             assert isinstance(sub2Data, dict)
#                             for sub3Key, sub3Data in sub2Data.items():
#                                 # dPrint('Quiet', debuggingThisModule, f"    {sub3Key} ({len(sub3Data)}) {sub3Data}")
#                                 assert sub3Key and sub3Data
#                                 assert isinstance(sub3Key, str) and sub3Key!='>'
#                                 assert sub3Key.strip() == sub3Key and '  ' not in sub3Key # Don't want leading or trailing whitespace
#                                 if isinstance(sub3Data, str):
#                                     assert sub3Data and sub3Data!='>'
#                                     assert sub3Data.strip() == sub3Data and '  ' not in sub3Data # Don't want leading or trailing whitespace
#                                 else:
#                                     raise Exception("Not done yet")

#     return True
# # end of loadTheographicBibleData.clean_data()


people_map, peopleGroups_map, places_map, events_map = {}, {}, {}, {}
def normalise_data() -> bool:
    """
    If a name only occurs once, we use the name as the key, e.g., persons 'Abdiel' or 'David'.
    But if there are multiple people/places with the same name, the above code uses suffixes,
        e.g.,   Joshua, Joshua2, Joshua3.
    However, in this case, Joshua2 is the most well-known character and so we want to end up with
                Joshua1, Joshua, Joshua3.
    This is done by comparing the number of verse references.

    Optionally: Add our prefixes to our ID fields, e.g., P person, L location, etc.
                    See https://Freely-Given.org/BibleTranslations/English/OET/Tags.html
                This then also makes it easier to combine some of tables.

    Optionally: Change OSIS Bible references like '1Co.1.14' to BOS 'CO1_1:14'

    Optionally: Change references (like parents, siblings, partners, etc. to our ID fields
    """
    global prefixed_our_IDs, people_map, peopleGroups_map, places_map, events_map
    vPrint('Quiet', debuggingThisModule, "\nNormalising TheographicBibleData datasets…")

    for name,the_dict in DB_LIST:
        # if name not in ('books', 'chapters', 'verses', 'periods', 'Easton', ):
        vPrint('Normal', debuggingThisModule, f"  Normalising {name}…")
        # create_combined_name_verse_references(name, the_dict) # Not needed for this dataset
        convert_field_types(name, the_dict)
        adjust_Bible_references(name, the_dict)
        if name != 'Easton': # I think
            ensure_best_known_name(name, the_dict)
        if PREFIX_OUR_IDS_FLAG: prefix_our_IDs(name, the_dict)

        people_map = { v['TBDPersonLookup']:k for k,v in people.items() if k != '__COLUMN_HEADERS__' }
        peopleGroups_map = { v['groupName']:k for k,v in peopleGroups.items() if k != '__COLUMN_HEADERS__' }
        places_map = { v['TBDPlaceLookup']:k for k,v in places.items() if k != '__COLUMN_HEADERS__' }
        events_map = { v['title']:k for k,v in events.items() if k != '__COLUMN_HEADERS__' }
        adjust_links_from_Theographic_to_our_IDs(name, the_dict)

    if PREFIX_OUR_IDS_FLAG:
        prefixed_our_IDs = True

    return True
# end of loadTheographicBibleData.normalise_data()

# def create_combined_name_verse_references(dataName:str, dataDict:dict) -> bool:
#     """
#     Create combined verse references where one person or place has multiple name fields, esp. OT and NT
#     """
#     vPrint('Normal', debuggingThisModule, f"    Creating {dataName} combined individual verse references for all names…")
#     for key,data in dataDict.items():
#         if key == '__COLUMN_HEADERS__':
#             continue
#         dPrint('Info', debuggingThisModule, f"      {key} ({len(data)}) {data}")
#         if len(data['names']) > 1:
#             combined_individual_verse_references = []
#             counts_list = []
#             for name_dict in data['names']:
#                 # dPrint('Info', debuggingThisModule, f"      {entry} ({len(name_dict)}) {name_dict['individualVerseReferences']=}")
#                 counts_list.append(len(name_dict['individualVerseReferences']))
#                 combined_individual_verse_references += name_dict['individualVerseReferences']
#             dPrint('Info', debuggingThisModule, f"      {key} ({len(counts_list)}) {counts_list=} sum={sum(counts_list):,}") # {len(combined_individual_verse_references)=}")
#             assert len(combined_individual_verse_references) == sum(counts_list)
#             data['verses'] = combined_individual_verse_references

#     return True
# # end of loadTheographicBibleData.create_combined_name_verse_references

def convert_field_types(dataName:str, dataDict:dict) -> bool:
    """
    Convert any lists inside strings to real lists
        and convert number strings to integers.
    """
    fnPrint(debuggingThisModule, "convert_field_types()")
    vPrint('Normal', debuggingThisModule, f"    Adjusting all verse references for {dataName}…")

    for key,value in dataDict.items():
        # dPrint( 'Normal', debuggingThisModule, f"  {dataName} {key}={value}")
        if key == '__COLUMN_HEADERS__':
            continue
        for comma_split_name in ('partners','children','siblings','halfSiblingsSameMother','halfSiblingsSameFather','people','places','peopleGroups', 'peopleBorn','peopleDied',
                                    'events', 'eventsDescribed', 'booksWritten',
                                    'people (from verses)', 'participants', 'places (from verses)', 'locations', 'groups', 'chaptersWritten', 'chapters', 'writer','writers'):
            if comma_split_name in value:
                if not value[comma_split_name]: value[comma_split_name] = []
                elif '"' not in value[comma_split_name]: # it's easy
                    value[comma_split_name] = value[comma_split_name].split(',')
                else: # we likely have an escaped comma, so have to go through char by char
                    field = value[comma_split_name]
                    results = []
                    inQuote = False
                    nextIx = 0
                    for _ in range(999):
                        if inQuote: ixComma = 99999
                        else:
                            ixComma = value[comma_split_name].find(',', nextIx)
                            if ixComma == -1: ixComma = 99999
                        ixQuote = value[comma_split_name].find('"', nextIx)
                        if ixQuote == -1: ixQuote = 99999
                        ixMin = min( ixComma, ixQuote )
                        if ixMin == 99999:
                            results.append( field[nextIx:] )
                            break
                        elif ixMin == ixComma:
                            results.append( field[nextIx:ixComma] )
                            nextIx = ixComma + 1
                        else:
                            assert ixMin == ixQuote
                            if inQuote:
                                results.append( field[nextIx:ixQuote] )
                                nextIx = ixQuote + 2
                                inQuote = False
                            else:
                                inQuote = True
                                nextIx += 1
                        if nextIx >= len(field)-1: break
                    value[comma_split_name] = results
        for str_to_int_name in ('TBDPersonNumber','TBDPlaceNumber','TBDEventNumber', 'index', 'verseCount' , 'peopleCount', 'placesCount', 'writer count'):
            if str_to_int_name in value:
                value[str_to_int_name] = int(value[str_to_int_name])
        if 'peopleCount' in value and 'people' in value:
            assert len(value['people']) == value['peopleCount']
            del value['peopleCount']
            try: dataDict['__COLUMN_HEADERS__'].remove('peopleCount')
            except ValueError: pass #already been done
        if 'placesCount' in value and 'places' in value:
            assert len(value['places']) == value['placesCount']
            del value['placesCount']
            try: dataDict['__COLUMN_HEADERS__'].remove('placesCount')
            except ValueError: pass #already been done
        if 'writer count' in value and 'writer' in value:
            assert len(value['writer']) == value['writer count']
            del value['writer count']
            try: dataDict['__COLUMN_HEADERS__'].remove('writer count')
            except ValueError: pass #already been done
        if 'verses' in value:
            value['verses'] = split_refs(value['verses']) if value['verses'] else []
            assert len(set(value['verses'])) == len(value['verses']) # i.e., no duplicates
            if 'verseCount' in value: assert value['verseCount'] == len(value['verses'])

    return True
# end of loadTheographicBibleData.convert_field_types

def split_refs(ref_string:str) -> List[str]:
    """
    Take a string of Bible references separated by commas
        and return a tidied list of separated references.
    """
    return ref_string.split(',')
# end of loadTheographicBibleData.split_refs

def adjust_Bible_references(dataName:str, dataDict:dict) -> bool:
    """
    Change OSIS Bible references like '2Chr.1.14' to 'CH2_1:14'
    """
    vPrint('Normal', debuggingThisModule, f"    Adjusting all verse references for {dataName}…")
    for key,value in dataDict.items():
        # dPrint( 'Normal', debuggingThisModule, f"{value}")
        if key == '__COLUMN_HEADERS__':
            continue
        # for name_data in value['names']:
        #     for j,ref_string in enumerate(name_data['individualVerseReferences']):
        #         name_data['individualVerseReferences'][j] = adjust_Bible_reference(ref_string)
        if 'verses' in value:
            for j,ref_string in enumerate(value['verses']):
                # dPrint( 'Quiet', debuggingThisModule, f"{j} {ref_string=}")
                value['verses'][j] = adjust_Bible_reference(ref_string)

    return True
# end of loadTheographicBibleData.adjust_Bible_references()

def adjust_Bible_reference(ref:str) -> str:
    """
    Change an OSIS Bible reference like '2Chr.1.14' to 'CH2_1:14'
    """
    assert len(ref) >= 6 # Uu.c.v
    assert ';' not in ref
    assert ':' not in ref
    assert ' ' not in ref
    assert ref.count('.') == 2
    adjRef = ref.replace('.','_',1).replace('.',':',1)

    pre = post = ''
    # if adjRef[0] in '([' and adjRef[-1] in '])':
    #     pre = adjRef[0]
    #     post = adjRef[-1]
    #     adjRef = adjRef[1:-1]

    osisBookCode, rest = adjRef.split('_')
    c, v = rest.split( ':' )
    assert c.isdigit()
    assert v.isdigit()

    ix = list(OSIS_BOOK_ID_MAP.values()).index(osisBookCode) + 1
    adjRef = f'{pre}{BOS_BOOK_ID_MAP[ix]}_{rest}{post}'
    # print(f"Converted '{ref}' to '{adjRef}'")
    return adjRef
# end of loadTheographicBibleData.adjust_Bible_reference


def ensure_best_known_name(dataName:str, dataDict:dict) -> bool:
    """
    If a name only occurs once, we use the name as the key, e.g., persons 'Abdiel' or 'David'.
    But if there are multiple people/places with the same name, the above code uses suffixes,
        e.g.,   Joshua, Joshua2, Joshua3.
    However, in this case, Joshua2 is the most well-known character and so we want to end up with
                Joshua1, Joshua, Joshua3.
    This is done by comparing the number of verse references.

    Note: This only changes the internal records, not the actual dictionary keys.
            That gets handled later.
    """
    vPrint('Normal', debuggingThisModule, f"    Normalising {dataName} to ensure best known name…")
    if dataName in ('books','chapters','verses'): # nothing to do here
        return False

    for key,value in dataDict.items():
        if key == '__COLUMN_HEADERS__':
            continue
        dPrint('Verbose', debuggingThisModule, f"{key=} {value=}")
        old_id = value['FGid'] # Which may or may not match the original key by now
        if old_id.endswith('2') and not old_id[-2].isdigit():
            # dPrint('Info', debuggingThisModule, f"      {value}")
            base_id = old_id[:-1]
            # dPrint('Normal', debuggingThisModule, f"      {old_id=} {base_id=} {key}={value}")
            references_count = dataDict[base_id]['verseCount']
            references_counts = { base_id: references_count }
            max_count, num_maxes, second_highest = references_count, 1, 0
            for suffix in range(2,30):
                suffixed_entry = f'{base_id}{suffix}'
                try: references_count = len( dataDict[suffixed_entry]['verses']
                                                if 'verses' in dataDict[suffixed_entry]
                                                else dataDict[suffixed_entry]['names'][0] )
                except KeyError: break # Gone too far
                references_counts[suffixed_entry] = references_count
                if references_count == max_count:
                    num_maxes += 1
                elif references_count > max_count:
                    second_highest = max_count
                    max_count, num_maxes = references_count, 1
            if num_maxes == 1:
                if references_counts[base_id] == max_count:
                    dPrint('Verbose', debuggingThisModule, f"      Already have best name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                else:
                    dPrint('Verbose', debuggingThisModule, f"      Selecting best name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    new_base_id = f'{base_id}1'
                    dPrint('Info', debuggingThisModule, f"      Renaming '{base_id}' to '{new_base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    assert dataDict[base_id]['FGid'] == base_id
                    dataDict[base_id]['FGid'] = new_base_id
                    # We only save the prefixed ID internally -- will fix the keys later

                    suffix = list(references_counts.values()).index(max_count) + 1
                    max_id = f'{base_id}{suffix}'
                    dPrint('Info', debuggingThisModule, f"      Renaming '{max_id}' to '{base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    assert dataDict[max_id]['FGid'] == max_id
                    dataDict[max_id]['FGid'] = base_id
                    # We only save the prefixed ID internally -- will fix the keys later
            else: # multiple entries had the same maximum number
                if references_counts[base_id] == max_count:
                    dPrint('Info', debuggingThisModule, f"      Unable to select best known name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts} but current one is a candidate")
                else:
                    dPrint('Info', debuggingThisModule, f"      Unable to select best known name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                new_base_id = f'{base_id}1'
                dPrint('Info', debuggingThisModule, f"      Renaming '{base_id}' to '{new_base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                assert dataDict[base_id]['FGid'] == base_id
                dataDict[base_id]['FGid'] = new_base_id
                # We only save the prefixed ID internally -- will fix the keys later

    return True
# end of loadTheographicBibleData.ensure_best_known_name()


def prefix_our_IDs(dataName:str, dataDict:dict) -> bool:
    """
    Add our prefixes to our ID fields, e.g., P person, L location, etc.
        See https://Freely-Given.org/BibleTranslations/English/OET/Tags.html

Here is a list of the use of the semantic (and other) tagging characters:

    xxxA (angelic being) Indicates that the referrent is an angelic type of being. This must be followed by the name or unique description of the being if that's not already specified.
    xxxD (deity or god) Indicates that the referrent is a deity or god. However, since Yeshua/Jesus is both God and man, we made the decision to exempt references to the earthly Jesus from this. This must be followed by the name or unique description of the god or deity if that's not already specified. For example, we might have God=G or {the father}=GGodTheFather.
    L (location) Indicates that the referrent is a place or location. This must be followed by the name or unique description of the location if that's not already specified. For example, we might have Nineveh=L or city=LNineveh or there=LNineveh.
    xxxO (object) Indicates that the referrent is a thing. This must be followed by the name or unique description of the thing if that's not already specified. For example, we might have staff=OAaronsStaff or ship=OJonahsShip. (Note that this doesn't imply that Jonah owned the ship -- it is simply a convenient unique name used as a reference.)
    P (person) Indicates that the referrent is a single human person. (We include references to the person Yeshua/Yesous/Jesus in this category.) This must be followed by the name or unique description of the person if that's not already specified. For example, we might have David=P or he=PDavid or him=PDavid.
    G (person group) Indicates that the referrent is a group of two or more human people (but not a tribe/nation see T below). This must be followed by the name or unique description of the person group. For example, we might have we=QPeterAndJohn or they=QJonah1Sailors. (Note that underline characters may not be used within tags.)
    xxxT (tribal/national group) Indicates that the referrent is a tribe or all citizens of a nation. This must be followed by the name of the people group. For example, we might have they=TMiddianites or them=TSamaritans.

    This then also makes it easier to recombine the tables.

    Note: This only changes the internal records, not the actual dictionary keys.
            That gets handled later.
    """
    vPrint('Normal', debuggingThisModule, f"    Prefixing our ID fields for {dataName}…")
    try: default_prefix = PREFIX_MAP[dataName]
    except KeyError: return False
    for key,value in dataDict.items():
        if key == '__COLUMN_HEADERS__':
            continue
        old_id = value['FGid']
        new_id = f'{default_prefix}{old_id}'
        # dPrint('Info', debuggingThisModule, f"      {old_id=} {new_id=}")
        value['FGid'] = new_id
        # assert dataDict[key]['FGid'] == new_id
        # We only save the prefixed ID internally -- will fix the keys later

    return True
# end of loadTheographicBibleData.prefix_our_IDs()


def adjust_links_from_Theographic_to_our_IDs(dataName:str, dataDict:dict) -> bool:
    """
    Change references (like parents, siblings, partners, etc. to our ID fields (remove @bibleRef parts)
    """
    vPrint('Normal', debuggingThisModule, f"    Normalising all internal ID links for {dataName}…")
    # dPrint('Verbose', debuggingThisModule, f"{dataName} {str(dataDict)[:1200]}")

    # Now make any necessary adjustments
    for key,data in dataDict.items():
        if key == '__COLUMN_HEADERS__':
            continue
        dPrint('Verbose', debuggingThisModule, f"{key}={str(data)[:100]}")
        for fieldName in ('father','mother'): # single entries
            if fieldName in data:
                # dPrint('Verbose', debuggingThisModule, f"{fieldName}={data[fieldName]}")
                field_string = data[fieldName]
                assert isinstance(field_string, str)
                if field_string:
                    data[fieldName] = people_map[field_string]
        for fieldName in ('siblings','halfSiblingsSameFather','halfSiblingsSameMother', 'partners', 'children', 'people', 'places', 'peopleGroups', 'peopleBorn','peopleDied', 'events',
                                'people (from verses)', 'participants', 'places (from verses)', 'locations', 'groups', 'writer','writers' ): # list entries
            if fieldName in data:
                map = places_map if fieldName in ('places', 'places (from verses)', 'locations') \
                        else peopleGroups_map if fieldName in ('peopleGroups', 'groups') \
                        else events_map if fieldName in ('events','eventsDescribed') \
                        else people_map
                assert isinstance(data[fieldName], list)
                for j,field_string in enumerate(data[fieldName]):
                    # if fieldName=='events': print(j, field_string, map)
                    try: data[fieldName][j] = map[field_string]
                    except KeyError:
                        logging.critical( f"Unable to map {dataName} {key} {fieldName} '{field_string}' to appropriate entry")
                        data[fieldName][j] = f'<<<ERROR_{field_string}_>>>'

    return True
# end of loadTheographicBibleData.adjust_links_from_Theographic_to_our_IDs()


def rebuild_dictionaries(key_name:str) -> bool:
    """
    The dictionaries likely have some internal IDs changed.

    Change the actual keys to match those internal IDs.
F
    Also, add in our headers with conversion info.

    Note that after this, we would could theoretically delete the
        now-duplicated 'FGid' fields but we'll leave them in for
        maximum future flexibility (at the cost of a little extra hard disk).
    """
    vPrint('Normal', debuggingThisModule, f"  Rebuilding dictionaries with {key_name}…")
    assert key_name in ('FGid',)

    if prefixed_our_IDs: # We can safely combine all the dictionaries into one
        allEntries.clear()

    # These rebuilds retain the original entry orders
    all_count = 0
    for dict_name,the_dict in DB_LIST:
        # dPrint('Normal', debuggingThisModule, f"  {dict_name=} ({len(the_dict)}) {the_dict.keys()}")
        assert '__HEADERS__' not in the_dict # and '__HEADERS__' not in the_dict['dataDict']
        column_headers_list = the_dict['__COLUMN_HEADERS__']
        if 'dataDict' in the_dict:
            old_length = len(the_dict['dataDict']) + 1
            new_dict = { v[key_name]:v for _k,v in the_dict['dataDict'].items() }
        else:
            old_length = len(the_dict)
            new_dict = { v[key_name]:v for k,v in the_dict.items() if k!='__COLUMN_HEADERS__' }
        the_dict.clear()            # We do it this way so that we update the existing (global) dict
        the_dict['__COLUMN_HEADERS__'] = column_headers_list
        the_dict.update(new_dict)   #  rather than creating an entirely new dict
        if len(the_dict) != old_length:
            logging.critical(f"rebuild_dictionaries({key_name}) for {dict_name} unexpectedly went from {old_length:,} entries to {len(the_dict):,}")
        if prefixed_our_IDs: # We can safely combine all the dictionaries into one
            if dict_name in ('people','peopleGroups','places','events'): # so not books,chapters,verses, Easton, periods
                all_count += len(the_dict) - 1 # Don't count COLUMN_HEADERS entry
                allEntries.update(the_dict)

    if prefixed_our_IDs: # We can safely combine all the dictionaries into one
        del allEntries['__COLUMN_HEADERS__'] # it's irrelevant
        dPrint('Quiet', debuggingThisModule, f"    Got {len(allEntries):,} 'all' entries")
        assert len(allEntries) == all_count

    return True
# end of loadTheographicBibleData.rebuild_dictionaries()


def check_data() -> bool:
    """
    Check closed sets

    Create stats for numbered and non-numbered people, places, etc.
    """
    # vPrint('Quiet', debuggingThisModule, "\nCross-checking TheographicBibleData datasets…")

    # for name,the_dict in DB_LIST:
    #     vPrint('Normal', debuggingThisModule, f"  Cross-checking {name}…")
    return True
# end of loadTheographicBibleData.check_data()


def export_JSON(subType:str) -> bool:
    """
    Export the dictionaries as JSON.
    """
    assert subType
    vPrint('Quiet', debuggingThisModule, f"\nExporting {subType} JSON TheographicBibleData files…")

    for dict_name,the_dict in ALL_DB_LIST:
        if the_dict:
            # dPrint('Normal', debuggingThisModule, f"  {dict_name=} ({len(the_dict)}) {the_dict.keys()}")
            if len(the_dict) == 2:
                assert '__COLUMN_HEADERS__' in the_dict and 'dataList' in the_dict
                data_length = len(the_dict['dataList'])
            elif dict_name == 'all': data_length = len(the_dict)
            else: data_length = len(the_dict) - 1
            filepath = TheographicBibleData_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}.json')
            vPrint( 'Quiet', debuggingThisModule, f"  Exporting {data_length:,} {dict_name} to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                # WARNING: The following code would convert any int keys to str !!!
                json.dump( HEADER_DICT | the_dict, outputFile, ensure_ascii=False, indent=2 )

    return True
# end of loadTheographicBibleData.export_JSON()


def export_xml(subType:str) -> bool:
    """
    """
    assert subType
    vPrint('Quiet', debuggingThisModule, f"\nExporting {subType} XML TheographicBibleData file…")

    # vPrint( 'Quiet', debuggingThisModule, f"  NOT Wrote {len(xml_lines):,} XML lines.")
    return True
# end of loadTheographicBibleData.export_xml()


def export_verse_index() -> bool:
    """
    Pivot the data to determine which names exist in each verse,
        and save this in JSON.
    """
    vPrint('Quiet', debuggingThisModule, f"\nCalculating and exporting index files…")
    subType = 'normalised'
    for dict_name,the_dict in ALL_DB_LIST:
        keyName = 'TBDPersonLookup' if dict_name=='people' else 'groupName' if dict_name=='peopleGroups' else 'TBDPlaceLookup' if dict_name=='places' else None
        if not keyName: continue
        # if dict_name not in ('people','peopleGroups','places'):
            # continue

        ref_index_dict = defaultdict(list)
        TheographicBibleData_index_dict = {}
        for jj, (key,value) in enumerate(the_dict.items()):
            if key == '__COLUMN_HEADERS__':
                continue
            if jj == 0 and len(value)==len(HEADER_DICT) and 'conversion_software' in value: # it's our __HEADERS__ entry
                continue

            FGid = value['FGid']
            for ref in value['verses']:
                ref_index_dict[ref].append(FGid)
            unifiedNameTheographicBibleData = value[keyName]
            TheographicBibleData_index_dict[unifiedNameTheographicBibleData] = FGid
            # for name in value['names']:
            #     uniqueNameTheographicBibleData = name['uniqueNameTheographicBibleData']
            #     if uniqueNameTheographicBibleData != unifiedNameTheographicBibleData:
            #         if uniqueNameTheographicBibleData in TheographicBibleData_index_dict:
            #             if TheographicBibleData_index_dict[uniqueNameTheographicBibleData] != FGid:
            #                 print(f"Why do we already have {TheographicBibleData_index_dict[uniqueNameTheographicBibleData]} for {uniqueNameTheographicBibleData} now wanting {FGid}")
            #         else: TheographicBibleData_index_dict[uniqueNameTheographicBibleData] = FGid

        # Save the dicts as JSON files
        if ref_index_dict:
            filepath = TheographicBibleData_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}_verseRef_index.json')
            vPrint( 'Quiet', debuggingThisModule, f"  Exporting {len(ref_index_dict):,} verse ref index entries to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                json.dump( HEADER_DICT | ref_index_dict, outputFile, ensure_ascii=False, indent=2 )
        if TheographicBibleData_index_dict:
            filepath = TheographicBibleData_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}_TheographicBibleData_index.json')
            vPrint( 'Quiet', debuggingThisModule, f"  Exporting {len(TheographicBibleData_index_dict):,} TheographicBibleData index entries to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                json.dump( HEADER_DICT | TheographicBibleData_index_dict, outputFile, ensure_ascii=False, indent=2 )

    return True
# end of loadTheographicBibleData.export_verse_index()


if __name__ == '__main__':
    # from multiprocessing import freeze_support
    # freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic Bible Organisational System (BOS) set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    main()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of loadTheographicBibleData.py
