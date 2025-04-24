# INITIALIZATION

# import os

# import pip
# pip.main(["install","numpy"])
import numpy as np
import math
from scipy.io.wavfile import write
import matplotlib.pyplot as plt

# SETTINGS AND GLOBAL VARIABLES

# Custom message (containing letters and/or spaces ' ')
msg = "SOS HELP ";

# Morse elements to pulses
interelement_space = '0';
interletter_space = '000';
interword_space = '0000000';
dot = '1';
dash = '111';

# Letters (excluding space character ' ') and their morse codes.
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

# Pulse duration, in seconds
pulse_duration = 0.1;
pulse_rate = 1.0/pulse_duration;

# Sound frequency, in Hz
sound_freq = ;
# Sound amplitude, in arbitrary units (value must be from 0 to 32767)
sound_amplitude = ; 

# Sampling rate, in samples per second
samp_rate = 44100;

# FUNCTION DEFINITIONS

def morse_to_pulses(morse, interelement_space, dot, dash):
	# Converts a string containing only '.'s or '-' into a string of '0's and '1's
	# morse should not contain any space characters ' '.
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
			print('Error: input of morse_to_pulses should only contain .s and -s.');
			[0][1]; # Crashes the programme
		j = j + 1;

	return pulses;

def add_pulses_to_key(key, interelement_space, dot, dash):
	# Appends the binary string representing the morse code of each letter
	# to the end of each row of the key array
	j = 0;
	j_max = len(key) - 1;
	while j <= j_max:
		morse = key[j][1];
		key[j].append(morse_to_pulses(morse, interelement_space, dot, dash));
		j = j + 1;

	return key;

def letter_to_pulses(letter, key):
	# Converts a letter (excluding ' ') to a binary string of its morse code
	ok_letters = [row[0] for row in key];
	pulses = [row[2] for row in key];
	j = ok_letters.index(letter);
	return pulses[j];

def msg_to_pulses(msg, key, interletter_space, interword_space):
	# Converts a message (containing letters and/or spaces ' ')
	# to a binary string of its morse code (pulses)
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
	t = j * pulse_duration;
	return t;

def t_to_samp_index(t, samp_rate):
	# SOLUTION HERE
	return n;

def samp_ts(start_t, end_t, samp_rate):
	# SOLUTION HERE
	return ts;

def tone(sound_freq, sound_amplitude, start_t, end_t, samp_rate):
        # Consider a sound of a given frequency, amplitude, start and end times.
        # The sound is sampled at samp_rate.
        # This function returns an array of sound samples.
	
	# SOLUTION HERE
	# Angular frequency, in radians per second
	# SOLUTION HERE
	# Sinusoidal wave of a single tone
	# SOLUTION HERE

def pulses_to_samps(pulses, pulse_duration, sound_freq, sound_amplitude, samp_rate):
        # Converts a binary string (pulses) to an int16 array of the sound samples.
	# SOLUTION HERE
	
	# Rounds each element of samps to the nearest integer
        # and converts it to the int16 data type.
	# SOLUTION HERE
	return samps;

# EXECUTION

print(msg);

# Pulses
add_pulses_to_key(key, interelement_space, dot, dash);
pulses = msg_to_pulses(msg, key, interletter_space, interword_space);
print(pulses);

# Sound samples
samps = pulses_to_samps(pulses, pulse_duration, sound_freq, sound_amplitude, samp_rate);

# Times, in seconds, of the signal values in samps
ts = samp_ts(0, pulse_index_to_start_t(len(pulses), pulse_duration), samp_rate);

# Converts the array of samps into a .wav sound file.
write('02_sound.wav', samp_rate, samps.astype(np.int16));

# GRAPH PLOTTING

# The graph scales can be adjusted to see different features of the graph.

# Figure 1
# The axes scales are set to see the envelope representing the pulses of the morse code.
plt.clf();
x_axis = ts;
y_axis = samps;
plt.plot(x_axis, y_axis);
plt.ylim([-32768, 32767]);
plt.xlabel('time / s');
plt.ylabel('signal / arbitrary units');
plt.savefig('03 Transmitted sound envelope.png');

# Figure 2
# The axes scales are set to see the periodicity of the sound signal 
# of a '1'/on-pulse with respect to time.
# Hover the cursor over a peak (e.g. maximum positive displacement) on the graph.
# Record the x-coordinate (t / s) shown on the bottom-right of the window.
# Repeat by hovering the cursor over the next peak (1 period later).
# Calculate sound_period = the difference between the two values of t/s.
# Calculate sound_freq = 1/sound_period.
plt.figure();
x_axis = ts;
y_axis = samps;
plt.plot(x_axis, y_axis);
plt.xlabel('time / s');
plt.ylabel('signal / arbitrary units');
plt.xlim([1, 1.01]);
plt.ylim([-32768, 32767]);
plt.savefig('04 Transmitted sound period.png');

plt.show()

print("Done!");
