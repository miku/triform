# Run as sameas mysql user, e.g.
# $ mysql -usameas -psameas sameas < contrib/tables.sql

CREATE TABLE IF NOT EXISTS mapping (
    uri VARCHAR(2083) NOT NULL,
    hash VARCHAR(40) PRIMARY KEY
);

# sha1 hexdigest is 40b
CREATE TABLE IF NOT EXISTS sameas (
    a VARCHAR(40) NOT NULL,
    b VARCHAR(40) NOT NULL,
    PRIMARY KEY (a, b)
);

-- DROP TABLE mapping;
-- DROP TABLE sameas;
