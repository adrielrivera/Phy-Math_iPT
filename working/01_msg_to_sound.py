# getting things ready

# import os

# import pip
# pip.main(["install","numpy"])
import numpy as np
import math
import os
import glob
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

# grab the current folder path
current_dir = os.path.dirname(os.path.abspath(__file__))

# make a folder for our output stuff
output_dir = os.path.join(current_dir, "transmitter_output")
os.makedirs(output_dir, exist_ok=True)

# hey, put your message here! (spaces are cool too)
msg = "  HELLO WORLD  "  # stick 2 spaces at start and end, 1 space between words
# clean up the message so we can use it in filenames
clean_msg = ''.join(c for c in msg.strip() if c.isalnum())

# setup where we're gonna save all our files
OUTPUT_FILES = {
    'morse_sound': os.path.join(output_dir, f'transmitter_morse_{clean_msg}.wav'),
    'envelope': os.path.join(output_dir, 'transmitter_signal_envelope.png'),
    'period': os.path.join(output_dir, 'transmitter_signal_period.png')
}

# stuff for making morse code patterns
interelement_space = '0';  # gap between dots and dashes
interletter_space = '000';  # gap between letters
interword_space = '0000000';  # big gap between words
dot = '1';  # short beep
dash = '111';  # long beep

# here's all the morse code translations
# each letter gets its dots and dashes
key = \
[['A', '.-'], ['B', '-...'], ['C', '-.-.'], ['D', '-..'], ['E', '.'], \
 ['F', '..-.'], ['G', '--.'], ['H', '....'], ['I', '..'], ['J', '.---'], \
 ['K', '-.-'], ['L', '.-..'], ['M', '--'], ['N', '-.'], ['O', '---'], \
 ['P', '.--.'], ['Q', '--.-'], ['R', '.-.'], ['S', '...'], ['T', '-'], \
 ['U', '..-'], ['V', '...-'], ['W', '.--'], ['X', '-..-'], ['Y', '-.--'], \
 ['Z', '--..'], \
 ['0', '-----'], ['1', '.----'], ['2', '..---'], ['3', '...--'], ['4', '....-'], \
 ['5', '.....'], ['6', '-....'], ['7', '--...'], ['8', '---..'], ['9', '----.'], \
 ['.', '.-.-.-'], [',', '--..--'], ['?', '..--..'], [':', '---...'], ['-', '-....-']];

# how long each pulse should be
pulse_duration = 0.1;  # seconds
pulse_rate = 1.0/pulse_duration;  # pulses per second

# sound settings
sound_freq = 2349;  # the beep frequency in Hz (from the assignment)
sound_amplitude = 20000;  # how loud the beep is (max 32767)

# audio quality settings
samp_rate = 44100;  # samples per second (CD quality)

# all the functions we need

def morse_to_pulses(morse, interelement_space, dot, dash):
    # turns dots and dashes into 1s and 0s
    # don't put spaces in here!
    pulses = '';
    j = 0;
    j_max = len(morse) - 1;
    while j <= j_max:

        if j != 0:
            pulses = pulses + interelement_space;

        if morse[j] == '.':
            pulses = pulses + dot;
        elif morse [j] == '-':
            pulses = pulses + dash;
        else:
            print('whoops! only dots and dashes allowed here');
            [0][1];  # crash the program
        j = j + 1;

    return pulses;

def add_pulses_to_key(key, interelement_space, dot, dash):
    # adds the binary pattern to each letter in our lookup table
    j = 0;
    j_max = len(key) - 1;
    while j <= j_max:
        morse = key[j][1];
        key[j].append(morse_to_pulses(morse, interelement_space, dot, dash));
        j = j + 1;

    return key;

def letter_to_pulses(letter, key):
    # converts a single letter to its beep pattern
    ok_letters = [row[0] for row in key];
    pulses = [row[2] for row in key];
    j = ok_letters.index(letter);
    return pulses[j];

def msg_to_pulses(msg, key, interletter_space, interword_space):
    # turns your whole message into a beep pattern
    pulses = '';
    j = 0;
    j_max = len(msg) - 1;
    while j <= j_max:

        if msg[j] == ' ':
            pulses = pulses + interword_space;
        else:
            if j != 0:
                if msg[j-1] != ' ':
                    pulses = pulses + interletter_space;
            
            pulses = pulses + letter_to_pulses(msg[j], key);

        j = j + 1;
    
    return pulses;

def pulse_index_to_start_t(j, pulse_duration):
    # figures out when a pulse should start
    t = j * pulse_duration;
    return t;

def t_to_samp_index(t, samp_rate):
    # converts time to sample number
    n = int(round(t * samp_rate));
    return n;

