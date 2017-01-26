from ws4py.client.threadedclient import WebSocketClient
import base64, json, ssl, subprocess, threading, time, re, subprocess
from conversation_v1 import ConversationV1
from TextToSpeechV1 import TextToSpeechV1

class SpeakingTrashCan(WebSocketClient):
    def __init__(self):
        ws_url = "wss://stream.watsonplatform.net/speech-to-text/api/v1/recognize"
        
        #Ville
        #username = "b60f87ae-48fd-4204-a33a-bed260f941d6"
        #password = "ujeweaMYGZbJ"
        #JH
        username = "be89b371-e09b-478b-82e8-3d9dd1722039"
        password = "kNhYRV0vJztt"		
        auth_string = "%s:%s" % (username, password)
        base64string = base64.encodestring(auth_string).replace("\n", "")

        self.listening = False

        try:
            WebSocketClient.__init__(self, ws_url,
                headers=[("Authorization", "Basic %s" % base64string)])
            self.connect()
        except: print "Failed to open WebSocket."
			
    def opened(self):
        self.send('{"action": "start", "content-type": "audio/l16;rate=16000"}')
        self.stream_audio_thread = threading.Thread(target=self.stream_audio)
        self.stream_audio_thread.start()

    def received_message(self, message):
        message = json.loads(str(message))
        		
        if "state" in message:
            if message["state"] == "listening":
                self.listening = True
				            
        if "results" in message:
            str_message = message["results"]							
				
            str_message = str(str_message)								
            str_message = re.sub('^(.*: u)', '', str_message)
            str_message = re.sub('(}], u\'final.*)', '', str_message)
		
            print "Message received: " + str_message
            	
            #ville
            #conversation = ConversationV1(username='1f3ca126-9946-49c4-a25c-81cb5e143825',password='BSpYb5CaQigD',version='2016-09-20')
            #JH
            conversation = ConversationV1(username='d0dce5ab-62f8-4cde-98a2-8d9465d638c9',password='JEhNIRrWrrDT',version='2017-01-23')

            #Ville		
            #workspace_id = '96dfa8c9-f0d9-4218-8351-a58cc6695eca'
            #JH
            workspace_id = '7674692e-1485-4f96-8df1-9eed1d3ddb43'
			
            response = conversation.message(workspace_id=workspace_id, message_input={'text': str_message})
	
            response = response["output"]
            response = str(response["text"])
		
            response = re.sub('\[u', '', response)
            response = re.sub('\]', '', response)
						
            print "Response received: " + str(response)

            #Ville			
            #text_to_speech = TextToSpeechV1(username='3ec3ea94-ea45-4569-b9ca-0e6ed058b2ad',password='wofYhGQhvrP2')
            #JH
            text_to_speech = TextToSpeechV1(username='846a7aa5-2094-4e26-bd15-bcb3e22cf38c',password='5jqjRu0LNcRd')
				
            with open('./output.wav','wb') as audio_file: audio_file.write(text_to_speech.synthesize(str(response), accept='audio/wav',voice="en-US_AllisonVoice"))
            audio_file.close()
            subprocess.call(["play", "./output.wav"])
            		
            try:
                stt_client.close()
            finally:
                self.close()
                stt_client = SpeakingTrashCan()
                raw_input()
		
    def stream_audio(self):
        while not self.listening:
            time.sleep(0.1)

        reccmd = ["arecord", "-f", "S16_LE", "-r", "16000", "-t", "raw"]
        p = subprocess.Popen(reccmd, stdout=subprocess.PIPE)

        while self.listening:
            data = p.stdout.read(1024)

            try: self.send(bytearray(data), binary=True)
            except ssl.SSLError: pass

        p.kill()		
		
    def close(self):
        self.listening = False
        self.stream_audio_thread.join()
        WebSocketClient.close(self)
		
try:
    stt_client = SpeakingTrashCan()
    raw_input()
finally:
    stt_client.close()
