#   Copyright 2013 Eluvatar
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

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

def request(query,log=False):
    """ requests information from the NS API using trawler
        defaults to using version 5 (the latest when this code was written) """
    if 'v' in query:
        query['v'] = str(query['v'])
    else:
        query['v']='5'
    qs = map(lambda k: k+"="+(query[k] if isinstance(query[k],basestring) else "+".join(query[k])), query)
    path = "/cgi-bin/api.cgi"
    querystr = "&".join(qs)
    if log:
        logger.debug("GET %s?%s", path, querystr)
    res = __connection().request('GET',path,querystr)
    if log:
        logger.debug("GET %s?%s -> %d", path, querystr, res.result)
    if( res.result == 200 ):
        try:
            return ET.parse(res)
        except (EE,PE):
            __handle_ee(querystr, res)
            raise
    elif( res.result == 404 ):
        if 'nation' in query:
            raise CTE(query['nation'])
        elif 'region' in query:
            raise CTE(query['region'])
        else:
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

def __handle_ee(query,res):
    logger.error("api.request of %s failed to parse",query)
    if logger.isEnabledFor(logging.DEBUG):
        logger.debug("---begin---")
        res.seek(0)
        logger.debug(res.read())
        logger.debug("---end---")
        for reply in res.replies:
            print reply
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
