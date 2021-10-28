#!/usr/bin/env python3
import argparse
from tqdm import tqdm
from .spi.spi_flash import (SPIFlashParser)


def main():
    parser = argparse.ArgumentParser(prog='saleae-csv-parser')
    parser.add_argument('csv', type=argparse.FileType('r'))
    args = parser.parse_args()

    spiParser = SPIFlashParser()

    print('Loading packets...')
    packets = [pkt for pkt in tqdm(spiParser.parse_file(args.csv))]
    print(f'Got {len(packets)} packets')

    for pkt in packets:
        if pkt.info['cmd_type'] != 'unknown':
            pkt.print_info()


if __name__ == '__main__':
    main()
