#!/bin/bash
set -e

# Start the real Cassandra server in the background (this replaces the
# image's default entrypoint, so we have to launch it ourselves).
docker-entrypoint.sh cassandra -f &
CASSANDRA_PID=$!

echo "Waiting for Cassandra to accept connections..."
until cqlsh -e "describe keyspaces" >/dev/null 2>&1; do
    sleep 3
done

echo "Applying schema (idempotent: safe to re-run on every container start)..."
cqlsh -f /init-cassandra/init.cql
echo "Cassandra schema ready."

# Keep the server in the foreground so docker can track/restart it correctly.
wait "$CASSANDRA_PID"
