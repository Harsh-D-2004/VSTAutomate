from flask import Flask, request, jsonify
import requests
import mido
import time
import json
import openai
from apiKey import OPEN_AI_API_KEY

app = Flask(__name__)

# 🎹 Set up MIDI output (update with your correct MIDI port name)
midi_ports = mido.get_output_names()

if midi_ports:
    # selected_port = midi_ports[0]  # Use the first available port
    # print(f"Using MIDI port: {selected_port}")
    midi_out = mido.open_output("loopMIDI Port 1 1")
else:
    print("No MIDI output ports available!")
    exit()


# # 🔑 Google Gemini API Key (Replace with your actual key)
# API_KEY = "AIzaSyBzRisNmv2lm0nw1fj4Kml_t-2V_KIQtn0"  # Replace with your actual API key
# URL = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={API_KEY}"

# 🎛️ MIDI CC Mappings
MIDI_CC_PARAMS = {
    "Cutoff": 74,       # Filter Cutoff
    "Resonance": 71,    # Filter Resonance
    "Volume": 7,        # Master Volume
}

# Store last MIDI values
display_values = {}

# 🎵 Function to send a MIDI Control Change (CC) message
def send_cc(control, value):
    global display_values
    
    NOTE = 60       # Middle C
    VELOCITY = 100  # Loudness
    DURATION = 1.0  # Seconds

    msg = mido.Message('control_change', control=control, value=value)
    midi_out.send(msg)
    print(f"🎚️ Set CC {control} = {value}")
    
    # Update stored values
    for key, cc_num in MIDI_CC_PARAMS.items():
        if cc_num == control:
            display_values[key] = value
    
    # Play the note
    midi_out.send(mido.Message('note_on', note=NOTE, velocity=VELOCITY))
    time.sleep(DURATION)
    
    # Stop the note
    midi_out.send(mido.Message('note_off', note=NOTE, velocity=0))
    print(f"🎵 Stopped Note {NOTE}")
    
    time.sleep(0.5)

# 🧠 Function to get MIDI values from LLM

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


def get_better_responce(prompt):
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


@app.route('/generate', methods=['POST'])
def generate_midi():
    global display_values
    
    prompt = request.json.get("prompt", "Make it sound like a Martin Garrix-style synth.")
    
    context = f"""
    Generate MIDI CC values for filter cutoff (CC74), resonance (CC71), and volume (CC7) 
    in the range of 0-127. Format the response strictly as JSON:
    {{"Cutoff": 80, "Resonance": 50, "Volume": 100}}.
    {prompt}
    """
    
    llm_response = get_llm_response(context)
    print(f"🧠 LLM Response: {llm_response}")
    
    if llm_response:
        try:
            midi_values = json.loads(llm_response)
            print(f"🎵 MIDI Values: {midi_values}")
            for param, cc_value in midi_values.items():
                cc_number = MIDI_CC_PARAMS.get(param)
                if cc_number is not None:
                    send_cc(cc_number, cc_value)

            prnt = "🎵 MIDI Values: " + str(midi_values) + "This are the values that you have to send to the VST Host\n this is a api that will send the values to the frontend i want the response message to be little gen-z and genalpha type of response and don't include much technical information and it fun to read and see \n and just give me message as a response no need of anything else"
            llm_response = get_better_responce(prnt)
            new_res = json.loads(llm_response) 
            print("🧠 LLM Response: "+ new_res.get("message"))
            return jsonify({"message": new_res.get("message"), "values": midi_values})
        except json.JSONDecodeError:
            return jsonify({"error": "Failed to parse LLM response as JSON."}), 400
    
    return jsonify({"error": "LLM request failed."}), 500

@app.route('/status', methods=['GET'])
def get_status():
    return jsonify(display_values)

if __name__ == '__main__':
    app.run(debug=True)
