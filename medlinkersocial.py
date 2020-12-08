import pickle
from collections import defaultdict

from utils import cui_stys_map
from utils import cui_stys_map
from utils import yake_tokenizer
from utils import replace_variants
from utils import normalize_str
from utils import cui_mfa
from utils import sty_labels
from utils import efcni_cuis

from umls_simstring import SimString_UMLS

import yake


class MedLinkerSocial(object):

    def __init__(self,
                 db_path='data/SimString/umls_2020_aa_cat0129_ext.3gram.5toks.db',
                 map_path='data/SimString/umls_2020_aa_cat0129_ext.5toks.alias.map',
                 alpha=0.5,
                 n=5):

        self.matcher = None
        self.extractor = None
        self.alpha = alpha
        
        self.load_matcher(db_path, map_path, self.alpha)
        self.load_extractor(n)

    def load_matcher(self, db_path, map_path, alpha=0.5):
        self.matcher = SimString_UMLS(db_path, map_path, alpha=alpha)

    def load_extractor(self, n=5):
        self.extractor = yake.KeywordExtractor(lan='en', n=n, dedupLim=0.9, dedupFunc='seqm', windowsSize=1, top=999)

    def extract_keywords(self, sent_tokens):

        def locate_sublist(a, b):
            if len(a) > len(b):
                return None
            for i in range(0, len(b) - len(a) + 1):
                if b[i:i+len(a)] == a:
                    return (i, i+len(a))
            return None

        # tokens provided must be tokenized using the same tokenizer as yake
        try:
            kws = self.extractor.extract_keywords(' '.join(sent_tokens))
        except ValueError:
            kws = []

        # invert scores
        kws = [(1/score, kw) for (kw, score) in kws]
        sum_score = sum([score for (score, kw) in kws])
        kws = [(score/sum_score, kw) for (score, kw) in kws]

        # locate extracted kws
        kws_with_idxs = []
        for score, kw in kws:
            kw_tokens = kw.split()
            try:
                s, e = locate_sublist(kw_tokens, sent_tokens)
            except:
                continue
            kws_with_idxs.append((score, kw, s, e))

        return kws_with_idxs

    def search(self, sentence, alpha=None, add_yake_score=True, overlapping=True):

        if alpha is None:
            alpha = self.alpha

        r = {'sentence': sentence, 'tokens': yake_tokenizer(sentence), 'matches': []}

        for score, kw, s, e in self.extract_keywords(r['tokens']):
            kw = normalize_str(kw)
            kw = replace_variants(kw)

            try:
                cui, alias, sim = self.matcher.match_cuis(kw)[0]
            except IndexError:
                continue

            match = {'keyword': kw, 'cui': cui,  'stys': cui_stys_map[cui], 'alias': alias, 'start': s, 'end': e, 'score': score, 'similarity': sim}
            r['matches'].append(match)

        r['matches'] = [m for m in r['matches'] if m['similarity'] > alpha]
        if add_yake_score:  # better for matching longer sequences
            r['matches'] = sorted(r['matches'], key=lambda m: m['similarity'] + m['score'], reverse=True)
        else:  # yake score just used to settle similarity ties
            r['matches'] = sorted(r['matches'], key=lambda m: (m['similarity'], m['score']), reverse=True)

        if not overlapping:
            matched_idxs = set()
            matches_filtered = []
            for m in r['matches']:
                idxs = list(range(m['start'], m['end']))
                if all([i not in matched_idxs for i in idxs]):
                    matches_filtered.append(m)
                    matched_idxs.update(idxs)

            r['matches'] = matches_filtered
        
        return r

    def get_mfa(self, cui):
        # CUI's Most Frequent Alias according to Reddit Corpus            
        if cui in cui_mfa:
            return cui_mfa[cui]
        else:
            return cui_alias_map[cui][0]

    def get_types(self, cui, include_name=False):
        stys = cui_stys_map[cui]

        if include_name:
            stys = ['%s (%s)' % (sty, sty_labels[sty]) for sty in stys]
        
        return stys

    def get_aliases(self, cui):
        return cui_alias_map[cui]


if __name__ == "__main__":

    db_path='data/SimString/umls_2020_aa_cat0129_ext.3gram.5toks.db'
    map_path='data/SimString/umls_2020_aa_cat0129_ext.5toks.alias.map'

    linker = MedLinkerSocial(db_path, map_path, alpha=0.5, n=5)

    txt = "But I often check on her because I'm paranoid and scared of positional asphyxiation ."

    r = linker.search(txt, alpha=0.7)

    print(r)

    for m in r['matches']:
        print(m)

