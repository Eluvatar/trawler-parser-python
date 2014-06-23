import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError as EE
import client.trawler as trawler
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def api_request(query,log=False):
    """ requests information from the NS API using trawler
        defaults to using version 4 """
    if 'v' in query:
        query['v'] = str(query['v'])
    else:
        query['v']='4'
    qs = map(lambda k: k+"="+(query[k] if isinstance(query[k],basestring) else "+".join(query[k])), query)
    path = "/cgi-bin/api.cgi"
    query = "&".join(qs)
    if log:
        logger.debug("GET %s?%s", path, query)
    res = __connection().request('GET',path,query)
    if log:
        logger.debug("GET %s?%s -> %d", path, query, res.result)
    if( res.result == 200 ):
        try:
            return ET.parse(res)
        except EE:
            __handle_ee(path, res)
            raise
    elif( res.result == 404 ):
        if 'nation' in query:
            raise CTE(query['nation'])
        elif 'region' in query:
            raise CTE(query['region'])
        else:
            raise res
    else:
        raise res

class CTE(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

def __handle_ee(path,res):
    logger.error("api_request of %s failed to parse",path)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("---begin---")
        logger.debug(res.read())
        logger.debug("---end---")
        del res
    else:
        res.read()

def __connection():
    if not __connection.conn:
        if not user_agent:
            raise Exception("User Agent required")
        __connection.conn = trawler.connection(user_agent)
    return __connection.conn
user_agent = None
__connection.conn = None
