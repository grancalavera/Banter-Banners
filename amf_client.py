import logging

from pyamf.remoting.client import RemotingService
	
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)-5.5s [%(name)s] %(message)s'
)

path = 'http://localhost:8080/amf'
gw = RemotingService(path, logger=logging)
service = gw.getService('banter_banners')

print service.getBanner('Bolton Wanderers')