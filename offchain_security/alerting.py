import requests
from config import ALERT_WEBHOOK

def send_alert(msg):
    requests.post(ALERT_WEBHOOK, json={"content": msg})
