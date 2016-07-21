from uuid import UUID

from celery import Celery
from kombu.serialization import register
import iron_celery
from django.conf import settings
from anyjson import loads as json_loads, dumps as json_dumps


iron_celery  # iron_celery must be imported to inject the ironmq transport

app = Celery('genepc')
app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)


@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))


# Custom Serializer


def _loads(data):
    if isinstance(obj, bytes_t):
        obj = obj.decode('utf-8')
    return json_loads(obj)


def _dumps(data):
    """ Serialize all UUID fields to a string before passing
    the rest to json.dumps.
    """
    data['args'] = [str(arg) if isinstance(arg, UUID) else arg
        for arg in data['args']]
    return json_dumps(data)


def register_uuid_json():
    """Register a encoder/decoder for UUID compatable JSON serialization."""
    register('uuid_json', _dumps, _loads,
                      content_type='application/json',
                      content_encoding='utf-8')
register_uuid_json()
