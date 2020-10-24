import time
import struct


class Dataflash:
    HEADER = bytes.fromhex('A3 95')
    BYTESIZE = {
        'a': 64,  # int16_t[32]
        'b': 1,  # int8_t
        'B': 1,  # uint8_t
        'h': 2,  # int16_t
        'H': 2,  # uint16_t
        'i': 4,  # int32_t
        'I': 4,  # uint32_t
        'f': 4,  # float
        'd': 8,  # double
        'n': 4,  # char[4]
        'N': 16,  # char[16]
        'Z': 64,  # char[64]
        'c': 200,  # int16_t * 100
        'C': 200,  # uint16_t * 100
        'e': 400,  # int32_t * 100
        'E': 400,  # uint32_t * 100
        'L': 4,  # int32_t latitude/longitude
        'M': 1,  # uint8_t flight mode
        'q': 8,  # int64_t
        'Q': 8  # uint64_t
    }
    PACKED = ['b', 'B', 'h', 'H', 'i', 'I', 'f', 'd', 'L', 'q', 'Q']
    TEXT = ['n', 'N', 'Z']

    def __init__(self, output_buffer):
        self.start_time = time.perf_counter_ns()
        self.output_buffer = output_buffer
        self.next_msg_id = 101
        self.max_msg_id = 126  # inclusive
        self.msg_defs = [
            {'id': 128, 'name': 'FMT', 'fields': 'BBnNZ', 'labels': 'Type,Length,Name,Format,Columns',
             'units': '-b---', 'multipliers': '-----'},
            {'id': 219, 'name': 'UNIT', 'fields': 'QbZ', 'labels': 'TimeUS,Id,Label',
             'units': 's--', 'multipliers': 'F--'},
            {'id': 218, 'name': 'FMTU', 'fields': 'QBNN', 'labels': 'TimeUS,FmtType,UnitIds,MultIds',
             'units': 's---', 'multipliers': 'F---'},
            {'id': 220, 'name': 'MULT', 'fields': 'Qbd', 'labels': 'TimeUS,Id,Mult',
             'units': 's--', 'multipliers': 'F--'},
            {'id': 129, 'name': 'PARM', 'fields': 'QNf', 'labels': 'TimeUS,Name,Value',
             'units': 's--', 'multipliers': 'F--'},
            {'id': 134, 'name': 'MSG', 'fields': 'QZ', 'labels': 'TimeUS,Message',
             'units': 's-', 'multipliers': 'F-'},
        ]
        self.unit_defs = [
            {'id': '-', 'unit': ''},  # no units e.g. Pi, or a string
            {'id': '?', 'unit': 'UNKNOWN'},  # Units which haven't been worked out yet....
            {'id': 'A', 'unit': 'A'},  # Ampere
            {'id': 'd', 'unit': 'deg'},  # of the angular variety, -180 to 180
            {'id': 'b', 'unit': 'B'},  # bytes
            {'id': 'k', 'unit': 'deg/s'},
            # degrees per second. Degrees are NOT SI, but is some situations more user-friendly than radians
            {'id': 'D', 'unit': 'deglatitude'},  # degrees of latitude
            {'id': 'e', 'unit': 'deg/s/s'},
            # degrees per second per second. Degrees are NOT SI, but is some situations more user-friendly than radians
            {'id': 'E', 'unit': 'rad/s'},  # radians per second
            {'id': 'G', 'unit': 'Gauss'},
            # Gauss is not an SI unit, but 1 tesla = 10000 gauss so a simple replacement is not possible here
            {'id': 'h', 'unit': 'degheading'},  # 0.? to 359.?
            {'id': 'i', 'unit': 'A.s'},  # Ampere second
            {'id': 'J', 'unit': 'W.s'},  # Joule (Watt second)
            {'id': 'l', 'unit': 'l'},  # litres
            {'id': 'L', 'unit': 'rad/s/s'},  # radians per second per second
            {'id': 'm', 'unit': 'm'},  # metres
            {'id': 'n', 'unit': 'm/s'},  # metres per second
            {'id': 'N', 'unit': 'N'},  # Newton
            {'id': 'o', 'unit': 'm/s/s'},  # metres per second per second
            {'id': 'O', 'unit': 'degC'},  # degrees Celsius. Not SI, but Kelvin is too cumbersome for most users
            {'id': '%', 'unit': '%'},  # percent
            {'id': 'S', 'unit': 'satellites'},  # number of satellites
            {'id': 's', 'unit': 's'},  # seconds
            {'id': 'q', 'unit': 'rpm'},  # rounds per minute. Not SI, but sometimes more intuitive than Hertz
            {'id': 'r', 'unit': 'rad'},  # radians
            {'id': 'U', 'unit': 'deglongitude'},  # degrees of longitude
            {'id': 'u', 'unit': 'ppm'},  # pulses per minute
            {'id': 'v', 'unit': 'V'},  # Volt
            {'id': 'P', 'unit': 'Pa'},  # Pascal
            {'id': 'w', 'unit': 'Ohm'},  # Ohm
            {'id': 'W', 'unit': 'Watt'},  # Watt
            {'id': 'Y', 'unit': 'us'},  # pulse width modulation in microseconds
            {'id': 'z', 'unit': 'Hz'},  # Hertz
            {'id': '#', 'unit': 'instance'}  # (e.g.)Sensor instance number
        ]
        self.mult_defs = [
            {'id': '-', 'multiplier': 0},  # no multiplier e.g. a string
            {'id': '?', 'multiplier': 1},  # multipliers which haven't been worked out yet....
            # <leave a gap here, just in case....>
            {'id': '2', 'multiplier': 1e2},
            {'id': '1', 'multiplier': 1e1},
            {'id': '0', 'multiplier': 1e0},
            {'id': 'A', 'multiplier': 1e-1},
            {'id': 'B', 'multiplier': 1e-2},
            {'id': 'C', 'multiplier': 1e-3},
            {'id': 'D', 'multiplier': 1e-4},
            {'id': 'E', 'multiplier': 1e-5},
            {'id': 'F', 'multiplier': 1e-6},
            {'id': 'G', 'multiplier': 1e-7},
            # <leave a gap here, just in case....>
            {'id': '!', 'multiplier': 3.6},  # (ampere*second => milliampere*hour) and (km/h => m/s)
            {'id': '/', 'multiplier': 3600},  # (ampere*second => ampere*hour)
        ]

    def add_message(self, name, fields, labels, units=None, multipliers=None):
        msg_id = self.next_msg_id
        self.next_msg_id += 1
        if self.next_msg_id > self.max_msg_id:
            raise RuntimeError('Too many messages added to this logger')

        msg_def = {'id': msg_id, 'name': name, 'fields': fields, 'labels': labels}
        if units or multipliers:
            assert units, f'Missing units in message {msg_def["name"]}'
            assert len(units) == len(msg_def['fields']), f'Invalid units length in message {msg_def["name"]}'
            assert multipliers, f'Missing multipliers in message {msg_def["name"]}'
            assert len(multipliers) == len(msg_def['fields']), f'Invalid mult length in message {msg_def["name"]}'
            valid_ids = [unit['id'] for unit in self.unit_defs]
            for unit_id in units:
                if unit_id not in valid_ids:
                    raise ValueError(f'Invalid unit {unit_id} in message {msg_def["name"]}')
            valid_ids = [mult['id'] for mult in self.mult_defs]
            for mult_id in multipliers:
                if mult_id not in valid_ids:
                    raise ValueError(f'Invalid multiplier {mult_id} in message {msg_def["name"]}')

            msg_def['units'] = units
            msg_def['multipliers'] = multipliers

        self.msg_defs.append(msg_def)

    @staticmethod
    def msg_len(fields):
        res = 2 + 1  # header + id
        for char in fields:
            if char in Dataflash.BYTESIZE:
                res += Dataflash.BYTESIZE[char]
            else:
                raise ValueError('Invalid descriptor of field: {}'.format(char))
        return res

    @staticmethod
    def encode_and_pad(text, length):
        content = text.encode('ascii')
        return content + b'\0' * (length - len(content))

    def pack_message(self, name, *fields):
        msg_def = next((msg for msg in self.msg_defs if msg['name'] == name), None)
        if msg_def is None:
            raise RuntimeError(f'Message definition for {name} not found')
        assert len(fields) == len(msg_def['fields']), \
            f'Invalid argument count {len(fields)} for message {name} with {len(msg_def["fields"])} fields defined'

        result = [0] * Dataflash.msg_len(msg_def['fields'])
        result[:2] = Dataflash.HEADER
        result[2] = msg_def['id']
        offset = 3
        for index, field in enumerate(fields):
            length = Dataflash.BYTESIZE[msg_def['fields'][index]]
            if msg_def['fields'][index] in Dataflash.PACKED:
                result[offset:offset + length] = struct.pack('<' + msg_def['fields'][index], field)
            elif msg_def['fields'][index] in Dataflash.TEXT:
                result[offset:offset + length] = Dataflash.encode_and_pad(field, length)
            else:
                raise NotImplementedError(f'Type of field {msg_def["fields"][index]} not handled by pack_message')
            offset += length

        return bytearray(result)

    def time_us(self):
        return int((time.perf_counter_ns() - self.start_time) / 1000)

    def write_header(self):
        for msg in self.msg_defs:
            self.output_buffer.write(self.pack_message('FMT', msg['id'], self.msg_len(msg['fields']),
                                                       msg['name'], msg['fields'], msg['labels']))
        for unit in self.unit_defs:
            self.output_buffer.write(self.pack_message('UNIT', self.time_us(), ord(unit['id']), unit['unit']))
        for mult in self.mult_defs:
            self.output_buffer.write(self.pack_message('MULT', self.time_us(), ord(mult['id']), mult['multiplier']))
        for msg in self.msg_defs:
            self.output_buffer.write(self.pack_message('FMTU', self.time_us(), msg['id'],
                                                       msg['units'], msg['multipliers']))
