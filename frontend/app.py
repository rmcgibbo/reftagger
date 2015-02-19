import sys
import json
import pickle
from os.path import dirname, abspath, join

import pycrfsuite
from unidecode import unidecode
import tornado.ioloop
import tornado.web

# load up the tokenizer
STATIC_PATH = join(dirname(abspath(__file__)), 'static')
PROJECT_DIR = join(dirname(abspath(__file__)), '..')
sys.path.insert(0, PROJECT_DIR)
from bibtagger.tokenizer import tokenize
from bibtagger.featurize import featurize

TAGGER = pycrfsuite.Tagger()
TAGGER.open(join(PROJECT_DIR, 'model.crfsuite'))

class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


class ResolveHandler(tornado.web.RequestHandler):
    def get(self):
        q = self.get_argument('q', default=None)
        if q is None:
            #? bail
            self.write({'tokens': [], 'tags': [], 'q': ''})
            return

        q = unidecode(q)
        tokens = tokenize(q)

        if len(tokens) == 0:
            self.write({'tokens': [], 'tags': [], 'q': ''})
            return

        X = featurize(tokens)
        tags = TAGGER.tag(X)
        self.write({'tokens': tokens, 'tags': tags, 'q': q})



class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        # with open(join(STATIC_PATH, 'index.html'), 'r') as f:
        #     self.write(f.read())
        self.render('static/index.html')

    # def set_extra_headers(self, path):
    #     self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')
    #

application = tornado.web.Application([
    (r"/", IndexHandler),
    (r"/resolve", ResolveHandler),
    # (r'/static/(.*)', tornado.web.StaticFileHandler, {'path': STATIC_PATH}),
    # handled with nginx in production anyways.
    (r"/static/(.*)", NoCacheStaticFileHandler, {"path": STATIC_PATH})
])

if __name__ == "__main__":
    application.listen(int(sys.argv[1]))
    tornado.ioloop.IOLoop.instance().start()
