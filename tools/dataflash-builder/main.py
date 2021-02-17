import os
import math
import argparse

from dataflash import Dataflash
from df_kaitaistruct import write_ksy

parser = argparse.ArgumentParser()
parser.add_argument('-i', '--input', help='Dataflash log to create ksy definitions from')
args = parser.parse_args()

def main():
    out_dir = 'out'
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root_dir, out_dir)):
        os.makedirs(os.path.join(root_dir, out_dir), 0o777)

    filename = 'output.bin'
    with open(os.path.join(root_dir, out_dir, filename), 'wb') as fout:
        df = Dataflash(fout)
        if args.input:
            parsed_msg_defs = []
            with open(args.input, 'rb') as fin:
                parsed_msg_defs = df.parse_msg_defs(fin)
                write_ksy(parsed_msg_defs)
        else:
            df.add_message('SINE', 'Qf', 'TimeUS,Sine', units='s-', multipliers='F?')
            df.write_header()
            write_ksy(df.msg_defs)
            start = df.time_us()
            for i in range(200):
                fout.write(df.pack_message('SINE', start + i*int(1e6), math.sin(float(i)/10.0)))


if __name__ == '__main__':
    main()
