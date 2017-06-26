import pytest
import os

from aligner.lm.generator import LMGenerator

from aligner.models import LanguageModel

from aligner import __version__


def test_generate(sick_corpus, sick_dict, sick_lm_model_path):
    gen = LMGenerator(sick_corpus, sick_dict, sick_lm_model_path, order=1)
    gen.generate()
