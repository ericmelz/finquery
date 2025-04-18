# export USER_PASSWORD='<secret>';envsubst < create_db.sql | mysql --local-infile=1 -uroot -p
# mysql --local-infile=1 -uroot -p<password> < create_db.sql
#SET GLOBAL local_infile = 1;  # TODO: not sure if this needs to be execute beforehand

DROP DATABASE IF EXISTS finquery;
DROP USER IF EXISTS finuser@'%';
CREATE DATABASE finquery;
CREATE USER finuser@'%' identified by '$USER_PASSWORD';
GRANT SELECT ON finquery.* TO finuser@'%';
FLUSH PRIVILEGES;

USE finquery;
CREATE TABLE financial_transactions (
    transaction_id BIGINT NOT NULL PRIMARY KEY,
    date DATE,
    customer_id BIGINT NOT NULL,
    amount DECIMAL(15, 2),
    type VARCHAR(10),
    description TEXT
);

CREATE TABLE accounting_transactions (
    Transaction_ID VARCHAR(50) NOT NULL PRIMARY KEY,
    Date DATE,
    Account_Number BIGINT,
    Transaction_Type VARCHAR(100),
    Amount DECIMAL(15, 2),
    Currency VARCHAR(10),
    Counterparty VARCHAR(255),
    Category VARCHAR(100),
    Payment_Method VARCHAR(50),
    Risk_Incident TINYINT, -- 0 or 1
    Risk_Type VARCHAR(100),
    Incident_Severity VARCHAR(10),
    Error_Code VARCHAR(50),
    User_ID VARCHAR(50),
    System_Latency DECIMAL(10, 4),
    Login_Frequency INT,
    Failed_Attempts INT,
    IP_Region VARCHAR(100)
);

CREATE TABLE sales_data (
    order_id VARCHAR(10),
    product_id VARCHAR(10),
    product_name VARCHAR(100),
    category VARCHAR(50),
    quantity INT,
    unit_price DECIMAL(10, 2),
    total_price DECIMAL(10, 2),
    order_date DATE
);

LOAD DATA LOCAL INFILE '/Users/ericmelz/Data/code/finquery/data/financial_transactions.csv'
INTO TABLE financial_transactions
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(transaction_id, date, customer_id, amount, type, description);

LOAD DATA LOCAL INFILE '/Users/ericmelz/Data/code/finquery/data/accounting_transactions.csv'
INTO TABLE accounting_transactions
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(transaction_id, date, account_number, transaction_type, amount, currency, counterparty, category, payment_method, risk_incident, risk_type, incident_severity, error_code, user_id, system_latency, login_frequency, failed_attempts, ip_region);

LOAD DATA LOCAL INFILE '/Users/ericmelz/Data/code/finquery/data/sample_sales_data.csv'
INTO TABLE sales_data
FIELDS TERMINATED BY ','
ENCLOSED BY '"'
LINES TERMINATED BY '\n'
IGNORE 1 LINES
(order_id, product_id, product_name, category, quantity, unit_price, total_price, order_date);
