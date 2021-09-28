User Stories
############

> To what extent can classes created for connecting to database, which represent tables, overlap OOP tables (ex. the class for connecting to the vendors table is also the vendors class in the OOP)

Stories
*******

Collecting and Storing Usage Statistics
=======================================
* As an **e-resources library associate**, I want the system to *store* all **usage stats** so that I can *create* custom **cross-platform reports** without *copying* and *pasting* from multiple **spreadsheets**.
* As an **e-resources library associate** responsible for *collecting* **usage stats**, I want the system to use **R5 SUSHI** to *collect* **COUNTER reports** so that I don't need to manually *download* the **reports**.
* As an **e-resources library associate** responsible for *collecting* **usage stats**, I want the option to *add* **notes** about an **interface** for a given **year** to *record* any **thoughts** for future **reference**.
* As an **e-resources library associate**, I want the system to *store** all **R4 reports** so that **historical usage data** is *retained** in a single **location**.
* As an **e-resources library associate** responsible for *collecting* **usage stats**, I want the system to *generate* **emails** to the **vendors** that don't provide **COUNTER stats** so that I don't need to *send* each **email** individually.
* As an **e-resources library associate**, I want to *upload* **non-COUNTER usage stats** in whatever **file format** they come in so that those **files** are in the same **location** as the **COUNTER reports**.
* As an **e-resources library associate** responsible for *collecting* **usage stats**, I want to *dedupe* the **resources** in incoming **SUSHI reports** against **resources** already in the **database** so I can have a **normalized list of resources** for database normalization.

Searching and Retrieving Data
=============================
* As an **e-resources library associate**, I want the system to automatically *sum up* the **e-resources usage numbers** requested by **ARL** and **ACRL/IPEDS** so that I don't need to *create* additional **workbooks** to get these **numbers**.
* As a **selector librarian**, I want to *look* at the **usage statistics** by **platform/user interface**, so I can *know* if a **resource** is being *used* on a **publisher platform** or through an **aggregator**.
* As a **selector librarian**, I want to have all the **names of a database** available so I can *find* specific **databases** even if the **official name** has recently *changed*.

Connecting to Other Data
========================
* As an **e-resources library associate**, I want to be able to *match* **order numbers** from any current or legacy **ILS** to **platforms** and/or **resources** to *add* historical **price data**.
* As the **e-resources librarian**, I want to *know* what **Databases A-Z** **items** are on which **platforms/user interfaces** so I can more easily *organize* the **Databases A-Z holdings** by **provider**.
* As the **e-resources librarian**, I want a **list** of all the **names** a **databases** goes and *has gone by* so I can more easily *connect* **databases** to **invoices**.

Technical Aspects
=================
* As the **database developer**, I want to *create* a growing **list** of unique **resources** from the **R4 reports** for the **initial database data** so I can *start* **SUSHI** *harvesting* with a known **unique resource list**.
* As an **assessment librarian**, I want to *know* when the **ACRL/IPEDS** and **ARL numbers** were *pulled* from the **database** so I can *tell* if any of the **data for a given reporting year** was *changed* due to **platform/vendor-issued correction notices** after the **report** was *submitted*.