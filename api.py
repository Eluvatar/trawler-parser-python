#   Copyright 2013-2015 Eluvatar
#
#   This file is part of Trawler.
#
#   Trawler is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   Trawler is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with Trawler.  If not, see <http://www.gnu.org/licenses/>.

"""
  This module defines a python interface wrapping the trawler client for the
  purposes of accessing the NationStates API. 

  his interface provides a request method which returns takes a dict object 
  defining the API parameters and returns an ElementTree object or throws an 
  exception. If the API returned a 404, it will throw a CTE exception.
  
  api.user_agent MUST be set prior to calling the request method.
"""

import xml.etree.ElementTree as ET
from xml.parsers.expat import ExpatError as EE
from xml.etree.ElementTree import ParseError as PE
import client.trawler as trawler
import logging
import io
from urllib import urlencode
from time import sleep

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def request(query,header=False,log=False,retries=5,backoff=0.0):
    """ requests information from the NS API using trawler
        defaults to using version 5 (the latest when this code was written) """
    if retries<0:
        return None
    if 'v' in query:
        query['v'] = str(query['v'])
    else:
        query['v']='7'
    path = "/cgi-bin/api.cgi"
    if 'q' in query and not isinstance(query['q'],basestring):
        query['q'] = "+".join(query['q'])
    querystr = urlencode(query)
    if log:
        logger.debug("GET %s?%s", path, querystr)
    res = __connection().request('GET',path,querystr,headers=True)
    if log:
        logger.debug("GET %s?%s -> %d", path, querystr, res.result)
    if( res.result == 200 ):
        if 'a' in query and query['a'] == 'sendTG':
            # Why does this have to be plaintext and not XML? :(
            return res.read()
        try:
            xml = ET.parse(res)
            xml.headers = res.info()
            return xml
        except (EE,PE):
            _handle_parse_error(querystr, res)
            raise
    elif( res.result == 404 ):
        if 'nation' in query:
            raise CTE(query['nation'])
        elif 'region' in query:
            raise CTE(query['region'])
        else:
            raise ApiError(res)
    elif( res.result == 0 or (res.result >= 500 and res.result < 600)):
        sleep(backoff)
        backoff = backoff * 2 if backoff > 0 else 1.0
        xml = request(query, header, log, retries-1, backoff)
        if xml is None:
            raise ApiError(res)
    else:
        raise ApiError(res)

class CTE(Exception):
    def __init__(self, value):
        self.value = value
    def __str__(self):
        return repr(self.value)

class ApiError(Exception):
    def __init__(self, value):
        self.value = value
        self.result = value.result
        self.read = value.read
    def __str__(self):
        return ("Api Error %d:"%self.result)+repr(self.value)

def _handle_parse_error(query,res):
    logger.error("api.request of %s failed to parse",query)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("---begin---")
        res.seek(0)
        logger.debug(res.read())
        logger.debug("---end---")
#        for reply in res.replies:
#            print reply
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
