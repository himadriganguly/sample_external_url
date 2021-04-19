import concurrent.futures, os, requests
from prometheus_client import Gauge, make_wsgi_app
from wsgiref.simple_server import make_server

urlState = Gauge('sample_external_url_up',
                    'External URL state', ['url'])
urlResp = Gauge('sample_external_url_response_ms',
                    'External URL response in milliseconds', ['url'])

class ProcessURL:
    def __init__(self,urls,timeoutSec,urlState,urlResp):
        self.urls = urls
        self.timeoutSec = timeoutSec
        self.urlState = urlState
        self.urlResp = urlResp

    def __process_request(self,url):
        try:
            r = requests.get(url, timeout=self.timeoutSec)
            respTime = round(r.elapsed.total_seconds()*1000,2)
            return [respTime, r.status_code, url]
        except Exception as err:
            raise Exception(err)

    def request_loop(self):
        try:
            with concurrent.futures.ThreadPoolExecutor() as executor:
                results = [executor.submit(self.__process_request, url) for url in self.urls]

                for f in concurrent.futures.as_completed(results):
                    self.urlResp.labels(f.result()[2]).set(f.result()[0])
                    if f.result()[1] == 200:
                        self.urlState.labels(f.result()[2]).set(1)
                    else:
                        self.urlState.labels(f.result()[2]).set(0)
        except Exception as err:
            raise Exception(err)

def my_app(environ, start_fn):
    try:
        if environ['PATH_INFO'] == '/metrics':
            global processUrlObj
            processUrlObj.request_loop()
            metrics_app = make_wsgi_app()
            return metrics_app(environ, start_fn)

        start_fn('200 OK', [])
        return [b'Praying For Safe And Healthy World!']
    except Exception as err:
        raise Exception(err)

if __name__ == '__main__':
    try:
        urls = os.getenv('URLS').split(',')
        timeoutSec = int(os.getenv('TIMEOUT'))
        processUrlObj = ProcessURL(urls,timeoutSec,urlState,urlResp)

        port = int(os.getenv('PORT') or 8000)
        httpd = make_server('0.0.0.0', port, my_app)
        print("Serving on port {}".format(port))
        httpd.serve_forever()
    except KeyboardInterrupt as err:
        print("Shuting Down App. Good Bye!")
        exit(0)
    except Exception as err:
        print("Error ocurred: ", err)
        exit(1)
