CREATE KEYSPACE IF NOT EXISTS stockdata WITH replication = {'class':'SimpleStrategy', 'replication_factor' : 1};

-- TTL'd: every trade is appended, so this grows without bound unless old rows expire.
CREATE TABLE IF NOT EXISTS stockdata.stocks (
    stock text,
    trade_id uuid,
    price decimal,
    quantity int,
    trade_type text,
    trade_date date,
    trade_time time,
    PRIMARY KEY (stock, trade_id)
) WITH default_time_to_live = 3600;

-- Natural key (trade_type), Spark overwrites in place each micro-batch: bounded size.
CREATE TABLE IF NOT EXISTS stockdata.grouped_stocks (
    trade_type text PRIMARY KEY,
    avg_price decimal
);

-- Natural key (stock), overwritten in place each micro-batch: bounded size.
CREATE TABLE IF NOT EXISTS stockdata.pivoted_stocks (
    stock text PRIMARY KEY,
    avg_price_buy decimal,
    avg_price_sell decimal
);

-- TTL'd: ranks are recomputed and appended every micro-batch, so this grows without bound.
CREATE TABLE IF NOT EXISTS stockdata.ranked_stocks (
    stock text,
    trade_id text,
    price double,
    quantity int,
    trade_date date,
    trade_time time,
    trade_type text,
    rank int,
    PRIMARY KEY ((trade_type), rank)
) WITH default_time_to_live = 3600;

-- TTL'd: per-trade rows are appended every micro-batch, so this grows without bound.
CREATE TABLE IF NOT EXISTS stockdata.analytics_stocks (
    stock text,
    trade_id text,
    price double,
    quantity int,
    trade_date date,
    trade_time time,
    trade_type text,
    avg_price_overall double,
    PRIMARY KEY ((trade_type), trade_date)
) WITH default_time_to_live = 3600;

-- Natural key (trade_date, trade_type), overwritten in place: bounded size.
CREATE TABLE IF NOT EXISTS stockdata.rollup_stocks (
    trade_date text,
    trade_type text,
    avg_price double,
    PRIMARY KEY (trade_date, trade_type)
);
