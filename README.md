# IPL Analysis

A small project to load Indian Premier League (IPL) match data from CSV files into a MySQL database and generate basic analysis plots using Matplotlib.

Features
- Load match and delivery data from CSV files into a MySQL database.
- Produce simple visual analyses (for example: team wins, top players, run distributions) using Matplotlib.

Requirements
- Python 3.8 or later
- MySQL server (or update scripts to use another database)
- Python packages: pandas, matplotlib, mysql-connector-python (or mysqlclient)

Setup
1. Create and start a MySQL database. Note the host, port, user, password, and database name.
2. Install Python dependencies:

   pip install pandas matplotlib mysql-connector-python

3. Place the CSV data files (for example `matches.csv`, `deliveries.csv`) in the project directory or update the script paths to point to your data files.

Database
Update the script to use your MySQL connection settings or use environment variables. The script loads CSV data into database tables (it may create tables if needed). Review the script before running to confirm table names and schema.

Running
Run the main script from the project directory.

On Windows:
  "C:/path/to/python.exe" ipl_analysis_p1.py

Or with the default python in your PATH:
  python ipl_analysis_p1.py

Output
The script will load data and open Matplotlib windows with plots. Depending on the code it may also save figures to files.

Notes
- Verify and update file paths and database connection settings inside the script before running.
- If you prefer not to use MySQL, the scripts can be adapted to use SQLite or to analyze CSVs directly in memory.

Contributing
Suggestions and improvements are welcome. Please open an issue or submit a pull request.

License
Add a LICENSE file to indicate how you want to license the project.
