#!/bin/bash
set -e

/opt/bitnami/scripts/kafka/entrypoint.sh /opt/bitnami/scripts/kafka/run.sh &
KAFKA_PID=$!

echo "Waiting for Kafka to accept connections..."
until kafka-topics.sh --bootstrap-server localhost:9092 --list >/dev/null 2>&1; do
    sleep 2
done

echo "Ensuring 'stocks' topic exists..."
kafka-topics.sh --create --if-not-exists --topic stocks \
    --bootstrap-server localhost:9092 --partitions 1 --replication-factor 1
echo "Kafka topic ready."

wait "$KAFKA_PID"
