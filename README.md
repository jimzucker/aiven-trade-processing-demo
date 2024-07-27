# Trade Processing Demo

## 1. Create the infrastructure
### Services
	kafka
	flink
	m3db (prometheus)
	grafana
### Integrations
	flink -> Kafka
	kafka -> m3db
	grafana -> m3db

## 2. Setup Pre-requisites install python and kafka-python to run the 'order generator'

- Install Python client
``` python3 -m pip install kafka-python ```

## 3. Download the cert/pem/key files from the UI and put them in the certs directory

## 4. Create 3 topics with 3 partitions and set retention to 120000
	orders
	flow_orders
	buy_orders

## 5. Create a flink application with the following configurations

### Source:
```
CREATE TABLE orders (
    trade_id INT,
    quantity INT,
    account STRING,
    symbol STRING,
    uuid STRING,
    execution_time STRING,
    execution_ts AS TO_TIMESTAMP( SUBSTRING(execution_time, 1, 23), 'yyyy-MM-dd''T''HH:mm:ss.SSS')
) WITH (
    'connector' = 'kafka',
    'properties.bootstrap.servers' = '',
    'scan.startup.mode' = 'earliest-offset',
    'topic' = 'orders',
    'value.format' = 'json'
)
```

### Sink:
```
CREATE TABLE flow_orders (
    trade_id INT,
    quantity INT,
    account STRING,
    symbol STRING,
    uuid STRING,
    execution_ts TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'properties.bootstrap.servers' = '',
    'scan.startup.mode' = 'earliest-offset',
    'topic' = 'flow_orders',
    'value.format' = 'json'
```

```
CREATE TABLE structured_orders (
    trade_id INT,
    quantity INT,
    account STRING,
    symbol STRING,
    uuid STRING,
    execution_ts TIMESTAMP(3)
) WITH (
    'connector' = 'kafka',
    'properties.bootstrap.servers' = '',
    'scan.startup.mode' = 'earliest-offset',
    'topic' = 'structured_orders',
    'value.format' = 'json'
)
```

### SQL:
```
EXECUTE STATEMENT SET
BEGIN
INSERT INTO flow_orders 
SELECT trade_id, quantity, account, symbol, uuid, execution_ts 
    FROM orders
    WHERE account like 'flow%';
INSERT INTO structured_orders
SELECT trade_id, quantity, account, symbol, uuid, execution_ts 
    FROM orders
    WHERE account like 'struct%';
END
```
*** 'Run' the query to verify everything works

## 6. Configure a grafan dashboard for all 3 topics to track rate of records inserted per second
```
rate(kafka_server:BrokerTopicMetrics_MessagesInPerSec_Count{topic=\"orders\"}[$__rate_interval])
rate(kafka_server:BrokerTopicMetrics_MessagesInPerSec_Count{topic=\"flow_orders\"}[$__rate_interval])
rate(kafka_server:BrokerTopicMetrics_MessagesInPerSec_Count{topic=\"structured_orders\"}[$__rate_interval])
```

## 7. Deploy the flink application with parallism '3'

## 8. Run the 'order generator'
python order_generator.py

You will see output like this:
```
Message sent: {    "trade_id" : "144941",     "quantity" : "14494100",     "account" : "struct144941",     "symbol": "AMZN",     "uuid" : "045598d7-f059-4f68-98b3-d9a30530af72",     "execution_time" : "2024-06-24T18:21:15.562+00:00"     }
Message sent: {    "trade_id" : "144942",     "quantity" : "14494200",     "account" : "flow144942",     "symbol": "AMZN",     "uuid" : "a50674f9-0fd2-4507-87f6-c6f0dbdc2f13",     "execution_time" : "2024-06-24T18:21:15.562+00:00"     }
```

## 9. Review results
## You can now view date topics using the Aiven UI 
## See the progress in the grana dashboard we created 'Trade Processing'

## 10. REMINDER: Stop your services so you dont run up your bill
