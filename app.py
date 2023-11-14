# from flask import Flask, render_template, request, jsonify
# from amadeus import Client, ResponseError
# import requests
# from elevenlabs import Voice, VoiceSettings
# from elevenlabs import set_api_key, generate
# import logging
# from datetime import datetime
# import openai
# import base64
# import os

# app = Flask(__name__)

# # Set your Eleven Labs API key
# set_api_key("68f3a83510f8eb969512ab39fc3825e3")

# BASE_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
# # Amadeus API configuration
# amadeus = Client(
#     client_id='PNYuOqaIHL2ejettffphI2mhicO20aEa',
#     client_secret='FaDIs7LgLd4KV4hv'
# )

# def get_iata_code(city_name):
#     """Function to get IATA code for a given city name using the provided API."""
#     api_url = f'https://api.api-ninjas.com/v1/airports?city={city_name}'
#     headers = {'X-Api-Key': '7h1sjfSTZYwWhbQ8gqU2lQ==WFlQgav23fzycnHa'}
#     response = requests.get(api_url, headers=headers)
#     if response.status_code == 200:
#         airports = response.json()
#         iata_codes = [airport['iata'] for airport in airports if airport['iata']]
#         return iata_codes[0] if iata_codes else None
#     else:
#         logging.error(f"Failed to fetch IATA code for city: {city_name}. Status code: {response.status_code}")
#         return None


# @app.route('/')
# def index():
#     return render_template('index.html')

# @app.route('/generate_audio', methods=['GET'])
# def generate_audio():
#     audio = generate(
#         text="Hey There, umm- Let me check, uh- Please wait...",
#         voice=Voice(
#             voice_id='21m00Tcm4TlvDq8ikWAM',
#             settings=VoiceSettings(stability=0.5, similarity_boost=0.5, style=0.2, use_speaker_boost=True)
#         )
#     )
#     audio_base64 = base64.b64encode(audio).decode('utf-8')
#     return jsonify({'audio': audio_base64})

# @app.route('/ask', methods=['POST'])
# def ask():
#     if request.method == 'POST':
#         user_query = request.json['question']
#         current_date = datetime.now().strftime('%Y-%m-%d')


#         headers = {
#             'Authorization': f'Bearer {openai.api_key}',
#             'Content-Type': 'application/json',
#         }

#         data = {
#             'model': 'gpt-4',
#             'messages': [
#                 {'role': 'user', 'content': f"Extract the origin city, destination city, and departure date "
#                                              "in the following format year-month-day from the following user query: "
#                                              f"'{user_query}'. If the year isn't specified, consider it as 2023. "
#                                              "If the extracted date is in the past compared to the current date, then "
#                                              f"consider the year as 2024. For example, if the day is tomorrow or something like "
#                                              f"2 days later, then consider the date of tomorrow or 2 days later from today's date, "
#                                              f"which is {current_date}. Please format your response as follows:\n"
#                                              "Origin City: <origin_city>\n"
#                                              "Destination City: <destination_city>\n"
#                                              "Departure Date: <departure_date>"}
#             ]
#         }

#         response = requests.post('https://api.openai.com/v1/chat/completions', headers=headers, json=data)
#         query_response = response.json()
#         print(query_response)

#         parsed_response = query_response['choices'][0]['message']['content'].strip().split('\n')
#         origin_city = parsed_response[0].split(":")[1].strip()
#         destination_city = parsed_response[1].split(":")[1].strip()
#         departure_date = parsed_response[2].split(":")[1].strip()

#         origin_iata = get_iata_code(origin_city)
#         destination_iata = get_iata_code(destination_city)

#         logging.debug(f"Parsed values: Origin City: {origin_city} (IATA: {origin_iata}), "
#                       f"Destination City: {destination_city} (IATA: {destination_iata}), "
#                       f"Departure Date: {departure_date}")

#         if origin_iata is None or destination_iata is None or not departure_date:
#             return jsonify({"error": "Failed to fetch IATA codes or departure date is invalid."}), 400
        
#         # Sending data to search_flights function and include audio data in the response

#         return search_flights(origin_iata, destination_iata, departure_date)

#     return render_template('index.html')

# def search_flights(origin, destination, date):
#     logging.info('Received request to search flights')
#     logging.debug(f'Searching for flights: Origin: {origin}, Destination: {destination}, Date: {date}')

#     if not origin or not destination or not date:
#         logging.error(f"Invalid parameters provided. Origin: {origin}, Destination: {destination}, Date: {date}")
#         return jsonify({"error": "Invalid parameters provided."}), 400

#     today = datetime.now().date()
#     departure_date = datetime.strptime(date, "%Y-%m-%d").date()
#     logging.debug(f"Today: {today}, Departure Date: {departure_date}")

