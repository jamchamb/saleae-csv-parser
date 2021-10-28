import struct


def unpack_addr(addr_bytes, endianness):
    if len(addr_bytes) > 8:
        raise Exception('addr bytes too long')

    # Reverse bytes if little endian
    if endianness == '<':
        addr_bytes = addr_bytes[::-1]

    # Pad and unpack as 64-bit unsigned value
    pad = b'\x00' * (8 - len(addr_bytes))
    return struct.unpack('>Q', pad + addr_bytes)[0]


class SPIWriteCmd:

    magic = b'\x02'

    @staticmethod
    def decode(packet, state=None):
        end = state['endianness']
        addr_len = state['addr_len']

        addr_bytes = packet.mosi[1:1 + addr_len]
        address = unpack_addr(addr_bytes, end)
        data = packet.mosi[1 + addr_len:]

        info = {
            'cmd_type': 'write',
            'address': address,
            'data': data
        }

        return info


class SPIReadCmd:

    magic = [b'\x03', b'\x0b', b'\x0c']

    @staticmethod
    def decode(packet, state=None):
        end = state['endianness']
        addr_len = state['addr_len']

        data_offset = 0

        if packet.mosi[0] == b'\x0b':
            # Fast read
            subtype = 'fast'
            data_offset = 1
        elif packet.mosi[0] == b'\x0c':
            # Fast read (4 byte addr)
            subtype = 'fast, 4 byte address'
            addr_len = 4
            data_offset = 1
        else:
            subtype = 'basic'

        addr_bytes = packet.mosi[1:1 + addr_len]
        data = packet.miso[1 + addr_len + data_offset:]

        address = unpack_addr(addr_bytes, end)

        info = {
            'cmd_type': 'read',
            'cmd_subtype': subtype,
            'address': address,
            'data': data
        }

        return info


class SPIDevIdCmd:

    magic = b'\x9f'

    @staticmethod
    def decode(packet, state=None):
        end = state['endianness']

        if len(packet.miso) != 4:
            raise Exception('Device ID pkt invalid length %u' % (len(packet.miso)))

        data = packet.miso[1:]
        manufacturer, device = struct.unpack(
            end + 'BH',
            data)

        info = {
            'cmd_type': 'device_id',
            'manufacturer_id': manufacturer,
            'device_id': device
        }

        return info
