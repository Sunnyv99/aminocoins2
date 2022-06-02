parameters = {
    "community-link": "http://aminoapps.com/c/" 
}

import os
from base64 import b64encode
from hmac import new
from hashlib import sha1
import time
#from keep_alive import keep_alive
import json
import random
from box import tzFilter
try:
    import requests
    from flask import Flask
    from json_minify import json_minify
except:
    os.system("pip3 install requests flask json_minify")
finally:
    import requests
    from flask import Flask
    from json_minify import json_minify
os.system("clear")
print(f"{os.getcwd()}\n")
session = requests.Session()

class Client:
    def __init__(self):
        self.api = "https://service.narvii.com/api/v1"
        self.device_Id = self.generate_device_Id()
        self.headers = {"NDCDEVICEID": self.device_Id, "SMDEVICEID": "b89d9a00-f78e-46a3-bd54-6507d68b343c", "Accept-Language": "en-EN", "Content-Type": "application/json; charset=utf-8", "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 5.1.1; SM-G973N Build/beyond1qlteue-user 5; com.narvii.amino.master/3.4.33562)", "Host": "service.narvii.com", "Accept-Encoding": "gzip", "Connection": "keep_alive"}
        self.sid, self.auid = None, None

    def generate_signature_message(self, data):
        signature_message = b64encode(bytes.fromhex("42") + new(bytes.fromhex("F8E7A61AC3F725941E3AC7CAE2D688BE97F30B93"),data.encode("utf-8"), sha1).digest()).decode("utf-8")
        self.headers["NDC-MSG-SIG"]=signature_message
        return signature_message

    def generate_device_Id(self):
        identifier = os.urandom(20)
        mac = new(bytes.fromhex("02B258C63559D8804321C5D5065AF320358D366F"), bytes.fromhex("42") + identifier, sha1)
        return f"42{identifier.hex()}{mac.hexdigest()}".upper()

    def login(self, email: str, password: str):
        data = json.dumps({"email": email, "secret": f"0 {password}", "deviceID": self.device_Id, "clientType": 100, "action": "normal", "timestamp": (int(time.time() * 1000))})
        self.headers["ndc-msg-sig"] = self.generate_signature_message(data = data)
        request = session.post(f"{self.api}/g/s/auth/login", data = data, headers = self.headers)
        try: self.sid, self.auid = request.json()["sid"], request.json()["auid"]
        except: pass
        return request.json()

    def send_active_object(self, comId: int, start_time: int = None, end_time: int = None, timers: list = None, tz: int = -time.timezone // 1000):
        data = {"userActiveTimeChunkList": [{"start": start_time, "end": end_time}], "timestamp": int(time.time() * 1000), "optInAdsFlags": 2147483647, "timezone": tz}
        if timers: data["userActiveTimeChunkList"] = timers
        data = json_minify(json.dumps(data))
        self.headers["ndc-msg-sig"] = self.generate_signature_message(data = data)
        request = session.post(f"{self.api}/x{comId}/s/community/stats/user-active-time?sid={self.sid}", data = data, headers = self.headers)
        return request.json()

    def watch_ad(self): return session.post(f"{self.api}/g/s/wallet/ads/video/start?sid={self.sid}", headers = self.headers).json()

    def get_from_link(self, link: str): return session.get(f"{self.api}/g/s/link-resolution?q={link}", headers = self.headers).json()

    def lottery(self, comId, time_zone: str = -int(time.timezone) // 1000):
        data = json.dumps({"timezone": time_zone, "timestamp": int(time.time() * 1000)})
        self.headers["ndc-msg-sig"] = self.generate_signature_message(data = data)
        request = session.post(f"{self.api}/x{comId}/s/check-in/lottery?sid={self.sid}", data = data, headers = self.headers)
        return request.json()

    def join_community(self, comId: int, inviteId: str = None):
        data = {"timestamp": int(time.time() * 1000)}
        if inviteId: data["invitationId"] = inviteId
        data = json.dumps(data)
        self.headers["ndc-msg-sig"] = self.generate_signature_message(data=data)
        request = session.post(f"{self.api}/x{comId}/s/community/join?sid={self.sid}", data = data, headers = self.headers)
        return request.json()

class App:
    def __init__(self):
        self.client = Client()
        extensions = self.client.get_from_link(parameters["community-link"])["linkInfoV2"]["extensions"]
        self.comId = extensions["community"]["ndcId"]
        try: self.invitationId = extensions["invitationId"]
        except: self.invitationId = None 
    def tzc(self): return tzFilter()
    def generation(self, email: str, password: str):
        try:           
            print(f"\n[\033[1;31mcoins-generator\033[0m][\033[1;34mlogin\033[0m][{email}]: {self.client.login(email = email, password = password)['api:message']}.")          
            print(f"[\033[1;31mcoins-generator\033[0m][\033[1;36mjoin-community\033[0m]: {self.client.join_community(comId = self.comId, inviteId = self.invitationId)['api:message']}.")
            print(f"[\033[1;31mcoins-generator\033[0m][\033[1;32mlottery\033[0m]: {self.client.lottery(comId = self.comId, time_zone = tzFilter())['api:message']}")
            print(f"[\033[1;31mcoins-generator\033[0m][\033[1;33mwatch-ad\033[0m]: {self.client.watch_ad()['api:message']}.")
            for i2 in range(24):
                time.sleep(12)
                print(f"[\033[1;31mcoins-generator\033[0m][\033[1;35mmain-proccess\033[0m][{email}]: {self.client.send_active_object(comId = self.comId, timers = [{'start': int(time.time()), 'end': int(time.time()) + 300} for _ in range(50)], tz = tzFilter())['api:message']}.")
            print(f"[\033[1;31mcoins-generator\033[0m][\033[1;25;32mend\033[0m][{email}]: Finished.")
        except Exception as error: print(f"[\033[1;31mC01?-G3?3R4?0R\033[0m]][\033[1;31merror\033[0m]]: {error}")

    def run(self):
        print("COIN GENERATOR ")
        with open("accounts.json", "r") as emails:
            emails = json.load(emails)
            print(f"{len(emails)} Accounts loaded")
            for account in emails:
                self.client.device_Id = account["device"]
                self.client.headers["NDCDEVICEID"] = self.client.device_Id
                self.generation(email = account["email"], password = account["password"])

if __name__ == "__main__":
    #keep_alive()
    while True:
      App().run()