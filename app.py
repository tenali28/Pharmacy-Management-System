
import os
from datetime import date
from decimal import Decimal, InvalidOperation
from functools import wraps

from flask import (
    Flask, render_template, request, redirect,
    url_for, session, g
)
from werkzeug.security import check_password_hash
from mysql.connector import Error

from db import get_connection


app = Flask(__name__)

app.secret_key = os.environ.get("FLASK_SECRET_KEY")

if not app.secret_key:
    raise RuntimeError(
        "Set the FLASK_SECRET_KEY environment variable before starting Flask."
    )


# --------------------------------------------------
# LOGIN PROTECTION
# --------------------------------------------------

PUBLIC_ENDPOINTS = {"login", "static"}


@app.before_request
def require_login():
    if request.endpoint in PUBLIC_ENDPOINTS:
        return None

    if "admin_id" not in session:
        return redirect(url_for("login", next=request.path))

    return None


# --------------------------------------------------
# LOGIN
# --------------------------------------------------

@app.route("/login", methods=["GET", "POST"])
def login():
    error = None

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        connection = None
        cursor = None

        try:
            connection = get_connection()
            cursor = connection.cursor(dictionary=True)

            cursor.execute(
                """
                SELECT admin_id, username, password_hash
                FROM AdminUser
                WHERE username = %s AND is_active = TRUE
                """,
                (username,)
            )
            admin = cursor.fetchone()

            if admin and check_password_hash(
                admin["password_hash"], password
            ):
                session.clear()
                session["admin_id"] = admin["admin_id"]
                session["username"] = admin["username"]

                destination = request.args.get("next", "")

                if (
                    destination.startswith("/")
                    and not destination.startswith("//")
                ):
                    return redirect(destination)

                return redirect(url_for("dashboard"))

            error = "Invalid username or password."

        except Error:
            app.logger.exception("Login database error")
            error = "Login is temporarily unavailable. Please try again."

        finally:
            if cursor is not None:
                cursor.close()
            if connection is not None and connection.is_connected():
                connection.close()

    return render_template("login.html", error=error)


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return redirect(url_for("login"))


# --------------------------------------------------
# DASHBOARD
# --------------------------------------------------

@app.route("/")
def dashboard():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("SELECT COUNT(*) AS total FROM Medicine")
        total_medicines = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Supplier")
        total_suppliers = cursor.fetchone()["total"]

        cursor.execute("SELECT COUNT(*) AS total FROM Sale")
        total_sales = cursor.fetchone()["total"]

        cursor.execute("""
            SELECT COALESCE(SUM(total_amount), 0) AS revenue
            FROM Sale
        """)
        revenue = cursor.fetchone()["revenue"]

        return render_template(
            "index.html",
            total_medicines=total_medicines,
            total_suppliers=total_suppliers,
            total_sales=total_sales,
            revenue=revenue
        )

    except Error:
        app.logger.exception("Dashboard database error")
        return "Could not load dashboard.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# --------------------------------------------------
# MEDICINES
# --------------------------------------------------

