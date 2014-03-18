# Run as root mysql user, e.g.
# $ mysql -uroot < init.sql
CREATE DATABASE sameas;
CREATE USER 'sameas'@'localhost' IDENTIFIED BY 'sameas';
GRANT ALL ON `sameas`.* TO 'sameas'@'localhost';
FLUSH PRIVILEGES;
