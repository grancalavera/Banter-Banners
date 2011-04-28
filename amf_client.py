import logging

from pyamf.remoting.client import RemotingService
	
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
)

path = 'http://localhost:8080/amf'
gw = RemotingService(path, logger=logging)
service = gw.getService('banter_banners')

teams = [
    'Arsenal',
    'Aston Villa',
    'Birmingham City',
    'Blackburn Rovers',
    'Blackpool',
    'Bolton Wanderers',
    'Chelsea',
    'Everton',
    'Fulham',
    'Liverpool',
    'Manchester City',
    'Manchester United',
    'Newcastle United',
    'Stoke City',
    'Sunderland',
    'Tottenham Hotspur',
    'West Bromwich Albion',
    'West Ham United',
    'Wigan Athletic',
    'Wolverhampton Wanderers',
]

for i in range(0, 3):
    for team in teams:
        service.getBanner(team)

print('Done.');