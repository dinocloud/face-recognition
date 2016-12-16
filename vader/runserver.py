import tornado.ioloop
import tornado.httpserver
import tornado.options
import tornado.web

from tornado.options import define, options
from handlers import StreamHandler

define("port", default=8888, help="run on the given port", type=int)

def main():
    tornado.options.parse_command_line()
    application = tornado.web.Application([
        #(r"/", tornado.web.StaticFileHandler, {"path": "templates", "default_filename": "index.html"}),
        (r'.*/video_feed', StreamHandler)]) #*/video_feed/?([^/]*)$'
    http_server = tornado.httpserver.HTTPServer(application)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.current().start()

if __name__ == "__main__":
    main()