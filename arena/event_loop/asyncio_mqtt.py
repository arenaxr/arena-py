import socket
import asyncio
import paho.mqtt.client as mqtt
from .async_worker import AsyncWorker

class AsyncioMQTTHelper:
    """Adapted from: https://github.com/eclipse/paho.mqtt.python/blob/master/examples/loop_asyncio.py"""
    def __init__(self, event_loop, client):
        self.event_loop = event_loop
        self.loop = self.event_loop.loop

        self.client = client

        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

    def on_socket_open(self, client, userdata, sock):
        def cb():
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.misc_loop_worker = AsyncWorker(
                                func=self.misc_loop,
                                event=None,
                            )
        self.misc = self.event_loop.add_task(self.misc_loop_worker)

    def on_socket_close(self, client, userdata, sock):
        self.loop.remove_reader(sock)
        # self.misc.cancel()

    def on_socket_register_write(self, client, userdata, sock):
        def cb():
            client.loop_write()

        self.loop.add_writer(sock, cb)

    def on_socket_unregister_write(self, client, userdata, sock):
        self.loop.remove_writer(sock)

    async def misc_loop(self):
        while self.client.loop_misc() == mqtt.MQTT_ERR_SUCCESS:
            try:
                await asyncio.sleep(1)
            except asyncio.CancelledError:
                break
