

import mido
import time

# Open the correct MIDI output port (verify the exact name)
midi_out = mido.open_output("loopMIDI Port 1 1")  # Check the exact port name

# Define MIDI note values
NOTE = 60  # Middle C
VELOCITY = 100  # Loudness

# TAL-Noisemaker Basic MIDI CC Mappings
MIDI_CC_PARAMS = {
    "Cutoff": 74,       # Filter Cutoff
    "Resonance": 71,    # Filter Resonance
    "Volume": 7,        # Master Volume
}

# Custom values you want to keep
DESIRED_VALUES = {
    "Cutoff": 90,       # Keep cutoff at 90
    "Resonance": 60,    # Keep resonance at 60
    "Volume": 100,      # Keep volume at 100
}

# Function to send a Control Change (CC) message
def send_cc(param_name, control, value):
    msg = mido.Message('control_change', control=control, value=value)
    midi_out.send(msg)
    print(f"Set {param_name} (CC {control}) = {value}")
    time.sleep(0.2)  # Allow VSTHost to process

# Play Note On
midi_out.send(mido.Message('note_on', note=NOTE, velocity=VELOCITY))
print(f"Playing Note {NOTE}")

# Set CC values and keep them
for param_name, cc in MIDI_CC_PARAMS.items():
    send_cc(param_name, cc, DESIRED_VALUES[param_name])  # Set to the desired value

# Stop the note (Note Off)
time.sleep(1)  # Hold note for 1 second before stopping
midi_out.send(mido.Message('note_off', note=NOTE, velocity=0))
print(f"Stopped Note {NOTE}")

print("🎛️ MIDI automation complete!")
