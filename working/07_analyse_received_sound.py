# getting things ready

# import os

# import pip
# pip.main(['install','numpy'])
import numpy as np
import math
import os.path
import sys
import glob
import json
from scipy.io.wavfile import read, write
import matplotlib.pyplot as plt

# grab the current folder path
current_dir = os.path.dirname(os.path.abspath(__file__))

# make a folder for our output stuff
output_dir = os.path.join(current_dir, "receiver_output")
os.makedirs(output_dir, exist_ok=True)

# where to find the transmitted signal
transmitter_dir = os.path.join(current_dir, "transmitter_output")

# set this to true if you wanna test with fake data
test_mode = False

# try to grab the message details if they exist
message_info = None
message_info_path = os.path.join(transmitter_dir, 'message_info.json')
if os.path.exists(message_info_path):
    with open(message_info_path, 'r') as f:
        message_info = json.load(f)
    print("loaded message info:")
    print(f"message: {message_info['message']}")
    print(f"duration: {message_info['duration']:.2f} seconds")
    print(f"sample rate: {message_info['sample_rate']} Hz")
    print(f"frequency: {message_info['frequency']} Hz")
    print(f"audio file: {message_info['audio_file']}")

# setup where we'll find/save all our files
FILES = {
    # input files - test file in working dir, real file from transmitter
    'test_sound': os.path.join(current_dir, 'test_received_sound.wav'),
    'input_sound': os.path.join(transmitter_dir, message_info['audio_file'] if message_info else 'transmitter_morse.wav'),
    # output files in our output folder
    'envelope_full': os.path.join(output_dir, 'receiver_signal_envelope.png'),
    'period': os.path.join(output_dir, 'receiver_signal_period.png'),
    'model_fit': os.path.join(output_dir, 'receiver_signal_model_fit.png')
}

# cleanup time! get rid of old files
print("cleaning up previous output files...")
# close any plots that might be open
plt.close('all')

# clean out the output folder if it exists
if os.path.exists(output_dir):
    print(f"cleaning output directory: {output_dir}")
    for file in os.listdir(output_dir):
        file_path = os.path.join(output_dir, file)
        try:
            if os.path.isfile(file_path):
                os.remove(file_path)
                print(f"deleted previous file: {file}")
        except Exception as e:
            print(f"couldn't delete {file}: {e}")

# also clean up any old test files lying around
for test_file in ['test_received_sound.wav']:
    test_path = os.path.join(current_dir, test_file)
    if os.path.exists(test_path):
        try:
            os.remove(test_path)
            print(f"deleted previous test file: {test_file}")
        except Exception as e:
            print(f"couldn't delete {test_file}: {e}")

# FUNCTION DEFINITIONS

def samp_index_to_t(n, samp_rate):
	# Convert sample index to time (in seconds)
	t = n * 1.0 / samp_rate
	return t

def samp_ts(samps, samp_rate):
	# Generate an array of time instants for all samples in samps
	ns = np.array(range(0, len(samps)))
	ts = samp_index_to_t(ns, samp_rate)
	return ts

def sound_wave_model(ts):
	# A sound wave is mathematically modelled using a cosine function.
	# Returns an array of samples of this mathematical model.
	
	# These parameters should be adjusted based on the actual received signal analysis
	# The values might need to be updated after examining the received sound
	A = 673        # Amplitude
	f = 2349       # Frequency in Hz (using the assigned sound frequency)
	t_max = 2.135547  # Time offset
	c = -6511      # Vertical offset
	
	model_samps = A * np.cos(2 * math.pi * f * (ts - t_max)) + c
	return model_samps

def create_test_file():
    """makes a fake signal file for testing"""
    print("\nmaking a dummy file for testing...")
    # first make a test signal
    duration = 10  # seconds
    sample_rate = 44100  # Hz
    t = np.linspace(0, duration, int(sample_rate * duration))
    # make something that looks like morse code
    test_signal = 1000 * np.sin(2 * np.pi * 2349 * t) + 300 * np.random.normal(0, 1, len(t))
    # add some on-off patterns
    morse_pattern = np.zeros_like(t)
    # just make some random pulses
    for i in range(10):
        start = i * 0.5
        end = start + 0.2
        morse_pattern[(t >= start) & (t < end)] = 1
    # combine the signal and pattern
    final_signal = test_signal * morse_pattern
    
    # convert to the right format
    final_signal = final_signal.astype(np.int16)
    
    # save it
    write(FILES['test_sound'], 44100, final_signal)
    print("made a test file 'test_received_sound.wav'")
    return FILES['test_sound']

