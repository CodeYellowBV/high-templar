from wiremock.server import WireMockServer
from wiremock.constants import Config
from wiremock.client import Mapping, Mappings
from wiremock.resources.mappings import MappingRequest, HttpMethods, MappingResponse
import json



def set_bootstrap_response(data):
    Config.base_url = 'http://127.0.0.1:8080/__admin'

    if data is None:
        mapping = Mapping(
            priority=100,
            request=MappingRequest(
                method=HttpMethods.GET,
                url='/api/bootstrap/'
            ),
            response=MappingResponse(
                status=403,
            ),
            persistent=False,
        )
    else:
        mapping = Mapping(
            priority=100,
            request=MappingRequest(
                method=HttpMethods.GET,
                url='/api/bootstrap/'
            ),
            response=MappingResponse(
                status=200,
                body=json.dumps(data)
            ),
            persistent=False,
        )
    Mappings.create_mapping(mapping=mapping)
