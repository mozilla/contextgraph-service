#!/bin/sh
PGHOST=$DB_HOST PGUSER=$DB_USER PGPASSWORD=$DB_PASSWORD PGDATABASE=miracle \
    psql $1 $2 $3 $4 $5 $6 $7 $8 $9
