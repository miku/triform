# coding: utf-8

"""
SQL for main database (MySQL for now).
"""

SETUP = """
# Run as root mysql user, e.g.
# $ mysql -uroot < init.sql
CREATE DATABASE sameas;
CREATE USER 'sameas'@'localhost' IDENTIFIED BY 'sameas';
GRANT ALL ON `sameas`.* TO 'sameas'@'localhost';
FLUSH PRIVILEGES;
"""


CREATE_TABLES = """
# sha1 hexdigest is 40b
CREATE TABLE IF NOT EXISTS sameas (
    a VARCHAR(40) NOT NULL,
    b VARCHAR(40) NOT NULL,
    PRIMARY KEY (a, b)
);
"""


DROP_TABLES = """
DROP TABLE mapping;
DROP TABLE sameas;
"""
