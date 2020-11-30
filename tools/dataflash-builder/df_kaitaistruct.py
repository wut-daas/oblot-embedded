import os
import typing

start = '''meta:
  id: ap_dataflash
  file-extension: bin
  endian: le
seq:
  - id: messages
    type: message
    repeat: eos
types:
  message:
    seq:
      - id: magic
        contents: [0xA3, 0x95]
      - id: type
        type: u1
      - id: body
        type:
          switch-on: type
          cases:
'''

msg_unknown_def = '''  msg_unknown:
    seq:
      - id: body
        type: u1
        repeat: eos # multibyte terminators not supported'''

typedefs = {
    'a': 's2\n        repeat: expr\n        repeat-expr: 32',  # int16_t[32]
    'b': 's1',  # int8_t
    'B': 'u1',  # uint8_t
    'h': 's2',  # int16_t
    'H': 'u2',  # uint16_t
    'i': 's4',  # int32_t
    'I': 'u4',  # uint32_t
    'f': 'f4',  # float
    'd': 'f8',  # double (some online services don't support it)
    'n': 'str\n        encoding: ascii\n        size: 4',  # char[4]
    'N': 'str\n        encoding: ascii\n        size: 16',  # char[16]
    'Z': 'str\n        encoding: ascii\n        size: 64',  # char[64]
    'c': 's2\n        repeat: expr\n        repeat-expr: 100',  # int16_t * 100
    'C': 'u2\n        repeat: expr\n        repeat-expr: 100',  # uint16_t * 100
    'e': 's4\n        repeat: expr\n        repeat-expr: 100',  # int32_t * 100
    'E': 'u4\n        repeat: expr\n        repeat-expr: 100',  # uint32_t * 100
    'L': 's4',  # int32_t latitude/longitude
    'M': 'u1',  # uint8_t flight mode
    'q': 's8',  # int64_t
    'Q': 'u8'  # uint64_t
}


def write_ksy(msg_defs: dict, filename: typing.Optional[str] = None, allow_unknown: bool = False):
    """Writes a Kaitai Struct format description to specified .ksy file. See https://kaitai.io/ for more details

    Parameters
    ----------
    msg_defs : dict
        Dictionary of message definitions as defined in `Dataflash.msg_defs`
    filename : typing.Optional[str], optional
        Filename of .ksy file to write into, by default None saves to ``out/ap_dataflash.ksy``
    allow_unknown : bool
        Include a `msg_unknown_def` definition which will consume bytes until end of file but prevent errors.
        It should be done with a magic terminator, but Kaitai Struct does not support it currently (Issue #158).
    """
    if filename is None:
        out_dir = 'out'
        root_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.exists(os.path.join(root_dir, out_dir)):
            os.makedirs(os.path.join(root_dir, out_dir), 0o777)
        filename = 'ap_dataflash.ksy'
        filename = os.path.join(root_dir, out_dir, filename)

    with open(filename, 'w') as fout:
        fout.write(start)
        for msg in msg_defs:
            fout.write(f'            {msg["id"]}: {msg["name"].lower()}\n')
        if allow_unknown:
            fout.write('            _: msg_unknown\n')
        for msg in msg_defs:
            fout.write(f'  {msg["name"].lower()}:\n    seq:\n')
            labels = msg['labels'].lower().split(',')
            for i, field in enumerate(msg['fields']):
                fout.write(f'      - id: {labels[i]}\n        type: {typedefs[field]}\n')
        if allow_unknown:
            fout.write(msg_unknown_def)
