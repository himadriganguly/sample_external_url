import pytest
from prometheus_client import Gauge, CollectorRegistry, generate_latest
from app import ProcessURL

registry =  CollectorRegistry()
urlState = Gauge('test_external_url_up',
                    'External URL state', ['url'],registry=registry)
urlResp = Gauge('test_external_url_response_ms',
                    'External URL response in milliseconds', ['url'], registry=registry)

@pytest.fixture
def create_processurl():
    processUrlObj = ProcessURL(['https://httpstat.us/503'],2,urlState,urlResp)
    processUrlObj.request_loop()
    result = generate_latest(registry).decode('utf8').split('\n')
    return result
