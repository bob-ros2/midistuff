#/usr/bin/env python
#
# Copyright 2023 BobRos
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import sys, time, logging, traceback, argparse, rtmidi, mido
from datetime import datetime, timedelta
from mido import Message, MidiTrack, MidiFile

# library

class MidiRecorder(object):
    """Very simple MIDI recorder class."""
    def __init__(self):
        self.msg = None
        self.time_last_msg = datetime.now()
        self.midiin = rtmidi.MidiIn()
        self.ports = self.midiin.get_ports()

    # channel voice messages
    STAT_NOFF   = 0b1000 # Note Off event
    STAT_NON    = 0b1001 # Note On event
    STAT_PKEYPR = 0b1010 # Polyphonic Key Pressure (Aftertouch)
    STAT_CCHNG  = 0b1011 # Control Change
    STAT_PCHNG  = 0b1100 # Program Change
    STAT_CHANPR = 0b1101 # Channel Pressure (After-touch)
    STAT_PWHEEL = 0b1110 # Pitch Wheel Change

    def get_ports(self):
        """Get MIDI port list determined in the init constructor."""
        return self.ports
    
    def open_port(self, port):
        """Open the given MIDI port by index."""
        if self.ports:
            self.midiin.open_port(port)
            # no sysex, timing and active sense messages
            self.midiin.ignore_types(True, True, False)
        else:
            raise Exception("No midi port for '%d'" % port)
        
    def close_port(self):
        """Close open MIDI port."""
        self.midiin.close_port()
    
    def wait_first_event(self):
        """Wait for first event on opened MIDI port."""
        while True:
            self.msg = self.midiin.get_message()
            if self.msg:
                message, deltatime = self.msg
                if message[0] != 254: # active sense ignore
                    if message[0]:
                        self.time_last_msg = datetime.now()
                        return
                    
    def save_track(self, path):
        """Save track to MIDI file."""
        self.mid.save(path)

    def start_recording(self, tempo=120, debug=False):
        """Start recording of a new Track."""
        self.tempo = tempo
        self.debug = debug
        self.abstime = 0
        self.mid = MidiFile(type=0)
        self.track = MidiTrack()
        self.mid.tracks.append(self.track)
        if self.msg: self.__call__(self.msg)
        self.midiin.set_callback(self)

    def __call__(self, event, data=None):
        """This function is called for every incoming event."""
        msg, deltatime = event
        channel = msg[0] & 0x0F
        self.abstime += deltatime
        if msg[0] != 254: # ignore active sense
            miditime = int(round(mido.second2tick(self.abstime, 
                self.mid.ticks_per_beat, mido.bpm2tempo(self.tempo))))

            if msg[0] >> 4 == self.STAT_NON:
                self.track.append(Message('note_on', channel=channel, 
                    note=msg[1], velocity=msg[2], time=miditime))
                if self.debug: self.verbose('note_on', msg, deltatime)
                self.abstime = 0
            elif msg[0] >> 4 == self.STAT_NOFF:
                self.track.append(Message('note_off', channel=channel, 
                    note=msg[1], velocity=msg[2], time=miditime))
                if self.debug: self.verbose('note_off', msg, deltatime)
                self.abstime = 0
            elif msg[0] >> 4 == self.STAT_PKEYPR:
                self.track.append(Message('polytouch', channel=channel, 
                    control=msg[1], value=msg[2], time=miditime))
                if self.debug: self.verbose('polytouch', msg, deltatime)
            elif msg[0] >> 4 == self.STAT_CCHNG:
                self.track.append(Message('control_change', channel=channel, 
                    control=msg[1], value=msg[2], time=miditime))
                if self.debug: self.verbose('control_change', msg, deltatime)
            elif msg[0] >> 4 == self.STAT_PCHNG:
                self.track.append(Message('program_change', channel=channel, 
                    control=msg[1], value=msg[2], time=miditime))
                if self.debug: self.verbose('program_change', msg, deltatime)
            elif msg[0] >> 4 == self.STAT_CHANPR:
                self.track.append(Message('aftertouch', channel=channel, 
                    control=msg[1], value=msg[2], time=miditime))
                if self.debug: self.verbose('aftertouch', msg, deltatime)
            elif msg[0] >> 4 == self.STAT_PWHEEL:
                self.track.append(Message('pitchwheel', channel=channel, 
                    control=msg[1], value=msg[2], time=miditime))
                if self.debug: self.verbose('pitchwheel', msg, deltatime)
            elif self.debug:
                self.verbose('unknown', msg, deltatime)

            self.time_last_msg = datetime.now()

    def verbose(self, name, msg, deltatime):
        """Prints incoming event."""
        logging.info(
            "%-14s %s channel: %2d delta: %6.3f absolute: %6.3f msg: %s" 
            % (name, '{0:b}'.format(msg[0]), msg[0] & 0x0F, 
               deltatime, self.abstime, str(msg)))


# entry point as script

if __name__ == '__main__':
    parser = argparse.ArgumentParser(
        description='The very simple MIDI recorder.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-l', '--list', 
        action="store_true", 
        help='list available devices')
    parser.add_argument(
        '-d', '--device', 
        type=int, 
        help='MIDI device to be opened by index', 
        default=0)
    parser.add_argument(
        '-n', '--name', 
        type=str, 
        help='name of MIDI file(s) to be stored, can be a path', 
        default="track")
    parser.add_argument(
        '-a', '--auto', 
        type=int, 
        help='auto mode silence timeout when to record a new track', 
        default=0, metavar="SECS")
    parser.add_argument(
        '-v', '--verbose', 
        action="store_true", 
        help='debug mode, this can have impact on timings')
    args = parser.parse_args()

    # init

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    timeout = timedelta(seconds=args.auto)
    if args.auto:
        filename = args.name + '_' + datetime.now().strftime(
            "%Y%m%d-%H%M%S") + '.mid'
    else:
        filename = args.name + '.mid'
    recorder = MidiRecorder()

    # option list devices

    if args.list:
        ports = recorder.get_ports()
        for port in ports:
            print(ports.index(port), ":", port)
        sys.exit(0)

    # start recording

    try:
        recorder.open_port(args.device)
        logging.info("Waiting for first event ...")
        recorder.wait_first_event()
        recorder.start_recording(debug=args.verbose)
        logging.info("Recording started")

        # program loop

        while True:
            time.sleep(0.01)
            # nothing to do here, the mido event callback runs in 
            # another thread
            # in auto mode take care to produce new tracks after a certain 
            # break timeout
            if args.auto:
                if datetime.now() > recorder.time_last_msg + timeout:
                    logging.info("Save MIDI file " + filename)
                    logging.info("Timeout exceeded, starting a new track")
                    recorder.save_track(filename)
                    recorder.close_port()
                    recorder.open_port(args.device)
                    logging.info("Waiting for first event ...")
                    recorder.wait_first_event()
                    filename = "%s_%s.mid" % ( 
                        args.name, datetime.now().strftime("%Y%m%d-%H%M%S"))
                    recorder.start_recording(debug=args.verbose)
                    logging.info("Recording started")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.info("%s: %s %s" 
            % (type(e).__name__, str(e)), str(traceback.format_exception(e)))
        sys.exit(1)

    recorder.close_port()
    logging.info("Save MIDI file " + filename)
    recorder.save_track(filename)
