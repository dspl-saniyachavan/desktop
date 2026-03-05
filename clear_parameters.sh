#!/bin/bash

echo "Clearing parameter tables from both databases..."
echo "=================================================="

# Clear PostgreSQL parameters
echo "Clearing PostgreSQL parameters..."
PGPASSWORD=secure_password_123 psql -h localhost -U precision_pulse_user -d precision_pulse_db -f clear_postgres_parameters.sql 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✓ PostgreSQL parameters table cleared"
else
    echo "✗ Failed to clear PostgreSQL parameters (database may not be running)"
fi

# Clear SQLite parameters (if database exists)
echo "Clearing SQLite parameters..."
if [ -f ~/.precisionpulse/app.db ]; then
    sqlite3 ~/.precisionpulse/app.db < clear_sqlite_parameters.sql
    echo "✓ SQLite parameters table cleared"
elif [ -f ./dspl-precision-pulse-desktop/data/app.db ]; then
    sqlite3 ./dspl-precision-pulse-desktop/data/app.db < clear_sqlite_parameters.sql
    echo "✓ SQLite parameters table cleared"
else
    echo "✓ SQLite database not found (will be created empty when desktop app starts)"
fi

echo "=================================================="
echo "Parameter tables cleared. Table structures remain intact."