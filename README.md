# MarketPulse Stream

MarketPulse Stream is a streamlined system for processing live stock market data. It uses Apache Kafka for data input, Apache Spark for data handling, and Apache Cassandra for data storage, making it a powerful yet easy-to-use tool for financial data analysis 💹🕊️


![real-time-stock-stream](./assets/background.jpg)

## Getting Started

This guide will walk you through setting up and running MarketPulse Stream on your local machine for development and testing.

### Prerequisites

Ensure you have the following software installed:
- Docker
- Python (version 3.11 or higher)


### Todo Features

1. **Live Market Data Integration** ⌛
2. **Advanced Analytics Features** ⌛
3. **Interactive Data Visualization** ⌛
4. **Improved Scalability** ⌛
5. **User Customization Options** ⌛
6. **Stronger Security** ⌛


### Used Techs

![used techs](./assets/usedTechs.jpg)

- Appache Kafka
- Appache Cassandra
- Appache ZooKeeper
- Appache Spark
- Python


### Installation

Everything — the Kafka topic, the Cassandra keyspace/tables, and the Spark
streaming job — is bootstrapped automatically by Docker Compose on startup.
There are no manual setup steps; see **Docker Compose** below.


## Suppored Data Opreations

1. **Grouping Aggregation:** Summarize data by groups.
2. **Pivot Aggregation:** Reshape data, converting rows to columns.
3. **Rollups and Cubes:** Perform hierarchical and combinational aggregations.
4. **Ranking Functions:** Assign ranks within data partitions.
5. **Analytic Functions:** Compute aggregates while maintaining row-level details.


## Database Schema

![stockdata-schema](./assets/stockdata-schema.png)

#### Configuring Cassandra

The schema (keyspace + all 6 tables, including TTLs on the tables that grow
per-trade) lives in [`init-cassandra/init.cql`](./init-cassandra/init.cql) and
is applied automatically by the `cassandra` container's entrypoint on every
start — it's idempotent (`IF NOT EXISTS`), so restarts are safe.

## System Architecture

![system-architecture](./assets/systemArchitecture.svg)


#### Docker Compose

The full stack — Zookeeper, Kafka, Cassandra, Spark, the trade producer, and
the dashboard — is defined in [`docker-compose.yaml`](./docker-compose.yaml).
Each service's `entrypoint` handles its own readiness/init (creating the Kafka
topic, applying the Cassandra schema, waiting for dependencies before
submitting the Spark job), and `healthcheck`s gate startup order so dependent
services never start against a not-yet-ready broker/cluster.

**Launch everything:**
```bash
docker compose up -d
```

That single command starts the whole pipeline end to end — no manual
`kafka-topics.sh`, `cqlsh`, or `spark-submit` steps required. Services
restart automatically (`restart: always`) if a container crashes, and the
Spark job itself retries on failure without needing a container restart.

**Check status / logs:**
```bash
docker compose ps
docker compose logs -f spark       # watch the streaming job
docker compose logs -f dashboard   # watch the web app
```

## Monitoring and Logging

Check the logs for each service with `docker compose logs -f <service>` for
monitoring and debugging.


## Visualizations

The dashboard (in [`dashboard/`](./dashboard)) is a multi-page Dash web app
that's started automatically by Docker Compose — no manual run step needed.
Once the stack is up, open it at **http://localhost:8050**.

![graph 1](./assets/graph1.png)


![graph 2](./assets/graph2.png)


![graph 3](./assets/graph3.png)


![graph 4](./assets/graph4.png)

## Testing

![docker-compose-d](./assets/docker-compose-d.png)

![docker-monitoring](./assets/docker-monitoring.png)

![docker-ps](./assets/docker-ps.png)

![cqlsh](./assets/cqlsh.png)

![stocks-data-before](./assets/stocks-data-before.png)

![creat-kafka-topic](./assets/create-kafka-topic.png)

![kafka-producer](./assets/kafka-producer.png)

![spark-processing-1](./assets/spark-processing-1.png)

![spark-processing-1](./assets/spark-processing-2.png)

![cassandra](./assets/cassandra-data.png)


## Tables Results

### Stocks Table
![stocks](./assets/stocks.png)

### Analysis Stocks Table
![analytics_stocks](./assets/analytics_stocks.png)

### Analysis Stocks Table
![grouped_stocks](./assets/grouped_stocks.png)

### Pivoted Stocks Table
![grouped_stocks](./assets/pivoted_stocks.png)

### Ranked Stocks Table
![grouped_stocks](./assets/ranked_stocks.png)

### Rollup Stocks Table
![grouped_stocks](./assets/rollup_stocks.png)


## Contributing

Contributions to MarketPulse Stream are welcome, just open a PR 😊.

## Authors

- [Abdullah Alqahtani🚀](https://github.com/anqorithm)

## License

This project is licensed under the MIT License.
