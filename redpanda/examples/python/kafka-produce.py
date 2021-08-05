#
# Examples of use for DH testing together with web UI.
#
# == Common to all:
#
#  * Start the redpanda compose: (cd redpanda && docker-compose up --build)
#  * From web UI do: > from deephaven import KafkaTools
#
# == Example (1)
#
# From web UI do:
# > t = KafkaTools.consumeToTable({'bootstrap.servers':'redpanda:29092', 'deephaven.key.column.name':'Symbol', 'deephaven.value.column.name':'Price', 'deephaven.value.column.type':'double'}, 'quotes')
# You should see a table show up with columns [ KafkaPartition, KafkaOffset, KafkaTimestamp, symbol, price ]
#
# Run this script to produce one row:
# $ python ./kafka-produce.py quotes MSFT double:274.82
# You should see one row show up on the web UI table, data matching above.
#
# == Example (2) 
#
# From web UI do:
# > t2 = KafkaTools.consumeToTable({'bootstrap.servers':'redpanda:29092', 'deephaven.key.column.name':'Metric', 'deephaven.value.column.name':'Value', 'deephaven.value.column.type':'long', 'deephaven.offset.column.name':'', 'deephaven.partition.column.name':''}, 'metrics')
# You should see a table show up with columns: [ KafkaTimestamp, Metric, Value ]
#
# Run this script to produce one row:
# $ python ./kafka-produce.py metrics us_west.latency.millis long:29
#

from confluent_kafka import Producer

import sys
import struct

data_arg_form = "type:value"

if len(sys.argv) < 3 or len(sys.argv) > 4 or (len(sys.argv) == 2 and sys.argv[1] == '-h'):
    print("Usage: " + sys.argv[0] + " topic-name " +
          data_arg_form + " [" + data_arg_form + "]", file=sys.stderr)
    sys.exit(1)

c = 1
topic_name = sys.argv[c]
c += 1

def delivery_report(err, msg):
    """ Called once for each message produced to indicate delivery result.
        Triggered by poll() or flush(). """
    if err is not None:
        print('Message delivery failed: {}'.format(err))
    else:
        print('Message key=|{}|, value=|{}| delivered to topic {} partition {}'
              .format(msg.key(), msg.value(), msg.topic(), msg.partition()))


#
producer = Producer({
    'bootstrap.servers': 'localhost:9092',
    'on_delivery': delivery_report,
})

def wrong_form(data_arg):
    print(sys.argv[0] + ": Error, argument " + data_arg +
          " is not of the form " + data_arg_form + ".", file=sys.stderr)
    sys.exit(1)

def data_arg_to_data(data_arg):
    s = data_arg.split(':', 1)
    if len(s) != 2:
        if len(s) == 1:
            # Assume string.
            return s[0]
        else:
            wrong_form(data_arg)
    if (s[0] == "str"):
        return s[1]
    if s[0] == "float":
        return struct.pack('>f', float(s[1]))
    if s[0] == "double":
        return struct.pack('>d', float(s[1]))
    if s[0] == "int":
        return int(s[1]).to_bytes(4, "big")
    if s[0] == "long":
        return int(s[1]).to_bytes(8, "big")
    print(sys.argv[0] + ": Error, type " + s[0] + " not supported.", file=sys.stderr)
    sys.exit(1)

if len(sys.argv) == 3:
    key = None
    value = data_arg_to_data(sys.argv[c])
    c += 1
else:
    key = data_arg_to_data(sys.argv[c])
    c += 1
    value = data_arg_to_data(sys.argv[c])
    c += 1

producer.produce(topic=topic_name, key=key, value=value)
producer.flush()
