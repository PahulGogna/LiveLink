import requests
import time
import Kafka
import threading

codes = {
    "100": "Continue",
    "101": "Switching Protocols",
    "102": "Processing",
    "103": "Early Hints",
    "200": "OK",
    "201": "Created",
    "202": "Accepted",
    "203": "Non-Authoritative Information",
    "204": "No Content",
    "205": "Reset Content",
    "206": "Partial Content",
    "207": "Multi-Status",
    "208": "Already Reported",
    "226": "IM Used",
    "300": "Multiple Choices",
    "301": "Moved Permanently",
    "302": "Found",
    "303": "See Other",
    "304": "Not Modified",
    "305": "Use Proxy",
    "306": "(Unused)",
    "307": "Temporary Redirect",
    "308": "Permanent Redirect",
    "400": "Bad Request",
    "401": "Unauthorized",
    "402": "Payment Required",
    "403": "Forbidden",
    "404": "Not Found",
    "405": "Method Not Allowed",
    "406": "Not Acceptable",
    "407": "Proxy Authentication Required",
    "408": "Request Timeout",
    "409": "Conflict",
    "410": "Gone",
    "411": "Length Required",
    "412": "Precondition Failed",
    "413": "Payload Too Large",
    "414": "URI Too Long",
    "415": "Unsupported Media Type",
    "416": "Range Not Satisfiable",
    "417": "Expectation Failed",
    "418": "I'm a teapot",
    "421": "Misdirected Request",
    "422": "Unprocessable Entity",
    "423": "Locked",
    "424": "Failed Dependency",
    "425": "Too Early",
    "426": "Upgrade Required",
    "428": "Precondition Required",
    "429": "Too Many Requests",
    "431": "Request Header Fields Too Large",
    "451": "Unavailable For Legal Reasons",
    "500": "Internal Server Error",
    "501": "Not Implemented",
    "502": "Bad Gateway",
    "503": "Service Unavailable",
    "504": "Gateway Timeout",
    "505": "HTTP Version Not Supported",
    "506": "Variant Also Negotiates",
    "507": "Insufficient Storage",
    "508": "Loop Detected",
    "510": "Not Extended",
    "511": "Network Authentication Required"
}


class Checker:
    def __init__(self) -> None:
        
        self.processes = {}
        
    def _getStatusCode(self,url:str,event:threading.Event, TimeInterval:int = 30) -> None:
        '''
        This is the status code monitoring process which runs in an infinite loop until stopped.
        '''
        print('starting...')
        producer = Kafka.Producer(topic='StatusCodes',key=url)
        dt = 0
        LoggingInterval = TimeInterval*5
        try:
            data = requests.head(url, allow_redirects=True).status_code

            if data >= 400 and data <= 599:
                    producer.produce({'url':url, 'status_code': data, 'exception':False, 'working':False, 'stopped': False})
                    dt = 0
                    time.sleep(TimeInterval)
            else:    
                producer.produce({'url':url, 'status_code': data, 'exception':False, 'working':True, 'stopped': False})
        except Exception as error:
            return error

        while not event.is_set():
            try:
                data = requests.head(url, allow_redirects=True).status_code
                print(codes[str(data)])

                if data >= 400 and data <= 599:
                    producer.produce({'url':url, 'status_code': data, 'exception':False, 'working':False, 'stopped': False})
                    dt = 0
                    time.sleep(TimeInterval)
                    continue

                if dt >= LoggingInterval:
                    producer.produce({'url':url, 'status_code': data, 'exception':False, 'working':True, 'stopped': False})
                    dt = 0
                

            except Exception as error:
                print(error)
                print('stopping for an extra of 10 seconds...')
                producer.produce({'url':url, 'status_code':None, 'exception':True, 'error':error, 'working':False, 'stopped': False})
                dt = 0
                time.sleep(10)
                
            time.sleep(TimeInterval)
            dt += TimeInterval

        producer.produce(data={'url':url, 'status_code': data, 'exception':False, 'working':True, 'stopped': True})

        return

    def startAnother(self, url:str, timeInterval=30):
        '''
        This is to start a new status code monitoring process which runs in an infinite loop.
        '''
        if url not in self.processes:
            event = threading.Event()
            self.processes[url] = {
                'thread':threading.Thread(target=self._getStatusCode,
                                          args=(url, event,timeInterval)).start(),
                'event':event
                }
    
    def stopChecking(self,url):
        if url in self.processes:
            threadData = self.processes[url]
            threadData['event'].set()
            print(threadData, 'was stopped.')
            del self.processes[url]
            print(self.processes)

        elif url == 'ALL':
            for p in self.processes:
                process = self.processes[p]
                process['event'].set()
                print(process, 'was stopped.')
                del process
            return
            


c1 = Checker()
c1.startAnother("https://spotify-playlists-lemon.vercel.app", 2)
time.sleep(5)
c1.startAnother("https://www.google.com/", 2)


input('enter to stop')

c1.stopChecking('ALL')