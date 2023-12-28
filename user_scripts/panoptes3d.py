#!/usr/bin/python3

def main(args):

    if args.start:
        print("PLACEHOLDER: TODO: Make functional")

    if args.stop:
        print("PLACEHOLDER: TODO: Make functional")

if __name__ == '__main__':
    import argparse
    import pickle

    parser = argparse.ArgumentParser('--start', '-on',
                                     action='store_true')
    
    parser = argparse.ArguemntParser('--stop', '--off',
                                     action='store_true')
    
    args = parser.parse_args()
    main(args)
