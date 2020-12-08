import logging
import pickle
import json
from collections import defaultdict
from functools import lru_cache

from simstring.feature_extractor.character_ngram import CharacterNgramFeatureExtractor
from simstring.measure.cosine import CosineMeasure
from simstring.database.dict import DictDatabase
from simstring.searcher import Searcher


from utils import yake_tokenizer
from utils import normalize_str
from utils import remove_dupes


logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%d-%b-%y %H:%M:%S')



class SimString_UMLS(object):

    def __init__(self, db_path, cui_mapping_path, alpha=0.5):
        self.db = None
        self.cui_mapping = None
        self.searcher = None
        self.alpha = alpha

        self.load(db_path, cui_mapping_path)

    def load(self, db_path, cui_mapping_path):

        logging.info('Loading DB ...')
        with open(db_path, 'rb') as db_f:
            self.db = pickle.load(db_f)
        
        logging.info('Loading Mapping ...')
        with open(cui_mapping_path, 'rb') as mapping_f:
            self.cui_mapping = pickle.load(mapping_f)

        logging.info('Creating Searcher ...')
        self.searcher = Searcher(self.db, CosineMeasure())

    @lru_cache(1024)
    def match(self, text):
        results = self.searcher.ranked_search(text, alpha=self.alpha)
        results = [(a, sim) for sim, a in results]  # to be consistent with other matchers
        return results

    def match_cuis(self, text, alpha=None):
        alias_results = self.match(text)

        if alpha is None:
            alpha = self.alpha

        cui_results = []
        included_cuis = set()
        for alias, sim in alias_results:
            for cui in self.cui_mapping[alias]:
                if cui not in included_cuis:
                    if sim > alpha:
                        cui_results.append((cui, alias, sim))
                        included_cuis.add(cui)

        # sort first by similarity, then by CUI number
        cui_results = sorted(cui_results, key=lambda x: (x[2], 1/int(x[0][1:])), reverse=True)

        return cui_results


def load_external_aliases(path):
    cui_aliases = defaultdict(list)

    with open(path) as f:
        for line in f:
            elems = line.strip().split('\t')
            cui, aliases = elems[0], elems[1:]
            cui_aliases[cui] = aliases

    return dict(cui_aliases)


def create_umls_ss_db(char_ngram_len=3, n_max_tokens=5, include_external=False):

    simstring_db = DictDatabase(CharacterNgramFeatureExtractor(char_ngram_len))

    external_aliases, external_mapping = set(), defaultdict(list)

    if include_external:
        for cui, aliases in load_external_aliases('data/thesaurus_v10.processed.matched.txt').items():
            for alias in aliases:
                alias = alias.lower()
                if alias not in external_aliases:
                    external_mapping[cui].append(alias)
                    external_aliases.add(alias)

        for cui, aliases in load_external_aliases('data/medmentions_all_annotations.tsv').items():
            for alias in aliases:
                alias = alias.lower()
                if alias not in external_aliases:
                    external_mapping[cui].append(alias)
                    external_aliases.add(alias)

    # preprocessing aliases and labels
    logging.info('Preprocessing aliases ...')
    alias_mapping = defaultdict(list)
    cui_mapping = defaultdict(list)

    aliases = []

    logging.info('Reading UMLS ...')
    with open('data/UMLS/umls_2020_aa_cat0129.jsonl') as jl_f:

        for jl_idx, jl_str in enumerate(jl_f):

            if jl_idx % 100000 == 0:
                print(jl_idx)

            jl = json.loads(jl_str)
            cui = jl['concept_id']
            cui_umls_aliases = [jl['canonical_name']] + jl['aliases']
            cui_external_aliases = external_mapping[cui]
            cui_aliases = cui_umls_aliases + cui_external_aliases

            cui_aliases = [normalize_str(a) for a in cui_aliases]
            cui_aliases = remove_dupes(cui_aliases)
            cui_aliases = [a for a in cui_aliases if not a.isnumeric()]
            cui_aliases = [a for a in cui_aliases if len(a.split()) <= n_max_tokens]

            # print(cui, cui_aliases)

            for alias in cui_aliases:
                alias_mapping[alias].append(cui)
                cui_mapping[cui].append(alias)
                aliases.append(alias)

    logging.info('Adding to DB ...')
    for alias_idx, alias in enumerate(aliases):
        simstring_db.add(alias)
        if alias_idx % 1000000 == 0:
            logging.info('At %d/%d ...' % (alias_idx, len(aliases)))

    # setting paths

    if include_external:
        db_path = 'data/SimString/umls_2020_aa_cat0129_ext.%dgram.%dtoks.db' % (char_ngram_len, n_max_tokens)
        alias_map_path = 'data/SimString/umls_2020_aa_cat0129_ext.%dtoks.alias.map' % (n_max_tokens)
        cui_map_path = 'data/SimString/umls_2020_aa_cat0129_ext.%dtoks.cui.map' % (n_max_tokens)
    else:
        db_path = 'data/SimString/umls_2020_aa_cat0129.%dgram.%dtoks.db' % (char_ngram_len, n_max_tokens)
        alias_map_path = 'data/SimString/umls_2020_aa_cat0129.%dtoks.alias.map' % (n_max_tokens)
        cui_map_path = 'data/SimString/umls_2020_aa_cat0129.%dtoks.cui.map' % (n_max_tokens)

    logging.info('Storing DB ...')
    with open(db_path, 'wb') as f:
        pickle.dump(simstring_db, f)

    logging.info('Storing Alias Mapping ...')
    with open(alias_map_path, 'wb') as f:
        alias_mapping = dict(alias_mapping)
        pickle.dump(alias_mapping, f)

    logging.info('Storing CUI Mapping ...')
    with open(cui_map_path, 'wb') as f:
        cui_mapping = dict(cui_mapping)
        pickle.dump(cui_mapping, f)


if __name__ == '__main__':

    ngram_db_path = 'data/SimString/umls_2020_aa_cat0129_ext.3gram.5toks.db'
    ngram_map_path = 'data/SimString/umls_2020_aa_cat0129_ext.5toks.alias.map'

    umls_string_matcher = SimString_UMLS(ngram_db_path, ngram_map_path)
    r = umls_string_matcher.match('apoptosis')

    # create_umls_ss_db(char_ngram_len=3, n_max_tokens=5, include_external=False)
    # create_umls_ss_db(char_ngram_len=3, n_max_tokens=5, include_external=True)
