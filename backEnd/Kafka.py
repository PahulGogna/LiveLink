from quixstreams import Application
import json
from typing import Generator

class Producer:
    def __init__(self, topic:str, key:str, broker_address = "localhost:9092") -> None:
        
        self.topic = topic
        self.key = key
        self.__app = Application(
                    broker_address=broker_address,
                    loglevel="DEBUG"
                )

    def produce(self, data, topic=None, key=None) -> None:
        
        topic = topic if topic else self.topic
        key = key if key else self.key
        try:
            with self.__app.get_producer() as producer:
                producer.produce(
                    topic= topic,
                    key= key,
                    value=json.dumps(data)
                )
        except Exception as error:
            raise error



class Consumer:
    def __init__(self, consumer_group:str, broker_address = "localhost:9092") -> None:
        self.__app = Application(
                    broker_address=broker_address,
                    loglevel="DEBUG",
                    consumer_group=consumer_group,
                    auto_offset_reset='latest'
                )
        
    def poll(self, topic:list[str], loop=True) -> Generator[dict, dict, None]:
        try:
            with self.__app.get_consumer() as consumer:
                consumer.subscribe(topic)

                while loop:
                    msg = consumer.poll(2)
                    
                    if msg is None:
                        print('Waiting...')
                    
                    elif msg.error() is not None:
                        raise Exception(msg.error())
                    else:
                        key = str(msg.key())
                        value = msg.value()
                        offset = msg.offset()
                        yield {'value':value, 'key':key, 'offset':offset}
                else:
                    msg = consumer.poll(2)
                    
                    if msg is None:
                        return
                    
                    elif msg.error() is not None:
                        raise Exception(msg.error())
                    else:
                        key = str(msg.key())
                        value = msg.value()
                        offset = msg.offset()
                        return {'value':value, 'key':key, 'offset':offset}

        except KeyboardInterrupt:
            pass