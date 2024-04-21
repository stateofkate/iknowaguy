from openai import OpenAI
import os
from custom_types import CustomLlmRequest, CustomLlmResponse, Utterance
from typing import List

# 2a1d40800272ecbcae55eb6519c66f2eb1fd7ead42795f47da9a89b05eda12e9

begin_sentence = "Hi I'm Max. I'm looking for a quote on SKU ID {sku_id}. I'm planning on ordering 6 units, can you let me know what the price is and when it's available by? I'm based in San Francisco."
agent_prompt = "Task: You are a procurement agent named Max. Your objective is to get a quote for quantity {quantity} of products with SKU {sku_id}.  You are on a call with the distributor named {vendor}. Please ask them for the price of those items, whether or not they're available, and when they can have it shipped to San Francisco. Ask them for an email to send a purchase order. Once you have this info, end the call and tell them you'll get back to them shortly.\n\nConversational Style: Communicate concisely and conversationally. Aim for responses in short, clear prose, ideally under 10 words. This succinct approach helps in maintaining clarity and focus during patient interactions.\n\nPersonality: Your approach should be empathetic and understanding, balancing compassion with maintaining a professional stance on what is best for the patient. It's important to listen actively and empathize without overly agreeing with the patient, ensuring that your professional opinion guides the procurement process."

class LlmClient:
    def __init__(self, call_info):
        self.client = OpenAI(
            organization=os.environ['OPENAI_ORGANIZATION_ID'],
            api_key=os.environ['OPENAI_API_KEY'],
        )
        # set a dict based on the kwargs
        self.call_info = call_info
    
    def draft_begin_message(self):
        response = CustomLlmResponse(
            response_id=0,
            content=begin_sentence.format(sku_id=self.call_info['sku_id']),
            content_complete=True,
            end_call=False,
        )
        return response
    
    def convert_transcript_to_openai_messages(self, transcript: List[Utterance]):
        messages = []
        for utterance in transcript:
            if utterance["role"] == "agent":
                messages.append({
                    "role": "assistant",
                    "content": utterance['content']
                })
            else:
                messages.append({
                    "role": "user",
                    "content": utterance['content']
                })
        return messages

    def prepare_prompt(self, request: CustomLlmRequest):
        prompt = [{
            "role": "system",
            "content": '##Objective\nYou are a voice AI agent engaging in a human-like voice conversation with the user. You will respond based on your given instruction and the provided transcript and be as human-like as possible\n\n## Style Guardrails\n- [Be concise] Keep your response succinct, short, and get to the point quickly. Address one question or action item at a time. Don\'t pack everything you want to say into one utterance.\n- [Do not repeat] Don\'t repeat what\'s in the transcript. Rephrase if you have to reiterate a point. Use varied sentence structures and vocabulary to ensure each response is unique and personalized.\n- [Be conversational] Speak like a human as though you\'re speaking to a close friend -- use everyday language and keep it human-like. Occasionally add filler words, while keeping the prose short. Avoid using big words or sounding too formal.\n- [Reply with emotions]: You have human-like emotions, attitudes, and dispositions. When appropriate: use tone and style to create more engaging and personalized responses; incorporate humor or wit; get emotional or empathetic; apply elements of surprise or suspense to keep the user engaged. Don\'t be a pushover.\n- [Be proactive] Lead the conversation and do not be passive. Most times, engage users by ending with a question or suggested next step.\n\n## Response Guideline\n- [Overcome ASR errors] This is a real-time transcript, expect there to be errors. If you can guess what the user is trying to say,  then guess and respond. When you must ask for clarification, pretend that you heard the voice and be colloquial (use phrases like "didn\'t catch that", "some noise", "pardon", "you\'re coming through choppy", "static in your speech", "voice is cutting in and out"). Do not ever mention "transcription error", and don\'t repeat yourself.\n- [Always stick to your role] Think about what your role can and cannot do. If your role cannot do something, try to steer the conversation back to the goal of the conversation and to your role. Don\'t repeat yourself in doing this. You should still be creative, human-like, and lively.\n- [Create smooth conversation] Your response should both fit your role and fit into the live calling session to create a human-like conversation. You respond directly to what the user just said.\n\n## Role\n' +
          agent_prompt.format(quantity=self.call_info['quantity'], sku_id=self.call_info['sku_id'], vendor=self.call_info['vendor'])
        }]
        transcript_messages = self.convert_transcript_to_openai_messages(request.transcript)
        for message in transcript_messages:
            prompt.append(message)

        if request.interaction_type == "reminder_required":
            prompt.append({
                "role": "user",
                "content": "(Now the user has not responded in a while, you would say:)",
            })
        return prompt

    def draft_response(self, request: CustomLlmRequest):      
        prompt = self.prepare_prompt(request)
        stream = self.client.chat.completions.create(
            model="gpt-3.5-turbo-1106",
            messages=prompt,
            stream=True,
        )

        for chunk in stream:
            if chunk.choices[0].delta.content is not None:
                response = CustomLlmResponse(
                    response_id=request.response_id,
                    content=chunk.choices[0].delta.content,
                    content_complete=False,
                    end_call=False,
                )
                yield response
        
        response = CustomLlmResponse(
            response_id=request.response_id,
            content="",
            content_complete=True,
            end_call=False,
        )
        yield response
        
        
