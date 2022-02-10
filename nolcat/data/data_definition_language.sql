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
    Notes_on_statisticsSources_Used TEXT,
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
    INDEX vendors_FK_INDX (Vendor_ID),
    CONSTRAINT vendors_FK_vendorNotes FOREIGN KEY vendors_FK_INDX (Vendor_ID)
        REFERENCES vendors(Vendor_ID)
        ON UPDATE restrict
        ON DELETE restrict
);


CREATE TABLE statisticsSources (
    Statistics_Source_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Statistics_Source_Name VARCHAR(100) NOT NULL,
    Statistics_Source_Retrieval_Code VARCHAR(30),
    Vendor_ID INT NOT NULL,
    INDEX vendors_FK_INDX (Vendor_ID),
    CONSTRAINT vendors_FK_statisticsSources FOREIGN KEY vendors_FK_INDX (Vendor_ID)
        REFERENCES vendors(Vendor_ID)
        ON UPDATE restrict
        ON DELETE restrict,
);

CREATE TABLE statisticsSourceNotes (
    Statistics_Source_Notes_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Note TEXT,
    Written_By VARCHAR(100),
    Date_Written TIMESTAMP,
    Statistics_Source_ID INT NOT NULL,
    INDEX statisticsSources_FK_INDX (Statistics_Source_ID),
    CONSTRAINT statisticsSources_FK_statisticsSourceNotes FOREIGN KEY statisticsSources_FK_INDX (Statistics_Source_ID)
        REFERENCES statisticsSources(Statistics_Source_ID)
        ON UPDATE restrict
        ON DELETE restrict
);


CREATE TABLE statisticsResourceSources (
    SRS_Statistics_Source INT NOT NULL,
    SRS_Resource_Source INT NOT NULL,
    Current_Statistics_Source BOOLEAN NOT NULL,
    PRIMARY KEY (SRS_Statistics_Source, SRS_Resource_Source),
    INDEX statisticsSources_FK_INDX (SRS_Statistics_Source),
    CONSTRAINT statisticsSources_FK_statisticsResourceSources FOREIGN KEY statisticsSources_FK_INDX (SRS_Statistics_Source)
        REFERENCES statisticsSources(Statistics_Source_ID)
        ON UPDATE restrict
        ON DELETE restrict,
    INDEX resourceSources_FK_INDX (SRS_Resource_Source),
    CONSTRAINT resourceSources_FK_statisticsResourceSources FOREIGN KEY resourceSources_FK_INDX (SRS_Resource_Source)
        REFERENCES resourceSources(Resource_Source_ID)
        ON UPDATE restrict
        ON DELETE restrict
);
        

CREATE TABLE resourceSources (
    Resource_Source_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Resource_Source_Name VARCHAR(100) NOT NULL,
    Source_in_Use BOOLEAN NOT NULL,
    Use_Stop_Date TIMESTAMP,
    Vendor_ID INT NOT NULL,
    INDEX vendors_FK_INDX (Vendor_ID),
    CONSTRAINT vendors_FK_resourceSources FOREIGN KEY vendors_FK_INDX (Vendor_ID)
        REFERENCES vendors(Vendor_ID)
        ON UPDATE restrict
        ON DELETE restrict
);

CREATE TABLE resourceSourceNotes (
    Resource_Source_Notes_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Note TEXT,
    Written_By VARCHAR(100),
    Date_Written TIMESTAMP,
    Resource_Source_ID INT NOT NULL,
    INDEX resourceSources_FK_INDX (Resource_Source_ID),
    CONSTRAINT resourceSources_FK_resourceSourceNotes FOREIGN KEY resourceSources_FK_INDX (Resource_Source_ID)
        REFERENCES resourceSources(Resource_Source_ID)
        ON UPDATE restrict
        ON DELETE restrict
);


