import tornado.ioloop
import tornado.web
import tornado.websocket
import redis
import json
import threading
import asyncio
import uuid

redis_client = redis.StrictRedis(host='localhost', port=6379, decode_responses=True)

class WebSocketHandler(tornado.websocket.WebSocketHandler):
    clients = set()

    def open(self):
        self.username = self.get_argument("username", None)
        if not self.username:
            self.username = f"User-{str(uuid.uuid4())[:8]}"

        self.clients.add(self)

        redis_client.sadd("online_clients", self.username)

        self.update_clients_list()

        self.write_message(json.dumps({
            "type": "welcome",
            "message": f"Добро пожаловать в чат, {self.username}!"
        }))


    def on_message(self, message):
        data = {
            "type": "message",
            "data": {
                "sender": self.username,
                "message": message
            }
        }
        redis_client.publish('chat_channel', json.dumps(data))

    def on_close(self):
        self.clients.remove(self)
        redis_client.srem("online_clients", self.username)

        self.update_clients_list()


    def check_origin(self, origin):
        return True

    def update_clients_list(self):
        online_clients = list(redis_client.smembers("online_clients"))

        data = {
            "type": "clients",
            "clients": online_clients
        }

        for client in self.clients:
            client.write_message(json.dumps(data))


async def redis_listener():
    pubsub = redis_client.pubsub()
    pubsub.subscribe("chat_channel")
    for message in pubsub.listen():
        if message["type"] == "message":
            data = json.loads(message["data"])
            for client in WebSocketHandler.clients:
                client.write_message(json.dumps(data))


def start_redis_listener():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(redis_listener())


if __name__ == "__main__":
    app = tornado.web.Application([
        (r"/websocket", WebSocketHandler),
        (r"/(.*)", tornado.web.StaticFileHandler, {"path": "./static", "default_filename": "index.html"})
    ])
    app.listen(8888)

    print("Сервер запущен: http://localhost:8888")
    threading.Thread(target=start_redis_listener, daemon=True).start()

    tornado.ioloop.IOLoop.current().start()
