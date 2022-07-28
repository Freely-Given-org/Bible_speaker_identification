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
from re import S
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import date
import os
import logging
import json

import BibleOrgSysGlobals
from BibleOrgSysGlobals import fnPrint, vPrint, dPrint


LAST_MODIFIED_DATE = '2022-07-28' # by RJH
SHORT_PROGRAM_NAME = "loadTheographicBibleData"
PROGRAM_NAME = "Load Viz.Bible Theographic Bible Data exported CSV tables"
PROGRAM_VERSION = '0.03'
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = True


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

Bbb_BOOK_ID_MAP = {
            1: 'Gen', 2: 'Exo', 3: 'Lev', 4: 'Num', 5: 'Deu',
            6: 'Jos', 7: 'Jdg', 8: 'Rut', 9: '1Sa', 10: '2Sa',
            11: '1Ki', 12: '2Ki', 13: '1Ch', 14: '2Ch', 15: 'Ezr', 16: 'Neh', 17: 'Est', 18: 'Job',
            19: 'Psa', 20: 'Pro', 21: 'Ecc', 22: 'Sng', 23: 'Isa', 24: 'Jer', 25: 'Lam',
            26: 'Ezk', 27: 'Dan', 28: 'Hos', 29: 'Jol', 30: 'Amo', 31: 'Oba',
            32: 'Jon', 33: 'Mic', 34: 'Nam', 35: 'Hab', 36: 'Zep', 37: 'Hag', 38: 'Zec', 39: 'Mal',
            40: 'Mat', 41: 'Mrk', 42: 'Luk', 43: 'Jhn', 44: 'Act',
            45: 'Rom', 46: '1Co', 47: '2Co', 48: 'Gal', 49: 'Eph', 50: 'Php', 51: 'Col', 52: '1Th', 53: '2Th', 54: '1Ti', 55: '2Ti', 56: 'Tit', 57: 'Phm',
            58: 'Heb', 59: 'Jas', 60: '1Pe', 61: '2Pe', 62: '1Jn', 63: '2Jn', 64: '3Jn', 65: 'Jud', 66: 'Rev'}
assert len(Bbb_BOOK_ID_MAP) == 66
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
                if debuggingThisModule: export_JSON('mid')
                if normalise_data() and check_data():
                    rebuild_dictionaries(key_name='FGid')
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


def load_individual_TheographicBibleData_CSV_file(which:str) -> bool:
    """
    We use the DictReader package for this.

    XX Note that this code revises the TSV column headings as the file is read in. XX
    """
    fnPrint(debuggingThisModule, "load_individual_TheographicBibleData_CSV_file()")

    csv_filename = f'{which}-Grid view.csv'
    try_filepath = TheographicBibleData_INPUT_FOLDERPATH.joinpath(csv_filename)
    tries = 1
    while not os.access(try_filepath, os.R_OK):
        tries += 1
        if tries > 4:
            logging.error(f"Unable to load {which} csv from {TheographicBibleData_INPUT_FOLDERPATH} {csv_filename}")
            return
        try_filepath = Path('../'*tries).joinpath(TheographicBibleData_INPUT_FOLDERPATH).joinpath(csv_filename)
        vPrint('Quiet', debuggingThisModule, f"  Trying to find TheographicBibleData {which} CSV file at {try_filepath}…")

    vPrint('Quiet', debuggingThisModule,
        f"  Loading TheographicBibleData {which} table from {try_filepath if BibleOrgSysGlobals.verbosityLevel > 2 else csv_filename}…")
    with open(try_filepath, 'rt', encoding='utf-8') as csv_file:
        csv_lines = csv_file.readlines()

    # Remove BOM
    if csv_lines[0].startswith("\ufeff"):
        print(f"  Removing Byte Order Marker (BOM) from start of {which} CSV file…")
        csv_lines[0] = csv_lines[0][1:]

    # Get the headers before we start
    original_column_headers = [
        header for header in csv_lines[0].strip().split(',')
    ]  # assumes no commas in headings
    dPrint('Info', debuggingThisModule, f"  Original column headers: ({len(original_column_headers)}): {original_column_headers}")
    # assert len(csv_column_headers) == NUM_EXPECTED_COLUMNS

    # column_name_replacement_dict = {'personLookup':'TBDPersonLookup', 'personID':'TBDPersonID'}
    # revised_column_headers = [column_name_replacement_dict[item] if item in column_name_replacement_dict else item for item in original_column_headers]
    # dPrint('Info', debuggingThisModule, f"  Revised column headers: ({len(revised_column_headers)}): {revised_column_headers}")

    # Read, check the number of columns, and summarise row contents all in one go
    # dict_reader = DictReader(csv_lines, fieldnames=revised_column_headers) # Override the original column names
    dict_reader = DictReader(csv_lines)
    csv_rows = []
    # csv_column_counts = defaultdict(lambda: defaultdict(int))
    for n, row in enumerate(dict_reader):
        if len(row) != len(original_column_headers):
            print(f"Line {n} has {len(row)} column(s) instead of {len(original_column_headers)}")
        csv_rows.append(row)
        # for key, value in row.items():
        #     # csv_column_sets[key].add(value)
        #     csv_column_counts[key][value] += 1
    print(f"  Loaded {len(csv_rows):,} '{which}' data rows.")

    return original_column_headers, csv_rows
