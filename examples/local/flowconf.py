from flowbber.loaders import source, aggregator, sink
from flowbber.components import Source, Aggregator, Sink


@source.register('my_source')
class MySource(Source):
    def collect(self):
        return {'my_value': 1000}


@aggregator.register('my_aggregator')
class MyAggregator(Aggregator):
    def accumulate(self, data):
        data['num_sources'] = {'total': len(data.keys())}


@sink.register('my_sink')
class MySink(Sink):
    def distribute(self, data):
        print(data)
