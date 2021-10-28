#!/usr/bin/env python3
import argparse
from hexdump import hexdump
from saleae_csv_parser.spi.spi_base import (SPIParser)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('filename', type=str)
    parser.add_argument(
        '--pktdelta', type=float, default=None,
        help="split packets by time delta when there's no CS line (seconds)")
    args = parser.parse_args()

    with open(args.filename, 'r') as csvfile:
        parser = SPIParser(time_split=args.pktdelta)

        for pkt in parser.parse_file(csvfile):
            print(pkt)
            print('MOSI:')
            hexdump(pkt.mosi)
            print('MISO:')
            hexdump(pkt.miso)
            print('')


if __name__ == '__main__':
    main()