# end of loadTheographicBibleData.load_individual_TheographicBibleData_CSV_file()


COLUMN_NAME_REPLACEMENT_MAP = {'personLookup':'TBDPersonLookup', 'personID':'TBDPersonNumber',
                               'placeLookup':'TBDPlaceLookup', 'placeID':'TBDPlaceNumber',
                               'ID':'TBDEventNumber'}

def add_FGids() -> bool:
    """
    Take the raw data dict (containing __COLUMN_HEADERS__ and dataList lists),
        and add our Freely-Given ids,
        while at the same time converting the data from a list into a dict.
    """
    fnPrint(debuggingThisModule, "add_FGids()")
    vPrint('Quiet', debuggingThisModule, "Adding Freely-Given IDs to raw data…")

    for dict_name,the_dict in DB_LIST:
        assert len(the_dict) == 2 # '__COLUMN_HEADERS__' and 'dataList'
        column_header_list, data_row_list = the_dict['__COLUMN_HEADERS__'], the_dict['dataList']

        # Adjust and rename the list of column headers first
        # if dict_name in ('people','places'):
        column_header_list.insert(0, 'FGid')
        column_header_list = [COLUMN_NAME_REPLACEMENT_MAP[item] if item in COLUMN_NAME_REPLACEMENT_MAP else item
                                for item in column_header_list]

        new_data_dict = {}
        for j1,entry_dict in enumerate(data_row_list):
            # dPrint('Info', debuggingThisModule, f"{dict_name} {j1} {len(entry_dict)}")
            new_entry_dict = {}
            for j2, (entry_key,entry_value) in enumerate(entry_dict.items()):
                # dPrint('Info', debuggingThisModule, f"{dict_name} {j1} {len(entry_dict)} {j2} {entry_key} {entry_value}")
                if entry_key in COLUMN_NAME_REPLACEMENT_MAP: # Rename the original keys as we go
                    entry_key = COLUMN_NAME_REPLACEMENT_MAP[entry_key]
                if j2 == 0: # Create an initial FGid
                    FGid = entry_value # Default to the first field/column in the original table
                    if entry_key in ('TBDPersonLookup','TBDPlaceLookup'): # We only want the initial Person and Place keys
                        assert dict_name in ('people','places')
                        FGid = ''.join(FGid.rsplit('_', 1)) # Delete the last underline
                    elif entry_key == 'osisRef': # in Chapters, Verses
                        FGid = FGid.replace('.', '_', 1).replace('.', ':', 1) # There'll be nothing for the second replace to do in Chapters
                    elif entry_key in ('dictLookup','title','groupName'): # in Easton and Events and PeopleGroups
                        FGid = FGid.replace(' ', '_')
                    assert ' ' not in FGid # We want single tokens
                    new_entry_dict['FGid'] = FGid
                new_entry_dict[entry_key] = entry_value
            new_data_dict[FGid] = new_entry_dict
        del the_dict['dataList']
        the_dict['dataDict'] = new_data_dict
    # vPrint('Quiet', debuggingThisModule, f"{db_count:,} tables loaded from TheographicBibleData CSV files.")
    return True
# end of loadTheographicBibleData.add_FGids()


def split_refs(ref_string:str) -> List[str]:
    """
    Take a string of Bible references separated by semicolons
        and return a tidied list of separated references.
    """
    # ref_string = ref_string.rstrip(';') # Remove unnecessary final delimiter
    # ref_string = ref_string.replace(' ','') # Remove all spaces for consistency
    # ref_string = ref_string.replace('Eze','Ezk') # Fix human inconsistencies
    # ref_string = ref_string.replace('Gen.1:1','Gen.1.1') # Fix human inconsistencies
    # ref_string = ref_string.replace(';Etc.00','') # Fix unexpected entry
    # ref_string = ref_string.replace(';Etc.0.0','') # Fix unexpected entry
    return ref_string.split(';')