def samp_ts(start_t, end_t, samp_rate):
    # makes a list of times for all our samples
    start_n = t_to_samp_index(start_t, samp_rate);
    end_n = t_to_samp_index(end_t, samp_rate);
    
    # make a list from start to end
    ns = np.arange(start_n, end_n + 1);
    
    # convert to actual times
    ts = ns / samp_rate;
    
    return ts;

def tone(sound_freq, sound_amplitude, start_t, end_t, samp_rate):
    # makes a beep sound between start and end time
    
    # get all the sample times
    ts = samp_ts(start_t, end_t, samp_rate);
    
    # math stuff for making waves
    omega = 2 * math.pi * sound_freq;
    
    # make the actual wave
    samps = sound_amplitude * np.sin(omega * ts);
    
    return samps;

def pulses_to_samps(pulses, pulse_duration, sound_freq, sound_amplitude, samp_rate):
    # turns our beep pattern into actual sound data
    
    # start with empty sound
    samps = np.array([]);
    
    # go through each pulse
    for j in range(len(pulses)):
        # when should this bit start and end?
        start_t = pulse_index_to_start_t(j, pulse_duration);
        end_t = pulse_index_to_start_t(j+1, pulse_duration);
        
        # make the sound for this bit
        if pulses[j] == '1':
            # make a beep for 1s
            pulse_samps = tone(sound_freq, sound_amplitude, start_t, end_t, samp_rate);
        else:
            # make silence for 0s
            pulse_samps = tone(sound_freq, 0, start_t, end_t, samp_rate);
        
        # add it to our sound
        samps = np.append(samps, pulse_samps);
    
    # round everything to whole numbers
    samps = np.round(samps);
    
    return samps;

# let's do it!

print("Input message:", msg)

# make the morse code
add_pulses_to_key(key, interelement_space, dot, dash)
pulses = msg_to_pulses(msg, key, interletter_space, interword_space)
print("Morse code pattern:", pulses)

# make the sound
samps = pulses_to_samps(pulses, pulse_duration, sound_freq, sound_amplitude, samp_rate)

# figure out the timing
ts = np.linspace(0, len(samps)/samp_rate, len(samps))

# save the sound file
write(OUTPUT_FILES['morse_sound'], samp_rate, samps.astype(np.int16))

# make some cool graphs

# first, show the whole signal
plt.figure(1)
plt.clf()
x_axis = ts
y_axis = samps
plt.plot(x_axis, y_axis)
plt.ylim([-32768, 32767])
plt.xlabel('Time (seconds)')
plt.ylabel('Signal Amplitude')
plt.title(f'Transmitted Morse Code Signal Envelope\nMessage: "{msg.strip()}"')
plt.grid(True)
plt.savefig(OUTPUT_FILES['envelope'], dpi=300, bbox_inches='tight')
plt.close(1)

# then zoom in to see the waves
plt.figure(2)
plt.clf()
x_axis = ts
y_axis = samps
# find where the signal starts making noise
non_zero_indices = np.where(np.abs(samps) > 1000)[0]
if len(non_zero_indices) > 0:
    start_idx = non_zero_indices[0]
    start_time = ts[start_idx]
    plt.plot(ts[ts >= start_time][0:441], samps[start_idx:start_idx+441])
    plt.xlabel('Time (seconds)')
    plt.ylabel('Signal Amplitude')
    plt.title(f'Transmitted Signal Period Analysis\nFrequency: {sound_freq} Hz')
    plt.grid(True)
    plt.savefig(OUTPUT_FILES['period'], dpi=300, bbox_inches='tight')
plt.close(2)

# save some info for the receiver
message_info = {
    'audio_file': os.path.basename(OUTPUT_FILES['morse_sound']),
    'message': msg.strip(),
    'duration': len(samps)/samp_rate,
    'sample_rate': samp_rate,
    'frequency': sound_freq,
    'amplitude': sound_amplitude
}

# dump it to a file
import json
with open(os.path.join(output_dir, 'message_info.json'), 'w') as f:
    json.dump(message_info, f, indent=4)

print("\nTransmission complete! Files created:")
print(f"1. {os.path.basename(OUTPUT_FILES['morse_sound'])}")
print(f"   - Contains the Morse code audio for: {msg.strip()}")
print(f"   - Duration: {len(samps)/samp_rate:.2f} seconds")
print(f"   - Sample rate: {samp_rate} Hz")
print(f"   - Frequency: {sound_freq} Hz")

print(f"\n2. {os.path.basename(OUTPUT_FILES['envelope'])}")
print("   - Shows the full signal envelope")

print(f"\n3. {os.path.basename(OUTPUT_FILES['period'])}")
print("   - Shows detailed signal waveform")
print("   - Used to verify signal frequency")

print("\n4. message_info.json")
print("   - Contains message metadata for the receiver")

print("\nReady for transmission!")
