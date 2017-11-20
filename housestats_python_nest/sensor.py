import click
import logging
import nest
import os

from housestats.metric import Metric
from housestats.sensor.base import BaseSensor

LOG = logging.getLogger(__name__)


class NestSensor(BaseSensor):
    sensor_type = 'nest'
    defaults = {
        'access_token_cache': os.path.join(
            os.environ['HOME'], '.config', 'nest_token_cache')
    }

    def __init__(self, config):
        super().__init__(config)

        LOG.info('authenticating to nest api')
        self.napi = nest.Nest(
            client_id=self.config['client_id'],
            client_secret=self.config['client_secret'],
            access_token_cache_file=self.config['access_token_cache'],
            access_token=self.config['access_token'])

        if self.napi.authorization_required:
            pin = config.get('pin')
            if pin:
                LOG.info('requesting access token')
                self.napi.request_token(pin)
            else:
                raise click.ClickException('nest api requires authorization')

    def sample(self):

        for therm in self.napi.thermostats:
            if therm.structure._serial != self.config['location']:
                continue

            if therm.temperature_scale == 'F':
                temp = nest.utils.f_to_c(therm.temperature)
                target = nest.utils.f_to_c(therm.target)
            else:
                temp = therm.temperature
                target = therm.target

            hvac_state = ['off', 'heating', 'cooling'].index(
                therm.hvac_state)

            yield ({'location': therm.name.lower(),
                    'id': therm.device_id
                    },
                   {
                       'temperature': temp,
                       'temperature_target': target,
                       'humidity': therm.humidity,
                       'hvac_state': hvac_state,
                   })

    def fetch(self):
        for sample in self.sample():
            tags = sample[0]
            tags.update(self.config.get('tags', {}))

            yield Metric.load(dict(
                sensor_type=self.sensor_type,
                sensor_id=sample[0]['id'],
                tags=tags,
                fields=sample[1]
            ))