@app.route("/medicines")
def medicines():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        search = request.args.get("search", "").strip()

        cursor.execute(
            "SELECT category_id, category_name FROM Category "
            "ORDER BY category_name"
        )
        categories = cursor.fetchall()

        if search:
            cursor.execute("""
                SELECT m.*, c.category_name
                FROM Medicine m
                JOIN Category c ON m.category_id = c.category_id
                WHERE m.medicine_name LIKE %s
                   OR m.brand LIKE %s
                   OR c.category_name LIKE %s
                ORDER BY m.medicine_name
            """, (f"%{search}%", f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("""
                SELECT m.*, c.category_name
                FROM Medicine m
                JOIN Category c ON m.category_id = c.category_id
                ORDER BY m.medicine_name
            """)

        medicine_list = cursor.fetchall()

        return render_template(
            "medicines.html",
            medicines=medicine_list,
            categories=categories,
            search=search
        )

    except Error:
        app.logger.exception("Medicine list error")
        return "Could not load medicines.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/medicines/add", methods=["GET", "POST"])
def add_medicine():
    connection = None
    cursor = None

    try:
        connection = get_connection()

        if request.method == "POST":
            medicine_name = request.form.get("medicine_name", "").strip()
            brand = request.form.get("brand", "").strip() or None
            category_id = int(request.form.get("category_id", "0"))
            unit = request.form.get("unit", "Strip").strip() or "Strip"
            selling_price = Decimal(request.form.get("selling_price", "0"))
            reorder_level = int(request.form.get("reorder_level", "10"))

            if not medicine_name:
                raise ValueError("Medicine name is required.")
            if category_id <= 0:
                raise ValueError("Choose a valid category.")
            if not selling_price.is_finite() or selling_price < 0:
                raise ValueError("Enter a valid non-negative price.")
            if reorder_level < 0:
                raise ValueError("Reorder level cannot be negative.")

            cursor = connection.cursor()
            cursor.execute("""
                INSERT INTO Medicine
                    (medicine_name, brand, category_id, unit,
                     selling_price, reorder_level)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, (
                medicine_name, brand, category_id, unit,
                selling_price, reorder_level
            ))
            connection.commit()
            return redirect(url_for("medicines"))

        cursor = connection.cursor(dictionary=True)
        cursor.execute("SELECT * FROM Category ORDER BY category_name")
        categories = cursor.fetchall()
        return render_template("add_medicine.html", categories=categories)

    except (ValueError, InvalidOperation) as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        return f"Invalid medicine details: {error}", 400

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        app.logger.exception("Add medicine error")
        return "Could not save the medicine. Check the details.", 400

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/medicines/<int:medicine_id>/edit", methods=["GET", "POST"])
def edit_medicine(medicine_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        if request.method == "POST":
            medicine_name = request.form.get("medicine_name", "").strip()
            brand = request.form.get("brand", "").strip() or None
            category_id = int(request.form.get("category_id", "0"))
            unit = request.form.get("unit", "Strip").strip() or "Strip"
            selling_price = Decimal(request.form.get("selling_price", "0"))
            reorder_level = int(request.form.get("reorder_level", "10"))

            if not medicine_name:
                raise ValueError("Medicine name is required.")
            if category_id <= 0:
                raise ValueError("Choose a valid category.")
            if not selling_price.is_finite() or selling_price < 0:
                raise ValueError("Enter a valid non-negative price.")
            if reorder_level < 0:
                raise ValueError("Reorder level cannot be negative.")

            cursor.execute("""
                UPDATE Medicine
                SET medicine_name=%s, brand=%s, category_id=%s,
                    unit=%s, selling_price=%s, reorder_level=%s
                WHERE medicine_id=%s
            """, (
                medicine_name, brand, category_id, unit,
                selling_price, reorder_level, medicine_id
            ))
            connection.commit()
            return redirect(url_for("medicines"))

        cursor.execute(
            "SELECT * FROM Medicine WHERE medicine_id=%s",
            (medicine_id,)
        )
        medicine = cursor.fetchone()

        if medicine is None:
            return "Medicine not found.", 404

        cursor.execute("SELECT * FROM Category ORDER BY category_name")
        categories = cursor.fetchall()

        return render_template(
            "edit_medicine.html",
            medicine=medicine,
            categories=categories
        )

    except (ValueError, InvalidOperation) as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        return f"Invalid medicine details: {error}", 400

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        app.logger.exception("Edit medicine error")
        return "Could not update the medicine.", 400

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/medicines/<int:medicine_id>/delete", methods=["POST"])
def delete_medicine(medicine_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM Medicine WHERE medicine_id=%s",
            (medicine_id,)
        )
        connection.commit()
        return redirect(url_for("medicines"))

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        return "Could not delete medicine. It may be linked to purchases.", 400

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# --------------------------------------------------
# SUPPLIERS
# --------------------------------------------------

@app.route("/suppliers")
def suppliers():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        search = request.args.get("search", "").strip()

        if search:
            cursor.execute("""
                SELECT * FROM Supplier
                WHERE supplier_name LIKE %s OR phone LIKE %s
                ORDER BY supplier_name
            """, (f"%{search}%", f"%{search}%"))
        else:
            cursor.execute("SELECT * FROM Supplier ORDER BY supplier_name")

        return render_template(
            "suppliers.html",
            suppliers=cursor.fetchall(),
            search=search
        )

    except Error:
        app.logger.exception("Supplier list error")
        return "Could not load suppliers.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/suppliers/add", methods=["POST"])
def add_supplier():
    connection = None
    cursor = None

    try:
        supplier_name = request.form.get("supplier_name", "").strip()
        phone = request.form.get("phone", "").strip()
        email = request.form.get("email", "").strip() or None
        address = request.form.get("address", "").strip() or None

        if not supplier_name or not phone:
            return "Supplier name and phone are required.", 400
        if not phone.isdigit() or not 7 <= len(phone) <= 15:
            return "Enter a valid phone number.", 400
        if email and ("@" not in email or "." not in email.rsplit("@", 1)[-1]):
            return "Enter a valid email address.", 400

        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO Supplier (supplier_name, phone, email, address)
            VALUES (%s, %s, %s, %s)
        """, (supplier_name, phone, email, address))
        connection.commit()
        return redirect(url_for("suppliers"))

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        return "Could not add supplier. Check for duplicate details.", 400

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/suppliers/<int:supplier_id>/delete", methods=["POST"])
def delete_supplier(supplier_id):
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor()
        cursor.execute(
            "DELETE FROM Supplier WHERE supplier_id=%s",
            (supplier_id,)
        )
        connection.commit()
        return redirect(url_for("suppliers"))

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        return "Could not delete supplier. It may be linked to purchases.", 400

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# --------------------------------------------------
# INVENTORY
# --------------------------------------------------

@app.route("/inventory")
def inventory():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)
        search = request.args.get("search", "").strip()

        query = """
            SELECT i.*, m.reorder_level
            FROM PharmacyInventory i
            JOIN Medicine m ON i.medicine_id = m.medicine_id
        """

        if search:
            query += """
                WHERE i.medicine_name LIKE %s
                   OR i.category_name LIKE %s
            """
            cursor.execute(
                query + " ORDER BY i.medicine_name",
                (f"%{search}%", f"%{search}%")
            )
        else:
            cursor.execute(query + " ORDER BY i.medicine_name")

        return render_template(
            "inventory.html",
            inventory=cursor.fetchall(),
            search=search
        )

    except Error:
        app.logger.exception("Inventory error")
        return "Could not load inventory.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# --------------------------------------------------