#     if departure_date < today:
#         logging.error(f"Invalid departure date: {date}. Date is in the past.")
#         return jsonify({"error": "Invalid departure date. Date must be today or in the future."}), 400

#     logging.info(f"Searching for flights from {origin} to {destination} on {date}")

#     try:
#         response = amadeus.shopping.flight_offers_search.get(
#             originLocationCode=origin,
#             destinationLocationCode=destination,
#             departureDate=date,
#             adults=1
#         )

#         if response.status_code == 200:
#             flights = response.data
#             if not flights:  # check if flights list is empty
#                 audio_text = "-Oh Sorry, there are no flight options available -umm for your specified date."
#                 audio = generate(
#                     text=audio_text,
#                     voice=Voice(
#                         voice_id='21m00Tcm4TlvDq8ikWAM',
#                         settings=VoiceSettings(stability=0.5, similarity_boost=0.5, style=0.2, use_speaker_boost=True)
#                     )
#                 )
#                 audio_base64 = base64.b64encode(audio).decode('utf-8')
#                 return jsonify({"audio": audio_base64, "audio_text": audio_text})
#             else:
#                 first_flight = flights[0]  # get first flight from the list
#                 price = first_flight['price']['total']
#                 departure = first_flight['itineraries'][0]['segments'][0]['departure']['iataCode']
#                 arrival = first_flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']
#                 departure_time = first_flight['itineraries'][0]['segments'][0]['departure']['at']
#                 arrival_time = first_flight['itineraries'][0]['segments'][-1]['arrival']['at']
#                 audio_text = f"-umm Here is a flight option:\nSo, the Flight is from {departure} to {arrival} -umm on {departure_time} to {arrival_time} time for price {price}.\n"
#                 audio = generate(
#                     text=audio_text,
#                     voice=Voice(
#                         voice_id='21m00Tcm4TlvDq8ikWAM',
#                         settings=VoiceSettings(stability=0.5, similarity_boost=0.5, style=0.2, use_speaker_boost=True)
#                     )
#                 )
#                 audio_base64 = base64.b64encode(audio).decode('utf-8')
#                 return jsonify({"flights": [first_flight], "audio": audio_base64})

#         else:
#             error_message = response.text  # change here
#             logging.error(error_message)
#             return jsonify({"error": error_message}), response.status_code

#     except ResponseError as error:
#         error_message = error.response.body
#         logging.error(error_message)
#         return jsonify({"error": error_message}), 500

#     except Exception as e:
#         logging.error(f"Exception occurred: {str(e)}")
#         error_message = str(e)
#         logging.error(error_message)
#         return jsonify({"error": error_message}), 500


# if __name__ == '__main__':
#     port = int(os.environ.get("PORT", 5000))
#     app.run(host="0.0.0.0", port=port, debug=True)

# app.py

from flask import Flask, render_template, request, jsonify, session
from flask_session import Session
import os
import openai
import speech_recognition as sr
import elevenlabs
from elevenlabs import Voice, VoiceSettings
from elevenlabs import set_api_key, generate
from amadeus import Client, ResponseError
from urllib.parse import urlparse
from datetime import datetime
import redis
import base64
import logging
import requests





# Set your Eleven Labs API key
set_api_key("764503f28a040d6f6b2450eb6310bf97")
openai.api_key = os.getenv("OPENAI_API_KEY")

BASE_URL = "https://test.api.amadeus.com/v1/security/oauth2/token"
# Amadeus API configuration
amadeus = Client(
    client_id='PNYuOqaIHL2ejettffphI2mhicO20aEa',
    client_secret='FaDIs7LgLd4KV4hv'
)

app = Flask(__name__)

# Parse the Redis URL from the environment variable

app.config['SECRET_KEY'] = '\x07\x8a\xf7\x93z\x04\xc2\xd7\xbd\xbe\x80\xcc\x05f\x80\xb7\x9d\x08\xf0\x1cY\xbd\xe5D'

# Use REDIS_TLS_URL for a TLS/SSL connection to Redis
redis_tls_url = os.environ.get('REDIS_TLS_URL')
if redis_tls_url:
    redis_url = urlparse(redis_tls_url)
    app.config['SESSION_REDIS'] = redis.Redis(
        host=redis_url.hostname,
        port=redis_url.port,
        password=redis_url.password,
        ssl=True,
        ssl_cert_reqs=None
    )
else:
    # Fallback to non-TLS Redis URL if REDIS_TLS_URL is not available
    redis_url = urlparse(os.environ.get('REDIS_URL', 'redis://localhost:6379'))
    app.config['SESSION_REDIS'] = redis.from_url(redis_url.geturl())

app.config['SESSION_COOKIE_NAME'] = 'my_session_cookie_name'
app.config['SESSION_TYPE'] = 'redis'
app.config['SESSION_PERMANENT'] = False
app.config['SESSION_USE_SIGNER'] = True