def clean_data() -> bool:
    """
    Many data entry errors and inconsistencies are already discovered/fixed in the parsing code.

    This function removes leading and trailing whitespace, and doubled spaces,
        removes the final semicolon from verse Reference lists, etc.

    It also checks that we haven't accumulated empty strings and containers.

    Note: it's not written recursively as situational awareness of the various dicts and lists
            is also helpful to know (and the structure isn't THAT deep).
    """
    vPrint('Quiet', debuggingThisModule, "\nCleaning TheographicBibleData datasets…")

    for dict_name,the_dict in DB_LIST:
        vPrint('Normal', debuggingThisModule, f"  Cleaning {dict_name}…")
        for mainKey, mainData in the_dict.items():
            # dPrint('Quiet', debuggingThisModule, f"    {mainKey} ({len(mainData)}) {mainData}")
            assert mainKey and mainData and mainKey!='>'
            assert isinstance(mainKey, str) # a person/place/other id/name
            assert mainKey.strip() == mainKey and '  ' not in mainKey # Don't want leading or trailing whitespace
            if isinstance(mainData, str):
                assert mainData.strip() == mainData and '  ' not in mainData # Don't want leading or trailing whitespace
            else: # dict
                for subKey, subData in mainData.items():
                    # dPrint('Quiet', debuggingThisModule, f"    {mainKey=} {subKey=} ({len(subData)}) {subData=}")
                    assert subKey and subData and subKey!='>'
                    assert isinstance(subKey, str)
                    assert subKey.strip() == subKey and '  ' not in subKey # Don't want leading or trailing whitespace
                    if isinstance(subData, str):
                        assert subData and subData!='>'
                        if '  ' in subData:
                            dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} '{subData}'")
                            mainData[subKey] = subData = subData.replace('  ',' ')
                        assert subData.strip() == subData and '  ' not in subData # Don't want leading or trailing whitespace
                    else: # dict
                        for sub2Key, sub2Data in subData.items():
                            # dPrint('Quiet', debuggingThisModule, f"    {sub2Key} ({len(sub2Data)}) {sub2Data}")
                            assert sub2Key and sub2Data
                            assert isinstance(sub2Key, str) and sub2Key!='>'
                            assert sub2Key.strip() == sub2Key and '  ' not in sub2Key # Don't want leading or trailing whitespace
                            assert isinstance(sub2Data, dict)
                            for sub3Key, sub3Data in sub2Data.items():
                                # dPrint('Quiet', debuggingThisModule, f"    {sub3Key} ({len(sub3Data)}) {sub3Data}")
                                assert sub3Key and sub3Data
                                assert isinstance(sub3Key, str) and sub3Key!='>'
                                assert sub3Key.strip() == sub3Key and '  ' not in sub3Key # Don't want leading or trailing whitespace
                                if isinstance(sub3Data, str):
                                    assert sub3Data and sub3Data!='>'
                                    assert sub3Data.strip() == sub3Data and '  ' not in sub3Data # Don't want leading or trailing whitespace
                                else:
                                    not_done_yet

    return True
# end of loadTheographicBibleData.clean_data()


def normalise_data() -> bool:
    """
    Change signficance '- Named' to 'named', etc.

    Create combined verse references where one person or place has multiple name fields, esp. OT and NT

    If a name only occurs once, we use the name as the key, e.g., persons 'Abdiel' or 'David'.
    But if there are multiple people/places with the same name, the above code uses suffixes,
        e.g.,   Joshua, Joshua2, Joshua3.
    However, in this case, Joshua2 is the most well-known character and so we want to end up with
                Joshua1, Joshua, Joshua3.
    This is done by comparing the number of verse references.

    Optionally: Add our prefixes to our ID fields, e.g., P person, L location, etc.
                    See https://Freely-Given.org/BibleTranslations/English/OET/Tags.html
                This then also makes it easier to recombine the three tables.

    Optionally: Change Bible references like '1Co.1.14' to 'CO1_1:14'

    Optionally: Change references (like parents, siblings, partners, etc. to our ID fields (remove @bibleRef parts)
    """
    vPrint('Quiet', debuggingThisModule, "\nNormalising TheographicBibleData datasets…")

    for name,the_dict in DB_LIST:
        vPrint('Normal', debuggingThisModule, f"  Normalising {name}…")
        create_combined_name_verse_references(name, the_dict)
        adjust_Bible_references(name, the_dict)
        ensure_best_known_name(name, the_dict)
        if PREFIX_OUR_IDS_FLAG: prefix_our_IDs(name, the_dict)
        adjust_from_Theographic_to_our_IDs(name, the_dict)

    rebuild_dictionaries()
    return True
