@echo off
echo ========================================
echo PostgreSQL Password Reset
echo ========================================
echo.
echo This will reset the 'postgres' user password to: postgres
echo.
pause

echo.
echo Step 1: Stopping PostgreSQL service...
net stop postgresql-x64-16

echo.
echo Step 2: Backing up pg_hba.conf...
copy "C:\Program Files\PostgreSQL\16\data\pg_hba.conf" "C:\Program Files\PostgreSQL\16\data\pg_hba.conf.backup"

echo.
echo Step 3: Modifying pg_hba.conf for trust authentication...
powershell -Command "(Get-Content 'C:\Program Files\PostgreSQL\16\data\pg_hba.conf') -replace 'scram-sha-256', 'trust' -replace 'md5', 'trust' | Set-Content 'C:\Program Files\PostgreSQL\16\data\pg_hba.conf'"

echo.
echo Step 4: Starting PostgreSQL service...
net start postgresql-x64-16
timeout /t 10

echo.
echo Step 5: Resetting password...
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres';"

echo.
echo Step 6: Restoring pg_hba.conf...
copy "C:\Program Files\PostgreSQL\16\data\pg_hba.conf.backup" "C:\Program Files\PostgreSQL\16\data\pg_hba.conf" /Y

echo.
echo Step 7: Restarting PostgreSQL service...
net stop postgresql-x64-16
net start postgresql-x64-16
timeout /t 10

echo.
echo Step 8: Testing connection...
set PGPASSWORD=postgres
"C:\Program Files\PostgreSQL\16\bin\psql.exe" -U postgres -d postgres -c "SELECT 'Password reset successful!' as status;"

echo.
echo ========================================
echo Password reset complete!
echo.
echo New credentials:
echo   Username: postgres
echo   Password: postgres
echo   Host: localhost
echo   Port: 5432
echo ========================================
echo.
pause