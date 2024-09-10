CREATE TABLE IF NOT EXISTS accounts (
    account_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    username varchar(255),
    password varchar(255),
    is_admin boolean
);

-- NEW QUERY --

CREATE TABLE IF NOT EXISTS tickets (
    ticket_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    ticket_owner_id INTEGER,
    title varchar(255),
    content varchar(255),
    post_date timestamp,
    last_updated timestamp,
    FOREIGN KEY(ticket_owner_id) REFERENCES accounts(account_id)
);