# -*- coding: utf-8 -*-

import logging
import tornado.escape
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.websocket
import os.path
import uuid

import pyaudio
import wave
import sys
import json
import array
import base64
import time

from tornado.options import define, options

define("port", default=8888, help="run on the given port", type=int)


class Application(tornado.web.Application):
    def __init__(self):
        handlers = [
            (r"/", MainHandler),
            (r"/audio", ChatSocketHandler),
        ]
        settings = dict(
            cookie_secret="43oETzKXQAGaYdkL5gEmGeJJFuYh7EQnp2XdTP1o/Vo=",
            template_path=os.path.join(os.path.dirname(__file__), "templates"),
            static_path=os.path.join(os.path.dirname(__file__), "static"),
            xsrf_cookies=True,
            autoescape=None,
        )
        tornado.web.Application.__init__(self, handlers, **settings)


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

class ChatSocketHandler(tornado.websocket.WebSocketHandler):
    waiters = set()

    def allow_draft76(self):
        # for iOS 5.0 Safari
        return False

    def open(self):
        ChatSocketHandler.waiters.add(self)

    def on_close(self):
        ChatSocketHandler.waiters.remove(self)

    @classmethod
    def send_audio(cls):
        for waiter in cls.waiters:

            # # stream audio to browser works!
            # if len(sys.argv) < 2:
            #     print "Plays a wave file.\n\n" +\
            #           "Usage: %s filename.wav" % sys.argv[0]
            #     sys.exit(-1)

            # wf = open(sys.argv[1], 'r')
            # binary = wf.read()
            # wf.close()

            # b64_data = base64.b64encode(binary)
            # try:
            #     waiter.write_message( b64_data )
            # except:
            #     logging.error("Error sending message", exc_info=True)


            # record audio and playback!
            # really trip happy accident do this in a while True loop :)
            chunk = 1024
            FORMAT = pyaudio.paInt16
            CHANNELS = 1
            RATE = 44100
            RECORD_SECONDS = 5
            WAVE_OUTPUT_FILENAME = "output.wav"

            p = pyaudio.PyAudio()

            stream = p.open(format = FORMAT,
                            channels = CHANNELS,
                            rate = RATE,
                            input = True,
                            frames_per_buffer = chunk)

            print "* recording"
            all = []
            for i in range(0, RATE / chunk * RECORD_SECONDS):
                data = stream.read(chunk)
                all.append(data)
            print "* done recording"

            stream.close()
            p.terminate()

            # write data to WAVE file
            data = ''.join(all)
            wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(p.get_sample_size(FORMAT))
            wf.setframerate(RATE)
            wf.writeframes(data)
            wf.close()

            wf = open("output.wav", 'r')
            binary = wf.read()
            wf.close()

            b64_data = base64.b64encode(binary)
            try:
                waiter.write_message( b64_data )
            except:
                logging.error("Error sending message", exc_info=True)
            


    def on_message(self, _message):
        message = json.loads( _message )

        if message['msg'] == "play":
            ChatSocketHandler.send_audio()


def main():
    tornado.options.parse_command_line()
    app = Application()
    app.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()


if __name__ == "__main__":
    main()
