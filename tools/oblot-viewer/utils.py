import serial
import serial.tools.list_ports


def list_serial_ports():
    display = []
    names = []

    for n, (portname, desc, hwid) in enumerate(sorted(serial.tools.list_ports.comports())):
        display.append(u'{} - {}'.format(portname, desc))
        names.append(portname)

    return names, display


def heartbeat_format(msg):
    base_text = "time_boot_ms: {}ms , status: {}, sync_pwm: {}us"
    if msg is None:
        return base_text.format("{}", "{}", "{}")
    else:
        return base_text.format(msg.time_boot_ms, msg.status, msg.sync_pwm)


def battery_format(msg):
    base_text = "voltage: {}mV , main: {}cA, tail1: {}cA, tail2: {}cA, servo: {}cA, avio: {}cA"
    if msg is None:
        return base_text.format("{}", "{}", "{}", "{}", "{}", "{}")
    else:
        return base_text.format(msg.voltage, msg.current_motor_main,
                                msg.current_motor_tail1, msg.current_motor_tail2,
                                msg.current_servo, msg.current_avio)
