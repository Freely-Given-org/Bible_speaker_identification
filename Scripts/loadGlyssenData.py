#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# loadGlyssenData.py
#
# Module handling Glyssen data loading, cross-validating,
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
Module to load and process SIL Glyssen data files
    and then to export various parts of the dataset in various formats,
        especially JSON and XML.
"""
from gettext import gettext as _
from collections import defaultdict
from csv import DictReader
import re
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import date
import os
import logging
import json

import BibleOrgSysGlobals
from BibleOrgSysGlobals import fnPrint, vPrint, dPrint


LAST_MODIFIED_DATE = '2022-08-10' # by RJH
SHORT_PROGRAM_NAME = "loadGlyssenData"
PROGRAM_NAME = "Load SIL Glyssen data files"
PROGRAM_VERSION = '0.03'
PROGRAM_NAME_VERSION = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

DEBUGGING_THIS_MODULE = False


SOURCE_DATA_LAST_DOWNLOADED_DATE_STRING = '2022-07-25'

PREFIX_OUR_IDS_FLAG = True

# Create a header to go in the data files
HEADER_DICT = { '__HEADERS__':
    {
    'conversion_software': PROGRAM_NAME_VERSION,
    'conversion_software_last_modified_date': LAST_MODIFIED_DATE,
    'source_data_last_downloaded_date': SOURCE_DATA_LAST_DOWNLOADED_DATE_STRING,
    'conversion_date': str(date.today()),
    'conversion_format_version': '0.1'
    }
}

GlyssenData_INPUT_FOLDERPATH = Path(f'../outsideSources/GlyssenData/')
GlyssenData_OUTPUT_FOLDERPATH = GlyssenData_INPUT_FOLDERPATH.joinpath( 'derivedFiles/' )
GlyssenData_XML_OUTPUT_FILENAME = 'GlyssenData.xml'
GlyssenData_XML_OUTPUT_FILEPATH = GlyssenData_OUTPUT_FOLDERPATH.joinpath(GlyssenData_XML_OUTPUT_FILENAME)

UUU_BOOK_ID_MAP = {
             1: 'GEN',  2: 'EXO',  3: 'LEV',  4: 'NUM',  5: 'DEU',
             6: 'JOS',  7: 'JDG',  8: 'RUT',  9: '1SA', 10: '2SA',
            11: '1KI', 12: '2KI', 13: '1CH', 14: '2CH', 15: 'EZR', 16: 'NEH', 17: 'EST', 18: 'JOB',
            19: 'PSA', 20: 'PRO', 21: 'ECC', 22: 'SNG', 23: 'ISA', 24: 'JER', 25: 'LAM',
            26: 'EZK', 27: 'DAN', 28: 'HOS', 29: 'JOL', 30: 'AMO', 31: 'OBA',
            32: 'JON', 33: 'MIC', 34: 'NAM', 35: 'HAB', 36: 'ZEP', 37: 'HAG', 38: 'ZEC', 39: 'MAL',
            40: 'MAT', 41: 'MRK', 42: 'LUK', 43: 'JHN', 44: 'ACT',
            45: 'ROM', 46: '1CO', 47: '2CO', 48: 'GAL', 49: 'EPH', 50: 'PHP', 51: 'COL',
            52: '1TH', 53: '2TH', 54: '1TI', 55: '2TI', 56: 'TIT', 57: 'PHM',
            58: 'HEB', 59: 'JAS', 60: '1PE', 61: '2PE', 62: '1JN', 63: '2JN', 64: '3JN', 65: 'JUD', 66: 'REV'}
assert len(UUU_BOOK_ID_MAP) == 66
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
            45: 'ROM', 46: 'CO1', 47: 'CO2', 48: 'GAL', 49: 'EPH', 50: 'PHP', 51: 'COL',
            52: 'TH1', 53: 'TH2', 54: '1TI', 55: '2TI', 56: 'TIT', 57: 'PHM',
            58: 'HEB', 59: 'JAS', 60: 'PE1', 61: 'PE2', 62: 'JN1', 63: 'JN2', 64: 'JN3', 65: 'JDE', 66: 'REV'}
assert len(BOS_BOOK_ID_MAP) == 66

COLUMN_NAME_REPLACEMENT_MAP = {}



def main() -> None:
    """
    """
    BibleOrgSysGlobals.introduceProgram( __name__, PROGRAM_NAME_VERSION, LAST_MODIFIED_DATE )

    if load_all_Glyssen_data():
        if clean_data():
            export_JSON('raw')
            # export_xml('raw')
            if add_FGids():
                rebuild_dictionaries('FGid')
                # if DEBUGGING_THIS_MODULE:
                export_JSON('mid')
                if normalise_data() and check_data():
                    rebuild_dictionaries('FGid')
                    export_JSON('normalised')
                    export_xml('normalised')
                    export_verse_index()
# end of loadGlyssenData.main


prefixed_our_IDs = False
characters, verses = {}, {}
allEntries = {}
# NOTE: The following lists will be wrong if any of the above dict names are rebound to new/different objects
DB_LIST = ( ('characters',characters), ('verses',verses), )
ALL_DB_LIST = ( ('characters',characters), ('verses',verses),
            ('all',allEntries) )

def load_all_Glyssen_data() -> bool:
    """
    This is quite quick.
    """
    fnPrint(DEBUGGING_THIS_MODULE, "load_all_Glyssen_data()")
    vPrint('Quiet', DEBUGGING_THIS_MODULE, f"\nFinding GlyssenData files from {GlyssenData_INPUT_FOLDERPATH}…")

    db_count = 0
    for name, db in DB_LIST:
        result = load_individual_GlyssenData_TSV_file(name)
        if result is not None:
            db['__COLUMN_HEADERS__'], db['dataList'] = result
            db_count += 1

    vPrint('Quiet', DEBUGGING_THIS_MODULE, f"{db_count:,} tables loaded from GlyssenData files.")
    return True
# end of loadGlyssenData.load_all_Glyssen_data()


def load_individual_GlyssenData_TSV_file(which:str) -> Tuple[List[str],List[Dict[str,str]]]:
    """
    We use the DictReader package for this.

    We return a list of column headers (strings)
    as well as the list of entries (dicts).
    """
    fnPrint(DEBUGGING_THIS_MODULE, "load_individual_GlyssenData_TSV_file()")

    tsv_filename = 'CharacterDetail.tsv' if which=='characters' else 'CharacterVerse.tsv' if which=='verses' else None
    try_filepath = GlyssenData_INPUT_FOLDERPATH.joinpath(tsv_filename)
    tries = 1
    while not os.access(try_filepath, os.R_OK):
        tries += 1
        if tries > 4:
            logging.error(f"Unable to load {which} tsv from {GlyssenData_INPUT_FOLDERPATH} {tsv_filename}")
            return
        try_filepath = Path('../'*(tries-1)).joinpath(GlyssenData_INPUT_FOLDERPATH).joinpath(tsv_filename)
        vPrint('Quiet', DEBUGGING_THIS_MODULE, f"  Trying to find GlyssenData {which} TSV file at {try_filepath}…")

    vPrint('Quiet', DEBUGGING_THIS_MODULE,
        f"  Loading GlyssenData {which} table from {try_filepath if BibleOrgSysGlobals.verbosityLevel > 2 else tsv_filename}…")
    with open(try_filepath, 'rt', encoding='utf-8') as tsv_file:
        tsv_lines = tsv_file.readlines()

    # Remove BOM
    if tsv_lines[0].startswith("\ufeff"):
        vPrint('Quiet', DEBUGGING_THIS_MODULE, f"  Removing Byte Order Marker (BOM) from start of {which} TSV file…")
        tsv_lines[0] = tsv_lines[0][1:]
    # Remove first (version number) line from CharacterVerse.tsv
    if tsv_filename == 'CharacterVerse.tsv':
        tsv_lines = tsv_lines[1:]
    # Remove # from start of first line with column headers
    if tsv_lines[0].startswith("#\t"):
        tsv_lines[0] = tsv_lines[0].replace('#', 'B', 1)
    elif tsv_lines[0].startswith("#"):
        tsv_lines[0] = tsv_lines[0][1:]

    # Get the headers before we start
    original_column_headers = [ header for header in tsv_lines[0].strip().split('\t') ]
    dPrint('Info', DEBUGGING_THIS_MODULE, f"  Original column headers: ({len(original_column_headers)}): {original_column_headers}")

    # Read, check the number of columns, and summarise row contents all in one go
    dict_reader = DictReader(tsv_lines, delimiter='\t')
    tsv_rows = []
    # tsv_column_counts = defaultdict(lambda: defaultdict(int))
    for n, row in enumerate(dict_reader):
        if len(row) != len(original_column_headers):
            logging.critical(f"Line {n} has {len(row)} column(s) instead of {len(original_column_headers)}: {row} from '{tsv_lines[n+1]}'")
        tsv_rows.append(row)
    vPrint('Quiet', DEBUGGING_THIS_MODULE, f"  Loaded {len(tsv_rows):,} '{which}' data rows.")

    return original_column_headers, tsv_rows
# end of loadGlyssenData.load_individual_GlyssenData_TSV_file()


def add_FGids() -> bool:
    """
    Take the raw data dict (containing __COLUMN_HEADERS__ and dataList lists),
        and add our Freely-Given ids,
        while at the same time converting the data from a list into a dict.
    """
    fnPrint(DEBUGGING_THIS_MODULE, "add_FGids()")
    vPrint('Quiet', DEBUGGING_THIS_MODULE, "\nAdding Freely-Given IDs to raw data…")

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
        max_suffix, max_name = 0, ''
        for j1,entry_dict in enumerate(data_row_list):
            # dPrint('Info', DEBUGGING_THIS_MODULE, f"{dict_name} {j1} {len(entry_dict)}")
            new_entry_dict = {}
            FGid = None
            for j2, (entry_key,entry_value) in enumerate(entry_dict.items()):
                # dPrint('Normal', DEBUGGING_THIS_MODULE, f"{dict_name} {j1} ({len(entry_dict)}) {j2} {entry_key}={entry_value}")
                if entry_key in COLUMN_NAME_REPLACEMENT_MAP: # Rename the original keys as we go
                    entry_key = COLUMN_NAME_REPLACEMENT_MAP[entry_key]
                if j2 == 0: # Create an initial FGid
                    # FGid = entry_value # Default to the first field/column in the original table
                    if dict_name == 'characters':
                        assert entry_key == 'Character ID'
                        # Find the first word
                        ixSP = entry_value.find(' ')
                        if ixSP == -1: ixSP = 99999
                        ixComma = entry_value.find(',')
                        if ixComma == -1: ixComma = 99999
                        ixMin = min(ixSP, ixComma)
                        firstWord = entry_value[:ixMin] # Might be hyphenated
                        if ("'" in firstWord # like "Fred's servant"
                        or firstWord[0].islower() # like "adviser to King Fred"
                        or firstWord in ('Jews','Israelite') # like "Jews from Asia"
                        or firstWord.isdigit()): # like "2 disciples"
                            FGid = entry_value.replace(' ','_')
                        else:
                            FGid = firstWord
                    elif dict_name == 'verses':
                        assert entry_key == 'B'
                        if entry_value.startswith('#'):
                            # print(f"{entry_dict['B']} {entry_dict['C']=}:{entry_dict['V']=}")
                            if entry_value!='# PRO' and entry_value!='#NAM':
                                assert not entry_dict['C'] and not entry_dict['V']
                            FGid = 'Comment'
                        else:
                            ix = list(UUU_BOOK_ID_MAP.values()).index(entry_dict['B']) + 1
                            FGid = f"{BOS_BOOK_ID_MAP[ix]}_{entry_dict['C']}:{entry_dict['V']}~" # Final character to separate suffixes
                    assert FGid
                    name_list.append(FGid)
                    if name_list.count(FGid) > 1:
                        thisCount = name_list.count(FGid)
                        if thisCount > max_suffix:
                            max_suffix = thisCount
                            max_name = FGid
                        FGid = f'{FGid}{thisCount}'
                    assert ' ' not in FGid # We want single tokens
                    assert FGid not in new_entry_dict # Don't want to be losing data
                    new_entry_dict['FGid'] = FGid
                new_entry_dict[entry_key] = entry_value
            new_data_dict[FGid] = new_entry_dict
        del the_dict['dataList']
        the_dict['__COLUMN_HEADERS__'] = column_header_list # which has been updated
        the_dict['dataDict'] = new_data_dict
        vPrint('Quiet', DEBUGGING_THIS_MODULE, f"  Max suffix for {dict_name} was {max_suffix} on {max_name}.")
    return True
# end of loadGlyssenData.add_FGids()


def clean_data() -> bool:
    """
    Many data entry errors and inconsistencies are already discovered/fixed in the parsing code.

    This function removes leading and trailing whitespace, and doubled spaces,
        removes the final semicolon from verse Reference lists, etc.

    It also checks that we haven't accumulated empty strings and containers.

    Note: it's not written recursively as situational awareness of the various dicts and lists
            is also helpful to know (and the structure isn't THAT deep).
    """
    vPrint('Quiet', DEBUGGING_THIS_MODULE, "\nCleaning Glyssen datasets…")

    for dict_name,the_dict in DB_LIST:
        vPrint('Normal', DEBUGGING_THIS_MODULE, f"  Cleaning {dict_name}…")
        for mainKey, mainData in the_dict.items():
            # dPrint('Quiet', DEBUGGING_THIS_MODULE, f"\n    {mainKey} ({len(mainData)}) {mainData}")
            assert mainKey and mainData and mainKey!='>'
            assert isinstance(mainKey, str) # a person/place/other id/name
            assert mainKey.strip() == mainKey and '  ' not in mainKey # Don't want leading or trailing whitespace
            assert mainKey in ('__COLUMN_HEADERS__', 'dataList')
            assert isinstance(mainData, list)
            for entry in mainData:
                if mainKey == '__COLUMN_HEADERS__': assert isinstance(entry, str)
                else:
                    assert isinstance(entry, dict)
                    assert len(entry) == (8 if dict_name=='characters' else 9)
                    for subKey, subData in entry.items():
                        # dPrint('Quiet', DEBUGGING_THIS_MODULE, f"    {mainKey=} {subKey=} ({len(subData) if subData is not None else 'None'}) {subData=}")
                        assert subKey and isinstance(subKey, str)
                        assert subKey.strip() == subKey and '  ' not in subKey # Don't want leading or trailing whitespace
                        assert isinstance(subData, str | None)
                        assert subKey.strip() == subKey and '  ' not in subKey # Don't want leading or trailing whitespace
                        if subKey=='Gender': assert subData in ('Male','Female','','PreferMale','PreferFemale','Either','Neuter')

    return True
# end of loadGlyssenData.clean_data()


people_map, peopleGroups_map, places_map = {}, {}, {}
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
    global prefixed_our_IDs, people_map, peopleGroups_map, places_map
    vPrint('Quiet', DEBUGGING_THIS_MODULE, "\nNormalising Glyssen datasets…")

    for name,the_dict in DB_LIST:
        vPrint('Normal', DEBUGGING_THIS_MODULE, f"  Normalising {name}…")
        # create_combined_name_verse_references(name, the_dict) # Not needed for this dataset
        convert_field_types(name, the_dict)
        adjust_Bible_references(name, the_dict)
        ensure_best_known_name(name, the_dict)
        if PREFIX_OUR_IDS_FLAG: prefix_our_IDs(name, the_dict)

        # people_map = { v['TBDPersonLookup']:k for k,v in people.items() if k != '__COLUMN_HEADERS__' }
        # peopleGroups_map = { v['groupName']:k for k,v in peopleGroups.items() if k != '__COLUMN_HEADERS__' }
        # places_map = { v['TBDPlaceLookup']:k for k,v in places.items() if k != '__COLUMN_HEADERS__' }
        adjust_links_from_Glyssen_to_our_IDs(name, the_dict)

    if PREFIX_OUR_IDS_FLAG:
        prefixed_our_IDs = True

    return True
# end of loadGlyssenData.normalise_data()

# def create_combined_name_verse_references(dataName:str, dataDict:dict) -> bool:
#     """
#     Create combined verse references where one person or place has multiple name fields, esp. OT and NT
#     """
#     vPrint('Normal', DEBUGGING_THIS_MODULE, f"    Creating {dataName} combined individual verse references for all names…")
#     for key,data in dataDict.items():
#         if key == '__COLUMN_HEADERS__':
#             continue
#         dPrint('Info', DEBUGGING_THIS_MODULE, f"      {key} ({len(data)}) {data}")
#         if len(data['names']) > 1:
#             combined_individual_verse_references = []
#             counts_list = []
#             for name_dict in data['names']:
#                 # dPrint('Info', DEBUGGING_THIS_MODULE, f"      {entry} ({len(name_dict)}) {name_dict['individualVerseReferences']=}")
#                 counts_list.append(len(name_dict['individualVerseReferences']))
#                 combined_individual_verse_references += name_dict['individualVerseReferences']
#             dPrint('Info', DEBUGGING_THIS_MODULE, f"      {key} ({len(counts_list)}) {counts_list=} sum={sum(counts_list):,}") # {len(combined_individual_verse_references)=}")
#             assert len(combined_individual_verse_references) == sum(counts_list)
#             data['verses'] = combined_individual_verse_references

#     return True
# # end of loadGlyssenData.create_combined_name_verse_references

def convert_field_types(dataName:str, dataDict:dict) -> bool:
    """
    Convert any lists inside strings to real lists
        and convert number strings to integers.
    """
    fnPrint(DEBUGGING_THIS_MODULE, "convert_field_types()")
    vPrint('Normal', DEBUGGING_THIS_MODULE, f"    Adjusting all verse references for {dataName}…")

    for key,value in dataDict.items():
        # dPrint( 'Normal', DEBUGGING_THIS_MODULE, f"  {dataName} {key}={value}")
        if key == '__COLUMN_HEADERS__':
            continue
        # for comma_split_name in ('partners','children','siblings','halfSiblingsSameMother','halfSiblingsSameFather','people','places','peopleGroups', 'peopleBorn','peopleDied'):
        #     if comma_split_name in value:
        #         value[comma_split_name] = value[comma_split_name].split(',') if value[comma_split_name] else []
        for str_to_int_name in ('Max Speakers',):
            if str_to_int_name in value:
                value[str_to_int_name] = int(value[str_to_int_name])
        # if 'peopleCount' in value and 'people' in value:
        #     assert len(value['people']) == value['peopleCount']
        #     del value['peopleCount']
        #     try: dataDict['__COLUMN_HEADERS__'].remove('peopleCount')
        #     except ValueError: pass #already been done
        # if 'placesCount' in value and 'places' in value:
        #     assert len(value['places']) == value['placesCount']
        #     del value['placesCount']
        #     try: dataDict['__COLUMN_HEADERS__'].remove('placesCount')
        #     except ValueError: pass #already been done
        # if 'verses' in value:
        #     value['verses'] = split_refs(value['verses']) if value['verses'] else []
        #     assert len(set(value['verses'])) == len(value['verses']) # i.e., no duplicates
        #     if 'verseCount' in value: assert value['verseCount'] == len(value['verses'])

    return True
# end of loadGlyssenData.convert_field_types

def split_refs(ref_string:str) -> List[str]:
    """
    Take a string of Bible references separated by commas
        and return a tidied list of separated references.
    """
    return ref_string.split(',')
# end of loadGlyssenData.split_refs

def adjust_Bible_references(dataName:str, dataDict:dict) -> bool:
    """
    Change OSIS Bible references like '2Chr.1.14' to 'CH2_1:14'
    """
    vPrint('Normal', DEBUGGING_THIS_MODULE, f"    Adjusting all verse references for {dataName}…")
    for key,value in dataDict.items():
        # dPrint( 'Normal', DEBUGGING_THIS_MODULE, f"{value}")
        if key == '__COLUMN_HEADERS__':
            continue
        # for name_data in value['names']:
        #     for j,ref_string in enumerate(name_data['individualVerseReferences']):
        #         name_data['individualVerseReferences'][j] = adjust_Bible_reference(ref_string)
        if 'verses' in value:
            for j,ref_string in enumerate(value['verses']):
                # dPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"{j} {ref_string=}")
                value['verses'][j] = adjust_Bible_reference(ref_string)

    return True
# end of loadGlyssenData.adjust_Bible_references()

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
# end of loadGlyssenData.adjust_Bible_reference


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
    vPrint('Normal', DEBUGGING_THIS_MODULE, f"    Normalising {dataName} to ensure best known name…")

    def get_reference_count(referenceEntry:str) -> int:
        """
        Returns the number of Bible references for a given character entry
        """
        if '&' in referenceEntry: return referenceEntry.count('&') + 1
        elif 'more)' in referenceEntry: # e.g., "EST 2:2 <-(3 more)-> EST 6:5"
            match = re.search("\((\d{1,4}) more\)", referenceEntry)
            assert match
            return int(match.group(1)) + 2
        else: return 1

    for key,value in dataDict.items():
        if key == '__COLUMN_HEADERS__':
            continue
        # dPrint('Quiet', DEBUGGING_THIS_MODULE, f"{key=} {value=}")
        old_id = value['FGid'] # Which may or may not match the original key by now
        if old_id.endswith('2') and not old_id[-2].isdigit():
            # dPrint('Info', DEBUGGING_THIS_MODULE, f"      {value}")
            base_id = old_id[:-1]
            # dPrint('Normal', DEBUGGING_THIS_MODULE, f"      {old_id=} {base_id=} {key}={value}")

            references_count = get_reference_count(dataDict[base_id]['Reference']) if dataName=='characters' else 0
            references_counts = { base_id: references_count }
            max_count, num_maxes, second_highest = references_count, 1, 0
            for suffix in range(2,30):
                suffixed_entry = f'{base_id}{suffix}'
                try:
                    if dataName=='characters': references_count = get_reference_count( dataDict[suffixed_entry]['Reference'] )
                    else:
                        _just_test_for_an_entry = dataDict[suffixed_entry]['B']
                        references_count = 0
                except KeyError: break # Gone too far
                references_counts[suffixed_entry] = references_count
                if references_count == max_count:
                    num_maxes += 1
                elif references_count > max_count:
                    second_highest = max_count
                    max_count, num_maxes = references_count, 1
            if num_maxes == 1:
                if references_counts[base_id] == max_count:
                    dPrint('Verbose', DEBUGGING_THIS_MODULE, f"      Already have best name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                else:
                    dPrint('Verbose', DEBUGGING_THIS_MODULE, f"      Selecting best name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    new_base_id = f'{base_id}1'
                    dPrint('Info', DEBUGGING_THIS_MODULE, f"      Renaming '{base_id}' to '{new_base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    assert dataDict[base_id]['FGid'] == base_id
                    dataDict[base_id]['FGid'] = new_base_id
                    # We only save the prefixed ID internally -- will fix the keys later

                    suffix = list(references_counts.values()).index(max_count) + 1
                    max_id = f'{base_id}{suffix}'
                    dPrint('Info', DEBUGGING_THIS_MODULE, f"      Renaming '{max_id}' to '{base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                    assert dataDict[max_id]['FGid'] == max_id
                    dataDict[max_id]['FGid'] = base_id
                    # We only save the prefixed ID internally -- will fix the keys later
            else: # multiple entries had the same maximum number
                if references_counts[base_id] == max_count:
                    dPrint('Info', DEBUGGING_THIS_MODULE, f"      Unable to select best known name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts} but current one is a candidate")
                else:
                    dPrint('Info', DEBUGGING_THIS_MODULE, f"      Unable to select best known name for {base_id} {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                new_base_id = f'{base_id}1'
                dPrint('Info', DEBUGGING_THIS_MODULE, f"      Renaming '{base_id}' to '{new_base_id}' for {max_count=} {num_maxes=} {second_highest=} {references_counts}")
                assert dataDict[base_id]['FGid'] == base_id
                dataDict[base_id]['FGid'] = new_base_id
                # We only save the prefixed ID internally -- will fix the keys later

    if dataName == 'verses': # do a final pass to remove trailing ~ off single verse references
        for key,value in dataDict.items():
            if key == '__COLUMN_HEADERS__':
                continue
            if value['FGid'][-1] == '~': value['FGid'] = value['FGid'][:-1] # Delete trailing ~

    return True
# end of loadGlyssenData.ensure_best_known_name()


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
    vPrint('Normal', DEBUGGING_THIS_MODULE, f"    Prefixing our ID fields for {dataName}…")
    for key,value in dataDict.items():
        if key == '__COLUMN_HEADERS__':
            continue
        if dataName == 'characters':
            old_id = value['FGid']
            count = value['Max Speakers']
            # NOTE: The following is really only a guess because this dataset
            #           uses -1 for "unknown" which could be 6 or 600,000!
            new_id = f"{'P' if count==1 else 'T' if count==-1 else 'G'}{old_id}" # P=person, G=group, T=tribe/kingdom/nation
            # dPrint('Info', DEBUGGING_THIS_MODULE, f"      {old_id=} {new_id=}")
            value['FGid'] = new_id
        # assert dataDict[key]['FGid'] == new_id
        # We only save the prefixed ID internally -- will fix the keys later

    return True
# end of loadGlyssenData.prefix_our_IDs()


def adjust_links_from_Glyssen_to_our_IDs(dataName:str, dataDict:dict) -> bool:
    """
    Change references (like parents, siblings, partners, etc. to our ID fields (remove @bibleRef parts)
    """
    vPrint('Normal', DEBUGGING_THIS_MODULE, f"    Normalising all internal ID links for {dataName}…")

    # Firstly create a cross-index
    dPrint('Verbose', DEBUGGING_THIS_MODULE, f"{dataName} {str(dataDict)[:1200]}")
    # keyName = 'TBDPersonLookup' if dataName=='people' else 'groupName' if dataName=='peopleGroups' else 'TBDPlaceLookup' if dataName=='places' else None
    # if keyName:
    #     unique_name_index = { v[keyName]:k for k,v in dataDict.items() if k != '__COLUMN_HEADERS__' }

    # Now make any necessary adjustments
    for key,data in dataDict.items():
        if key == '__COLUMN_HEADERS__':
            continue
        # dPrint('Verbose', DEBUGGING_THIS_MODULE, f"{key}={str(data)[:100]}")
        # for fieldName in ('father','mother'): # single entries
        #     if fieldName in data:
        #         dPrint('Verbose', DEBUGGING_THIS_MODULE, f"{fieldName}={data[fieldName]}")
        #         field_string = data[fieldName]
        #         assert isinstance(field_string, str)
        #         # assert len(field_string) >= 10 # ww.GEN.1.1
        #         # assert field_string.count('@') == 1
        #         # pre = post = ''
        #         # if field_string.endswith('(?)') or field_string.endswith('(d)'):
        #         #     field_string, post = field_string[:-3], field_string[-3:]
        #         # elif field_string.endswith('(d?)'):
        #         #     field_string, post = field_string[:-4], field_string[-4:]
        #         # data[fieldName] = f'{pre}{unique_name_index[field_string]}{post}'
        #         if field_string:
        #             data[fieldName] = people_map[field_string]
        #         # data[fieldName] = field_string.replace( '_', '', 1 )
        # for fieldName in ('siblings','halfSiblingsSameFather','halfSiblingsSameMother', 'partners', 'children', 'people', 'places', 'peopleGroups', 'peopleBorn', 'peopleDied'): # list entries
        #     if fieldName in data:
        #         map = places_map if fieldName=='places' else peopleGroups_map if fieldName=='peopleGroups' else people_map
        #         assert isinstance(data[fieldName], list)
        #         for j,field_string in enumerate(data[fieldName]):
        #             # assert len(field_string) >= 10 # ww.GEN.1.1
        #             # assert field_string.count('@') == 1
        #             # pre = post = ''
        #             # if field_string.endswith('(?)'):
        #             #     field_string, post = field_string[:-3], field_string[-3:]
        #             # data[fieldName][j] = f'{pre}{unique_name_index[field_string]}{post}'
        #             data[fieldName] = map[field_string]
        #             # data[fieldName][j] = field_string.replace( '_', '', 1 )

    return True
# end of loadGlyssenData.adjust_links_from_Glyssen_to_our_IDs()

def rebuild_dictionaries(key_name:str) -> bool:
    """
    The dictionaries likely have some internal IDs changed.

    Change the actual keys to match those internal IDs.

    Also, add in our headers with conversion info.

    Note that after this, we would could theoretically delete the
        now-duplicated 'FGid' fields but we'll leave them in for
        maximum future flexibility (at the cost of a little extra hard disk).
    """
    vPrint('Normal', DEBUGGING_THIS_MODULE, f"  Rebuilding dictionaries with {key_name}…")
    assert key_name in ('FGid',)

    if prefixed_our_IDs: # We can safely combine all the dictionaries into one
        allEntries.clear()

    # These rebuilds retain the original entry orders
    all_count = 0
    for dict_name,the_dict in DB_LIST:
        # dPrint('Normal', DEBUGGING_THIS_MODULE, f"  {dict_name=} ({len(the_dict)}) {the_dict.keys()}")
        assert '__HEADERS__' not in the_dict # and '__HEADERS__' not in the_dict['dataDict']
        column_headers_list = the_dict['__COLUMN_HEADERS__']
        if 'dataDict' in the_dict:
            old_length = len(the_dict['dataDict']) + 1
            new_dict = { v[key_name]:v for _k,v in the_dict['dataDict'].items() }
        else:
            old_length = len(the_dict)
            new_dict = { v[key_name]:v for k,v in the_dict.items() if k!='__COLUMN_HEADERS__'}
        the_dict.clear()            # We do it this way so that we update the existing (global) dict
        the_dict['__COLUMN_HEADERS__'] = column_headers_list
        the_dict.update(new_dict)   #  rather than creating an entirely new dict
        if len(the_dict) != old_length:
            logging.critical(f"rebuild_dictionaries({key_name}) for {dict_name} unexpectedly went from {old_length:,} entries to {len(the_dict):,}")
        if prefixed_our_IDs: # We can safely combine all the dictionaries into one
            if dict_name in ('characters',):
                all_count += len(the_dict) - 1 # Don't count COLUMN_HEADERS entry
                allEntries.update(the_dict)

    if prefixed_our_IDs: # We can safely combine all the dictionaries into one
        try: del allEntries['__COLUMN_HEADERS__'] # it's irrelevant
        except KeyError: pass
        dPrint('Quiet', DEBUGGING_THIS_MODULE, f"    Got {len(allEntries):,} 'all' entries")
        assert len(allEntries) == all_count

    return True
# end of loadGlyssenData.rebuild_dictionaries()


def check_data() -> bool:
    """
    Check closed sets like signficance, translation keys, etc.

    Create stats for numbered and non-numbered people, places, etc.
    """
    # vPrint('Quiet', DEBUGGING_THIS_MODULE, "\nCross-checking Glyssen datasets…")

    # for name,the_dict in DB_LIST:
    #     vPrint('Normal', DEBUGGING_THIS_MODULE, f"  Cross-checking {name}…")
    return True
# end of loadGlyssenData.check_data()


def export_JSON(subType:str) -> bool:
    """
    Export the dictionaries as JSON.
    """
    assert subType
    vPrint('Quiet', DEBUGGING_THIS_MODULE, f"\nExporting {subType} JSON GlyssenData files…")

    for dict_name,the_dict in ALL_DB_LIST:
        if the_dict:
            # dPrint('Normal', DEBUGGING_THIS_MODULE, f"  {dict_name=} ({len(the_dict)}) {the_dict.keys()}")
            if len(the_dict) == 2:
                assert '__COLUMN_HEADERS__' in the_dict and 'dataList' in the_dict
                data_length = len(the_dict['dataList'])
            elif dict_name == 'all': data_length = len(the_dict)
            else: data_length = len(the_dict) - 1
            filepath = GlyssenData_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}.json')
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"  Exporting {data_length:,} {dict_name} to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                # WARNING: The following code would convert any int keys to str !!!
                json.dump( HEADER_DICT | the_dict, outputFile, ensure_ascii=False, indent=2 )

    return True
# end of loadGlyssenData.export_JSON()


def export_xml(subType:str) -> bool:
    """
    """
    assert subType
    vPrint('Quiet', DEBUGGING_THIS_MODULE, f"\nExporting {subType} XML GlyssenData file…")

    # vPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"  NOT Wrote {len(xml_lines):,} XML lines.")
    return True
# end of loadGlyssenData.export_xml()


def export_verse_index() -> bool:
    """
    Pivot the data to determine which names exist in each verse,
        and save this in JSON.
    """
    vPrint('Quiet', DEBUGGING_THIS_MODULE, f"\nCalculating and exporting index files…")
    subType = 'normalised'
    for dict_name,the_dict in ALL_DB_LIST:
        keyName = 'Character ID'
        if not keyName: continue
        # if dict_name not in ('people','peopleGroups','places'):
            # continue

        ref_index_dict = defaultdict(list)
        GlyssenData_index_dict = {}
        for jj, (key,value) in enumerate(the_dict.items()):
            if key == '__COLUMN_HEADERS__':
                continue
            if jj == 0 and len(value)==len(HEADER_DICT) and 'conversion_software' in value: # it's our __HEADERS__ entry
                continue

            FGid = value['FGid']
            # for ref in value['verses']:
            #     ref_index_dict[ref].append(FGid)
            unifiedNameGlyssenData = value[keyName]
            GlyssenData_index_dict[unifiedNameGlyssenData] = FGid
            # for name in value['names']:
            #     uniqueNameGlyssenData = name['uniqueNameGlyssenData']
            #     if uniqueNameGlyssenData != unifiedNameGlyssenData:
            #         if uniqueNameGlyssenData in GlyssenData_index_dict:
            #             if GlyssenData_index_dict[uniqueNameGlyssenData] != FGid:
            #                 print(f"Why do we already have {GlyssenData_index_dict[uniqueNameGlyssenData]} for {uniqueNameGlyssenData} now wanting {FGid}")
            #         else: GlyssenData_index_dict[uniqueNameGlyssenData] = FGid

        # Save the dicts as JSON files
        if ref_index_dict:
            filepath = GlyssenData_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}_verseRef_index.json')
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"  Exporting {len(ref_index_dict):,} verse ref index entries to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                json.dump( HEADER_DICT | ref_index_dict, outputFile, ensure_ascii=False, indent=2 )
        if GlyssenData_index_dict:
            filepath = GlyssenData_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}_GlyssenData_index.json')
            vPrint( 'Quiet', DEBUGGING_THIS_MODULE, f"  Exporting {len(GlyssenData_index_dict):,} GlyssenData index entries to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                json.dump( HEADER_DICT | GlyssenData_index_dict, outputFile, ensure_ascii=False, indent=2 )

    return True
# end of loadGlyssenData.export_verse_index()


if __name__ == '__main__':
    # from multiprocessing import freeze_support
    # freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic Bible Organisational System (BOS) set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    main()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of loadGlyssenData.py
