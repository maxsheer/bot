import requests
from yandex_geocoder import Client
from yandex_geocoder.exceptions import NothingFound

token = '1156750871:AAG0ddHtJ7xAL1NtNuxBolXhiKSEMpQZhjg'
y_apikey = '85685983-4ddd-4ba2-a000-58b8c2a39789'
g_apikey = 'AIzaSyCoFHbhr9WsaeCqsmKisicX111Ve8KLeKE'


class Bot:

    def __init__(self, token):
        self.token = token
        self.api_url = "https://api.telegram.org/bot{}/".format(token)

    def send_message(self, chat_id, text):
        params = {'chat_id': chat_id, 'text': text}
        method = 'sendMessage'
        resp = requests.post(self.api_url + method, params)
        return resp


def getYUrl(inp, key):
    url = 'https://geocode-maps.yandex.ru/1.x/?geocode=' + str(inp['longitude']) + ',' + str(inp['latitude']) \
          + '&kind=metro&format=json&apikey=' + key
    url = requests.utils.requote_uri(url)
    return url


def getGUrl(orig, dest, key):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json?origins=' + str(orig['latitude']) + ',' \
          + str(orig['longitude']) + '&destinations=' + str(dest['latitude']) + ',' + str(dest['longitude']) + \
          '&mode=walking&key=' + key
    url = requests.utils.requote_uri(url)
    return url


def get_coord_by_add(address):
    loc = {"latitude": 0, "longitude": 0}
    cl = Client(y_apikey)
    coord = cl.coordinates(address)
    loc['latitude'] = round(float(coord[1]), 6)
    loc['longitude'] = round(float(coord[0]), 6)
    return loc
    

def get_metro_by_loc(loc):
    metro = {"name": "", "location": {"latitude": 0,
                                      "longitude": 0}
             }
    met_j = requests.get(getYUrl(loc, y_apikey)).json()
    metro["name"] = met_j['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['name']
    met_costr = met_j['response']['GeoObjectCollection']['featureMember'][0]['GeoObject']['Point']['pos']
    metro["location"]["latitude"] = round(float(met_costr.split()[1]), 6)
    metro["location"]["longitude"] = round(float(met_costr.split()[0]), 6)
    return metro


def form_msg(inp):
    err = False
    if 'text' in inp['message']:
        loc = get_coord_by_add(inp['message']['text'])
    elif 'location' in inp['message']:
        loc = inp['message']['location']
    else:
        err = True

    if not err:
        metro = get_metro_by_loc(loc)
        dist_j = requests.get(getGUrl(loc, metro["location"], g_apikey)).json()
        dist = dist_j['rows'][0]['elements'][0]['duration']['text']
        msg = "Hi, closest metro to you is {metro}, and approximate duration is {duration}".format(
            metro=metro["name"], duration=dist
        )
    else:
        msg = 'There\'s no text or location in your message'
    return msg


def botHandler(event, context):
    print(event)
    hbtb = Bot(token)
    chat_id = event['message']['chat']['id']
    try:
        msg = form_msg(event)
    except NothingFound:
        msg = 'Yandex GeoApi found nothing for your location'
    except IndexError:
        msg = 'Your location seems to far from Moscow according to Yandex GeoApi'
    except:
        msg = 'Something went wrong'
    hbtb.send_message(chat_id, msg)
    return 1
