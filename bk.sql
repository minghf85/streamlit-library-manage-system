CREATE TABLE Books (
    BookID INT AUTO_INCREMENT PRIMARY KEY,
    Title VARCHAR(255) NOT NULL,
    Author VARCHAR(255),
    ISBN VARCHAR(20) UNIQUE,
    Publisher VARCHAR(255),
    PublishDate DATE,
    Stock INT DEFAULT 0
);

-- 采购表
CREATE TABLE Procurement (
    ProcurementID INT AUTO_INCREMENT PRIMARY KEY,
    BookID INT,
    Quantity INT NOT NULL,
    Price DECIMAL(10, 2) NOT NULL,
    PurchaseDate DATE NOT NULL,
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
);

-- 淘汰表
CREATE TABLE Decommission (
    DecommissionID INT AUTO_INCREMENT PRIMARY KEY,
    BookID INT,
    Quantity INT NOT NULL,
    Reason TEXT,
    DecommissionDate DATE NOT NULL,
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
);

-- 租借表
CREATE TABLE Borrowing (
    BorrowingID INT AUTO_INCREMENT PRIMARY KEY,
    BookID INT,
    BorrowerName VARCHAR(255) NOT NULL,
    BorrowDate DATE NOT NULL,
    ReturnDate DATE,
    FOREIGN KEY (BookID) REFERENCES Books(BookID)
);