# end of loadTheographicBibleData.normalise_data()

def create_combined_name_verse_references(dataName:str, dataDict:dict) -> bool:
    """
    Create combined verse references where one person or place has multiple name fields, esp. OT and NT
    """
    vPrint('Normal', debuggingThisModule, f"    Creating {dataName} combined individual verse references for all names…")
    for entry,data in dataDict.items():
        # dPrint('Info', debuggingThisModule, f"      {entry} ({len(data)}) {data}")
        if len(data['names']) > 1:
            combined_individual_verse_references = []
            counts_list = []
            for name_dict in data['names']:
                # dPrint('Info', debuggingThisModule, f"      {entry} ({len(name_dict)}) {name_dict['individualVerseReferences']=}")
                counts_list.append(len(name_dict['individualVerseReferences']))
                combined_individual_verse_references += name_dict['individualVerseReferences']
            dPrint('Info', debuggingThisModule, f"      {entry} ({len(counts_list)}) {counts_list=} sum={sum(counts_list):,}") # {len(combined_individual_verse_references)=}")
            assert len(combined_individual_verse_references) == sum(counts_list)
            data['combinedIndividualVerseReferences'] = combined_individual_verse_references

    return True
# end of loadTheographicBibleData.create_combined_name_verse_references()

def adjust_Bible_references(dataName:str, dataDict:dict) -> bool:
    """
    Change Bible references like '1Co.1.14' to 'CO1_1:14'

    There might be a's or b's at the end of the verse number.
    """
    vPrint('Normal', debuggingThisModule, f"    Adjusting all verse references for {dataName}…")
    for value in dataDict.values():
        for name_data in value['names']:
            for j,ref_string in enumerate(name_data['individualVerseReferences']):
                name_data['individualVerseReferences'][j] = adjust_Bible_reference(ref_string)
        if 'combinedIndividualVerseReferences' in value:
            for j,ref_string in enumerate(value['combinedIndividualVerseReferences']):
                value['combinedIndividualVerseReferences'][j] = adjust_Bible_reference(ref_string)

    return True
# end of loadTheographicBibleData.adjust_Bible_references()

