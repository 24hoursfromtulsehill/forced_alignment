import os
from ..config import TEMP_DIR


class Transcriber(object):
    def __init__(self, corpus, dictionary, acoustic_model, language_model, output_directory,
                 temp_directory=None, num_jobs=3, speaker_independent=False,
                 call_back=None, debug=False):
        self.debug = debug
        if temp_directory is None:
            temp_directory = TEMP_DIR
        self.acoustic_model = acoustic_model
        self.language_model = language_model
        self.temp_directory = temp_directory
        self.output_directory = output_directory
        self.corpus = corpus
        self.speaker_independent = speaker_independent
        self.dictionary = dictionary
        self.setup()

        if self.corpus.num_jobs != num_jobs:
            num_jobs = self.corpus.num_jobs
        self.num_jobs = num_jobs
        self.call_back = call_back
        if self.call_back is None:
            self.call_back = print
        self.verbose = False

    def setup(self):
        self.dictionary.write()
        self.corpus.initialize_corpus(self.dictionary)
        self.language_model.initialize_model(self.dictionary)
        print(self.corpus.speaker_utterance_info())