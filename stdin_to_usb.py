import sys
import serial
import time

def parse_cmdline(argv):
    baud_rate = 115200
    com_port = "COM3"

    if (len(argv) == 1):
        return com_port, baud_rate

    elif (len(argv) == 2):
        com_port = argv[1]
        return com_port, baud_rate

    elif (len(argv) == 3):
        com_port = argv[1]
        baud_rate = int(argv[2])
        return com_port, baud_rate

    else:
        return "", -1


def print_help():
    print "stdin_to_usb.py"
    print ""
    print "Forwards standard input to USB"
    print ""
    print "Usage:"
    print "  python stdin_to_usb.py [com_port [baud_rate]]"
    print ""
    print "  com_port - set com port which will be used for communication (COM1|COM2|COM3...)"
    print "  baud_rate - set serial connection speed (115200, 9600, ...)"
    print ""


if __name__ == "__main__":
    com_port, baud_rate = parse_cmdline(sys.argv)

    if com_port == "":
        # parsing of command line did not succeed!
        print "error parsing command line!\n"
        print_help()
        exit()

    # print settings
    print "port: " + com_port + "speed: " + str(baud_rate)

    print "connecting..."
    usb_serial = serial.Serial(com_port, baud_rate, timeout=.1)
    time.sleep(2)
    print "connection established"

    # state machine:
    #   0. pipe_to_arduino
    #   1. pipe_to_stdout
    #   2. exit
    state = 0
    magic_char = '\xFF'
    last = "       "
    
    while state != 2:
        stdin_char = sys.stdin.read(1)

        if state == 0:
            if stdin_char != magic_char:
                usb_serial.write(stdin_char)
                sys.stdout.write("$"+stdin_char)
            else:
                # message start: switch to state 1
                state = 1
                
        elif state == 1:
            if stdin_char != magic_char:
                sys.stdout.write(stdin_char)

                last = last + stdin_char
                last = last[-6:]
                if last == "#EXIT#":
                    state = 2
            else:
                # end of message: switch to state 0
                state = 0
            
