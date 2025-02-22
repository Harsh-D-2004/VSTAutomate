import requests
import mido
import time
import json

# 🎹 Set up MIDI output (update with your correct MIDI port name)
MIDI_PORT = "loopMIDI Port 1 1"  # Adjust if needed
midi_out = mido.open_output(MIDI_PORT)

# 🔑 Google Gemini API Key (Replace with your actual key)
API_KEY = "AIzaSyBzRisNmv2lm0nw1fj4Kml_t-2V_KIQtn0"  # Replace with your actual API key
URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

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

# 🧠 Function to get MIDI values from LLM
def get_llm_response(prompt):
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    headers = {"Content-Type": "application/json"}
    
    try:
        response = requests.post(URL, headers=headers, json=data)
        response.raise_for_status()
        
        result = response.json()
        llm_text = result.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "")

        # 🛠️ Clean JSON output
        cleaned_str = llm_text.replace("```json", "").replace("```", "").strip()
        print("🔄 LLM Response:", cleaned_str)

        return cleaned_str
    except requests.exceptions.RequestException as e:
        print(f"❌ API Error: {e}")
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
