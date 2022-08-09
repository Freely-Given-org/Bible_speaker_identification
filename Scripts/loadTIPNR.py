#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# loadTIPNR.py
#
# Module handling loadTIPNR functions
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
Module to load and process exported Tyndale House (Cambridge)
    TIPNR - Translators Individualised Proper Names with all References TSV file.
    and then to export various parts of the dataset in various formats,
    especially JSON and XML.
"""
from gettext import gettext as _
from collections import defaultdict
from typing import Dict, List, Tuple
from pathlib import Path
from datetime import date
import os
import logging
import json

import BibleOrgSysGlobals
from BibleOrgSysGlobals import fnPrint, vPrint, dPrint


LAST_MODIFIED_DATE = '2022-08-09' # by RJH
SHORT_PROGRAM_NAME = "loadTIPNR"
PROGRAM_NAME = "Load Translators Individualised Proper Names file"
PROGRAM_VERSION = '0.55'
programNameVersion = f'{SHORT_PROGRAM_NAME} v{PROGRAM_VERSION}'

debuggingThisModule = False

SOURCE_DATA_LAST_DOWNLOADED_DATE_STRING = '2022-07-20'

PREFIX_OUR_IDS_FLAG = True



# Create a header to go in the data files
HEADER_DICT = { '__HEADERS__':
    {
    'conversion_software': programNameVersion,
    'conversion_software_last_modified_date': LAST_MODIFIED_DATE,
    'source_data_last_downloaded_date': SOURCE_DATA_LAST_DOWNLOADED_DATE_STRING,
    'conversion_date': str(date.today()),
    'conversion_format_version': '0.5'
    }
}

TIPNR_INPUT_FILENAME = 'TIPNR - Tyndale Individualised Proper Names with all References - TyndaleHouse.com STEPBible.org CC BY.tsv'
TIPNR_INPUT_FOLDERPATH = Path(f'../outsideSources/STEPBible/')
TIPNR_INPUT_FILEPATH = TIPNR_INPUT_FOLDERPATH.joinpath(TIPNR_INPUT_FILENAME)
TIPNR_OUTPUT_FOLDERPATH = TIPNR_INPUT_FOLDERPATH.joinpath( 'derivedFiles/' )
TIPNR_XML_OUTPUT_FILENAME = 'TIPNR.xml'
TIPNR_XML_OUTPUT_FILEPATH = TIPNR_OUTPUT_FOLDERPATH.joinpath(TIPNR_XML_OUTPUT_FILENAME)

# NOTE: USFM books codes at https://ubsicap.github.io/usfm/master/identification/books.html
#           are all UPPERCASE but TIPNR uses a Title-case form
Uuu_BOOK_ID_MAP = {
            1: 'Gen', 2: 'Exo', 3: 'Lev', 4: 'Num', 5: 'Deu',
            6: 'Jos', 7: 'Jdg', 8: 'Rut', 9: '1Sa', 10: '2Sa',
            11: '1Ki', 12: '2Ki', 13: '1Ch', 14: '2Ch', 15: 'Ezr', 16: 'Neh', 17: 'Est', 18: 'Job',
            19: 'Psa', 20: 'Pro', 21: 'Ecc', 22: 'Sng', 23: 'Isa', 24: 'Jer', 25: 'Lam',
            26: 'Ezk', 27: 'Dan', 28: 'Hos', 29: 'Jol', 30: 'Amo', 31: 'Oba',
            32: 'Jon', 33: 'Mic', 34: 'Nam', 35: 'Hab', 36: 'Zep', 37: 'Hag', 38: 'Zec', 39: 'Mal',
            40: 'Mat', 41: 'Mrk', 42: 'Luk', 43: 'Jhn', 44: 'Act',
            45: 'Rom', 46: '1Co', 47: '2Co', 48: 'Gal', 49: 'Eph', 50: 'Php', 51: 'Col', 52: '1Th', 53: '2Th', 54: '1Ti', 55: '2Ti', 56: 'Tit', 57: 'Phm',
            58: 'Heb', 59: 'Jas', 60: '1Pe', 61: '2Pe', 62: '1Jn', 63: '2Jn', 64: '3Jn', 65: 'Jud', 66: 'Rev'}
assert len(Uuu_BOOK_ID_MAP) == 66
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

    if load_TIPNR_data():
        if clean_data():
            rebuild_dictionaries('unifiedNameTIPNR')
            export_JSON('raw')
            export_xml('raw')
            rebuild_dictionaries('FGid')
            # if debuggingThisModule:
            export_JSON('mid')
            if normalise_data() and check_data():
                rebuild_dictionaries('FGid')
                export_JSON('normalised')
                export_xml('normalised')
                export_verse_index()
# end of loadTIPNR.main


prefixed_our_IDs = False
xml_lines = []
people, places, others, allEntries = {}, {}, {}, {}


def load_TIPNR_data() -> bool:
    """
    This is quite quick.
    """
    fnPrint(debuggingThisModule, "load_TIPNR_data()")
    vPrint('Quiet', debuggingThisModule, f"\nFinding TIPNR TSV file starting at {TIPNR_INPUT_FILEPATH}…")

    try_filepath = TIPNR_INPUT_FILEPATH
    while not os.access(try_filepath, os.R_OK):
        if try_filepath == TIPNR_INPUT_FILEPATH: try_filepath = TIPNR_INPUT_FILENAME
        else: try_filepath = f'../{try_filepath}'
        if try_filepath.startswith('../'*4): break
        vPrint('Quiet', debuggingThisModule, f"  Trying to find TIPNR TSV file at {try_filepath}…")

    vPrint('Quiet', debuggingThisModule, f"  Loading TIPNR TSV file from {try_filepath}…")
    in_data = in_annotatedExamples = False
    with open(try_filepath, 'rt', encoding='utf-8') as text_file:
        for j, line in enumerate(text_file):
            line = line.rstrip('\n')
            # if in_annotatedExamples:
            #     dPrint('Normal', debuggingThisModule, f"{j:5} {in_data=} {line=}")
            if line.startswith('ANNOTATED EXAMPLES'):
                break # At the end of valid data
            #     assert not in_data
            #     in_annotatedExamples = True
            if line.startswith('$=====') or line.startswith('\t'):
                if in_data == 'Person2':
                    if raw_person['UnifiedName'] != 'UnifiedName=uStrong': # heading fields
                        process_and_add_person(raw_person)
                    in_data = False
                elif in_data == 'Place2':
                    if raw_place['UnifiedName'] != 'UniqueName=uStrong': # heading fields
                        process_and_add_place(raw_place)
                    in_data = False
                elif in_data == 'Other2':
                    if raw_other['UnifiedName'] != 'UniqueName=uStrong': # heading fields
                        process_and_add_other(raw_other)
                    in_data = False
                # elif in_data == 'PersonNotes':
                #     del people[raw_other[raw_other['UnifiedName'].split('@')[0]]] # Assumes it has no suffix
                #     process_and_add_person(raw_person)
                #     in_data = False
                # elif in_data == 'PlaceNotes':
                #     del places[raw_place[raw_place['UnifiedName'].split('@')[0]]] # Assumes it has no suffix
                #     process_and_add_place(raw_place)
                #     in_data = False
                # elif in_data == 'OtherNotes':
                #     del others[raw_other[raw_other['UnifiedName'].split('@')[0]]] # Assumes it has no suffix
                #     process_and_add_other(raw_other)
                #     in_data = False

            if in_data == 'Person1':
                columns = line.split('\t')
                assert len(columns) == 13
                raw_person['UnifiedName'], raw_person['Description'], raw_person['Parents'], siblings, \
                    partners, offspring, tribeNation, \
                    raw_person['SummaryDescription'], _1,_2,_3,_4,_5 = columns
                assert raw_person['UnifiedName']
                assert raw_person['Description']
                assert raw_person['Parents']
                if siblings: raw_person['Siblings'] = siblings
                if partners: raw_person['Partners'] = partners
                if offspring: raw_person['Offspring'] = offspring
                if tribeNation and tribeNation!='>': raw_person['Tribe/Nation'] = tribeNation
                assert not _1 or _2 or _3 or _4 or _5
                raw_person['Names'] = []
                in_data = 'Person2'
            elif in_data == 'Person2':
                if in_annotatedExamples and line.startswith('NOTES:'):
                    in_data = 'PersonNotes'
                else:
                    columns = line.split('\t')
                    assert len(columns) == 13
                    this = {}
                    this['Significance'], this['UniqueName'], this['Strongs'], this['Translations'], \
                        this['STEPBibleFirstLink'], this['AllRefs'], _1,_2,_3,_4,_5,_6,_7 = columns
                    assert not _1 or _2 or _3 or _4 or _5 or _6 or _7
                    raw_person['Names'].append(this)
            # elif in_data == 'PersonNotes':
            #     columns = line.split('\t')
            #     assert len(columns) == 13
            #     assert line.endswith('\t'*12) or line.endswith('\t\t\t\t\t\t>\t\t\t\t\t\t') # ie., all columns except the first are blank
            #     assert columns[0]
            #     try: raw_person['Notes'] = f"{raw_person['Notes']}\\n{columns[0]}" # Add line with escaped newline
            #     except KeyError: raw_person['Notes'] = columns[0]
            elif in_data == 'Place1':
                columns = line.split('\t')
                assert len(columns) == 13
                raw_place['UnifiedName'], openBibleName, founder, people_, \
                    googleMapsURL, palopenMapsURL, geographicalArea, \
                    _1,_2,_3,_4,_5,_6 = columns
                assert raw_place['UnifiedName']
                if openBibleName: raw_place['OpenBibleName'] = openBibleName
                if founder: raw_place['Founder'] = founder
                if people_: raw_place['People'] = people_
                if googleMapsURL: raw_place['GoogleMapsURL'] = googleMapsURL
                if palopenMapsURL: raw_place['PalopenMapsURL'] = palopenMapsURL
                if geographicalArea and geographicalArea != '>':
                    raw_place['GeographicalArea'] = geographicalArea
                if _1 and _1.startswith('#'):
                    raw_place['Comment'] = _1[1:]
                assert not _2 or _3 or _4 or _5 or _6
                raw_place['Names'] = []
                in_data = 'Place2'
            elif in_data == 'Place2':
                if in_annotatedExamples and line.startswith('NOTES:'):
                    in_data = 'PlaceNotes'
                else:
                    columns = line.split('\t')
                    assert len(columns) == 13
                    this = {}
                    this['Significance'], this['UniqueName'], this['Strongs'], this['Translations'], \
                        this['STEPBibleFirstLink'], this['AllRefs'], _1,_2,_3,_4,_5,_6,_7 = columns
                    if (_1 or _2 or _3 or _4 or _5 or _6 or _7) and raw_place['UnifiedName'] != 'UniqueName=uStrong':
                        logging.critical(f"Losing {raw_place['UnifiedName']} place column: {_1=} {_2=} {_3=} {_4=} {_5=} {_6=} {_7=}")
                    raw_place['Names'].append(this)
            # elif in_data == 'PlaceNotes':
            #     columns = line.split('\t')
            #     assert len(columns) == 13
            #     assert line.endswith('\t'*12) or line.endswith('\t\t\t\t\t\t>\t\t\t\t\t\t') # ie., all columns except the first are blank
            #     assert columns[0]
            #     try: raw_place['Notes'] = f"{raw_place['Notes']}\\n{columns[0]}" # Add line with escaped newline
            #     except KeyError: raw_place['Notes'] = columns[0]
            elif in_data == 'Other1':
                columns = line.split('\t')
                assert len(columns) == 13
                raw_other['UnifiedName'], raw_other['Description'], \
                    _1,_2,_3,_4,_5,_6,_7,_8,_9,_10,_11 = columns
                assert not _1 or _2 or _3 or _4 or _5 or _6 or _7 or _8 or _9 or _10 or _11
                raw_other['Names'] = []
                in_data = 'Other2'
            elif in_data == 'Other2':
                if in_annotatedExamples and line.startswith('NOTES:'):
                    in_data = 'OtherNotes'
                else:
                    columns = line.split('\t')
                    assert len(columns) == 13
                    this = {}
                    this['Significance'], this['UniqueName'], this['Strongs'], this['Translations'], \
                        this['STEPBibleFirstLink'], this['AllRefs'], _1,_2,_3,_4,_5,_6,_7 = columns
                    assert not _1 or _2 or _3 or _4 or _5 or _6 or _7
                    raw_other['Names'].append(this)
            # elif in_data == 'OtherNotes':
            #     columns = line.split('\t')
            #     assert len(columns) == 13
            #     assert line.endswith('\t'*12) or line.endswith('\t\t\t\t\t\t>\t\t\t\t\t\t') # ie., all columns except the first are blank
            #     assert columns[0]
            #     try: raw_other['Notes'] = f"{raw_other['Notes']}\\n{columns[0]}" # Add line with escaped newline
            #     except KeyError: raw_other['Notes'] = columns[0]
            elif line == '$========== PERSON(s)\t\t\t\t\t\t\t\t\t\t\t\t':
                in_data = 'Person1'
                raw_person = {}
            elif line == '$========== PLACE\t\t\t\t\t\t\t\t\t\t\t\t':
                in_data = 'Place1'
                raw_place = {}
            elif line == '$========== OTHER\t\t\t\t\t\t\t\t\t\t\t\t':
                in_data = 'Other1'
                raw_other = {}
            else:
                xml_lines.append(f"<-- {line} -->")

    vPrint('Quiet', debuggingThisModule, f"    {j:,} lines loaded from TIPNR TSV.")
    return True
# end of loadTIPNR.load_TIPNR_data()


def process_and_add_person( raw_data: dict) -> bool:
    """
    We don't append a numerical suffix for the first entry we find.
    However, if the same name is used for another person, we append suffixes starting with 2.
    So might end up with "Fred, Fred2, Fred3" here.
    (Later we will convert that to "Fred1, Fred2, Fred3"
        and if Fred3 is the most well-known one, to "Fred1, Fred2, Fred".)
    """
    # fnPrint(debuggingThisModule, f"\nprocess_and_add_person( {raw_data} )")
    new_person = {}

    # UnifiedName is something like 'Aaron@Exo.4.14=H0175'
    # UniqueName can be something like 'wielded|Adino@2Sa.23.8'
    unifiedName, uStrongs = raw_data['UnifiedName'].split('=')
    del raw_data['UnifiedName']
    name = unifiedName.split('@')[0]
    if name not in people:
        FGid = name
    else:
        for suffix in range(2,30): # see Azariah (19x) and Maaseiah (20x) and Shemaiah (26x) and Zechariah (29x)
            if f'{name}{suffix}' not in people:
                FGid = f'{name}{suffix}'
                break
        else: unable_to_create_unique_person_id
    new_person['FGid'] = FGid
    new_person['name'] = name
    new_person['unifiedNameTIPNR'] = unifiedName
    # if unifiedName != uniqueName:
    #     dPrint('Normal', debuggingThisModule, f"  Person '{FGid}' {unifiedName=} vs {uniqueName=}")
    #     new_person['uniqueNameTIPNR'] = uniqueName
    new_person['uStrongs'] = uStrongs

    if raw_data['Description']:
        new_person['description'] = raw_data['Description']
    del raw_data['Description']
    if raw_data['SummaryDescription']:
        new_person['summaryDescription'] = raw_data['SummaryDescription'][1:] if raw_data['SummaryDescription'].startswith('#') else raw_data['SummaryDescription']
    del raw_data['SummaryDescription']
    if raw_data['Parents']:
        if raw_data['Parents'] == '=+': pass
        elif ' + ' in raw_data['Parents']:
            new_person['father'], new_person['mother'] = raw_data['Parents'].split(' + ')
        elif raw_data['Parents'].startswith('=+ '):
            new_person['mother'] = raw_data['Parents'][3:]
        elif raw_data['Parents'].endswith(' +'):
            new_person['father'] = raw_data['Parents'][:-2]
        elif raw_data['Parents'] == '#ERROR!': # original spreadsheet error!!!
            logging.critical(f"Ignoring spreadsheet #ERROR! for {unifiedName} parents.")
        else: not_done
    del raw_data['Parents']
    if 'Siblings' in raw_data:
        assert raw_data['Siblings']
        new_person['siblings'] = raw_data['Siblings'].split(', ')
        del raw_data['Siblings']
    if 'Partners' in raw_data:
        assert raw_data['Partners']
        new_person['partners'] = raw_data['Partners'].split(', ')
        del raw_data['Partners']
    if 'Offspring' in raw_data:
        assert raw_data['Offspring']
        new_person['offspring'] = raw_data['Offspring'].split(', ')
        del raw_data['Offspring']
    if 'Tribe/Nation' in raw_data:
        assert raw_data['Tribe/Nation']
        new_person['tribe/nation'] = raw_data['Tribe/Nation']
        del raw_data['Tribe/Nation']

    for raw_name_data in raw_data['Names']:
        # dPrint('Normal', debuggingThisModule, f"  Person {raw_name_data=}")
        if 'names' not in new_person:
            new_person['names'] = []
        new_person_name = {}

        if raw_name_data['Significance']:
            new_person_name['significance'] = raw_name_data['Significance']
        del raw_name_data['Significance']
        if raw_name_data['UniqueName']:
            new_person_name['uniqueNameTIPNR'] = raw_name_data['UniqueName']
        del raw_name_data['UniqueName']

        if raw_name_data['Strongs']:
            if '+' in raw_name_data['Strongs']: # it's a multi-word name like Bath-shua
                word1Info, word2Info = raw_name_data['Strongs'].split('+')
                dStrongs1, rest1 = word1Info.split('«')
                eStrongs1, sourceWord1 = rest1.split('=')
                dStrongs2, rest2 = word2Info.split('«')
                eStrongs2, sourceWord2 = rest2.split('=')
                new_person_name['dStrongs'] = [dStrongs1, dStrongs2]
                new_person_name['eStrongs'] = [eStrongs1, eStrongs2]
                new_person_name['sourceWord'] = [sourceWord1, sourceWord2]
            elif '«' in raw_name_data['Strongs']: # normal case -- a single word with three parts
                new_person_name['dStrongs'], rest = raw_name_data['Strongs'].split('«')
                new_person_name['eStrongs'], new_person_name['sourceWord'] = rest.split('=', 1) # Might be two equals / two words
            else: # special case -- a single word with two parts
                bits = raw_name_data['Strongs'].split('=')
                if bits[0]: new_person_name['dStrongs'] = bits[0] # or is it eStrongs? or both???
                if bits[1]: new_person_name['sourceWord'] = bits[1] # What does '.' mean???
        del raw_name_data['Strongs']

        translations = {}
        if raw_name_data['Translations'] and raw_name_data['Translations'] != '[ ]':
            raw_name_data['Translations'] = raw_name_data['Translations'].replace('JKV','KJV').replace('  ',' ') # Fix apparent error and double-space on Hanochite
            if raw_name_data['Translations'] == 'Joda (Var, KJV= Juda)':
                translations['ESV'] = translations['NIV'] = 'Joda (variant)'
                translations['Variant'] = 'Joda'
                translations['KJB'] = 'Juda'
            elif raw_name_data['Translations'].endswith(' (=Var, KJV)'):
                name = raw_name_data['Translations'][:-12]
                translations['ESV'] = translations['NIV'] = f'{name} (variant)'
                translations['KJB'] = name
            elif ' (=Qere, KJV= ' in raw_name_data['Translations'] and 'NIV' not in raw_name_data['Translations'] and 'ESV' not in raw_name_data['Translations']:
                assert raw_name_data['Translations'].endswith(')')
                qere, translations['KJB'] = raw_name_data['Translations'][:-1].split(' (=Qere, KJV= ')
                translations['ESV'] = translations['NIV'] = translations['Qere'] = qere
            elif raw_name_data['Translations'] == 'Moses (=LXX; KJV= Manasseh)':
                translations['ESV'] = translations['NIV'] = translations['LXX'] = 'Moses'
                translations['KJB'] = 'Manasseh'
            elif ' (Var, KJV, NIV= ' in raw_name_data['Translations']:
                assert raw_name_data['Translations'].endswith(')')
                translations['ESV'], other = raw_name_data['Translations'][:-1].split(' (Var, KJV, NIV= ')
                translations['variant'] = translations['KJB'] = translations['NIV'] = other
            elif 'Ketiv' in raw_name_data['Translations']:
                if raw_name_data['Translations'] == 'Birzaith (=Qere. Ketiv= Birzoth; KJV= Birzavith)':
                    translations['ESV'] = translations['ESV'] = 'Birzaith'
                    translations['Ketiv'] = 'Birzoth'
                    translations['KJB'] = 'Birzavith'
            elif 'ESV' not in raw_name_data['Translations'] and 'NIV' not in raw_name_data['Translations'] and 'KJV' not in raw_name_data['Translations']:
                if 'Qere' not in raw_name_data['Translations']: # The following two asserts fail on 'Ammihud (=Qere)'
                    assert '(' not in raw_name_data['Translations'] and ')' not in raw_name_data['Translations']
                    # assert ' ' not in raw_name_data['Translations'] # Fails on 'Canaanite woman'
                translations['ESV'] = translations['NIV'] = translations['KJB'] = raw_name_data['Translations']
            elif 'ESV' not in raw_name_data['Translations']:
                assert '(' in raw_name_data['Translations'] and ')' in raw_name_data['Translations']
                if 'KJV' not in raw_name_data['Translations']: # must be NIV
                    try: translations['ESV'], rest = raw_name_data['Translations'].split(' (NIV= ')
                    except ValueError: # missing space ???
                        translations['ESV'], rest = raw_name_data['Translations'].split(' (NIV=')
                    translations['KJB'] = translations['ESV']
                    assert rest.endswith(')')
                    translations['NIV'] = rest[:-1]
                elif 'NIV' not in raw_name_data['Translations']: # must be KJV
                    try: translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV= ')
                    except ValueError: # missing space ???
                        try: translations['ESV'], rest = raw_name_data['Translations'].split('(KJV= ')
                        except ValueError: # missing space ???
                            translations['ESV'], rest = raw_name_data['Translations'].split('(KJV=')
                    translations['NIV'] = translations['ESV']
                    assert rest.endswith(')')
                    translations['KJB'] = rest[:-1]
                else: # must be both
                    if '(KJV, NIV=' in raw_name_data['Translations']:
                        translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV, NIV= ')
                        assert rest.endswith(')')
                        translations['KJB'] = translations['NIV'] = rest[:-1]
                    elif raw_name_data['Translations'].index('KJV') < raw_name_data['Translations'].index('NIV'):
                        try: translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV= ')
                        except ValueError: # missing space ???
                            try: translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV=')
                            except ValueError: # missing space ???
                                translations['ESV'], rest = raw_name_data['Translations'].split('(KJV=')
                        assert rest.endswith(')')
                        try: translations['KJB'], translations['NIV'] = rest[:-1].split('; NIV= ')
                        except ValueError: # missing space ???
                            try: translations['KJB'], translations['NIV'] = rest[:-1].split('; NIV=')
                            except ValueError: translations['KJB'], translations['NIV'] = rest[:-1].split(', NIV=')
                    else: # NIV is listed first this time!
                        translations['ESV'], rest = raw_name_data['Translations'].split(' (NIV= ')
                        assert rest.endswith(')')
                        translations['NIV'], translations['KJV'] = rest[:-1].split('; KJV= ')
            else: # must have 'ESV' -- why???
                if raw_name_data['Translations'] == 'Ammi/-nadib (ESV= my kinsman, a prince; NIV= royal of my people)':
                    translations['ESV'] = 'Ammi-nadib (my kinsman, a prince)'
                    translations['NIV'] = 'Ammi-nadib (royal of my people)'
                    translations['KJB'] = 'Ammi-nadib'
                elif raw_name_data['Translations'] == 'Rapha (KJV, ESV= "giant")':
                    translations['ESV'] = translations['KJB'] = '"giant"'
                    translations['NIV'] = 'Rapha'
                elif raw_name_data['Translations'] == 'Raphaite (KJV, ESV= "giant")':
                    translations['ESV'] = translations['KJB'] = '"giant"'
                    translations['NIV'] = 'Raphaite'
                elif raw_name_data['Translations'] == 'Misgab (ESV= fortress; NIV= stronghold)':
                    translations['ESV'] = '"fortress"'
                    translations['NIV'] = '"stronghold"'
                    translations['KJB'] = 'Misgab'
                elif raw_name_data['Translations'].endswith(' (ESV, NIV= [ ])'):
                    translations['KJB'] = raw_name_data['Translations'][:-16]
                    translations['ESV'] = translations['NIV'] = ''
                else: not_done_yet
        if translations: new_person_name['translations'] = translations
        del raw_name_data['Translations']

        if raw_name_data['STEPBibleFirstLink']:
            new_person_name['STEPBibleFirstLink'] = raw_name_data['STEPBibleFirstLink']
        del raw_name_data['STEPBibleFirstLink']
        if raw_name_data['AllRefs']:
            new_person_name['individualVerseReferences'] = split_refs(raw_name_data['AllRefs'])
        del raw_name_data['AllRefs']
        assert not raw_name_data, f"Why do we have person left-over {raw_name_data=}?"
        if new_person_name:
            new_person['names'].append(new_person_name)
    del raw_data['Names']

    if 'Notes' in raw_data:
        assert raw_data['Notes']
        new_person['notes'] = raw_data['Notes']
        del raw_data['Notes']

    assert not raw_data, f"Why do we have person left-over {raw_data=}?"

    assert FGid not in people
    if FGid == 'Ben-Geber2':
        logging.critical("Have duplicate person 'Ben-Geber@1Ki.4.13' (Ben-Geber2)")
    else:
        people[FGid] = new_person # We use FGid as the key to create the original dicts
    # dPrint('Quiet', debuggingThisModule, f"\n{len(people)} {new_person=}")
    return True

def process_and_add_place( raw_data: dict) -> bool:
    """
    """
    # fnPrint(debuggingThisModule, f"\nprocess_and_add_place( {raw_data} )")
    new_place = {}

    # UnifiedName is something like 'Aaron@Exo.4.14=H0175'
    # UniqueName can be something like 'wielded|Adino@2Sa.23.8'
    unifiedName, uStrongs = raw_data['UnifiedName'].split('=')
    del raw_data['UnifiedName']
    name = unifiedName.split('@')[0]
    if name not in places:
        FGid = name
    else:
        for suffix in range(2,9):
            if f'{name}{suffix}' not in places:
                FGid = f'{name}{suffix}'
                break
        else: unable_to_create_unique_place_id
    new_place['FGid'] = FGid
    new_place['name'] = name
    new_place['unifiedNameTIPNR'] = unifiedName
    # if unifiedName != uniqueName:
    #     dPrint('Normal', debuggingThisModule, f"  Place '{FGid}' {unifiedName=} vs {uniqueName=}")
    #     new_place['uniqueNameTIPNR'] = uniqueName
    new_place['uStrongs'] = uStrongs

    if 'OpenBibleName' in raw_data:
        assert raw_data['OpenBibleName']
        new_place['OpenBibleName'] = raw_data['OpenBibleName']
        del raw_data['OpenBibleName']
    if 'Founder' in raw_data:
        assert raw_data['Founder']
        new_place['founder'] = raw_data['Founder']
        del raw_data['Founder']
    if 'People' in raw_data:
        assert raw_data['People']
        new_place['people'] = raw_data['People']
        del raw_data['People']
    if 'GoogleMapsURL' in raw_data:
        assert raw_data['GoogleMapsURL']
        new_place['GoogleMapsURL'] = raw_data['GoogleMapsURL']
        del raw_data['GoogleMapsURL']
    if 'PalopenMapsURL' in raw_data:
        assert raw_data['PalopenMapsURL']
        new_place['PalopenMapsURL'] = raw_data['PalopenMapsURL']
        del raw_data['PalopenMapsURL']
    if 'GeographicalArea' in raw_data:
        assert raw_data['GeographicalArea']
        new_place['geographicalArea'] = raw_data['GeographicalArea']
        del raw_data['GeographicalArea']

    for raw_name_data in raw_data['Names']:
        # dPrint('Normal', debuggingThisModule, f"  Place {raw_name_data=}")
        if 'names' not in new_place:
            new_place['names'] = []
        new_place_name = {}

        if raw_name_data['Significance']:
            new_place_name['significance'] = raw_name_data['Significance']
        del raw_name_data['Significance']
        if raw_name_data['UniqueName']:
            new_place_name['uniqueNameTIPNR'] = raw_name_data['UniqueName']
        del raw_name_data['UniqueName']

        if raw_name_data['Strongs']:
            if raw_name_data['Strongs'].endswith('+'):
                raw_name_data['Strongs'] = raw_name_data['Strongs'][:-1] # Fix apparent errors
            if '+' in raw_name_data['Strongs']: # it's a multi-word name like Achor_Valley
                try:
                    word1Info, word2Info = raw_name_data['Strongs'].split('+')
                    dStrongs1, rest1 = word1Info.split('«')
                    eStrongs1, sourceWord1 = rest1.split('=')
                    dStrongs2, rest2 = word2Info.split('«')
                    eStrongs2, sourceWord2 = rest2.split('=')
                    new_place_name['dStrongs'] = [dStrongs1, dStrongs2]
                    new_place_name['eStrongs'] = [eStrongs1, eStrongs2]
                    new_place_name['sourceWord'] = [sourceWord1, sourceWord2]
                except ValueError:
                    word1Info, word2Info, word3Info = raw_name_data['Strongs'].split('+')
                    if '«' in word1Info:
                        dStrongs1, rest1 = word1Info.split('«')
                        eStrongs1, sourceWord1 = rest1.split('=')
                    else:
                        eStrongs1, sourceWord1 = word1Info.split('=')
                        dStrongs1 = eStrongs1
                    dStrongs2, rest2 = word2Info.split('«')
                    eStrongs2, sourceWord2 = rest2.split('=')
                    dStrongs3, rest3 = word3Info.split('«')
                    eStrongs3, sourceWord3 = rest3.split('=')
                    new_place_name['dStrongs'] = [dStrongs1, dStrongs2, dStrongs3]
                    new_place_name['eStrongs'] = [eStrongs1, eStrongs2, eStrongs3]
                    new_place_name['sourceWord'] = [sourceWord1, sourceWord2, sourceWord3]
            elif '«' in raw_name_data['Strongs']: # normal case -- a single word with three parts
                new_place_name['dStrongs'], rest = raw_name_data['Strongs'].split('«')
                new_place_name['eStrongs'], new_place_name['sourceWord'] = rest.split('=')
            else: # normal case -- a single word with three parts
                bits = raw_name_data['Strongs'].split('=')
                if bits[0]: new_place_name['dStrongs'] = bits[0] # or is it eStrongs? or both???
                if bits[1]: new_place_name['sourceWord'] = bits[1] # What does '.' mean???
        del raw_name_data['Strongs']

        translations = {}
        if raw_name_data['Translations'] and raw_name_data['Translations'] != '[ ]':
            if raw_name_data['Translations'] == 'Put (KJV=Phut': # Fix missing closing parenthesis
                raw_name_data['Translations'] = 'Put (KJV=Phut)'
            if raw_name_data['Translations'] == 'Achshaph NIV= Akshaph)':
                translations['ESV'] = translations['KJB'] = 'Achshaph'
                translations['NIV'] = 'Akshaph'
            elif raw_name_data['Translations'] == 'city (=Ketiv. Qere, KJV, NIV= Ai)':
                translations['ESV'] = translations['Ketiv'] = '"city"'
                translations['Qere'] = translations['KJB'] = translations['NIV'] = 'Ai'
            elif raw_name_data['Translations'] == 'Bajith (ESV, NIV= temple)':
                translations['KJB'] = 'Bajith'
                translations['ESV'] = translations['NIV'] = '"temple"'
            elif raw_name_data['Translations'] == 'Beth-merchak (ESV= the last house; KJV= a place that was far off; NIV= the edge of the city)':
                translations['ESV'] = '"the last house"'
                translations['NIV'] = '"the edge of the city"'
                translations['KJB'] = '"a place that was far off"'
            elif raw_name_data['Translations'] == 'Chephar/-ammoni (=Ketiv. Qere= Chephar-ammonah; KJV= Chephar-haammonai; NIV= Kephar Ammoni)':
                translations['ESV'] = 'Chephar-ammoni'
                translations['Qere'] = 'Chephar-ammonah'
                translations['NIV'] = 'Kephar Ammoni'
                translations['KJB'] = 'Chephar-haammonai'
            elif ' (Var, KJV= ' in raw_name_data['Translations'] and 'NIV' not in raw_name_data['Translations'] and 'ESV' not in raw_name_data['Translations']:
                assert raw_name_data['Translations'].endswith(')')
                esv, kjv = raw_name_data['Translations'].split(' (Var, KJV= ')
                translations['ESV'] = translations['NIV'] = esv
                translations['variant'] = translations['KJB'] = kjv
            elif ' (=Qere, KJV= ' in raw_name_data['Translations'] and 'NIV' not in raw_name_data['Translations'] and 'ESV' not in raw_name_data['Translations']:
                assert raw_name_data['Translations'].endswith(')')
                qere, translations['KJB'] = raw_name_data['Translations'][:-1].split(' (=Qere, KJV= ')
                translations['ESV'] = translations['NIV'] = translations['Qere'] = qere
            elif raw_name_data['Translations'].endswith(' (ESV, NIV= [ ])'):
                translations['KJB'] = raw_name_data['Translations'][:-16]
                translations['ESV'] = translations['NIV'] = ''
            elif raw_name_data['Translations'] == 'Geruth/ Chimham (=Qere. Ketiv= Geruth like.them; KJV= habitation of Chimham; NIV= Geruth Kimham)':
                translations['ESV'] = 'Geruth Chimham'
                translations['Ketiv'] = 'Geruth like them'
                translations['NIV'] = 'Geruth Kimham'
                translations['KJB'] = 'habitation of Chimham'
            elif raw_name_data['Translations'] == 'Great( Sea) (=Qere. Ketiv= border; KJV= the great sea; NIV= Mediterranean Sea)':
                translations['ESV'] = translations['Qere'] = 'Great (Sea)'
                translations['Ketiv'] = '"border"'
                translations['KJB'] = 'the great sea'
                translations['NIV'] = 'Mediterranean Sea'
            elif raw_name_data['Translations'] == 'Jaan (ESV= Dan they went)': # not totally sure what this means
                translations['ESV'] = 'Dan they went'
                translations['KJB'] = translations['NIV'] = 'Jaan'
            elif ' (=Ketiv. Qere, KJV= ' in raw_name_data['Translations'] and 'ESV' not in raw_name_data['Translations']:
                assert raw_name_data['Translations'].endswith(')')
                ketiv, qere = raw_name_data['Translations'][:-1].split(' (=Ketiv. Qere, KJV= ')
                translations['ESV'] = translations['NIV'] = translations['Ketiv'] = ketiv
                translations['KJB'] = translations['Qere'] = qere
            elif raw_name_data['Translations'] == 'Tamar (=Ketiv. Qere, KJV, NIV= Tadmor)':
                translations['ESV'] = translations['Ketiv'] = 'Tamar'
                translations['KJB'] = translations['NIV'] = translations['Ketiv'] = 'Tadmor'
            elif raw_name_data['Translations'] == 'Zaanannim (=Qere. Ketiv, KJV= Zaanaim)':
                translations['ESV'] = translations['NIV'] = 'Zaanannim'
                translations['KJB'] = translations['Ketiv'] = 'Zaanaim'
            elif raw_name_data['Translations'] == 'Zaphon (KJV, ESV= north)':
                translations['KJB'] = translations['ESV'] = '"north"'
                translations['NIV'] = 'Zaphon'
            elif 'ESV' not in raw_name_data['Translations'] and 'NIV' not in raw_name_data['Translations'] and 'KJV' not in raw_name_data['Translations']:
                if 'Ketiv' not in raw_name_data['Translations']: # The following two asserts fail on 'Abana (=Ketiv)'
                    # assert '(' not in raw_name_data['Translations'] and ')' not in raw_name_data['Translations'] # Fails on '(Mount )Baalah'
                    # assert ' ' not in raw_name_data['Translations'] # Fails on 'Valley of Achor'
                    raw_name_data['Translations'] = raw_name_data['Translations'].replace('(Mount )Baalah','(Mount) Baalah')
                translations['ESV'] = translations['NIV'] = translations['KJB'] = raw_name_data['Translations']
            elif 'ESV' not in raw_name_data['Translations']:
                assert '(' in raw_name_data['Translations'] and ')' in raw_name_data['Translations']
                if 'KJV' not in raw_name_data['Translations']: # must be NIV
                    try: translations['ESV'], rest = raw_name_data['Translations'].split(' (NIV= ')
                    except ValueError: # missing space ???
                        translations['ESV'], rest = raw_name_data['Translations'].split(' (NIV=')
                    translations['KJB'] = translations['ESV']
                    assert rest.endswith(')')
                    translations['NIV'] = rest[:-1]
                elif 'NIV' not in raw_name_data['Translations']: # must be KJV
                    try: translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV= ')
                    except ValueError: # missing space ???
                        try: translations['ESV'], rest = raw_name_data['Translations'].split('(KJV= ')
                        except ValueError: # missing space ???
                            translations['ESV'], rest = raw_name_data['Translations'].split('(KJV=')
                    translations['NIV'] = translations['ESV']
                    assert rest.endswith(')')
                    translations['KJB'] = rest[:-1]
                else: # must be both
                    if '(KJV, NIV=' in raw_name_data['Translations']:
                        assert raw_name_data['Translations'].endswith(')')
                        try: translations['ESV'], rest = raw_name_data['Translations'][:-1].split(' (KJV, NIV= ')
                        except ValueError: # missing space ???
                            translations['ESV'], rest = raw_name_data['Translations'][:-1].split(' (KJV, NIV=')
                        translations['KJB'] = translations['NIV'] = rest[:-1]
                    else:
                        assert raw_name_data['Translations'].endswith(')')
                        try: translations['ESV'], rest = raw_name_data['Translations'][:-1].split(' (KJV= ')
                        except ValueError: # missing space ???
                            translations['ESV'], rest = raw_name_data['Translations'][:-1].split(' (KJV=')
                        try: translations['KJB'], translations['NIV'] = rest.split('; NIV= ')
                        except ValueError: # missing space ???
                            try: translations['KJB'], translations['NIV'] = rest.split('; NIV=')
                            except ValueError: translations['KJB'], translations['NIV'] = rest.split(', NIV=')
            # else: # must have 'ESV' -- why???
            #     if raw_name_data['Translations'] == 'Ammi/-nadib (ESV= my kinsman, a prince; NIV= royal of my people)':
            #         translations['ESV'] = 'Ammi-nadib (my kinsman, a prince)'
            #         translations['NIV'] = 'Ammi-nadib (royal of my people)'
            #         translations['KJB'] = 'Ammi-nadib'
            #     elif raw_name_data['Translations'] == 'Rapha (KJV, ESV= "giant")':
            #         translations['ESV'] = translations['KJB'] = '"giant"'
            #         translations['NIV'] = 'Rapha'
            #     elif raw_name_data['Translations'] == 'Misgab (ESV= fortress; NIV= stronghold)':
            #         translations['ESV'] = '"fortress"'
            #         translations['NIV'] = '"stronghold"'
            #         translations['KJB'] = 'Misgab'
            else: not_done_yet
        if translations: new_place_name['translations'] = translations
        del raw_name_data['Translations']

        if raw_name_data['STEPBibleFirstLink']:
            new_place_name['STEPBibleFirstLink'] = raw_name_data['STEPBibleFirstLink']
        del raw_name_data['STEPBibleFirstLink']
        if raw_name_data['AllRefs']:
            new_place_name['individualVerseReferences'] = split_refs(raw_name_data['AllRefs'])
        del raw_name_data['AllRefs']
        assert not raw_name_data, f"Why do we have place left-over {raw_name_data=}?"
        if new_place_name:
            new_place['names'].append(new_place_name)
    del raw_data['Names']

    if 'Comment' in raw_data:
        assert raw_data['Comment']
        new_place['comment'] = raw_data['Comment']
        del raw_data['Comment']
    if 'Notes' in raw_data:
        assert raw_data['Notes']
        new_place['notes'] = raw_data['Notes']
        del raw_data['Notes']

    assert not raw_data, f"Why do we have place left-over {raw_data=}?"

    assert FGid not in places
    places[FGid] = new_place # We use FGid as the key to create the original dicts
    # dPrint('Quiet', debuggingThisModule, f"\n{len(places)} {new_place=}")
    return True

def process_and_add_other( raw_data: dict) -> bool:
    """
    """
    # fnPrint(debuggingThisModule, f"\nprocess_and_add_other( {raw_data} )")
    new_other = {}

    # UnifiedName is something like 'Aaron@Exo.4.14=H0175'
    # UniqueName can be something like 'wielded|Adino@2Sa.23.8'
    if '=' in raw_data['UnifiedName']:
        unifiedName, uStrongs = raw_data['UnifiedName'].split('=')
    else: unifiedName = raw_data['UnifiedName'] # e.g., 'Herodian@Mat.22.16'
    del raw_data['UnifiedName']
    name = unifiedName.split('@')[0]
    if name not in others:
        FGid = name
    else:
        for suffix in range(2,9): # see
            if f'{name}{suffix}' not in others:
                FGid = f'{name}{suffix}'
                break
        else: unable_to_create_unique_other_id
    new_other['FGid'] = FGid
    new_other['name'] = name
    new_other['unifiedNameTIPNR'] = unifiedName
    # if unifiedName != uniqueName:
    #     dPrint('Normal', debuggingThisModule, f"  Other '{FGid}' {unifiedName=} vs {uniqueName=}")
    #     new_other['uniqueNameTIPNR'] = uniqueName
    try:
        new_other['uStrongs'] = uStrongs
    except UnboundLocalError: pass # no uStrongs, i.e., no '=' in first field

    if raw_data['Description']:
        new_other['description'] = raw_data['Description']
    del raw_data['Description']

    for raw_name_data in raw_data['Names']:
        # dPrint('Normal', debuggingThisModule, f"  Person {raw_name_data=}")
        if 'names' not in new_other:
            new_other['names'] = []
        new_other_name = {}

        if raw_name_data['Significance']:
            new_other_name['significance'] = raw_name_data['Significance']
        del raw_name_data['Significance']
        if raw_name_data['UniqueName']:
            new_other_name['uniqueNameTIPNR'] = raw_name_data['UniqueName']
        del raw_name_data['UniqueName']

        if raw_name_data['Strongs']:
            if raw_name_data['Strongs'] == 'G1673«G1673=Ἑλληνικός=Ἑλληνικός': # 'Greek'
                new_other_name['dStrongs'] = new_other_name['eStrongs'] = 'G1673'
                new_other_name['sourceWord'] = 'Ἑλληνικός'
            elif '+' in raw_name_data['Strongs']: # it's a multi-word name like El-berith
                word1Info, word2Info = raw_name_data['Strongs'].split('+')
                dStrongs1, rest1 = word1Info.split('«')
                eStrongs1, sourceWord1 = rest1.split('=', 1) # Might be two equals / two words
                dStrongs2, rest2 = word2Info.split('«')
                eStrongs2, sourceWord2 = rest2.split('=')
                new_other_name['dStrongs'] = [dStrongs1, dStrongs2]
                new_other_name['eStrongs'] = [eStrongs1, eStrongs2]
                new_other_name['sourceWord'] = [sourceWord1, sourceWord2]
            elif '«' in raw_name_data['Strongs']: # normal case -- a single word with three parts
                new_other_name['dStrongs'], rest = raw_name_data['Strongs'].split('«')
                new_other_name['eStrongs'], new_other_name['sourceWord'] = rest.split('=', 1) # Might be two equals / two words
            else: # special case -- a single word with two parts
                halt
                bits = raw_name_data['Strongs'].split('=')
                if bits[0]: new_other_name['dStrongs'] = bits[0] # or is it eStrongs? or both???
                if bits[1]: new_other_name['sourceWord'] = bits[1] # What does '.' mean???
        del raw_name_data['Strongs']

        translations = {}
        if raw_name_data['Translations'] and raw_name_data['Translations'] != '[ ]':
            if 'ESV' not in raw_name_data['Translations'] and 'NIV' not in raw_name_data['Translations'] and 'KJV' not in raw_name_data['Translations']:
                if 'Ketiv' not in raw_name_data['Translations']: # The following two asserts fail on 'Abana (=Ketiv)'
                    # assert '(' not in raw_name_data['Translations'] and ')' not in raw_name_data['Translations'] # Fails on '(Mount )Baalah'
                    # assert ' ' not in raw_name_data['Translations'] # Fails on 'Valley of Achor'
                    raw_name_data['Translations'] = raw_name_data['Translations'].replace('(Mount )Baalah','(Mount) Baalah')
                translations['ESV'] = translations['NIV'] = translations['KJB'] = raw_name_data['Translations']
            elif 'ESV' not in raw_name_data['Translations']:
                assert '(' in raw_name_data['Translations'] and ')' in raw_name_data['Translations']
                if 'KJV' not in raw_name_data['Translations']: # must be NIV
                    try: translations['ESV'], rest = raw_name_data['Translations'].split(' (NIV= ')
                    except ValueError: # missing space ???
                        translations['ESV'], rest = raw_name_data['Translations'].split(' (NIV=')
                    translations['KJB'] = translations['ESV']
                    assert rest.endswith(')')
                    translations['NIV'] = rest[:-1]
                elif 'NIV' not in raw_name_data['Translations']: # must be KJV
                    try: translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV= ')
                    except ValueError: # missing space ???
                        try: translations['ESV'], rest = raw_name_data['Translations'].split('(KJV= ')
                        except ValueError: # missing space ???
                            translations['ESV'], rest = raw_name_data['Translations'].split('(KJV=')
                    translations['NIV'] = translations['ESV']
                    assert rest.endswith(')')
                    translations['KJB'] = rest[:-1]
                else: # must be both
                    if '(KJV, NIV=' in raw_name_data['Translations']:
                        translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV, NIV= ')
                        assert rest.endswith(')')
                        translations['KJB'] = translations['NIV'] = rest[:-1]
                    else:
                        try: translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV= ')
                        except ValueError: # missing space ???
                            translations['ESV'], rest = raw_name_data['Translations'].split(' (KJV=')
                        assert rest.endswith(')')
                        try: translations['KJB'], translations['NIV'] = rest[:-1].split('; NIV= ')
                        except ValueError: # missing space ???
                            try: translations['KJB'], translations['NIV'] = rest[:-1].split('; NIV=')
                            except ValueError: translations['KJB'], translations['NIV'] = rest[:-1].split(', NIV=')
            else: # must have 'ESV' -- why???

                if raw_name_data['Translations'] == 'Gentiles (ESV, NIV= nations)':
                    translations['ESV'] = translations['NIV'] = '"nations"'
                    translations['KJB'] = 'Gentiles'
                elif raw_name_data['Translations'] == 'Gentiles (ESV, NIV= pagans)':
                    translations['ESV'] = translations['NIV'] = '"pagans"'
                    translations['KJB'] = 'Gentiles'
                elif raw_name_data['Translations'] == 'Gentiles (ESV, NIV= people)':
                    translations['ESV'] = translations['NIV'] = '"people"'
                    translations['KJB'] = 'Gentiles'
                elif raw_name_data['Translations'] == 'Gentiles (ESV, NIV= peoples)':
                    translations['ESV'] = translations['NIV'] = '"peoples"'
                    translations['KJB'] = 'Gentiles'
                elif raw_name_data['Translations'] == 'Gentiles (ESV= peoples; KJV= heathen)':
                    translations['NIV'] = 'Gentiles'
                    translations['ESV'] = '"peoples"'
                    translations['KJB'] = '"heathen"'
                elif raw_name_data['Translations'] == 'Gentiles (ESV= nations)':
                    translations['NIV'] = translations['KJB'] = 'Gentiles'
                    translations['ESV'] = '"nations"'
                elif raw_name_data['Translations'] == 'Peor (ESV, NIV= Baal of Peor)':
                    translations['ESV'] = translations['NIV'] = 'Baal of Peor'
                    translations['KJB'] = 'Peor'
                elif raw_name_data['Translations'].endswith(' (ESV, NIV= [ ])'):
                    translations['KJB'] = raw_name_data['Translations'][:-16]
                    translations['ESV'] = translations['NIV'] = ''
                else: not_done_yet
        if translations: new_other_name['translations'] = translations
        del raw_name_data['Translations']

        if raw_name_data['STEPBibleFirstLink']:
            new_other_name['STEPBibleFirstLink'] = raw_name_data['STEPBibleFirstLink']
        del raw_name_data['STEPBibleFirstLink']
        if raw_name_data['AllRefs']:
            new_other_name['individualVerseReferences'] = split_refs(raw_name_data['AllRefs'])
        del raw_name_data['AllRefs']
        assert not raw_name_data, f"Why do we have other left-over {raw_name_data=}?"
        if new_other_name:
            new_other['names'].append(new_other_name)
    del raw_data['Names']

    if 'Notes' in raw_data:
        assert raw_data['Notes']
        new_other['notes'] = raw_data['Notes']
        del raw_data['Notes']

    assert not raw_data, f"Why do we have other left-over {raw_data=}?"

    assert FGid not in others
    others[FGid] = new_other # We use FGid as the key to create the original dicts
    # dPrint('Quiet', debuggingThisModule, f"\n{len(others)} {new_other=}")
    return True


def split_refs(ref_string:str) -> List[str]:
    """
    Take a string of Bible references separated by semicolons
        and return a tidied list of separated references.
    """
    ref_string = ref_string.rstrip(';') # Remove unnecessary final delimiter
    ref_string = ref_string.replace(' ','') # Remove all spaces for consistency
    ref_string = ref_string.replace('Eze','Ezk') # Fix human inconsistencies
    ref_string = ref_string.replace('Gen.1:1','Gen.1.1') # Fix human inconsistencies
    ref_string = ref_string.replace(';Etc.00','') # Fix unexpected entry
    ref_string = ref_string.replace(';Etc.0.0','') # Fix unexpected entry
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
    vPrint('Quiet', debuggingThisModule, "\nCleaning TIPNR datasets…")

    for dict_name,the_dict in (('people',people), ('places',places), ('others',others)):
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
                    elif isinstance(subData, list): # e.g., siblings, partners, offspring, names
                        for sub2Data in subData:
                            assert sub2Data
                            # if subKey == 'names':
                            #     dPrint('Quiet', debuggingThisModule, f"    ({len(sub2Data)}) {sub2Data}")
                            if isinstance(sub2Data, str):
                                assert sub2Data and sub2Data!='>'
                                assert sub2Data.strip() == sub2Data and '  ' not in sub2Data # Don't want leading or trailing whitespace
                            else: # dict
                                for sub3Key, sub3Data in sub2Data.items():
                                    # dPrint('Quiet', debuggingThisModule, f"    {mainKey=} {subKey=} {sub3Key=} ({len(sub3Data)}) {sub3Data=}")
                                    assert sub3Key and sub3Data and sub3Key!='>'
                                    assert isinstance(sub3Key, str)
                                    assert sub3Key.strip() == sub3Key and '  ' not in sub3Key # Don't want leading or trailing whitespace
                                    if isinstance(sub3Data, str):
                                        assert sub3Data and sub3Data!='>'
                                        if '  ' in sub3Data:
                                            dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} {sub3Key=} '{sub3Data}'")
                                            sub2Data[sub3Key] = sub3Data = sub3Data.replace('  ',' ')
                                        assert sub3Data.strip() == sub3Data and '  ' not in sub3Data # Don't want leading or trailing whitespace
                                    elif isinstance(sub3Data, list):
                                        assert subKey == 'names'
                                        for j3,sub4Data in enumerate(sub3Data):
                                            assert sub4Key and sub4Data
                                            assert sub4Key!='>' and sub4Data!='>'
                                            assert isinstance(sub4Data, str)
                                            # print(f"{mainKey=} {subKey=} {sub3Key=} {sub4Data=}")
                                            if sub4Data.endswith(' '):
                                                logging.critical(f"What is {mainKey=} {subKey=} {sub3Key=} {sub4Data=}")
                                            else:
                                                # print(f"{mainKey=} {subKey=} {sub3Key=} {sub4Data=}")
                                                if sub4Data.startswith(' '):
                                                    dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} {sub3Key=} '{sub4Data}'")
                                                    sub4Data = sub4Data[1:]
                                                assert sub4Data.strip() == sub4Data and '  ' not in sub4Data # Don't want leading or trailing whitespace
                                            if sub3Key == 'individualVerseReferences':
                                                if sub4Data.endswith(' ;'):
                                                    dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} {sub3Key=} '{sub4Data}'")
                                                    sub3Data[j3] = sub4Data = sub4Data[:-2]
                                                elif sub4Data.endswith(';'):
                                                    dPrint('Verbose', debuggingThisModule, f"    Cleaning {mainKey=} {subKey=} {sub3Key=} '{sub4Data}'")
                                                    sub3Data[j3] = sub4Data = sub4Data[:-1]
                                                if sub4Data.endswith(' '):
                                                    dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} {sub3Key=} '{sub4Data}'")
                                                    sub3Data[j3] = sub4Data = sub4Data[:-1]
                                                # print(f"{mainKey=} {subKey=} {sub3Key=} {sub4Data=}")
                                                assert sub4Data.strip() == sub4Data and '  ' not in sub4Data # Don't want leading or trailing whitespace
                                    else:
                                        for sub4Key, sub4Data in sub3Data.items():
                                            # dPrint('Quiet', debuggingThisModule, f"    {mainKey=} {subKey=} {sub3Key=} {sub4Key=} ({len(sub4Data)}) {sub4Data=}")
                                            assert sub4Key and sub4Key!='>'
                                            if sub3Key != 'translations': # Translations can have empty strings to indicate where
                                                assert sub4Data           #     some words are not actually in the translation.
                                            assert isinstance(sub4Key, str)
                                            assert sub4Key.strip() == sub4Key and '  ' not in sub4Key # Don't want leading or trailing whitespace
                                            assert isinstance(sub4Data, str) and sub4Data!='>'
                                            if sub4Data.startswith(' '):
                                                dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} {sub3Key=} {sub4Key=} '{sub4Data}'")
                                                sub3Data[sub4Key] = sub4Data = sub4Data[1:]
                                            if sub4Data.endswith(' '):
                                                dPrint('Info', debuggingThisModule, f"  Cleaning {mainKey=} {subKey=} {sub3Key=} {sub4Key=} '{sub4Data}'")
                                                sub3Data[sub4Key] = sub4Data = sub4Data[:-1]
                                            # print(f"{mainKey=} {subKey=} {sub3Key=} {sub4Key=} {sub4Data=}")
                                            assert sub4Data.strip() == sub4Data and '  ' not in sub4Data # Don't want leading or trailing whitespace
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
                                    assert isinstance(sub3Data, list)
                                    for sub4Data in sub3Data:
                                        assert sub4Data
                                        assert isinstance(sub4Data, str) and sub4Data!='>'
                                        assert sub4Data.strip() == sub4Data and '  ' not in sub4Data # Don't want leading or trailing whitespace

    return True
# end of loadTIPNR.clean_data()


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
    global prefixed_our_IDs
    vPrint('Quiet', debuggingThisModule, "\nNormalising TIPNR datasets…")

    for dict_name,the_dict in (('people',people), ('places',places), ('others',others)):
        vPrint('Normal', debuggingThisModule, f"  Normalising {dict_name}…")
        normalise_significance(dict_name, the_dict)
        create_combined_name_verse_references(dict_name, the_dict)
        adjust_Bible_references(dict_name, the_dict)
        ensure_best_known_name(dict_name, the_dict)
        if PREFIX_OUR_IDS_FLAG: prefix_our_IDs(dict_name, the_dict)
        adjust_links_from_TIPNR_to_our_IDs(dict_name, the_dict)

    if PREFIX_OUR_IDS_FLAG: prefixed_our_IDs = True
    return True
# end of loadTIPNR.normalise_data()


def normalise_significance(dataName:str, dataDict:dict) -> bool:
    """
    Change signficance '- Named' to 'named', etc.

   Normalising people significance…
        Had '- Named': 3271, 'Greek': 114, '- (same as previous)': 218, '- Group': 189,
            '- Spelled': 58, '- Aramaic': 32, '- Name Combined': 5, '- Mentioned': 43
        Now 'named': 3271, 'Greek': 114, '(same as previous)': 218, 'group': 189,
            'spelled': 58, 'Aramaic': 32, 'name combined': 5, 'mentioned': 43

   Normalising places significance…
        Fixed places Bamoth-baal name_dict['significance']='- Name' to 'named'
        Fixed places Cherub name_dict['significance']='- Greek' to 'Greek'
        Fixed places Colossae name_dict['significance']='- Spelling' to 'spelled'
        Had '- Named': 1136, '- (same as previous)': 188, 'Greek': 59, '- Name Combined': 90,
            '- Group': 80, '- Spelled': 71, '- Aramaic': 10, '- Name': 1, '- Greek': 1,
            '- Spelling': 1, '- Spelled Combined': 2, '- Aramaic+Combined': 1
        Now 'named': 1137, '(same as previous)': 188, 'Greek': 60, 'name combined': 90,
            'group': 80, 'spelled': 72, 'Aramaic': 10, 'spelled combined': 2, 'Aramaic combined': 1

    Normalising others significance…
        Had '- Named': 142, '- (same as previous)': 48, '- Aramaic': 4, 'Greek': 12,
                    '- Form': 2, '- Name Combined': 3, '- Group': 2, '- Spelled': 6
        Now 'named': 142, '(same as previous)': 48, 'Aramaic': 4, 'Greek': 12,
                    'form': 2, 'name combined': 3, 'group': 2, 'spelled': 6
    """
    vPrint('Normal', debuggingThisModule, f"    Normalising {dataName} significance…")
    original_counts = defaultdict(int)
    new_counts = defaultdict(int)
    for entry,data in dataDict.items():
        for name_dict in data['names']:
            # dPrint('Info', debuggingThisModule, f"      {entry} ({len(name_dict)}) {name_dict['significance']=}")
            original_counts[name_dict['significance']] += 1
            if name_dict['significance'] == '- Named': name_dict['significance'] = 'named'
            elif name_dict['significance'] == '- Name': # is this an error?
                dPrint('Quiet', debuggingThisModule, f"      Fixed {dataName} {entry} {name_dict['significance']=} to 'named'")
                name_dict['significance'] = 'named'
            elif name_dict['significance'] == '- Name Combined': name_dict['significance'] = 'name combined'
            elif name_dict['significance'] == '- Mentioned': name_dict['significance'] = 'mentioned'
            elif name_dict['significance'] == '- Spelled': name_dict['significance'] = 'spelled'
            elif name_dict['significance'] == '- Spelled Combined': name_dict['significance'] = 'spelled combined'
            elif name_dict['significance'] == '- Spelling': # is this an error?
                dPrint('Quiet', debuggingThisModule, f"      Fixed {dataName} {entry} {name_dict['significance']=} to 'spelled'")
                name_dict['significance'] = 'spelled'
            elif name_dict['significance'] == '- Form': name_dict['significance'] = 'form'
            elif name_dict['significance'] == '- Group': name_dict['significance'] = 'group'
            elif name_dict['significance'] == '- (same as previous)': name_dict['significance'] = '(same as previous)'
            elif name_dict['significance'] == '- Aramaic': name_dict['significance'] = 'Aramaic'
            elif name_dict['significance'] == '- Aramaic+Combined': name_dict['significance'] = 'Aramaic combined'
            elif name_dict['significance'] == '- Greek': # is this an error?
                dPrint('Quiet', debuggingThisModule, f"      Fixed {dataName} {entry} {name_dict['significance']=} to 'Greek'")
                name_dict['significance'] = 'Greek'
            elif name_dict['significance'] != 'Greek': unexpected_significance
            new_counts[name_dict['significance']] += 1

    vPrint('Normal', debuggingThisModule, f"""      Had {str(original_counts).replace("defaultdict(<class 'int'>, {",'').replace('})','')}""")
    vPrint('Normal', debuggingThisModule, f"""      Now {str(new_counts).replace("defaultdict(<class 'int'>, {",'').replace('})','')}""")
    return True
# end of loadTIPNR.normalise_significance()


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
# end of loadTIPNR.create_combined_name_verse_references()


def adjust_Bible_references(dataName:str, dataDict:dict) -> bool:
    """
    Change Bible references like '1Co.1.14' to 'CO1_1:14'

    There might be a's or b's at the end of the verse number.
    """
    vPrint('Normal', debuggingThisModule, f"    Adjusting all verse references for {dataName}…")
    for dict_entry in dataDict.values():
        for name_data in dict_entry['names']:
            for j,ref_string in enumerate(name_data['individualVerseReferences']):
                name_data['individualVerseReferences'][j] = adjust_Bible_reference(ref_string)
        if 'combinedIndividualVerseReferences' in dict_entry:
            for j,ref_string in enumerate(dict_entry['combinedIndividualVerseReferences']):
                dict_entry['combinedIndividualVerseReferences'][j] = adjust_Bible_reference(ref_string)

    return True
# end of loadTIPNR.adjust_Bible_references()


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
    ix = list(Uuu_BOOK_ID_MAP.values()).index(Uuu) + 1
    adjRef = f'{pre}{BOS_BOOK_ID_MAP[ix]}{adjRef[3:]}{post}'
    # print(f"Converted '{ref}' to '{adjRef}'")
    return adjRef
# end of loadTIPNR.adjust_Bible_reference


def ensure_best_known_name(dataName:str, dataDict:dict) -> bool:
    """
    If a name only occurs once, we use the name as the key, e.g., persons 'Abdiel' or 'David'.
    But if there are multiple people/places with the same name, the above code uses suffixes,
        e.g.,   Joshua1, Joshua2, Joshua3.
    However, in this case, Joshua2 is the most well-known character and so we want to end up with
                Joshua1, Joshua, Joshua3.
    This is done by comparing the number of verse references.

    Note: This only changes the internal records, not the actual dictionary keys.
    """
    vPrint('Normal', debuggingThisModule, f"    Normalising {dataName} to ensure best known name…")
    for dict_entry in dataDict.values():
        old_id = dict_entry['FGid'] # Which may or may not match the original key by now
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
# end of loadTIPNR.ensure_best_known_name()


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
    for dict_entry in dataDict.values():
        old_id = dict_entry['FGid']
        new_id = f'{default_prefix}{old_id}'
        # dPrint('Info', debuggingThisModule, f"      {old_id=} {new_id=}")
        dict_entry['FGid'] = new_id
        # assert dataDict[key]['FGid'] == new_id
        # We only save the prefixed ID internally -- will fix the keys later

    return True
# end of loadTIPNR.prefix_our_IDs()


def adjust_links_from_TIPNR_to_our_IDs(dataName:str, dataDict:dict) -> bool:
    """
    Change individual people references (like father, mother)
        and list of people references (like parents, siblings, partners, etc.)
        to our FGid fields (without @bibleRef parts).
    """
    vPrint('Normal', debuggingThisModule, f"    Normalising all internal ID links for {dataName}…")

    # Firstly create a cross-index to FGid's
    unique_name_index = { v['unifiedNameTIPNR']:v['FGid'] for k,v in dataDict.items() }

    # Now make any necessary adjustments
    for dict_entry in dataDict.values():
        for fieldName in ('father','mother'): # single entries
            if fieldName in dict_entry:
                field_string = dict_entry[fieldName]
                assert isinstance(field_string, str)
                assert len(field_string) >= 10 # ww.GEN.1.1
                assert field_string.count('@') == 1
                pre = post = ''
                if field_string.endswith('(?)') or field_string.endswith('(d)'):
                    field_string, post = field_string[:-3], field_string[-3:]
                elif field_string.endswith('(d?)'):
                    field_string, post = field_string[:-4], field_string[-4:]
                dict_entry[fieldName] = f'{pre}{unique_name_index[field_string]}{post}'
        for fieldName in ('siblings','partners','offspring'): # list entries
            if fieldName in dict_entry:
                assert isinstance(dict_entry[fieldName], list)
                for j,field_string in enumerate(dict_entry[fieldName]):
                    assert len(field_string) >= 10 # ww.GEN.1.1
                    assert field_string.count('@') == 1
                    pre = post = ''
                    if field_string.endswith('(?)'):
                        field_string, post = field_string[:-3], field_string[-3:]
                    dict_entry[fieldName][j] = f'{pre}{unique_name_index[field_string]}{post}'

    return True
# end of loadTIPNR.adjust_links_from_TIPNR_to_our_IDs()


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
    assert key_name in ('unifiedNameTIPNR', 'FGid')

    # These rebuilds retain the original entry orders
    for dict_name,the_dict in (('people',people), ('places',places), ('others',others)):
        old_length = len(the_dict)-1 if '__HEADERS__' in the_dict else len(the_dict)
        new_dict = { v[key_name]:v for k,v in the_dict.items() if k!='__HEADERS__' }
        the_dict.clear()            # We do it this way so that we update the existing (global) dict
        the_dict.update(new_dict)   #  rather than creating an entirely new dict
        if len(the_dict) != old_length:
            logging.critical(f"rebuild_dictionaries({key_name}) for {dict_name} unexpectedly went from {old_length} entries to {len(the_dict)}")

    if prefixed_our_IDs: # We can safely combine the three dictionaries into one
        global allEntries
        allEntries = people | places | others
        dPrint('Quiet', debuggingThisModule, f"    Got {len(allEntries):,} entries from {len(people):,} + {len(places):,} + {len(others):,} = {len(people)+len(places)+len(others):,}")

    return True
# end of loadTIPNR.rebuild_dictionaries


def check_data() -> bool:
    """
    Check closed sets like signficance, translation keys, etc.

    Create stats for numbered and non-numbered people, places, etc.
    """
    vPrint('Quiet', debuggingThisModule, "\nCross-checking TIPNR datasets…")

    for dict_name,the_dict in (('people',people), ('places',places), ('others',others)):
        vPrint('Normal', debuggingThisModule, f"  Cross-checking {dict_name}…")
    return True
# end of loadTIPNR.check_data()


def export_JSON(subType:str) -> bool:
    """
    Export the dictionaries as JSON.
    """
    assert subType
    vPrint('Quiet', debuggingThisModule, f"\nExporting {subType} JSON TIPNR files…")

    for dict_name,the_dict in (('people',people), ('places',places), ('others',others), ('all',allEntries)):
        if the_dict:
            filepath = TIPNR_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}.json')
            vPrint( 'Quiet', debuggingThisModule, f"  Exporting {len(the_dict):,} {dict_name} to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                # WARNING: The following code would convert any int keys to str !!!
                json.dump( HEADER_DICT | the_dict, outputFile, ensure_ascii=False, indent=2 )

    return True
# end of loadTIPNR.export_JSON()


def export_xml(subType:str) -> bool:
    """
    """
    assert subType
    vPrint('Quiet', debuggingThisModule, f"\nExporting {subType} XML TIPNR file…")

    vPrint( 'Quiet', debuggingThisModule, f"  NOT Wrote {len(xml_lines):,} XML lines.")
    return True
# end of loadTIPNR.export_xml()


def export_verse_index() -> bool:
    """
    Pivot the data to determine which names exist in each verse,
        and save this in JSON.
    """
    vPrint('Quiet', debuggingThisModule, f"\nCalculating and exporting index files…")
    subType = 'normalised'
    for dict_name,the_dict in (('people',people), ('places',places), ('others',others), ('all',allEntries)):
        ref_index_dict = defaultdict(list)
        TIPNR_index_dict = {}
        for jj, value in enumerate(the_dict.values()):
            if jj == 0 and len(value)==len(HEADER_DICT) and 'conversion_software' in value: # it's our __HEADERS__ entry
                continue

            FGid = value['FGid']
            ref_list = value['combinedIndividualVerseReferences'] if 'combinedIndividualVerseReferences' in value \
                        else value['names'][0]['individualVerseReferences']
            for ref in ref_list:
                ref_index_dict[ref].append(FGid)
            unifiedNameTIPNR = value['unifiedNameTIPNR']
            TIPNR_index_dict[unifiedNameTIPNR] = FGid
            for name in value['names']:
                uniqueNameTIPNR = name['uniqueNameTIPNR']
                if uniqueNameTIPNR != unifiedNameTIPNR:
                    if uniqueNameTIPNR in TIPNR_index_dict:
                        if TIPNR_index_dict[uniqueNameTIPNR] != FGid:
                            print(f"Why do we already have {TIPNR_index_dict[uniqueNameTIPNR]} for {uniqueNameTIPNR} now wanting {FGid}")
                    else: TIPNR_index_dict[uniqueNameTIPNR] = FGid

        # Save the dicts as JSON files
        if ref_index_dict:
            filepath = TIPNR_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}_verseRef_index.json')
            vPrint( 'Quiet', debuggingThisModule, f"  Exporting {len(ref_index_dict):,} verse ref index entries to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                json.dump( HEADER_DICT | ref_index_dict, outputFile, ensure_ascii=False, indent=2 )
        if TIPNR_index_dict:
            filepath = TIPNR_OUTPUT_FOLDERPATH.joinpath(f'{subType}_{dict_name.title()}_TIPNR_index.json')
            vPrint( 'Quiet', debuggingThisModule, f"  Exporting {len(TIPNR_index_dict):,} TIPNR index entries to {filepath}…")
            with open( filepath, 'wt', encoding='utf-8' ) as outputFile:
                json.dump( HEADER_DICT | TIPNR_index_dict, outputFile, ensure_ascii=False, indent=2 )

    return True
# end of loadTIPNR.export_verse_index()


if __name__ == '__main__':
    # from multiprocessing import freeze_support
    # freeze_support() # Multiprocessing support for frozen Windows executables

    # Configure basic Bible Organisational System (BOS) set-up
    parser = BibleOrgSysGlobals.setup( SHORT_PROGRAM_NAME, PROGRAM_VERSION, LAST_MODIFIED_DATE )
    BibleOrgSysGlobals.addStandardOptionsAndProcess( parser )

    main()
    print()

    BibleOrgSysGlobals.closedown( PROGRAM_NAME, PROGRAM_VERSION )
# end of loadTIPNR.py
