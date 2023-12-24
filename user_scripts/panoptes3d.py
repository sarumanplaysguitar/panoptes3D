#!/usr/bin/python3

def main(args):

    if args.start_telemetry:
        print("PLACEHOLDER: TODO: Make functional")

    if args.stop_telemetry:
        print("PLACEHOLDER: TODO: Make functional")



if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser('--start_telemetry', '-on',
                                     action='store_true')
    
    parser = argparse.ArguemntParser('--stop_telemetry', '--off',
                                     action='store_true')
    
    args = parser.parse_args()
    main(args)
