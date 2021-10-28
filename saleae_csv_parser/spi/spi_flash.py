from .spi_base import (SPIPacket, SPIParser)
import saleae_csv_parser.spi.spi_flash_cmds as spi_flash_cmds


# Make lookup table for SPI flash command handlers
SPI_COMMANDS = {}
for clas in [cls for cls in spi_flash_cmds.__dict__.values()
             if isinstance(cls, type)]:
    if type(clas.magic) is list:
        for magic in clas.magic:
            SPI_COMMANDS[magic] = clas
    else:
        SPI_COMMANDS[clas.magic] = clas

SPI_COMMANDS_MAX_KEYLEN = max(map(len, SPI_COMMANDS.keys()))


class SPIFlashPacket(SPIPacket):

    def __init__(self, packet):
        SPIPacket.__init__(
            self,
            packet.pkt_id,
            packet.times,
            packet.mosi,
            packet.miso)
        self.decoded = False
        self.info = None

    def decode(self, state=None):
        global SPI_COMMANDS

        if self.decoded:
            return
        self.decoded = True

        # TODO: Tweak a little more to make the decoder
        # lookup/application more reusable
        for magic in SPI_COMMANDS.keys():
            # Note: if all magics are the same length it could
            # just be a dict lookup. Or, try every initial substring
            # up to the max key length.
            if self.mosi.startswith(magic):
                decoder = SPI_COMMANDS[magic]
                try:
                    self.info = decoder.decode(self, state)
                except Exception as e:
                    print(e)
                    self.print_info()
                break

        if self.info is None:
            self.info = {'cmd_type': 'unknown'}

    def print_info(self):
        SPIPacket.print_info(self)
        if self.info is not None:
            if self.info['cmd_type'] in ['read', 'write']:
                out = f'{self.info["cmd_type"]} '
                if self.info.get('cmd_subtype') not in [None, 'basic']:
                    out += f'({self.info["cmd_subtype"]}) '
                out += f'@ {self.info["address"]:#08x}: {self.info["data"][:8]}'
                print(out)
            else:
                print(self.info)
        else:
            #print(f'Command type unknown {self.mosi[0]:#02x}')
            pass

    def get_info(self):
        if self.decoded:
            return (self.cmd_type, self.info)
        return None


class SPIFlashParser(SPIParser):

    def __init__(self, addr_len=3, endianness='>'):
        SPIParser.__init__(self)
        self.state = {
            'addr_len': addr_len,
            'endianness': endianness
        }

    def consume_packet(self):
        result = SPIParser.consume_packet(self)
        if result is not None:
            flashPkt = SPIFlashPacket(result)
            flashPkt.decode(state=self.state)
            return flashPkt

        return None
