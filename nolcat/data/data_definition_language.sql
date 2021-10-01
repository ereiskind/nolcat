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
