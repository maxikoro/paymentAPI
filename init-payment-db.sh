set -e

psql -v ON_ERROR_STOP=1 --username "$POSTGRES_USER" --dbname "$POSTGRES_DB" <<-EOSQL
    CREATE USER paymentuser WITH PASSWORD 's3cure';
    CREATE DATABASE paymentdb
        WITH
        OWNER = paymentuser;

    \c paymentdb;

    SET ROLE paymentuser;

    CREATE TYPE payment_state AS ENUM
        ('pending', 'completed', 'rejected');

    CREATE TABLE payment
    (
        payment_id uuid NOT NULL,
        user_id uuid NOT NULL,
        created timestamp without time zone NOT NULL,
        processed timestamp without time zone,
        state payment_state NOT NULL,
        account_number character varying NOT NULL,
        amount double precision NOT NULL,
        description character varying,
        ext_payment_details character varying,
        CONSTRAINT payment_pkey PRIMARY KEY (payment_id)
    );
EOSQL
