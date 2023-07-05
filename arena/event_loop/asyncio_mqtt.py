import socket
import asyncio
import paho.mqtt.client as mqtt
from .async_worker import AsyncWorker


class AsyncioMQTTHelper:
    """Adapted from: https://github.com/eclipse/paho.mqtt.python/blob/master/examples/loop_asyncio.py"""
    def __init__(self, event_loop, client):
        self.event_loop = event_loop
        self.loop = self.event_loop.loop

        self.connected = False
        self.client = client

        self.client.on_socket_open = self.on_socket_open
        self.client.on_socket_close = self.on_socket_close
        self.client.on_socket_register_write = self.on_socket_register_write
        self.client.on_socket_unregister_write = self.on_socket_unregister_write

        self.misc_loop_worker = AsyncWorker(
                                self.event_loop,
                                func=self.misc_loop,
                                event=None,
                            )
        self.misc = self.event_loop.add_task(self.misc_loop_worker)

    def on_socket_open(self, client, userdata, sock):
        def cb():
            client.loop_read()

        self.loop.add_reader(sock, cb)
        self.connected = True

    def on_socket_close(self, client, userdata, sock):
        self.loop.remove_reader(sock)
        self.connected = False

    def on_socket_register_write(self, client, userdata, sock):
        def cb():
            try:
                client.loop_write()
            except:
                pass

        self.loop.add_writer(sock, cb)

    def on_socket_unregister_write(self, client, userdata, sock):
        self.loop.remove_writer(sock)

    async def misc_loop(self):
        prev_res = None
        while True:
            res = self.client.loop_misc()

            if res != mqtt.MQTT_ERR_SUCCESS and res != prev_res:
                print("Something went wrong with your connection to the ARENA. Attempting to reconnect...")
                print("=====")
                print("Connecting to the ARENA... ", end="", flush=True)

            prev_res = res

            # try reconnecting every minute
            while res != mqtt.MQTT_ERR_SUCCESS:
                try:
                    self.client.reconnect()
                except:
                    pass

                await asyncio.sleep(60)
                if self.connected:
                    break

            try:
                await asyncio.sleep(0.1)
            except asyncio.CancelledError:
                break
