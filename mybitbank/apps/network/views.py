from django.contrib.auth.decorators import login_required
from django.contrib.gis.geoip import GeoIP
from django.shortcuts import render
from django.utils.translation import ugettext as _

from mybitbank.libs import misc
from mybitbank.libs.config import MainConfig
from mybitbank.libs.connections import connector


current_section = 'network'

@login_required
def index(request, selected_provider_id=sorted(connector.config.keys())[0]):
    '''
    Handler for the accounts
    '''
    sections = misc.getSiteSections(current_section)
    selected_provider_id = int(selected_provider_id)
    
    g = GeoIP()
    notsupported = 0;
    peers = connector.getPeerInfo(selected_provider_id)
    if 'error' in peers :
        peers = {}
        notsupported = 1
    else :
        for peer in peers:
            info = g.city(peer['addr'].partition(':')[0])
            if info is None:
                info = {}
            peer['ip'] = peer['addr'].partition(':')[0]
            peer['port'] = peer['addr'].partition(':')[2]
            peer['country'] = info.get('country_name', "")
            peer['country_code'] = info.get('country_code', "")
            peer['city'] = info.get('city', None) if info.get('city', None) != None else ''
            peer['lat'] = info.get('latitude', "");
            peer['lon'] = info.get('longitude', "");
            peer['subver'] = peer['subver'].replace("/", "")
            peer['in'] = misc.humanBytes(peer['bytesrecv']) if 'bytesrecv' in peer else 'N/A'
            peer['out'] = misc.humanBytes(peer['bytessent']) if 'bytessent' in peer else 'N/A'
            peer['lastsend'] = misc.twitterizeDate(peer['lastsend']) if 'lastsend' in peer else 'N/A'
            peer['lastrecv'] = misc.twitterizeDate(peer['lastrecv']) if 'lastrecv' in peer else 'N/A'
            peer['conntime'] = misc.timeSince(peer['conntime']) if 'conntime' in peer else 'N/A'
            peer['syncnode'] = peer['syncnode'] if 'syncnode' in peer else False
    
    currency_codes = {}
    currency_names = {}
    currency_symbols = {}
    for provider_id in connector.config:
        currency_names[provider_id] = connector.config[provider_id]['name']
        currency_symbols[provider_id] = connector.config[provider_id]['symbol']
        currency_codes[provider_id] = connector.config[provider_id]['currency']
    
    currency_codes = sorted(currency_codes)
    
    page_title = _("Network")
    context = {
               'globals': MainConfig['globals'],
               'breadcrumbs': misc.buildBreadcrumbs(current_section, '', currency_names[selected_provider_id]),
               'system_errors': connector.errors,
               'system_alerts': connector.alerts,
               'page_title': page_title,
               'page_sections': sections,
               'request': request,
               'currency_codes': currency_codes,
               'currency_names': currency_names,
               'currency_symbols': currency_symbols,
               'selected_provider_id': selected_provider_id,
               'peers': peers,
               'notsupported': notsupported
               }
    return render(request, 'network/index.html', context)

    
