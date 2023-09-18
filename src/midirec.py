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
import sys, time, logging, argparse, rtmidi, mido
from typing import Any
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
                if message[0] != 254: #active sense ignore
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
        self.activesense = 0
        self.mid = MidiFile()
        self.track = MidiTrack()
        self.mid.tracks.append(self.track)
        self.midiin.set_callback(self)

    def __call__(self, event, data=None):
        """This function is called for every inconmning event."""
        if self.msg: # process once very first event
            msg = self.msg
            self.msg = None
            self.__call__(msg)
        message, deltatime = event
        self.activesense += deltatime
        if message[0] != 254: # ignore active sense
            self.time_last_msg = datetime.now()
            miditime = int(round(mido.second2tick(self.activesense, self.mid.ticks_per_beat, mido.bpm2tempo(self.tempo))))
            if self.debug:
                logging.info('deltatime: ' + str(deltatime) + ' msg: ' + str(message) + ' activecomp: ' + str(self.activesense))
            if message[0] == 144:
                self.track.append(Message('note_on', note=message[1], velocity=message[2], time=miditime))
                self.activesense = 0
            elif message[0] == 176:
                self.track.append(Message('control_change', channel=1, control=message[1], value=message[2], time=miditime))


# main

def main():
    parser = argparse.ArgumentParser(
        description='The very simple MIDI recorder.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter)
    parser.add_argument(
        '-l', '--list', action="store_true", help='list available devices')
    parser.add_argument(
        '-d', '--device', type=int, help='MIDI device to be opened by index', default=0)
    parser.add_argument(
        '-n', '--name', type=str, help='name of MIDI file(s) to be stored, can be a path', default="track")
    parser.add_argument(
        '-a', '--auto', type=int, help='auto mode silence timeout when to record a new track', default=0, metavar="SECS")
    parser.add_argument(
        '-v', '--verbose', action="store_true", help='debug mode')
    args = parser.parse_args()

    # init

    logging.basicConfig(
        format='%(asctime)s.%(msecs)03d %(message)s',
        level=logging.INFO,
        datefmt='%Y-%m-%d %H:%M:%S')
    recorder = MidiRecorder()
    timeout = timedelta(seconds=args.auto)
    if args.auto:
        filename = args.name + '_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.mid'
    else:
        filename = args.name + '.mid'

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
            time.sleep(0.001)
            # in auto mode take care to produce new tracks after a certain break timeout
            if args.auto:
                if datetime.now() > recorder.time_last_msg + timeout:
                    logging.info("Save MIDI file " + filename)
                    logging.info("Timeout exceeded, starting a new track")
                    recorder.save_track(filename)
                    recorder.close_port()
                    recorder.open_port(args.device)
                    logging.info("Waiting for first event ...")
                    recorder.wait_first_event()
                    filename = args.name + '_' + datetime.now().strftime("%Y%m%d-%H%M%S") + '.mid'
                    recorder.start_recording(debug=args.verbose)
                    logging.info("Recording started")
    except KeyboardInterrupt:
        pass
    except Exception as e:
        logging.info("Exception: " + type(e).__name__ + ': ' + str(e))
        sys.exit(1)

    logging.info("Save MIDI file " + filename)
    recorder.save_track(filename)

# entry point as script

if __name__ == '__main__':
    main()