# SALES
# --------------------------------------------------

@app.route("/sales")
def sales():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT pi.purchase_item_id, pi.batch_number,
                   pi.quantity_remaining, m.medicine_name,
                   m.selling_price
            FROM PurchaseItem pi
            JOIN Medicine m ON pi.medicine_id = m.medicine_id
            WHERE pi.quantity_remaining > 0
              AND pi.expiry_date >= CURRENT_DATE()
            ORDER BY m.medicine_name, pi.expiry_date
        """)
        batches = cursor.fetchall()

        cursor.execute("""
            SELECT sale_id, sale_date, customer_name,
                   payment_method, total_amount
            FROM Sale
            ORDER BY sale_id DESC
            LIMIT 20
        """)
        recent_sales = cursor.fetchall()

        return render_template(
            "sales.html",
            batches=batches,
            sales=recent_sales,
            message=request.args.get("message"),
            error=request.args.get("error")
        )

    except Error:
        app.logger.exception("Sales page error")
        return "Could not load sales.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


@app.route("/sales/add", methods=["POST"])
def add_sale():
    connection = None
    cursor = None

    try:
        customer_name = (
            request.form.get("customer_name", "").strip()
            or "Walk-in Customer"
        )
        payment_method = request.form.get("payment_method", "Cash").strip()
        purchase_item_id = int(request.form.get("purchase_item_id", "0"))
        quantity = int(request.form.get("quantity", "0"))

        if payment_method not in ("Cash", "Card", "UPI"):
            raise ValueError("Select a valid payment method.")
        if purchase_item_id <= 0 or quantity <= 0:
            raise ValueError("Choose a valid batch and quantity greater than zero.")

        connection = get_connection()
        connection.start_transaction()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT pi.quantity_remaining, pi.expiry_date,
                   m.selling_price, m.medicine_name
            FROM PurchaseItem pi
            JOIN Medicine m ON pi.medicine_id = m.medicine_id
            WHERE pi.purchase_item_id = %s
            FOR UPDATE
        """, (purchase_item_id,))
        batch = cursor.fetchone()

        if batch is None:
            raise ValueError("The selected batch does not exist.")
        if batch["expiry_date"] < date.today():
            raise ValueError("This batch has expired.")
        if batch["quantity_remaining"] < quantity:
            raise ValueError(
                f"Insufficient stock. Available quantity: "
                f"{batch['quantity_remaining']}."
            )

        unit_price = Decimal(str(batch["selling_price"]))
        total_amount = unit_price * quantity

        cursor.execute("""
            INSERT INTO Sale (customer_name, payment_method, total_amount)
            VALUES (%s, %s, %s)
        """, (customer_name, payment_method, total_amount))
        sale_id = cursor.lastrowid

        cursor.execute("""
            INSERT INTO SaleItem
                (sale_id, purchase_item_id, quantity, unit_price)
            VALUES (%s, %s, %s, %s)
        """, (sale_id, purchase_item_id, quantity, unit_price))

        # ReduceStockAfterSale trigger updates inventory.
        connection.commit()

        return redirect(url_for(
            "sales",
            message=f"Sale recorded successfully. Sale ID: {sale_id}"
        ))

    except (ValueError, InvalidOperation) as error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        return redirect(url_for("sales", error=str(error)))

    except Error:
        if connection is not None and connection.is_connected():
            connection.rollback()
        app.logger.exception("Sale creation error")
        return redirect(url_for(
            "sales",
            error="The sale could not be saved. Check stock and try again."
        ))

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


