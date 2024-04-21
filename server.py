import json
import os
import asyncio
from dotenv import load_dotenv
from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse, PlainTextResponse
from custom_types import CustomLlmRequest, CustomLlmResponse
from concurrent.futures import TimeoutError as ConnectionTimeoutError
from twilio_server import TwilioClient
from twilio.twiml.voice_response import VoiceResponse
from retell import Retell
from retell.resources.call import RegisterCallResponse

from llm_with_func_calling import LlmClient
# from llm import LlmClient

import csv
# from llm_with_func_calling import LlmClient

load_dotenv(override=True)
app = FastAPI()
retell = Retell(api_key=os.environ['RETELL_API_KEY'])
agent_id = os.environ['RETELL_AGENT_ID']

# Twilio functions
twilio_client = TwilioClient()
# twilio_client.create_phone_number(213, agent_id)
# twilio_client.delete_phone_number("+12133548310")
# twilio_client.register_phone_agent("+12135681465", agent_id)
# twilio_client.create_phone_call("+12137994675", "+19496892624", agent_id)

@app.get("/make-call/")
def make_call(request: Request):
    # read data.csv into rows
    rows = []
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
    rows = rows[1:]

    call_info = {
        'sku_id': rows[0][1],
        'vendor': rows[0][3],
        'price': rows[0][4],
        'phone': rows[0][5],
        'ship_by': rows[0][6],
    }
    
    twilio_client.create_phone_call("+12137994675", "+"+rows[0][5], agent_id)

# Only used for twilio phone call situations
@app.post("/twilio-voice-webhook/{agent_id_path}")
async def handle_twilio_voice_webhook(request: Request, agent_id_path: str):
    try:
        # Check if it is machine
        post_data = await request.form()
        if 'AnsweredBy' in post_data and post_data['AnsweredBy'] == "machine_start":
            twilio_client.end_call(post_data['CallSid'])
            return PlainTextResponse("")
        elif 'AnsweredBy' in post_data:
            return PlainTextResponse("")

        call_response: RegisterCallResponse = retell.call.register(
            agent_id=agent_id_path,
            audio_websocket_protocol="twilio",
            audio_encoding="mulaw",
            sample_rate=8000, # Sample rate has to be 8000 for Twilio
            from_number=post_data['From'],
            to_number=post_data['To'],
            metadata={"twilio_call_sid": post_data['CallSid'],}
        )
        print(f"Call response: {call_response}")

        response = VoiceResponse()
        start = response.connect()
        start.stream(url=f"wss://api.retellai.com/audio-websocket/{call_response.call_id}")
        return PlainTextResponse(str(response), media_type='text/xml')
    except Exception as err:
        print(f"Error in twilio voice webhook: {err}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

# Only used for web frontend to register call so that frontend don't need api key
@app.post("/register-call-on-your-server")
async def handle_register_call(request: Request):
    try:
        post_data = await request.json()
        call_response = retell.call.register(
            agent_id=post_data["agent_id"],
            audio_websocket_protocol="web",
            audio_encoding="s16le",
            sample_rate=post_data["sample_rate"], # Sample rate has to be 8000 for Twilio
        )
        print(f"Call response: {call_response}")
    except Exception as err:
        print(f"Error in register call: {err}")
        return JSONResponse(status_code=500, content={"message": "Internal Server Error"})

    

# Custom LLM Websocket handler, receive audio transcription and send back text response
@app.websocket("/llm-websocket/{call_id}")
async def websocket_handler(websocket: WebSocket, call_id: str):
    await websocket.accept()
    
    rows = []
    with open('data.csv', 'r') as file:
        reader = csv.reader(file)
        for row in reader:
            rows.append(row)
    rows = rows[1:]
    
    call_info = {
        'sku_id': rows[0][1],
        'vendor': rows[0][3],
        'price': rows[0][4],
        'phone': rows[0][5],
        'ship_by': rows[0][6],
        'quantity': 15,
    }
    
    llm_client = LlmClient(call_info=call_info)
    
    # Send optional config to Retell server
    config = CustomLlmResponse(
        response_type="config",
        config= {
            "auto_reconnect": True,
            "call_details": True,
        },
        response_id=1
    )
    await websocket.send_text(json.dumps(config.__dict__))
    
    # Send first message to signal ready of server
    response_id = 0
    first_event = llm_client.draft_begin_message()
    await websocket.send_text(json.dumps(first_event.__dict__))

    async def stream_response(request: CustomLlmRequest):
        nonlocal response_id
        for event in llm_client.draft_response(request):
            await websocket.send_text(json.dumps(event.__dict__))
            if request.response_id < response_id:
                return # new response needed, abandon this one
    try:
        while True:
            message = await asyncio.wait_for(websocket.receive_text(), timeout=100*60) # 100 minutes
            request_json = json.loads(message)
            request: CustomLlmRequest = CustomLlmRequest(**request_json)
            print(json.dumps(request.__dict__, indent=4))
            
            # There are 5 types of interaction_type: call_details, pingpong, update_only, response_required, and reminder_required.
            # Not all of them need to be handled, only response_required and reminder_required.
            if request.interaction_type == "call_details":
                continue
            if request.interaction_type == "ping_pong":
                await websocket.send_text(json.dumps({"response_type": "ping_pong", "timestamp": request.timestamp}))
                continue
            if request.interaction_type == "update_only":
                continue
            if request.interaction_type == "response_required" or request.interaction_type == "reminder_required":
                response_id = request.response_id
                asyncio.create_task(stream_response(request))
    except WebSocketDisconnect:
        print(f"LLM WebSocket disconnected for {call_id}")
    except ConnectionTimeoutError as e:
        print("Connection timeout error")
    except Exception as e:
        print(f"Error in LLM WebSocket: {e}")
    finally:
        print(f"LLM WebSocket connection closed for {call_id}")