# EXECUTION

# let's do it!

# figure out which file to use
input_file = FILES['test_sound'] if test_mode else FILES['input_sound']

# make sure we have a file to work with
if not os.path.exists(input_file):
    if test_mode:
        print(f"\nno test file found. making one...")
        # make a test signal
        duration = 10  # seconds
        t = np.linspace(0, duration, int(44100 * duration))
        # fake a morse code signal
        carrier = np.sin(2 * np.pi * 2349 * t)  # 2349 Hz beep
        message = np.where((t > 0.3) & (t < 4.0) | (t > 4.0) & (t < 8.1), 1, 0)  # on-off pattern
        signal = message * carrier * 10000  # combine them
        write(input_file, 44100, signal.astype(np.int16))
        print(f"made test file: {input_file}")
    else:
        raise FileNotFoundError(f"can't find input file {input_file}. run the transmitter first!")

# read in the sound file
print(f"\nreading sound file: {input_file}")
samp_rate, samps = read(input_file)
print(f"sample rate: {samp_rate} Hz")
print(f"number of samples: {len(samps)}")
print(f"duration: {len(samps)/samp_rate:.2f} seconds")

# make a time array for plotting
ts = np.linspace(0, len(samps)/samp_rate, len(samps))

# make some cool graphs

# first, show the whole signal
plt.figure(1)
plt.clf()
plt.plot(ts, samps)
plt.xlabel('Time (seconds)')
plt.ylabel('Signal Amplitude')
if message_info:
    plt.title(f'Received Signal Envelope\nMessage: "{message_info["message"]}"')
else:
    plt.title('Received Signal Envelope')
plt.grid(True)
plt.savefig(FILES['envelope_full'], dpi=300, bbox_inches='tight')
plt.close(1)

# then zoom in to see the waves
plt.figure(2)
plt.clf()
# find where the signal starts making noise
non_zero_indices = np.where(np.abs(samps) > 1000)[0]
if len(non_zero_indices) > 0:
    start_idx = non_zero_indices[0]
    start_time = ts[start_idx]
    plt.plot(ts[ts >= start_time][0:441], samps[start_idx:start_idx+441])
    plt.xlabel('Time (seconds)')
    plt.ylabel('Signal Amplitude')
    if message_info:
        plt.title(f'Received Signal Period Analysis\nFrequency: {message_info["frequency"]} Hz')
    else:
        plt.title('Received Signal Period Analysis')
    plt.grid(True)
    plt.savefig(FILES['period'], dpi=300, bbox_inches='tight')
plt.close(2)

# finally, compare it to our math model
plt.figure(3)
plt.clf()
# parameters for our wave equation
A = 20000  # how tall the waves are
f = message_info['frequency'] if message_info else 2349  # how fast they wiggle
phi = 2.135547  # shift left/right
C = 0      # shift up/down

# make the model wave
t_model = np.linspace(2, 2.01, 1000)
model = A * np.cos(2 * np.pi * f * (t_model - phi)) + C

# plot both real and model waves
mask = (ts >= 2.0) & (ts <= 2.01)
plt.plot(ts[mask], samps[mask], 'b-', label='Received Signal')
plt.plot(t_model, model, 'r--', label='Mathematical Model')
plt.xlabel('Time (seconds)')
plt.ylabel('Signal Amplitude')
plt.title('Received Signal vs Mathematical Model\n' + \
         f'Model: {A}·cos(2π·{f}·(t - {phi:.6f})) + {C}')
plt.legend()
plt.grid(True)
plt.savefig(FILES['model_fit'], dpi=300, bbox_inches='tight')
plt.close(3)

print("\nanalysis complete! files created:")
print(f"1. {os.path.basename(FILES['envelope_full'])}")
print("   - shows the complete signal envelope")
print(f"   - duration: {len(samps)/samp_rate:.2f} seconds")

print(f"\n2. {os.path.basename(FILES['period'])}")
print("   - shows detailed signal waveform")
print("   - used to verify signal frequency")

print(f"\n3. {os.path.basename(FILES['model_fit'])}")
print("   - compares received signal to mathematical model")
print("   - shows signal quality and accuracy")

if test_mode:
    print("\nnote: analysis performed on test file")
print("\nready for signal interpretation!")
