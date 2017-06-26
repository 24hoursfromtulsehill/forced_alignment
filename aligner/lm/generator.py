import os
import subprocess

from ..helper import thirdparty_binary

from ..config import TEMP_DIR

from ..models import LanguageModel


class LMGenerator(object):
    def __init__(self, corpus, dictionary, model_path, temp_directory=None, order=2):

        if not temp_directory:
            temp_directory = TEMP_DIR
        temp_directory = os.path.join(temp_directory, 'LM')

        self.name, _ = os.path.splitext(os.path.basename(model_path))
        self.temp_directory = os.path.join(temp_directory, self.name)
        os.makedirs(self.temp_directory, exist_ok=True)
        self.model_path = model_path
        self.order = order
        self.corpus = corpus
        self.dictionary = dictionary

    def generate(self):

        corpus_path = os.path.join(self.temp_directory, 'full.corpus')
        sym_path = os.path.join(self.temp_directory, 'full.syms')
        far_path = os.path.join(self.temp_directory, 'full.far')
        cnts_path = os.path.join(self.temp_directory, 'full.cnts')
        mod_path = os.path.join(self.temp_directory, 'full.mod')
        arpa_path = os.path.join(self.temp_directory, 'full.arpa')
        arpa_filtered_path = os.path.join(self.temp_directory, 'full.filtered.arpa')
        fst_path = os.path.join(self.temp_directory, 'full.fst')
        fst_text_path = os.path.join(self.temp_directory, 'full.text.fst')
        fst_disambig_text_path = os.path.join(self.temp_directory, 'full.text.disambig.fst')
        fst_disambig_path = os.path.join(self.temp_directory, 'full.disambig.fst')
        g_path = os.path.join(self.temp_directory, 'G.fst')
        g_text_path = os.path.join(self.temp_directory, 'G.text.fst')
        with open(corpus_path, 'w', encoding='utf8') as f:
            #for text in self.corpus.texts_for_lm(self.dictionary):
            for u, text in self.corpus.text_mapping.items():
                f.write(text + '\n')

        self.dictionary._write_word_file()

        subprocess.call([thirdparty_binary('ngramsymbols'), corpus_path, sym_path])

        subprocess.call(
            [thirdparty_binary('farcompilestrings'), '--symbols=' + self.dictionary.words_file_path, '--keep_symbols=1',
             corpus_path, far_path])

        subprocess.call([thirdparty_binary('ngramcount'), '--order={}'.format(self.order), far_path, cnts_path])

        subprocess.call([thirdparty_binary('ngrammake'), '--method=kneser_ney', cnts_path, mod_path])

        subprocess.call([thirdparty_binary('ngramprint'), '--ARPA', mod_path, arpa_path])
        self._filter_arpa(arpa_path, arpa_filtered_path)

        subprocess.call([thirdparty_binary('arpa2fst'), arpa_path, fst_path])
        subprocess.call([thirdparty_binary('fstprint'), fst_path, fst_text_path])
        self._eps2disambig(fst_text_path, fst_disambig_text_path)
        subprocess.call([thirdparty_binary('fstcompile'),
                         '--isymbols=' + self.dictionary.words_file_path,
                         '--osymbols=' + self.dictionary.words_file_path,
                         '--keep_isymbols=false', '--keep_osymbols=false',
                         fst_disambig_text_path, fst_disambig_path])
        subprocess.call([thirdparty_binary('fstprint'), fst_disambig_path, g_text_path])
        subprocess.call([thirdparty_binary('fstrmepsilon'), fst_disambig_path, g_path])
        #subprocess.call([thirdparty_binary('fstprint'), g_path, g_text_path])

    def _filter_arpa(self, arpa_path, arpa_filtered_path):
        with open(arpa_path, 'r', encoding='utf8') as inf, \
                open(arpa_filtered_path, 'w', encoding='utf8') as outf:
            for line in inf:
                if '<unk>' not in line:
                    outf.write(line)

    def _eps2disambig(self, fst_text_path, fst_disambig_text_path):
        """
        Follows eps2disambig.pl and s2eps.pl in Kaldi
        :return:
        """
        with open(fst_text_path, 'r', encoding='utf8') as inf, \
                open(fst_disambig_text_path, 'w', encoding='utf8') as outf:
            for line in inf:
                print(line)
                if '#0' in line:
                    raise Exception('$0: ERROR: LM has word #0, which is reserved as disambiguation symbol')
                line.replace('<eps>', '#0')
                line = line.strip().split()
                if line[2] in ['<s>', '</s>']:
                    line[2] = '<eps>'
                if line[3] in ['<s>', '</s>']:
                    line[3] = '<eps>'
                outf.write('\t'.join(line) + '\n')
