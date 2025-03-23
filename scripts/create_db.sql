# mysql -uroot -p<password> < create_db.sql
DROP DATABASE IF EXISTS finquery;
DROP USER IF EXISTS finuser@localhost;
CREATE DATABASE finquery;
CREATE USER finuser@localhost identified by 'fu';
GRANT ALL PRIVILEGES ON finquery.* TO finuser@localhost;
FLUSH PRIVILEGES;

USE finquery;
CREATE TABLE transactions (
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
