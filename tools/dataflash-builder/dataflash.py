import time
import struct
import typing


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
        'd': 8,  # double (some online services don't support it)
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

    def __init__(self, output_buffer: typing.BinaryIO):
        """Create a logger holding message types and writing data

        Parameters
        ----------
        output_buffer : typing.BinaryIO
            A file-like object to write the binary data into
        """
        self.start_time = time.perf_counter_ns()
        self.output_buffer = output_buffer
        self.next_msg_id = 1  # Ardupilot uses 0-63 for vehicle specific, 64 and up for common, where 128 must be FMT
        self.max_msg_id = 127  # inclusive
        self.msg_defs = [
            # These are the basic messages from LogFormat that will need to be in virtually every application
            # See documentation comments at end of file
            {'id': 128, 'name': 'FMT', 'fields': 'BBnNZ', 'labels': 'Type,Length,Name,Format,Columns',
             'units': '-b---', 'multipliers': '-----'},
            {'id': 129, 'name': 'UNIT', 'fields': 'QbZ', 'labels': 'TimeUS,Id,Label',
             'units': 's--', 'multipliers': 'F--'},
            {'id': 130, 'name': 'FMTU', 'fields': 'QBNN', 'labels': 'TimeUS,FmtType,UnitIds,MultIds',
             'units': 's---', 'multipliers': 'F---'},
            {'id': 131, 'name': 'MULT', 'fields': 'Qbd', 'labels': 'TimeUS,Id,Mult',
             'units': 's--', 'multipliers': 'F--'},
            {'id': 132, 'name': 'PARM', 'fields': 'QNf', 'labels': 'TimeUS,Name,Value',
             'units': 's--', 'multipliers': 'F--'},
            {'id': 133, 'name': 'MSG', 'fields': 'QZ', 'labels': 'TimeUS,Message',
             'units': 's-', 'multipliers': 'F-'},
            {'id': 134, 'name': 'ERR', 'fields': 'QBB', 'labels': 'TimeUS,Subsys,ECode',
             'units': 's--', 'multipliers': 'F--'},
            {'id': 135, 'name': 'MAVC', 'fields': 'QBBBHBBffffiifBB',
             'labels': 'TimeUS,TS,TC,Fr,Cmd,Cur,AC,P1,P2,P3,P4,X,Y,Z,Res,WL',
             'units': 's---------------', 'multipliers': 'F---------------'},
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

    def add_message(self, name: str, fields: str, labels: str,
                    units: typing.Optional[str] = None, multipliers: typing.Optional[str] = None) -> int:
        """Add and validate a message for logging

        Parameters
        ----------
        name : str
            Name for the message. Must be unique and not longer than 4 characters.
            By convention use uppercase letters and numbers
        fields : str
            Message field types defined in `Dataflash.BYTESIZE`. Cannot be longer than 16 characters.
            By convention make the first field TimeUS containing time from start of the system.
        labels : str
            Comma-separated list of field names. Cannot be longer than 64 characters.
        units : typing.Optional[str], optional
            Units for each field corresponding to a UNIT message, by default None
        multipliers : typing.Optional[str], optional
            Multipliers for each field corresponding to a MULT message, by default None

        Returns
        -------
        int
            Number of message ids left to assign
        """
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
        return self.max_msg_id - self.next_msg_id

    @staticmethod
    def msg_len(fields: str) -> int:
        """Get message length

        Parameters
        ----------
        fields : str
            String of fields corresponding to a FMT message

        Returns
        -------
        int
            Length of the message in bytes
        """
        res = 2 + 1  # header + id
        for char in fields:
            if char in Dataflash.BYTESIZE:
                res += Dataflash.BYTESIZE[char]
            else:
                raise ValueError('Invalid descriptor of field: {}'.format(char))
        return res

    @staticmethod
    def encode_and_pad(text: str, length: int) -> bytes:
        """Get a fixed length ascii-encoded bytes array

        Parameters
        ----------
        text : str
            Text to encode
        length : int
            Length of returned bytes object

        Returns
        -------
        bytes
            Containing encoded text padded with zero bytes up to length
        """
        content = text.encode('ascii')
        return content + b'\0' * (length - len(content))

    def pack_message(self, name: str, *fields) -> bytes:
        """Pack an already defined message into bytes

        Parameters
        ----------
        name : str
            Name of the message as defined in `add_message`

        Returns
        -------
        bytearray
            Bytes to write to file
        """
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

        return bytes(result)

    def time_us(self) -> int:
        """Get time from initialisation of the logger

        Returns
        -------
        int
            Time from initialising logger in microseconds
        """
        return int((time.perf_counter_ns() - self.start_time) / 1000)

    def write_header(self):
        """Write information about the defined messages into the `output_buffer`
        """
        for msg in self.msg_defs:
            self.output_buffer.write(self.pack_message('FMT', msg['id'], self.msg_len(msg['fields']),
                                                       msg['name'], msg['fields'], msg['labels']))
        for unit in self.unit_defs:
            self.output_buffer.write(self.pack_message('UNIT', self.time_us(), ord(unit['id']), unit['unit']))
        for mult in self.mult_defs:
            self.output_buffer.write(self.pack_message('MULT', self.time_us(), ord(mult['id']), mult['multiplier']))
        for msg in filter(lambda md: 'units' in md and 'multipliers' in md, self.msg_defs):
            self.output_buffer.write(self.pack_message('FMTU', self.time_us(), msg['id'],
                                                       msg['units'], msg['multipliers']))

# @LoggerMessage: FMT
# @Description: Message defining the format of messages in this file
# @URL: https://ardupilot.org/dev/docs/code-overview-adding-a-new-log-message.html
# @Field: Type: unique-to-this-log identifier for message being defined
# @Field: Length: the number of bytes taken up by this message (including all headers)
# @Field: Name: name of the message being defined
# @Field: Format: character string defining the C-storage-type of the fields in this message
# @Field: Columns: the labels of the message being defined

# @LoggerMessage: UNIT
# @Description: Message mapping from single character to SI unit
# @Field: TimeUS: Time since system startup
# @Field: Id: character referenced by FMTU
# @Field: Label: Unit - SI where available

# @LoggerMessage: FMTU
# @Description: Message defining units and multipliers used for fields of other messages
# @Field: TimeUS: Time since system startup
# @Field: FmtType: numeric reference to associated FMT message
# @Field: UnitIds: each character refers to a UNIT message. The unit at an offset corresponds to the field at the same offset in FMT.Format
# @Field: MultIds: each character refers to a MULT message. The multiplier at an offset corresponds to the field at the same offset in FMT.Format

# @LoggerMessage: MULT
# @Description: Message mapping from single character to numeric multiplier
# @Field: TimeUS: Time since system startup
# @Field: Id: character referenced by FMTU
# @Field: Mult: numeric multiplier

# @LoggerMessage: PARM
# @Description: parameter value
# @Field: TimeUS: Time since system startup
# @Field: Name: parameter name
# @Field: Value: parameter vlaue

# @LoggerMessage: MSG
# @Description: Textual messages
# @Field: TimeUS: Time since system startup
# @Field: Message: message text

# @LoggerMessage: ERR
# @Description: Specifically coded error messages
# @Field: TimeUS: Time since system startup
# @Field: Subsys: Subsystem in which the error occurred
# @Field: ECode: Subsystem-specific error code

# @LoggerMessage: MAVC
# @Description: MAVLink command we have just executed
# @Field: TimeUS: Time since system startup
# @Field: TS: target system for command
# @Field: TC: target component for command
# @Field: Fr: command frame
# @Field: Cmd: mavlink command enum value
# @Field: Cur: current flag from mavlink packet
# @Field: AC: autocontinue flag from mavlink packet
# @Field: P1: first parameter from mavlink packet
# @Field: P2: second parameter from mavlink packet
# @Field: P3: third parameter from mavlink packet
# @Field: P4: fourth parameter from mavlink packet
# @Field: X: X coordinate from mavlink packet
# @Field: Y: Y coordinate from mavlink packet
# @Field: Z: Z coordinate from mavlink packet
# @Field: Res: command result being returned from autopilot
# @Field: WL: true if this command arrived via a COMMAND_LONG rather than COMMAND_INT
