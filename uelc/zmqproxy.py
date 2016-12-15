import sys
import zmq
from django.conf import settings


zmq_context = zmq.Context()


def behave_socket_open(socket):
    """Make the socket behave-compatible. :-/"""
    if sys.argv[1:2] == ['behave']:
        socket.linger = 0


def behave_socket_recv(socket):
    """ZMQ socket.recv() that doesn't hang on behave"""
    # TODO: behave hangs on socket.recv()
    if sys.argv[1:2] == ['behave']:
        try:
            socket.recv(zmq.NOBLOCK)
        except zmq.ZMQError:
            pass
    else:
        socket.recv()


class ZMQProxy():
    def send(self, msg):
        socket = self.zmq_context.socket(zmq.REQ)
        behave_socket_open(socket)
        socket.connect(settings.WINDSOCK_BROKER_URL)
        socket.send(msg)
        behave_socket_recv(socket)


class DummyProxy():
    def send(self, msg):
        # we do nothing
        pass
