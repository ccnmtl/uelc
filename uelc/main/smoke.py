import json
import zmq
from django.contrib.auth.models import User
from django.conf import settings
from smoketest import SmokeTest
from websocket import create_connection
from .helper_functions import gen_token

zmq_context = zmq.Context()


class DBConnectivity(SmokeTest):
    def test_retrieve(self):
        cnt = User.objects.all().count()
        # all we care about is not getting an exception
        self.assertTrue(cnt > -1)


class BrokerConnectivity(SmokeTest):
    def test_connect(self):
        """ a simple check to see if we can open up a socket
        to the zmq broker.
        We send a message and wait three seconds for a response.
        Send the message to page "0", which should never
        conflict with an actual page.
        """
        socket = zmq_context.socket(zmq.REQ)
        socket.setsockopt(zmq.LINGER, 0)
        socket.connect(settings.WINDSOCK_BROKER_URL)

        try:
            # the message we are broadcasting
            md = dict(userId=0,
                      username='',
                      hierarchy='',
                      nextUrl='',
                      section=0,
                      notification='')
            # an envelope that contains that message serialized
            # and the address that we are publishing to
            e = dict(address="%s.0" % (settings.ZMQ_APPNAME),
                     content=json.dumps(md))
            # send it off to the broker
            socket.send(json.dumps(e))
            # wait for a response from the broker to be sure it was sent

            poller = zmq.Poller()
            poller.register(socket, zmq.POLLIN)
            if poller.poll(3 * 1000):  # 3s timeout in milliseconds
                socket.recv()
            else:
                raise IOError("Timeout connecting to broker")
            self.assertTrue(True)
        except:
            self.assertTrue(False)
        finally:
            socket.close()


class DummyUser(object):
    username = "smoketest"


class DummyRequest(object):
    def __init__(self):
        self.user = DummyUser()
        self.META = {'HTTP_X_FORWARDED_FOR': '127.0.0.1'}


class WindsockConnectivity(SmokeTest):
    def test_connect(self):
        try:
            r = DummyRequest()
            token = gen_token(r, "smoketest")
            ws = create_connection(
                settings.WINDSOCK_WEBSOCKETS_BASE + "?token=" + token)
            ws.close()
            self.assertTrue(True)
        except:
            self.assertTrue(False)