CREATE TABLE annualUsageCollectionTracking (
    AUCT_Statistics_Source INT NOT NULL,
    AUCT_Fiscal_Year INT NOT NULL,
    Usage_Is_Being_Collected BOOLEAN NOT NULL,
    Manual_Collection_Required BOOLEAN,
    Collection_Via_Email BOOLEAN,
    Is_COUNTER_Compliant BOOLEAN,
    Collection_Status ENUM(
        'N/A: Paid by Law',
        'N/A: Paid by Med',
        'N/A: Paid by Music',
        'N/A: Open access',
        'N/A: Other (see notes)',
        'Collection not started',
        'Collection in process (see notes)',
        'Collection issues requiring resolution',
        'Collection complete',
        'Usage not provided',
        'No usage to report'
    ),
    Usage_File_Path VARCHAR(150),
    Notes TEXT,
    PRIMARY KEY (AUCT_Statistics_Source, AUCT_Fiscal_Year),
    CHECK (-- A constraint to ensure only valid situations are represented
        (-- Usage collection not required
            Usage_Is_Being_Collected=false AND
            Manual_Collection_Required=null AND
            Collection_Via_Email=null AND
            Is_COUNTER_Compliant=null AND
            (
                Collection_Status='N/A: Paid by Law' OR
                Collection_Status='N/A: Paid by Med' OR
                Collection_Status='N/A: Paid by Music' OR
                Collection_Status='N/A: Open access' OR
                Collection_Status='N/A: Other (see notes)'
            )
        )
        OR
        (-- Manual usage collection, including COUNTER R4
            Usage_Is_Being_Collected=true AND
            (
                Collection_Via_Email=true OR
                Collection_Via_Email=false
            ) AND
            Manual_Collection_Required=true AND
            (
                Collection_Status='Collection not started' OR
                Collection_Status='Collection in process (see notes)' OR
                Collection_Status='Collection issues requiring resolution' OR
                Collection_Status='Collection complete' OR
                Collection_Status='Usage not provided' OR
                Collection_Status='No usage to report'
            )
        )
        OR
        (-- R5 SUSHI collection
            Usage_Is_Being_Collected=true AND
            Manual_Collection_Required=false AND
            Collection_Via_Email=null AND
            Is_COUNTER_Compliant=true AND
            (
                Collection_Status='Collection not started' OR
                Collection_Status='Collection issues requiring resolution' OR
                Collection_Status='Collection complete' OR
                Collection_Status='No usage to report'
            )
        )
    )
    INDEX statisticsSources_FK_INDX (AUCT_Statistics_Source),
    CONSTRAINT statisticsSources_FK_annualUsageCollectionTracking FOREIGN KEY statisticsSources_FK_INDX (AUCT_Statistics_Source)
        REFERENCES statisticsSources(Statistics_Source_ID)
        ON UPDATE restrict
        ON DELETE restrict,
    INDEX fiscalYears_FK_INDX (AUCT_Fiscal_Year),
    CONSTRAINT fiscalYears_FK_annualUsageCollectionTracking FOREIGN KEY fiscalYears_FK_INDX (AUCT_Fiscal_Year)
        REFERENCES fiscalYears(Fiscal_Year_ID)
        ON UPDATE restrict
        ON DELETE restrict
);


-- Usage Data Relations
CREATE TABLE resources (
    Resource_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    DOI VARCHAR(75),
    ISBN CHAR(17),
    Print_ISSN CHAR(9),
    Online_ISSN CHAR(9),
    Data_Type VARCHAR(25) NOT NULL,
    Section_Type VARCHAR(10),
);


CREATE TABLE resourceTitles (
    Resource_Title_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Resource_Title VARCHAR(2000),
    Resource_ID INT NOT NULL,
    INDEX resources_FK_INDX (Resource_ID),
    CONSTRAINT resources_FK_resourceTitles FOREIGN KEY resources_FK_INDX (Resource_ID)
        REFERENCES resources(Resource_ID)
        ON UPDATE restrict
        ON DELETE restrict
);


CREATE TABLE resourcePlatforms (
    Resource_Platform_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Publisher VARCHAR(225),
    Publisher_ID VARCHAR(50),
    Platform VARCHAR(75) NOT NULL,
    Proprietary_ID VARCHAR(100),
    URI VARCHAR(200),
    -- Parent_Data_Type VARCHAR(25),
    -- Parent_DOI VARCHAR(50),
    -- Parent_Proprietary_ID VARCHAR(100),
    Interface INT NOT NULL,
    Resource_ID INT NOT NULL,
    INDEX resources_FK_INDX (Resource_ID),
    INDEX statisticsSources_FK_INDX (Interface)
    CONSTRAINT resources_FK_resourcePlatforms FOREIGN KEY resources_FK_INDX (Resource_ID)
        REFERENCES resources(Resource_ID)
        ON UPDATE restrict
        ON DELETE restrict,
    CONSTRAINT statisticsSources_FK_resourcePlatforms FOREIGN KEY statisticsSources_FK_INDX (Interface)
        REFERENCES statisticsSources(Statistics_Source_ID)
        ON UPDATE restrict
        ON DELETE restrict
);


CREATE TABLE usageData (
    Usage_Data_ID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    Resource_Platform_ID INT NOT NULL,
    Metric_Type VARCHAR(75) NOT NULL,
    Usage_Date DATE NOT NULL,
    Usage_Count MEDIUMINT UNSIGNED NOT NULL,
    YOP SMALLINT,
    Access_Type VARCHAR(20),
    Access_Method VARCHAR(10),
    Report_Creation_Date DATE,
    INDEX resourcePlatforms_FK_INDX (Resource_Platform_ID),
    CONSTRAINT resourcePlatforms_FK_usageData FOREIGN KEY resourcePlatforms_FK_INDX (Resource_Platform_ID)
        REFERENCES resourcePlatforms(Resource_Platform_ID)
        ON UPDATE restrict
        ON DELETE restrict
);