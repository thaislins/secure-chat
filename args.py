'''CLI Parser'''
import argparse


def args_parser(args):
    '''Parce CLI arguments'''
    parser = argparse.ArgumentParser()

    # Algorithm group to ensure that have one (and only one) rc4 or s_des args
    alg_group = parser.add_mutually_exclusive_group(required=True)
    alg_group.add_argument(
        '--rc4', dest='algorithm', action='store_const', const='rc4',
        help='Use the RC4 algorithm')
    alg_group.add_argument(
        '--s_des', dest='algorithm', action='store_const', const='s_des',
        help='Use the S-DES algorithm')

    # Key argument
    parser.add_argument(
        '-k', '--key', type=str, required=True,
        help='The key to be used on encryption/decryption')

    return parser.parse_args(args)
