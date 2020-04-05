# -*- coding: utf-8 -*-

"""Chemical relation curation utilities."""

import logging
import os
from typing import Set

import pandas as pd
import requests

logger = logging.getLogger(__name__)

HERE = os.path.abspath(os.path.dirname(__file__))
RESOURCES_DIRECTORY = os.path.join(HERE, 'resources')
EXPORT_DIRECTORY = os.path.join(HERE, 'export')

#: Path to xrefs.tsv
XREFS_PATH = os.path.join(RESOURCES_DIRECTORY, 'xrefs.tsv')
XREFS_COLUMNS = [
    'source_db', 'source_id', 'source_name',
    'modulation',
    'target_type', 'target_db', 'target_id', 'target_name',
]


def get_xrefs_df() -> pd.DataFrame:
    """Get xrefs.tsv."""
    logger.info('reading xrefs from %s', XREFS_PATH)
    return pd.read_csv(XREFS_PATH, sep='\t', comment='#', dtype=str)


def sort_xrefs_df() -> None:
    """Sort xrefs.tsv."""
    df = get_xrefs_df()
    df = df.sort_values(['source_db', 'source_name', 'modulation'])
    df = df.drop_duplicates()
    df.to_csv(XREFS_PATH, index=False, sep='\t')


#: The base URL of the GILDA service
GILDA_URL = 'http://grounding.indra.bio'


def post_gilda(text: str, url: str = GILDA_URL) -> requests.Response:
    """Send text to GILDA."""
    return requests.post(f'{url}/ground', json={'text': text})


def get_single_mappings(df: pd.DataFrame, idx) -> Set:
    """Get ChEBI identifiers that are only mapped to one thing based on slicing the dataframe on the given index."""
    errors = set()
    chebi_ids = sorted(df.loc[idx, 'source_id'].unique())
    for chebi_id, sdf in df[df['source_id'].isin(chebi_ids)].groupby(['source_id']):
        if 1 != len(sdf.index):
            pass  # print(chebi_id, 'multiple!')
        else:
            target_id, target_name = list(sdf[['target_id', 'target_name']].values)[0]
            print(chebi_id, 'only mapped to', target_id, target_name)
            errors.add((chebi_id, target_id, target_name))
    return errors
