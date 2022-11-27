import requests
import json

url = "https://iqwhatsapp.airtel.in:443/gateway/airtel-xchange/basic/whatsapp-manager/v1/template/send"

def sendTemplateForYoutube(receiver,mediaId,mediaType,text):
    print("IN the template\n")
    print(text)

    payload = json.dumps({
    "templateId": "64cf2368-93d7-4084-9fac-e2883a787aa3 ",
    "to": receiver,
    "from": "918904587734",
    "mediaAttachment": {
        "type": mediaType,
        "id": mediaId
    },
    "message":{
        "variables": [text]
    },
    "filterBlacklistNumbers": False
    })
    headers = {
    'X-Correlation-Id': 'abcd',
    'X-Date': '{{date}}',
    'Authorization': 'Basic QUlSVEVMX0RJR19MeEk4VFVLOGVLZnRCa3lQdWlmTDoxeipMVTZLTjxrenNMPytiVzM2',
    'Content-Type': 'application/json'
    }
    response = requests.request("POST", url, headers=headers, data=payload)
    print(response.text)