Session(app)
# Global state to manage conversation stages
conversation_state = {'stage': 0, 'data': {}}

@app.route('/', methods=['GET'])
def home():
    session.clear()  # Clearing any existing session at the start of a new interaction
    # Serve the initial page
    return render_template('index.html')

@app.route('/generate_audio', methods=['POST'])
def generate_audio():
    data = request.get_json()
    prompt = data['gpt_response']  # The prompt text to generate audio for

    audio_base64 = generate_audio_response(prompt)
    return jsonify({'audio': audio_base64})


@app.route('/conversation', methods=['POST'])
def conversation():
    app.logger.debug("Starting conversation endpoint.")
    
    # Ensure that session['conversation_state'] exists
    if 'conversation_state' not in session:
        session['conversation_state'] = {'stage': 0, 'data': {}}
    
    # Retrieve the current conversation state from the session
    conversation_state = session['conversation_state']

    # Get JSON data from the request
    data = request.get_json()
    if not data or 'transcript' not in data:
        app.logger.error("No transcript provided in request.")
        return jsonify({'error': 'No transcript provided'}), 400

    transcript = data['transcript']
    app.logger.debug(f"Received transcript: {transcript}")

    app.logger.debug(f"Current conversation state before update: {conversation_state}")
    
    # Proceed based on the conversation stage
    if conversation_state['stage'] == 0:
        # First stage: capture user's intent
        conversation_state['data']['intent'] = transcript
        prompt = "Umm, okay. Can you tell me your destination city?"
        conversation_state['stage'] += 1
    elif conversation_state['stage'] == 1:
        # Capture destination city
        conversation_state['data']['destination'] = transcript
        destination_iata = get_iata_code(transcript)
        if destination_iata:
            conversation_state['data']['destination_iata'] = destination_iata
            prompt = "Got it. And where will you be departing from?"
        else:
            prompt = "I'm sorry, I couldn't find the airport code for that city. Could you please provide another nearby city?"
        conversation_state['stage'] += 1
    elif conversation_state['stage'] == 2:
        # Capture origin city
        conversation_state['data']['origin'] = transcript
        origin_iata = get_iata_code(transcript)
        if origin_iata:
            conversation_state['data']['origin_iata'] = origin_iata
            prompt = "Alright, and on what date will you be traveling?"
        else:
            prompt = "I'm sorry, I couldn't find the airport code for that city. Could you please provide another nearby city?"
        conversation_state['stage'] += 1
    elif conversation_state['stage'] == 3:
        # Capture travel date
        gpt_processed_date = process_date_with_gpt(transcript)
        conversation_state['data']['travel_date'] = gpt_processed_date

        # Play a message while fetching flight details
        thank_you_audio = generate_audio_response("Thank you. Let me fetch the details for you. Please Wait...")
        # Send the thank you response immediately
        jsonify({'audio': thank_you_audio})

        # Now proceed to fetch flight details
        if 'origin_iata' in conversation_state['data'] and 'destination_iata' in conversation_state['data']:
            flights_result, status_code = search_flights(
                origin=conversation_state['data']['origin_iata'],
                destination=conversation_state['data']['destination_iata'],
                date=conversation_state['data']['travel_date']
            )
            if status_code == 200:
                first_flight = flights_result[0]
                # Extract flight details
                price = first_flight['price']['total']
                departure = first_flight['itineraries'][0]['segments'][0]['departure']['iataCode']
                arrival = first_flight['itineraries'][0]['segments'][-1]['arrival']['iataCode']
                departure_time = first_flight['itineraries'][0]['segments'][0]['departure']['at']
                arrival_time = first_flight['itineraries'][0]['segments'][-1]['arrival']['at']

            # Construct your audio_text with flight information
                prompt = f"Here is a flight option: The Flight is from {departure} to {arrival}, departing on {departure_time} and arriving at {arrival_time}, for a price of {price}."
            elif status_code == 204:
                prompt = "I'm sorry, there are no flight options available for your specified date."
            else:
                prompt = ""
        else:
            prompt = "I'm sorry, we don't have enough information to search for flights. Please start over."

        # Generate the audio response for the flight information
        audio_response = generate_audio_response(prompt)
        # # Reset the conversation state for the next interaction
        # conversation_state = {'stage': 0, 'data': {}}
        
    else:
        # Handle unrecognized stage
        prompt = "I'm not sure what you're asking. Let's start over."
        conversation_state = {'stage': 0, 'data': {}}

    app.logger.debug(f"Current conversation state after update: {conversation_state}")

    # Save the updated state back into the session
    app.logger.debug(f"Updating session with conversation_state: {conversation_state}")

    session['conversation_state'] = conversation_state

    app.logger.debug(f"Session data after update: {session['conversation_state']}")


    # Generate the audio response
    audio_response = generate_audio_response(prompt)
    return jsonify({'audio': audio_response})