# --------------------------------------------------
# REPORTS
# --------------------------------------------------

@app.route("/reports")
def reports():
    connection = None
    cursor = None

    try:
        connection = get_connection()
        cursor = connection.cursor(dictionary=True)

        cursor.execute("""
            SELECT COUNT(*) AS total_sales,
                   COALESCE(SUM(total_amount), 0) AS total_revenue,
                   COALESCE(AVG(total_amount), 0) AS average_sale
            FROM Sale
        """)
        summary = cursor.fetchone()

        cursor.execute("""
            SELECT m.medicine_name,
                   SUM(si.quantity) AS quantity_sold,
                   SUM(si.quantity * si.unit_price) AS sales_amount
            FROM SaleItem si
            JOIN PurchaseItem pi
                ON si.purchase_item_id = pi.purchase_item_id
            JOIN Medicine m
                ON pi.medicine_id = m.medicine_id
            GROUP BY m.medicine_id, m.medicine_name
            ORDER BY quantity_sold DESC
        """)
        medicine_report = cursor.fetchall()

        cursor.execute("""
            SELECT DATE(sale_date) AS sale_day,
                   COUNT(*) AS number_of_sales,
                   SUM(total_amount) AS daily_revenue
            FROM Sale
            GROUP BY DATE(sale_date)
            ORDER BY sale_day DESC
        """)
        daily_report = cursor.fetchall()

        return render_template(
            "reports.html",
            summary=summary,
            medicine_report=medicine_report,
            daily_report=daily_report
        )

    except Error:
        app.logger.exception("Reports error")
        return "Could not load reports.", 500

    finally:
        if cursor is not None:
            cursor.close()
        if connection is not None and connection.is_connected():
            connection.close()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)