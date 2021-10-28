class SPIPacket:

    def __init__(self, id_, times, mosi, miso):
        self.pkt_id = id_
        self.times = times
        self.mosi = mosi
        self.miso = miso

    def __str__(self):
        return f'Packet #{self.pkt_id}\t {len(self.miso)} bytes\t({self.times[0]} - {self.times[-1]})'

    def print_info(self):
        print(self)
        print(f'MOSI: {self.mosi.hex()}')
        print(f'MISO: {self.miso.hex()}')

    def decode(self):
        pass


class SPIParser:

    def __init__(self, time_split=None):
        self.cur_pkt_id = 0
        self.cur_rows = []

        # When there is no CS line, attempt
        # to split packets by minimum time delta
        self.time_split = time_split
        self.last_time = None

    def consume(self, row):
        pkt = None
        pkt_id = -1

        if self.time_split is not None:
            # Split packets by time delta
            cur_time = float(row[0])
            if self.last_time is not None:
                delta = cur_time - self.last_time
                if delta >= self.time_split:
                    pkt_id = self.cur_pkt_id + 1
            self.last_time = cur_time
        elif len(row[1]) > 0:
            # Split packets with packet ID column
            pkt_id = int(row[1])

        if pkt_id > self.cur_pkt_id:
            pkt = self.consume_packet()
            self.cur_rows = []
            self.cur_pkt_id = pkt_id

        self.cur_rows.append(row)

        return pkt

    def consume_packet(self):
        if len(self.cur_rows) == 0:
            return None

        times = [float(r[0]) for r in self.cur_rows]
        mosi = bytes([int(r[2], 0) for r in self.cur_rows])
        miso = bytes([int(r[3], 0) for r in self.cur_rows])

        pkt = SPIPacket(self.cur_pkt_id, times, mosi, miso)

        return pkt

    def parse_file(self, file_):
        for i, line in enumerate(file_):
            if i == 0 or len(line) == 0:
                continue

            row = line.rstrip().split(',')

            if len(row) != 4:
                raise ValueError(f'row format invalid in line "{line}"')

            pkt = self.consume(row)
            if pkt is not None:
                yield pkt

        yield self.consume_packet()