def adjust_Bible_reference(ref:str) -> str:
    """
    Change a Bible reference like '1Co.1.14' to 'CO1_1:14'
    """
    assert len(ref) >= 7 # Uuu.c.v
    assert ';' not in ref
    assert ':' not in ref
    assert ' ' not in ref
    assert ref.count('.') == 2
    adjRef = ref.replace('.','_',1).replace('.',':',1)

    pre = post = ''
    if adjRef[0] in '([' and adjRef[-1] in '])':
        pre = adjRef[0]
        post = adjRef[-1]
        adjRef = adjRef[1:-1]

    Uuu = adjRef[:3]
    ix = list(Bbb_BOOK_ID_MAP.values()).index(Uuu) + 1
    adjRef = f'{pre}{BOS_BOOK_ID_MAP[ix]}{adjRef[3:]}{post}'
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
    """
    vPrint('Normal', debuggingThisModule, f"    Normalising {dataName} to ensure best known name…")
    for value in dataDict.values():
        old_id = value['FGid'] # Which may or may not match the original key by now
        if old_id.endswith('2') and not old_id[-2].isdigit():
            # dPrint('Info', debuggingThisModule, f"      {entry}")
            base_id = old_id[:-1]
            references_count = len( dataDict[base_id]['combinedIndividualVerseReferences']
                                        if 'combinedIndividualVerseReferences' in dataDict[base_id]
                                        else dataDict[base_id]['names'][0] )
            references_counts = { base_id: references_count }
            max_count, num_maxes, second_highest = references_count, 1, 0
            for suffix in range(2,30):
                suffixed_entry = f'{base_id}{suffix}'
                try: references_count = len( dataDict[suffixed_entry]['combinedIndividualVerseReferences']
                                                if 'combinedIndividualVerseReferences' in dataDict[suffixed_entry]
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
                    dPrint('Normal', debuggingThisModule, f"      Renaming '{base_id}' to '{new_base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    assert dataDict[base_id]['FGid'] == base_id
                    dataDict[base_id]['FGid'] = new_base_id
                    # We only save the prefixed ID internally -- will fix the keys later

                    suffix = list(references_counts.values()).index(max_count) + 1
                    max_id = f'{base_id}{suffix}'
                    dPrint('Normal', debuggingThisModule, f"      Renaming '{max_id}' to '{base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    assert dataDict[max_id]['FGid'] == max_id
                    dataDict[max_id]['FGid'] = base_id
                    # We only save the prefixed ID internally -- will fix the keys later
            else: # multiple entries had the same maximum number
                if references_counts[base_id] == max_count:
                    dPrint('Info', debuggingThisModule, f"      Unable to select best known name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts} but current one is a candidate")
                else:
                    dPrint('Info', debuggingThisModule, f"      Unable to select best known name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                new_base_id = f'{base_id}1'
                dPrint('Normal', debuggingThisModule, f"      Renaming '{base_id}' to '{new_base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
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

    A (angelic being) Indicates that the referrent is an angelic type of being. This must be followed by the name or unique description of the being if that's not already specified.
    D (deity or god) Indicates that the referrent is a deity or god. However, since Yeshua/Jesus is both God and man, we made the decision to exempt references to the earthly Jesus from this. This must be followed by the name or unique description of the god or deity if that's not already specified. For example, we might have God=G or {the father}=GGodTheFather.
    L (location) Indicates that the referrent is a place or location. This must be followed by the name or unique description of the location if that's not already specified. For example, we might have Nineveh=L or city=LNineveh or there=LNineveh.
    O (object) Indicates that the referrent is a thing. This must be followed by the name or unique description of the thing if that's not already specified. For example, we might have staff=OAaronsStaff or ship=OJonahsShip. (Note that this doesn't imply that Jonah owned the ship -- it is simply a convenient unique name used as a reference.)
    P (person) Indicates that the referrent is a single human person. (We include references to the person Yeshua/Yesous/Jesus in this category.) This must be followed by the name or unique description of the person if that's not already specified. For example, we might have David=P or he=PDavid or him=PDavid.
    Q (person group) Indicates that the referrent is a group of two or more human people (but not a tribe/nation see T below). This must be followed by the name or unique description of the person group. For example, we might have we=QPeterAndJohn or they=QJonah1Sailors. (Note that underline characters may not be used within tags.)
    T (tribal/national group) Indicates that the referrent is a tribe or all citizens of a nation. This must be followed by the name of the people group. For example, we might have they=TMiddianites or them=TSamaritans.
    
    This then also makes it easier to recombine the three tables.

    Note: This only changes the internal records, not the actual dictionary keys.
    """
    vPrint('Normal', debuggingThisModule, f"    Prefixing our ID fields for {dataName}…")
    # The following line is just general -- we really need to individually handle the 'other' entries
    default_prefix = 'P' if dataName=='people' else 'L' if dataName=='places' else 'D'
    for value in dataDict.values():
        old_id = value['FGid']
        new_id = f'{default_prefix}{old_id}'
        # dPrint('Info', debuggingThisModule, f"      {old_id=} {new_id=}")
        value['FGid'] = new_id
        # assert dataDict[key]['FGid'] == new_id
        # We only save the prefixed ID internally -- will fix the keys later

    return True
# end of loadTheographicBibleData.prefix_our_IDs()

def adjust_from_Theographic_to_our_IDs(dataName:str, dataDict:dict) -> bool:
    """
    Change references (like parents, siblings, partners, etc. to our ID fields (remove @bibleRef parts)
    """
    vPrint('Normal', debuggingThisModule, f"    Normalising all internal ID links for {dataName}…")
    
    # Firstly create a cross-index
    unique_name_index = { v['unifiedNameTheographicBibleData']:k for k,v in dataDict.items() }

    # Now make any necessary adjustments
    for data in dataDict.values():
        for fieldName in ('father','mother'): # single entries
            if fieldName in data:
                field_string = data[fieldName]
                assert isinstance(field_string, str)
                assert len(field_string) >= 10 # ww.GEN.1.1
                assert field_string.count('@') == 1
                pre = post = ''
                if field_string.endswith('(?)') or field_string.endswith('(d)'):
                    field_string, post = field_string[:-3], field_string[-3:]
                elif field_string.endswith('(d?)'):
                    field_string, post = field_string[:-4], field_string[-4:]
                data[fieldName] = f'{pre}{unique_name_index[field_string]}{post}'
        for fieldName in ('siblings','partners','offspring'): # list entries
            if fieldName in data:
                assert isinstance(data[fieldName], list)
                for j,field_string in enumerate(data[fieldName]):
                    assert len(field_string) >= 10 # ww.GEN.1.1
                    assert field_string.count('@') == 1
                    pre = post = ''
                    if field_string.endswith('(?)'):
                        field_string, post = field_string[:-3], field_string[-3:]
                    data[fieldName][j] = f'{pre}{unique_name_index[field_string]}{post}'
        
    return True
