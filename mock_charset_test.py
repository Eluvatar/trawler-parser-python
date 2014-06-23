import api,logging
api.user_agent = 'charset test by Eluvatar'
logging.basicConfig()
xml = api.request({'q':'happenings','sinceid':'7999000'},True)
events = xml.find("HAPPENINGS").findall("EVENT")
print filter(lambda x: x.get('id') == "7999047", events)[0].find("TEXT").text
xml = api.request({'q':'factbook','region':'swiss_confederation'},True)
print xml.find("FACTBOOK").text
 
