import requests

class SmsGateway():
    def post(request):
        url = "http://dma.com.bd:8888/send/sms"
        
        r = requests.post(url, request)
        # print(r)
        if (r.status_code == 200):
            print("Successfully sent to user!!")
        else:
            print("Unsuccessful sending to user!!")