# end of loadTheographicBibleData.adjust_from_Theographic_to_our_IDs()

def rebuild_dictionaries(key_name:str) -> bool:
    """
    The dictionaries likely have some internal IDs changed.

    Change the actual keys to match those internal IDs.

    Also, add in our headers with conversion info.

    Note that after this, we would could theoretically delete the
        now-duplicated 'FGid' fields but we'll leave them in for
        maximum future flexibility (at the cost of a little extra hard disk).
    """
    vPrint('Normal', debuggingThisModule, f"  Rebuilding dictionaries…")
    assert key_name in ('FGid',)

    if prefixed_our_IDs: # We can safely combine all the dictionaries into one
        allEntries.clear()

    # These rebuilds retain the original entry orders
    for dict_name,the_dict in DB_LIST:
        # dPrint('Normal', debuggingThisModule, f"  {dict_name=} ({len(the_dict)}) {the_dict.keys()}")
        assert '__HEADERS__' not in the_dict and '__HEADERS__' not in the_dict['dataDict']
        column_headers_list = the_dict['__COLUMN_HEADERS__']
        old_length = len(the_dict['dataDict']) if 'dataDict' in the_dict else len(the_dict)
        new_dict = { v[key_name]:v for _k,v in the_dict['dataDict'].items() }
        the_dict.clear()            # We do it this way so that we update the existing (global) dict
        column_headers_list = the_dict['__COLUMN_HEADERS__'] = column_headers_list
        the_dict.update(new_dict)   #  rather than creating an entirely new dict
        if len(the_dict) != old_length+1:
            logging.critical(f"rebuild_dictionaries({key_name}) for {dict_name} unexpectedly went from {old_length} entries to {len(the_dict)}")
        if prefixed_our_IDs: # We can safely combine all the dictionaries into one
            allEntries.update(the_dict)

    if prefixed_our_IDs: # We can safely combine all the dictionaries into one
        dPrint('Quiet', debuggingThisModule, f"    Got {len(allEntries):,} 'all' entries")

    return True
# end of loadTheographicBibleData.rebuild_dictionaries()


def check_data() -> bool:
    """
    Check closed sets like signficance, translation keys, etc.

    Create stats for numbered and non-numbered people, places, etc.
    """
    vPrint('Quiet', debuggingThisModule, "\nCross-checking TheographicBibleData datasets…")

    for name,the_dict in DB_LIST:
        vPrint('Normal', debuggingThisModule, f"  Cross-checking {name}…")
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

    vPrint( 'Quiet', debuggingThisModule, f"  NOT Wrote {len(xml_lines):,} XML lines.")
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
        ref_index_dict = defaultdict(list)
        TheographicBibleData_index_dict = {}
        for jj, value in enumerate(the_dict.values()):
            if jj == 0 and len(value)==len(HEADER_DICT) and 'conversion_software' in value: # it's our __HEADERS__ entry
                continue

            FGid = value['FGid']
            ref_list = value['combinedIndividualVerseReferences'] if 'combinedIndividualVerseReferences' in value \
                        else value['names'][0]['individualVerseReferences']
            for ref in ref_list:
                ref_index_dict[ref].append(FGid)
            unifiedNameTheographicBibleData = value['unifiedNameTheographicBibleData']
            TheographicBibleData_index_dict[unifiedNameTheographicBibleData] = FGid
            for name in value['names']:
                uniqueNameTheographicBibleData = name['uniqueNameTheographicBibleData']
                if uniqueNameTheographicBibleData != unifiedNameTheographicBibleData:
                    if uniqueNameTheographicBibleData in TheographicBibleData_index_dict:
                        if TheographicBibleData_index_dict[uniqueNameTheographicBibleData] != FGid:
                            print(f"Why do we already have {TheographicBibleData_index_dict[uniqueNameTheographicBibleData]} for {uniqueNameTheographicBibleData} now wanting {FGid}")
                    else: TheographicBibleData_index_dict[uniqueNameTheographicBibleData] = FGid

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
    print()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of loadTheographicBibleData.py
