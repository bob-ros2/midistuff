# MIDISTUFF

A very simple MIDI recorder which either can be used as importable library or as standalone script. It works on multiple plattforms with connected MIDI interface.

This project is still in Beta phase and timings may jitter!


## Installation Prerequisites

Use the package manager [pip3](https://pip.pypa.io/en/stable/) to install the below dependencies.


```bash
pip3 install python-rtmidi
pip3 install mido
```

## Usage

```bash
# print help
python midirec.py -h
usage: midirec.py [-h] [-l] [-d DEVICE] [-n NAME] [-a SECS] [-v]

The very simple MIDI recorder.

options:
  -h, --help            show this help message and exit
  -l, --list            list available devices (default: False)
  -d DEVICE, --device DEVICE
                        MIDI device to be opened by index (default: 0)
  -n NAME, --name NAME  name of MIDI file(s) to be stored, can be a path (default: track)
  -a SECS, --auto SECS  auto mode silence timeout when to record a new track (default: 0)
  -v, --verbose         debug mode (default: False)

# get device list
python midirec.py -l

# one shot recording using MIDI device 0, the first event starts the recording
# CTRL+C stops recording and saves the track as track.mid file
python midirec.py

# record in auto mode with n seconds silence timeout
# when timeout happens the current track will be stored and the recording starts again with a new midi track
python midirec.py -a 30
2023-09-18 19:23:29.854 Waiting for first event ...
2023-09-18 19:26:52.791 Recording started
2023-09-18 19:29:01.695 Save MIDI file track_20230918-192652.mid
2023-09-18 19:29:01.695 Timeout exceeded, starting a new track
2023-09-18 19:29:01.700 Waiting for first event ...

# additionally there are two OS wrapper scripts available which simplifies script execution
# midirec.sh
# midirec.bat
```

## Contributing

Pull requests are welcome. For major changes, please open an issue first
to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License

[Apache2.0](https://www.apache.org/licenses/LICENSE-2.0)