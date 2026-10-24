
-- Pharmacy Management System
-- DBMS Laboratory Project
-- Database: MySQL

-- WARNING: Running this setup section deletes an existing
-- pharmacy_db database. Do not execute against your live database.

DROP DATABASE IF EXISTS pharmacy_db;
CREATE DATABASE pharmacy_db;
USE pharmacy_db;

-- 1. Category
CREATE TABLE Category (
    category_id INT AUTO_INCREMENT PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE,
    description VARCHAR(255)
);

-- 2. Supplier
CREATE TABLE Supplier (
    supplier_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_name VARCHAR(150) NOT NULL,
    phone VARCHAR(15) NOT NULL UNIQUE,
    email VARCHAR(100),
    address VARCHAR(255)
);

-- 3. Medicine
CREATE TABLE Medicine (
    medicine_id INT AUTO_INCREMENT PRIMARY KEY,
    medicine_name VARCHAR(150) NOT NULL,
    brand VARCHAR(100),
    category_id INT NOT NULL,
    unit VARCHAR(30) NOT NULL DEFAULT 'Strip',
    selling_price DECIMAL(10,2) NOT NULL,
    reorder_level INT NOT NULL DEFAULT 10,

    CONSTRAINT fk_medicine_category
        FOREIGN KEY (category_id)
        REFERENCES Category(category_id),

    CONSTRAINT chk_medicine_price
        CHECK (selling_price >= 0),

    CONSTRAINT chk_medicine_reorder
        CHECK (reorder_level >= 0)
);

-- 4. Purchase
CREATE TABLE Purchase (
    purchase_id INT AUTO_INCREMENT PRIMARY KEY,
    supplier_id INT NOT NULL,
    purchase_date DATE NOT NULL DEFAULT (CURRENT_DATE),
    invoice_number VARCHAR(50) NOT NULL UNIQUE,

    CONSTRAINT fk_purchase_supplier
        FOREIGN KEY (supplier_id)
        REFERENCES Supplier(supplier_id)
);

-- 5. PurchaseItem
-- Each row represents a medicine batch with its expiry date.
CREATE TABLE PurchaseItem (
    purchase_item_id INT AUTO_INCREMENT PRIMARY KEY,
    purchase_id INT NOT NULL,
    medicine_id INT NOT NULL,
    batch_number VARCHAR(50) NOT NULL,
    expiry_date DATE NOT NULL,
    quantity_received INT NOT NULL,
    quantity_remaining INT NOT NULL,
    unit_cost DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_purchaseitem_purchase
        FOREIGN KEY (purchase_id)
        REFERENCES Purchase(purchase_id),

    CONSTRAINT fk_purchaseitem_medicine
        FOREIGN KEY (medicine_id)
        REFERENCES Medicine(medicine_id),

    CONSTRAINT uq_medicine_batch
        UNIQUE (medicine_id, batch_number),

    CONSTRAINT chk_received
        CHECK (quantity_received > 0),

    CONSTRAINT chk_remaining
        CHECK (quantity_remaining >= 0),

    CONSTRAINT chk_remaining_limit
        CHECK (quantity_remaining <= quantity_received),

    CONSTRAINT chk_unit_cost
        CHECK (unit_cost >= 0)
);

-- 6. Sale
CREATE TABLE Sale (
    sale_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_date DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    customer_name VARCHAR(150) DEFAULT 'Walk-in Customer',
    payment_method VARCHAR(20) NOT NULL DEFAULT 'Cash',
    total_amount DECIMAL(12,2) NOT NULL DEFAULT 0,

    CONSTRAINT chk_sale_total
        CHECK (total_amount >= 0),

    CONSTRAINT chk_payment_method
        CHECK (payment_method IN ('Cash', 'Card', 'UPI'))
);

