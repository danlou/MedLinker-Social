import re
import pickle
from collections import defaultdict
from segtok.segmenter import split_multi
from segtok.tokenizer import web_tokenizer, split_contractions


"""
ALIASES
"""

cui_alias_map = defaultdict(list)
with open('data/SimString/umls_2020_aa_cat0129_ext.5toks.cui.map', 'rb') as mapping_f:
    cui_alias_map = pickle.load(mapping_f)


cui_mfa = {}  # Most Frequent Alias
with open('data/cui_mfa.csv') as f:
    for line in f:
        elems = line.strip().split(',')
        cui, alias = elems
        cui_mfa[cui] = alias.capitalize()

"""
STYS
"""

cui_stys_map = {}
with open('data/UMLS/umls_2020_aa_cat0129.types_map.tsv') as tsv_f:
    for line in tsv_f:
        elems = line.strip().split('\t')
        cui, stys = elems[0], elems[1:]
        cui_stys_map[cui] = stys


selected_stys = set()
with open('data/UMLS/sty_labels_subset.csv') as sty_f:
    sty_f.readline()
    for line in sty_f:
        sty, label = line.strip().split('|')
        selected_stys.add(sty)


sty_labels = {}
with open('data/UMLS/sty_labels.csv') as sty_f:
    sty_f.readline()
    for line in sty_f:
        sty, label = line.strip().split('|')
        sty_labels[sty] = label


"""
OTHER LISTS
"""

en_freq_words = []
with open('data/google-10000-english.txt') as freq_f:
    en_freq_words = [w.strip() for w in freq_f.readlines()]
en_freq_words_set = set(en_freq_words)


lex_variants = {}
with open('data/penn_lexicon/LexicalVariants_PennLexiconofBirthDefects_v2.txt') as lex_variants_f:
    for line in lex_variants_f:
        elems = line.strip().split()
        w, variants = elems[0], elems[1:]
        for v in variants:
            lex_variants[v] = w
lex_variants_set = set(list(lex_variants.keys()))


efcni_cuis = set()
with open('data/efcni.cuis.csv') as f:
    for line in f:
        elems = line.strip().split('|')
        cat, cui, alias = elems
        efcni_cuis.add(cui)



def yake_tokenizer(txt):
    """ Follows YAKE tokenization to retrieve sentences with extracted keywords. """
    tokens = []
    for sent in split_multi(txt):
        tokens += [w for w in split_contractions(web_tokenizer(sent))]

    return tokens


def replace_variants(txt):
    toks = web_tokenizer(txt)
    toks = [lex_variants[t] if t in lex_variants_set else t for t in toks]
    return ' '.join(toks)


def normalize_str(s):
    s = s.lower()
    s = ''.join([c if c not in '()-,:/<>' else ' ' for c in s])
    toks = s.split()
    toks = [t for t in toks if t not in en_freq_words[:10]]

    return ' '.join(toks)


def remove_dupes(l):
    # preserves order
    l_dedup = []
    seen = set()
    for e in l:
        if e not in seen:
            l_dedup.append(e)
            seen.add(e)
    return l_dedup


# def fix_txt(txt):
#     txt = txt.replace('’', '\'')
#     txt = txt.replace('“', '"')
#     txt = txt.replace('”', '"')
#     txt = re.sub(r'\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*', '', txt)  # removes URLs
#     return ' '.join(txt.split())



# def detokenize_contractions(t):
#     t = t.replace(' n\'t ', 'n\'t ')
#     t = t.replace(' \'re ', '\'re ')
#     t = t.replace(' \'ve ', '\'ve ')
#     t = t.replace(' \'m ', '\'m ')
#     t = t.replace(' \'s ', '\'s ')
#     t = t.replace(' \'d ', '\'d ')
#     return t
