#!/bin/bash
set -e

wait_for_tcp() {
    local host=$1 port=$2
    echo "Waiting for ${host}:${port}..."
    until (echo > "/dev/tcp/${host}/${port}") >/dev/null 2>&1; do
        sleep 2
    done
}

wait_for_tcp 172.28.1.2 9092   # kafka
wait_for_tcp 172.28.1.3 9042   # cassandra

echo "Dependencies are up, submitting Spark job..."

until spark-submit \
  --conf "spark.jars.ivy=/opt/bitnami/spark/.ivy2" \
  --conf "spark.cassandra.connection.host=172.28.1.3" \
  --packages org.apache.spark:spark-sql-kafka-0-10_2.12:3.3.1,com.datastax.spark:spark-cassandra-connector_2.12:3.0.0 \
  /opt/bitnami/spark/jobs/spark_job.py stocks; do
    echo "Spark job exited, restarting in 10s..."
    sleep 10
done
