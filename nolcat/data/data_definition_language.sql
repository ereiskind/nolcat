/**** Data Defintiton Language: Defining the Schema ****/
/*
    Relations are named using camelCase
    Fields are named using Titlecase_with_Underscores

    The ERD corresponding to this schema can be found in the documentation; those relations with naming conventions not aligned with the above are from the initial planning stage.
*/

CREATE SCHEMA `nolcat`; -- If this changes, change in all "models.py" files
USE `nolcat`;


CREATE TABLE fiscalYears (
    Fiscal_Year_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Fiscal_Year CHAR(4) NOT NULL,
    Start_Date DATE NOT NULL,
    End_Date DATE NOT NULL,
    ACRL_60b SMALLINT,
    ACRL_63 SMALLINT,
    ARL_18 SMALLINT,
    ARL_19 SMALLINT,
    ARL_20 SMALLINT,
    Notes_on_Corrections_After_Submission TEXT
);


CREATE TABLE vendors (
    Vendor_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Vendor_Name VARCHAR(80) NOT NULL,
    Alma_Vendor_Code VARCHAR(10)
);

CREATE TABLE vendorNotes (
    Vendor_Notes_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Note TEXT,
    Written_By VARCHAR(100),
    Date_Written TIMESTAMP,
    Vendor_ID INT NOT NULL,
    INDEX vendor_INDX (vendor),
    CONSTRAINT vendors_FK_vendorNotes FOREIGN KEY vendor_INDX (vendor)
        REFERENCES vendors(VendorID)
        ON UPDATE restrict
        ON DELETE restrict
);