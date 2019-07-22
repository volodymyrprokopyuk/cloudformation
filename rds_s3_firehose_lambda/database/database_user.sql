-- Create ingest_role with privileges
CREATE ROLE ingest_role;
GRANT USAGE ON SCHEMA ingest TO ingest_role;
GRANT SELECT, INSERT, UPDATE ON ALL TABLES IN SCHEMA ingest TO ingest_role;
GRANT ALL ON ALL SEQUENCES IN SCHEMA ingest TO ingest_role;

-- Create ingest user and grant him ingest_role privileges
CREATE ROLE ingest WITH PASSWORD 'Password1!' LOGIN;
GRANT ingest_role TO ingest;
