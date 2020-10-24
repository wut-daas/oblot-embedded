import os
import math

from dataflash import Dataflash


def main():
    out_dir = 'out'
    root_dir = os.path.dirname(os.path.abspath(__file__))
    if not os.path.exists(os.path.join(root_dir, out_dir)):
        os.makedirs(os.path.join(root_dir, out_dir), 0o777)

    filename = 'output.bin'
    with open(os.path.join(root_dir, out_dir, filename), 'wb') as fout:
        df = Dataflash(fout)
        df.add_message('SINE', 'Qd', 'TimeUS,Sine', units='s-', multipliers='F?')
        df.write_header()
        start = df.time_us()
        for i in range(200):
            fout.write(df.pack_message('SINE', start + i*int(1e6), math.sin(float(i)/10.0)))


if __name__ == '__main__':
    main()