-- 7. SaleItem
-- Links each sale to the batch from which stock is sold.
CREATE TABLE SaleItem (
    sale_item_id INT AUTO_INCREMENT PRIMARY KEY,
    sale_id INT NOT NULL,
    purchase_item_id INT NOT NULL,
    quantity INT NOT NULL,
    unit_price DECIMAL(10,2) NOT NULL,

    CONSTRAINT fk_saleitem_sale
        FOREIGN KEY (sale_id)
        REFERENCES Sale(sale_id),

    CONSTRAINT fk_saleitem_batch
        FOREIGN KEY (purchase_item_id)
        REFERENCES PurchaseItem(purchase_item_id),

    CONSTRAINT chk_saleitem_quantity
        CHECK (quantity > 0),

    CONSTRAINT chk_saleitem_price
        CHECK (unit_price >= 0)
);

-- ==========================================
-- SECTION 2: SAMPLE DATA
-- Insert parent records before child records
-- ==========================================

-- 1. Categories
INSERT INTO Category (category_name, description) VALUES
('Pain Relief', 'Medicines used to relieve pain'),
('Antibiotics', 'Medicines used to treat bacterial infections'),
('Vitamins', 'Vitamin and nutritional supplements'),
('Antacids', 'Medicines for acidity and heartburn'),
('Allergy Relief', 'Medicines used for allergy symptoms'),
('Cough and Cold', 'Medicines for cough and cold symptoms'),
('Diabetes Care', 'Medicines and products for diabetes care'),
('First Aid', 'Products used for basic first aid'),
('Skin Care', 'Products for common skin conditions'),
('Digestive Health', 'Products supporting digestive health');

-- 2. Suppliers
INSERT INTO Supplier
(supplier_name, phone, email, address) VALUES
('Sunrise Pharma Distributors', '9000000001', 'sunrise@example.com', 'Kozhikode'),
('HealthFirst Supplies', '9000000002', 'healthfirst@example.com', 'Kochi'),
('MediCare Wholesale', '9000000003', 'medicare@example.com', 'Thrissur'),
('LifeLine Pharmaceuticals', '9000000004', 'lifeline@example.com', 'Kannur'),
('Wellness Drug Suppliers', '9000000005', 'wellness@example.com', 'Palakkad'),
('PrimeMed Distributors', '9000000006', 'primemed@example.com', 'Malappuram'),
('CarePlus Pharma', '9000000007', 'careplus@example.com', 'Wayanad'),
('CityMed Wholesale', '9000000008', 'citymed@example.com', 'Kottayam'),
('Apex Healthcare Supplies', '9000000009', 'apex@example.com', 'Alappuzha'),
('GreenCross Pharma', '9000000010', 'greencross@example.com', 'Kollam');

-- 3. Medicines
INSERT INTO Medicine
(medicine_name, brand, category_id, unit, selling_price, reorder_level)
VALUES
('Paracetamol 500mg', 'HealWell', 1, 'Strip', 25.00, 10),
('Amoxicillin 500mg', 'MediCare', 2, 'Strip', 85.00, 5),
('Vitamin C 500mg', 'NutriPlus', 3, 'Bottle', 120.00, 10),
('Antacid Tablets', 'AcidRelief', 4, 'Strip', 35.00, 8),
('Cetirizine 10mg', 'AllerCare', 5, 'Strip', 30.00, 10),
('Cough Syrup 100ml', 'CoughEase', 6, 'Bottle', 95.00, 5),
('Metformin 500mg', 'GlucoCare', 7, 'Strip', 45.00, 10),
('Antiseptic Liquid 100ml', 'FirstCare', 8, 'Bottle', 60.00, 5),
('Clotrimazole Cream', 'SkinCare', 9, 'Tube', 55.00, 5),
('Digestive Enzyme Tablets', 'DigestWell', 10, 'Strip', 70.00, 8);

-- 4. Purchases
INSERT INTO Purchase
(supplier_id, purchase_date, invoice_number) VALUES
(1, '2026-10-01', 'INV-1001'),
(2, '2026-10-02', 'INV-1002'),
(3, '2026-10-03', 'INV-1003'),
(4, '2026-10-04', 'INV-1004'),
(5, '2026-10-05', 'INV-1005'),
(6, '2026-10-06', 'INV-1006'),
(7, '2026-10-07', 'INV-1007'),
(8, '2026-10-08', 'INV-1008'),
(9, '2026-10-09', 'INV-1009'),
(10, '2026-10-10', 'INV-1010');

