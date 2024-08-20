CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username varchar(255),
    password varchar(255),
    account_type varchar(255)
)
