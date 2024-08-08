import time

class RateLimiter:
    def __init__(self, bufferTime = 2) -> None:
        self.recent = {}
        self.bufferTime = bufferTime

    def add(self, ip:str):
        currentTime = time.time()
        lastTime = self.recent.get(ip, False)
        if lastTime:
            if currentTime - lastTime > self.bufferTime:
                keys = list(self.recent.keys())
                self.recent = dict((k, self.recent[k]) for k in keys[keys.index(ip) + 1:])
                self.recent[ip] = currentTime
                return True
            else:
                self.recent.pop(ip)
                self.recent[ip] = currentTime
                return False
        else:
            self.recent[ip] = currentTime
            return True
        
rateLimit = RateLimiter()

def checkRateLimit(request):
    client_ip = request.client.host
    print(client_ip)
    return rateLimit.add(client_ip)