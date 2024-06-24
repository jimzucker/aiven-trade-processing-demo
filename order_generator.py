#
# example producer from aixen console
#

import time, uuid
from datetime import datetime, timezone, timedelta
from kafka import KafkaProducer

TOPIC_NAME="orders"
CERTS_DIR="certs"
BOOT_STRAP_SERVER="kafka-trade-processing-trade-processing.g.aivencloud.com:24051"
FLUSH_INTERVAL=5000 #frequency to flush the kafka buffers

print(f"INFO: Trying to connect to broker...")

producer = KafkaProducer(
    bootstrap_servers=BOOT_STRAP_SERVER,
    security_protocol="SSL",
    ssl_cafile=CERTS_DIR + "/ca.pem",
    ssl_certfile=CERTS_DIR + "/service.cert",
    ssl_keyfile=CERTS_DIR + "/service.key",
)

print(f"Connected to broker, starting sending ....")

#initialize
iso_date = datetime.now(timezone.utc).isoformat(timespec='milliseconds')
account = ""
for i in range(1000000):
    i += 1
    
    #create message content
    order_uuid = str(uuid.uuid4())
    
    #odd accounts are struct, even are flow
    if i % 2 != 0:
        account = "struct"
    else:
        account = "flow"

    message = f'{{\
    "trade_id" : "{i}", \
    "quantity" : "{i*100}", \
    "account" : "{account}{i}", \
    "symbol": "AMZN", \
    "uuid" : "{order_uuid}", \
    "execution_time" : "{iso_date}" \
    }}'
    
    #send the message
    producer.send(TOPIC_NAME, key=order_uuid.encode('utf-8'), value=message.encode('utf-8'))
    print(f"Message sent: {message}")
    
    #flush every FLUSH_INTERVAL orders
    if i % FLUSH_INTERVAL == 0:
        producer.flush();

producer.close()
