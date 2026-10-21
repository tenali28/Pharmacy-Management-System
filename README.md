# Pharmacy Management System

A web-based Pharmacy Management System developed using Python, Flask, MySQL, HTML, and CSS. The application helps manage medicines, suppliers, inventory, sales, and reports through an administrator interface.

## Features

- **Admin Authentication:** Login and logout with session-based access control.
- **Dashboard:** View medicine and supplier counts, sales, and revenue.
- **Medicine Management:** Add, edit, delete, and search medicines.
- **Supplier Management:** View, add, and delete supplier records.
- **Inventory Management:** Monitor available stock, batch details, and expiry information.
- **Sales Management:** Record sales and view sales information.
- **Reports:** Access sales and business-related reports.
- **Database Integrity:** MySQL constraints, a database view, a stored procedure, and triggers for stock validation and automatic stock reduction.

## Technology Stack

- **Backend:** Python, Flask
- **Database:** MySQL
- **Frontend:** HTML, CSS
- **Database Connectivity:** MySQL Connector/Python
- **Development Tools:** Visual Studio Code, MySQL Workbench

## Project Structure

```text
Pharmacy-Management-System/
├── app.py
├── db.py
├── create_admin.py
├── requirements.txt
├── README.md
├── .gitignore
├── database/
│   ├── pharmacy_management.sql
│   └── pharmacy_management_test.sql
└── templates/
    ├── index.html
    ├── login.html
    ├── medicines.html
    ├── edit_medicine.html
    ├── suppliers.html
    ├── inventory.html
    ├── sales.html
    └── reports.html
```

## Prerequisites

Install the following before running the application:

- Python 3
- MySQL Server
- MySQL Workbench (recommended)
- Git (optional, for cloning the repository)

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/tenali28/Pharmacy-Management-System.git
cd Pharmacy-Management-System
```

Alternatively, download the repository and open its folder in VS Code.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 3. Install dependencies

```powershell
python -m pip install -r requirements.txt
```

### 4. Configure the MySQL database

Ensure MySQL Server is running.

The database setup script is located at:

`database/pharmacy_management.sql`

**Warning:** This script drops and recreates the `pharmacy_db` database. Do not run it against a database containing data you want to preserve. Review the script and use it only when intentionally creating a fresh database.

Execute the setup script using MySQL Workbench or the MySQL command-line client.

Configure a MySQL user with the required privileges for the application database. Do not publish database passwords or other credentials.

### 5. Set environment variables

Set the variables in the same PowerShell terminal used to run the application:

```powershell
$env:DB_HOST = "localhost"
$env:DB_PORT = "3306"
$env:DB_NAME = "pharmacy_db"
$env:DB_USER = "your_mysql_username"
$env:DB_PASSWORD = Read-Host "Enter your MySQL password"
$env:FLASK_SECRET_KEY = python -c "import secrets; print(secrets.token_hex(32))"
```

Replace `your_mysql_username` with your configured MySQL username. Enter your password only in the terminal, not in the source code.

These environment variables apply to the current PowerShell session. Set them again when opening a new terminal.

### 6. Create the administrator account

```powershell
python create_admin.py
```

Follow the prompts to create the administrator account.

### 7. Run the application

```powershell
python app.py
```

Open the local application in your browser:

http://127.0.0.1:5000/

## Database Design

The database includes tables for categories, medicines, suppliers, purchases, purchase items, sales, and sale items, along with administrator account data.

Additional database components include:

- `PharmacyInventory` view for inventory information.
- `SearchMedicine` stored procedure for medicine searches.
- `ValidateSaleItem` trigger for sale validation.
- `ReduceStockAfterSale` trigger for updating stock after a sale.

## Database Testing

The file `database/pharmacy_management_test.sql` contains database testing commands and recreates the separate `pharmacy_db_test` database.

**Warning:** Run this script only when you intend to replace that test database. Never run it against your production or live project database.

## Security Notes

- Keep passwords and secret keys out of source code and GitHub.
- Do not commit `.env` files or virtual environments.
- Use a dedicated MySQL account with appropriate permissions.
- Use a fresh, unique Flask secret key for each deployment.
- This project is configured for local development; production deployment requires additional security and configuration.

## Future Enhancements

- Role-based access for pharmacists and other staff.
- Low-stock alerts and expiry notifications.
- Invoice generation and exportable reports.
- Improved validation and automated testing.
- Deployment to a secure hosting platform.

## Author

Developed as a database-driven web application project using Python, Flask, and MySQL.
