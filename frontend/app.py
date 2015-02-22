import sys
import json
import pickle
import functools
import hashlib
import ssl
import hmac
import base64
import time
from uuid import uuid4
from os.path import dirname, abspath, join

from tornado.options import options, define
import tornado.ioloop
import tornado.web
import streql
import pycrfsuite
from unidecode import unidecode

from bibtagger.tokenizer import tokenize
from bibtagger.featurize import featurize


def build_signature(json_obj):
    msg = json.dumps(json_obj, sort_keys=True).encode('utf-8')
    sig = hmac.new(SECRET_KEY, msg, digestmod=hashlib.sha256).digest()
    return base64.b64encode(sig).decode('utf-8')


class ResolveHandler(tornado.web.RequestHandler):
    def get(self):
        q = self.get_argument('q', default=None)
        result = {'request-id': str(uuid4()), 'tokens': [], 'tags': [], 'q': ''}
        if q is not None:
            result.update(self._tag(q))

        signature = build_signature(result)
        result['signature'] = signature
        self.write(result)

    @functools.lru_cache(maxsize=1024)
    def _tag(self, q):
        q = unidecode(q)
        tokens = tokenize(q)

        if len(tokens) == 0:
            return {'tokens': [], 'tags': [], 'q': ''}

        X = featurize(tokens)
        tags = TAGGER.tag(X)
        return {'tokens': tokens, 'tags': tags, 'q': q}


class FeedbackHandler(tornado.web.RequestHandler):
    def post(self, status):
        assert status in ('accept', 'reject')

        data = json.loads(self.request.body.decode('utf-8'))
        received_signature = data.pop('signature')
        signature = build_signature(data)

        if streql.equals(received_signature, signature):
            with open(FEEDBACK_LOG_PATH, 'a') as f:
                json.dump({
                    'status': status,
                    'time': time.time(),
                    'data': data
                }, f)
                f.write('\n')


class NoCacheStaticFileHandler(tornado.web.StaticFileHandler):
    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        with open(join(STATIC_PATH, 'index.html'), 'r') as f:
            self.write(f.read())

    def set_extra_headers(self, path):
        self.set_header('Cache-Control', 'no-store, no-cache, must-revalidate, max-age=0')


if __name__ == "__main__":
    define("host", default="localhost", help="app host", type=str)
    define("port", default=5000, help="app port", type=int)
    define("feedbackdir", default=".", help='directory for feedback log file', type=str)
    options.parse_command_line()

    # load up the tokenizer
    PROJECT_DIR = join(dirname(abspath(__file__)), '..')
    STATIC_PATH = join(dirname(abspath(__file__)), 'static')
    FEEDBACK_LOG_PATH = join(options.feedbackdir, 'feedback.jsonl')
    TAGGER = pycrfsuite.Tagger()
    TAGGER.open(join(PROJECT_DIR, 'model.crfsuite'))
    SECRET_KEY = ssl.RAND_bytes(16)

    application = tornado.web.Application([
        (r"/resolve", ResolveHandler),
        (r"/feedback/(accept|reject)", FeedbackHandler),

        # in production, these are handled by nginx, so here we just have
        # them as non-caching routes for dev.
        (r"/", IndexHandler),
        (r"/static/(.*)", NoCacheStaticFileHandler, {"path": STATIC_PATH})
    ])

    application.listen(options.port, options.host)
    tornado.ioloop.IOLoop.instance().start()