-- 5. Purchase batches
INSERT INTO PurchaseItem
(purchase_id, medicine_id, batch_number, expiry_date,
 quantity_received, quantity_remaining, unit_cost)
VALUES
(1, 1, 'BATCH-1001', '2028-06-30', 100, 98, 15.00),
(2, 2, 'BATCH-1002', '2027-12-31', 80, 80, 55.00),
(3, 3, 'BATCH-1003', '2028-03-31', 60, 60, 85.00),
(4, 4, 'BATCH-1004', '2027-09-30', 90, 90, 22.00),
(5, 5, 'BATCH-1005', '2028-01-31', 100, 100, 18.00),
(6, 6, 'BATCH-1006', '2027-11-30', 50, 50, 65.00),
(7, 7, 'BATCH-1007', '2028-05-31', 100, 100, 30.00),
(8, 8, 'BATCH-1008', '2027-10-31', 40, 40, 38.00),
(9, 9, 'BATCH-1009', '2028-02-29', 70, 70, 35.00),
(10, 10, 'BATCH-1010', '2027-08-31', 60, 60, 45.00);

-- 6. Original sales
INSERT INTO Sale
(sale_date, customer_name, payment_method, total_amount) VALUES
('2026-10-11 09:00:00', 'Customer A', 'Cash', 125.00),
('2026-10-11 10:00:00', 'Customer B', 'UPI', 170.00),
('2026-10-11 11:00:00', 'Customer C', 'Card', 240.00),
('2026-10-11 12:00:00', 'Customer D', 'Cash', 105.00),
('2026-10-11 13:00:00', 'Customer E', 'UPI', 150.00),
('2026-10-11 14:00:00', 'Customer F', 'Card', 190.00),
('2026-10-11 15:00:00', 'Customer G', 'Cash', 135.00),
('2026-10-11 16:00:00', 'Customer H', 'UPI', 120.00),
('2026-10-12 09:00:00', 'Customer I', 'Card', 110.00),
('2026-10-12 10:00:00', 'Customer J', 'Cash', 140.00);

-- 7. Original sale items
INSERT INTO SaleItem
(sale_id, purchase_item_id, quantity, unit_price) VALUES
(1, 1, 5, 25.00),
(2, 2, 2, 85.00),
(3, 3, 2, 120.00),
(4, 4, 3, 35.00),
(5, 5, 5, 30.00),
(6, 6, 2, 95.00),
(7, 7, 3, 45.00),
(8, 8, 2, 60.00),
(9, 9, 2, 55.00),
(10, 10, 2, 70.00);

-- 8. Additional demonstration sale
INSERT INTO Sale
(sale_date, customer_name, payment_method, total_amount)
VALUES
('2026-10-18 13:18:00', 'Test Customer', 'Cash', 50.00);

INSERT INTO SaleItem
(sale_id, purchase_item_id, quantity, unit_price)
VALUES
(LAST_INSERT_ID(), 1, 2, 25.00);

-- ==========================================
-- SECTION 3: VIEW, STORED PROCEDURE AND TRIGGERS
-- ==========================================

-- 1. View: calculate current stock and nearest unexpired batch expiry
CREATE VIEW PharmacyInventory AS
SELECT
    m.medicine_id,
    m.medicine_name,
    m.brand,
    c.category_name,
    m.selling_price,
    COALESCE(
        SUM(
            CASE
                WHEN pi.expiry_date >= CURRENT_DATE()
                THEN pi.quantity_remaining
                ELSE 0
            END
        ), 0
    ) AS available_stock,
    MIN(
        CASE
            WHEN pi.expiry_date >= CURRENT_DATE()
                 AND pi.quantity_remaining > 0
            THEN pi.expiry_date
            ELSE NULL
        END
    ) AS nearest_expiry
FROM Medicine m
JOIN Category c
    ON m.category_id = c.category_id
