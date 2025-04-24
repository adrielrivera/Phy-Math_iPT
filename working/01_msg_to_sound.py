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
msg = "  lebro james  ";  # 2 spaces before 1st word, 1 space between words, 2 spaces after 2nd word

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
sound_freq = 2349;  # Assigned value from the table
# Sound amplitude, in arbitrary units (value must be from 0 to 32767)
sound_amplitude = 20000;  # Setting a reasonable amplitude value

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
	# Convert time t (in seconds) to sample index n
	n = int(round(t * samp_rate));
	return n;

def samp_ts(start_t, end_t, samp_rate):
	# Generate an array of time instants for all samples between start_t and end_t
	# Calculate the sample indices corresponding to start and end times
	start_n = t_to_samp_index(start_t, samp_rate);
	end_n = t_to_samp_index(end_t, samp_rate);
	
	# Create array of sample indices from start_n to end_n (inclusive)
	ns = np.arange(start_n, end_n + 1);
	
	# Convert sample indices to time values
	ts = ns / samp_rate;
	
	return ts;

def tone(sound_freq, sound_amplitude, start_t, end_t, samp_rate):
    # Consider a sound of a given frequency, amplitude, start and end times.
    # The sound is sampled at samp_rate.
    # This function returns an array of sound samples.
	
    # Get array of time instants for all samples
    ts = samp_ts(start_t, end_t, samp_rate);
    
    # Angular frequency, in radians per second
    omega = 2 * math.pi * sound_freq;
    
    # Sinusoidal wave of a single tone
    samps = sound_amplitude * np.sin(omega * ts);
    
    return samps;

def pulses_to_samps(pulses, pulse_duration, sound_freq, sound_amplitude, samp_rate):
    # Converts a binary string (pulses) to an int16 array of the sound samples.
    
    # Initialize an empty array to store all samples
    samps = np.array([]);
    
    # Process each pulse in the binary string
    for j in range(len(pulses)):
        # Calculate start and end times for this pulse
        start_t = pulse_index_to_start_t(j, pulse_duration);
        end_t = pulse_index_to_start_t(j+1, pulse_duration);
        
        # Generate tone samples for this pulse
        if pulses[j] == '1':
            # For a '1' pulse, generate a tone
            pulse_samps = tone(sound_freq, sound_amplitude, start_t, end_t, samp_rate);
        else:
            # For a '0' pulse, generate silence (amplitude = 0)
            pulse_samps = tone(sound_freq, 0, start_t, end_t, samp_rate);
        
        # Append these samples to the overall samples array
        samps = np.append(samps, pulse_samps);
    
    # Rounds each element of samps to the nearest integer
    # and converts it to the int16 data type.
    samps = np.round(samps);
    
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
