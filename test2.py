import requests
import mido
import time
import json
import openai
from apiKey import OPEN_AI_API_KEY

# 🎹 Set up MIDI output (update with your correct MIDI port name)
midi_ports = mido.get_output_names()

if midi_ports:
    selected_port = midi_ports[0]  # Use the first available port
    print(f"Using MIDI port: {selected_port}")
    midi_out = mido.open_output(selected_port)
else:
    print("No MIDI output ports available!")
    exit()

# 🎛️ MIDI CC Mappings
MIDI_CC_PARAMS = {
    "Cutoff": 74,       # Filter Cutoff
    "Resonance": 71,    # Filter Resonance
    "Volume": 7,        # Master Volume
}

# 🎵 Function to send a MIDI Control Change (CC) message
def send_cc(control, value):
    NOTE = 60       # Middle C
    VELOCITY = 100  # Loudness
    DURATION = 1.0  # Seconds

    msg = mido.Message('control_change', control=control, value=value)
    midi_out.send(msg)
    print(f"🎚️ Set CC {control} = {value}")

    # Play the note
    midi_out.send(mido.Message('note_on', note=NOTE, velocity=VELOCITY))
    time.sleep(DURATION)  # Hold the note

    # Stop the note
    midi_out.send(mido.Message('note_off', note=NOTE, velocity=0))
    print(f"🎵 Stopped Note {NOTE}")

    time.sleep(0.5)  # Small delay

# Get API Key
# import from .apikey
api_key = OPEN_AI_API_KEY

if not api_key:
    raise ValueError("API key not found! Add it to .env file.")

# print(api_key)

client = openai.OpenAI(api_key=api_key)
# Function to send request to Gemini API
def get_llm_response(prompt):
    try:
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {"role": "system", "content": "You are an expert in sound design and MIDI automation. "
                                              "Respond only with a valid JSON object, nothing else."},
                {"role": "user", "content": prompt}
            ]
        )

        res = response.choices[0].message.content.strip()
        return res  # Directly return the response as a string
    except Exception as e:
        print("Error generating response:", e)
        return None


# 🎶 LLM Prompt
prompt = "Make it sound like a Martin Garrix-style synth."

context = f"""
Generate MIDI CC values for filter cutoff (CC74), resonance (CC71), and volume (CC7) 
in the range of 0-127. Format the response strictly as JSON:
{{"Cutoff": 80, "Resonance": 50, "Volume": 100}}.
{prompt}
"""


llm_response = get_llm_response(context)

if llm_response:
    try:
        # 📜 Parse JSON response from LLM
        midi_values = json.loads(llm_response)
        
        # 🎛️ Apply MIDI automation
        for param, cc_value in midi_values.items():
            cc_number = MIDI_CC_PARAMS.get(param)
            if cc_number is not None:
                send_cc(cc_number, cc_value)
    except json.JSONDecodeError:
        print("❌ Failed to parse LLM response as JSON.")

print("🎛️ MIDI automation complete! 🚀")