def get_iata_code(city_name):
    """Function to get IATA code for a given city name using the provided API."""
    city_name = city_name.strip()  # Add this line to strip whitespace from the city name
    api_url = f'https://api.api-ninjas.com/v1/airports?city={city_name}'
    headers = {'X-Api-Key': '7h1sjfSTZYwWhbQ8gqU2lQ==WFlQgav23fzycnHa'}
    response = requests.get(api_url, headers=headers)
    app.logger.debug(f"API response: {response.text}")  # Log the response body
    if response.status_code == 200:
        airports = response.json()
        iata_codes = [airport['iata'] for airport in airports if airport['iata']]
        return iata_codes[0] if iata_codes else None
    else:
        logging.error(f"Failed to fetch IATA code for city: {city_name}. Status code: {response.status_code}")
        return None

def process_date_with_gpt(date_input):
    current_year = datetime.now().year
    prompt = f"Given the date '{date_input}', convert it to the format 'year-month-day'. "\
             f"If the year isn't specified, assume the year is {current_year}. "\
             f"If the date is in the past, consider the year as {current_year + 1}. "\
             f"For dates like 'tomorrow' or 'in 2 days', use the date from today's context. "\
             "Just return the converted date in the format 'YYYY-MM-DD'. Don't include anything else or any text please."

    response = openai.ChatCompletion.create(
        model="gpt-4-1106-preview",  # Replace with your desired chat model
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ]
    )

    # Access the content of the bot's message from the response
    if response and 'choices' in response and len(response['choices']) > 0:
        # The bot's message is contained within the 'message' field of the response
        bot_message = response['choices'][0]['message']
        if bot_message:
            # Assuming the bot's message is a dict with a 'content' field
            return bot_message['content'].strip()

    return None

# Function to search flights (should be defined outside any routes)
def search_flights(origin, destination, date):
    logging.info('Received request to search flights')
    logging.debug(f'Searching for flights: Origin: {origin}, Destination: {destination}, Date: {date}')

    if not origin or not destination or not date:
        logging.error(f"Invalid parameters provided. Origin: {origin}, Destination: {destination}, Date: {date}")
        return {"error": "Invalid parameters provided."}, 400

    today = datetime.now().date()
    departure_date = datetime.strptime(date, "%Y-%m-%d").date()
    logging.debug(f"Today: {today}, Departure Date: {departure_date}")

    if departure_date < today:
        logging.error(f"Invalid departure date: {date}. Date is in the past.")
        return {"error": "Invalid departure date. Date must be today or in the future."}, 400

    logging.info(f"Searching for flights from {origin} to {destination} on {date}")

    try:
        response = amadeus.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=1
        )

        if response.status_code == 200:
            flights = response.data
            if not flights:  # check if flights list is empty
                return {"error": "No flight options available for your specified date."}, 204
            else:
                # Choose how you want to handle and return the flight data
                return flights, 200
        else:
            error_message = response.result
            logging.error(error_message)
            return {"error": error_message}, response.status_code

    except ResponseError as error:
        error_message = error.response.body
        logging.error(error_message)
        return {"error": error_message}, 500

    except Exception as e:
        logging.error(f"Exception occurred: {str(e)}")
        error_message = str(e)
        logging.error(error_message)
        return jsonify({'error': str(e)}), 500



def transcribe_audio(audio):
    r = sr.Recognizer()
    with sr.AudioFile(audio) as source:
        app.logger.info('Recording audio for transcription')
        audio_data = r.record(source)
        try:
            app.logger.info('Starting transcription using Google Speech Recognition')
            transcript = r.recognize_google(audio_data)
            app.logger.info(f'Transcription result: {transcript}')
        except sr.UnknownValueError:
            app.logger.error('Google Speech Recognition could not understand audio')
            transcript = ""
        except sr.RequestError as e:
            app.logger.error(f'Could not request results from Google Speech Recognition service; {e}')
            transcript = ""
    return transcript


def generate_enhanced_text(transcript):
    # Enhance or process the transcribed text
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=transcript,
        max_tokens=100
    )
    return response.choices[0].text.strip()

def generate_audio_response(text):
    # Generates an audio response using ElevenLabs API
    try:
        audio = generate(
            text=text,
            voice=Voice(
                voice_id='21m00Tcm4TlvDq8ikWAM',
                settings=VoiceSettings(stability=0.5, similarity_boost=0.5, style=0.2, use_speaker_boost=True)
            )
        )
        audio_base64 = base64.b64encode(audio).decode('utf-8')
        return audio_base64
    except elevenlabs.api.error.APIError as e:
        app.logger.error(f'Error generating audio: {e}')
        return jsonify({'error': 'An error occurred while generating audio. Please try again later.'}), 429

if __name__ == '__main__':
    logging.basicConfig(level=logging.DEBUG)
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)