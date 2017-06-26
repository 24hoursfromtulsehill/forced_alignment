import argparse
import os


from aligner.command_line.align import fix_path, unfix_path

def validate(args):
    pass

def generate_lm(args):
    pass

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Train a language model from a corpus")

    parser.add_argument('corpus_directory', help='Full path to the source directory to train from')

    parser.add_argument("output_model_path", help="Desired location of generated model")
    parser.add_argument('-t', '--temp_directory', type=str, default='',
                        help='Temporary directory root to use for LM training, default is ~/Documents/MFA')

    args = parser.parse_args()
    fix_path()
    validate(args)
    generate_lm(args)
    unfix_path()