LEFT JOIN PurchaseItem pi
    ON m.medicine_id = pi.medicine_id
GROUP BY
    m.medicine_id,
    m.medicine_name,
    m.brand,
    c.category_name,
    m.selling_price;

-- 2. Stored procedure: search medicines by name
DELIMITER $$

CREATE PROCEDURE SearchMedicine(IN search_text VARCHAR(100))
BEGIN
    SELECT
        medicine_id,
        medicine_name,
        brand,
        selling_price,
        reorder_level
    FROM Medicine
    WHERE medicine_name LIKE CONCAT('%', search_text, '%')
    ORDER BY medicine_name;
END $$

DELIMITER ;

-- 3. Trigger: validate stock and expiry before recording a sale item
DELIMITER $$

CREATE TRIGGER ValidateSaleItem
BEFORE INSERT ON SaleItem
FOR EACH ROW
BEGIN
    DECLARE stock_available INT;
    DECLARE batch_expiry DATE;

    SELECT quantity_remaining, expiry_date
    INTO stock_available, batch_expiry
    FROM PurchaseItem
    WHERE purchase_item_id = NEW.purchase_item_id;

    IF NEW.quantity > stock_available THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Insufficient stock for this sale';
    END IF;

    IF batch_expiry < CURRENT_DATE() THEN
        SIGNAL SQLSTATE '45000'
            SET MESSAGE_TEXT = 'Cannot sell an expired batch';
    END IF;
END $$

DELIMITER ;

-- 4. Trigger: reduce stock after a sale item is inserted
DELIMITER $$

CREATE TRIGGER ReduceStockAfterSale
AFTER INSERT ON SaleItem
FOR EACH ROW
BEGIN
    UPDATE PurchaseItem
    SET quantity_remaining = quantity_remaining - NEW.quantity
    WHERE purchase_item_id = NEW.purchase_item_id;
END $$

DELIMITER ;

-- ==========================================
-- END OF PHARMACY MANAGEMENT SYSTEM SQL SETUP
-- ==========================================

-- ==========================================
-- SECTION 4: VERIFICATION QUERIES
-- ==========================================

-- 1. Verify the number of records in each main table
SELECT 'Category' AS table_name, COUNT(*) AS total_records
FROM Category
UNION ALL
SELECT 'Supplier', COUNT(*) FROM Supplier
UNION ALL
SELECT 'Medicine', COUNT(*) FROM Medicine
UNION ALL
SELECT 'Purchase', COUNT(*) FROM Purchase
UNION ALL
SELECT 'PurchaseItem', COUNT(*) FROM PurchaseItem
UNION ALL
SELECT 'Sale', COUNT(*) FROM Sale
UNION ALL
SELECT 'SaleItem', COUNT(*) FROM SaleItem;

-- 2. Verify the inventory view
SELECT * FROM PharmacyInventory
ORDER BY medicine_name;

-- 3. Test the stored procedure
CALL SearchMedicine('Paracetamol');

-- 4. Verify that the triggers exist
SHOW TRIGGERS;

-- 5. Verify all tables and the view
SHOW FULL TABLES;

-- 6. Verify total sales revenue
SELECT
    COUNT(*) AS total_sales,
    SUM(total_amount) AS total_revenue,
    AVG(total_amount) AS average_sale
FROM Sale;

-- 7. Medicine sales report using JOIN and GROUP BY
SELECT
    m.medicine_name,
    SUM(si.quantity) AS units_sold,
    SUM(si.quantity * si.unit_price) AS sales_amount
FROM SaleItem si
JOIN PurchaseItem pi
    ON si.purchase_item_id = pi.purchase_item_id
JOIN Medicine m
    ON pi.medicine_id = m.medicine_id
GROUP BY m.medicine_id, m.medicine_name
ORDER BY sales_amount DESC;
CREATE TABLE IF NOT EXISTS AdminUser (
    admin_id INT NOT NULL AUTO_INCREMENT,
    username VARCHAR(50) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    is_active TINYINT(1) NOT NULL DEFAULT 1,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (admin_id),
    UNIQUE KEY username (username)
);