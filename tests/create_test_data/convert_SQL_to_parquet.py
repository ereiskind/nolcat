"""This procedure for changing in MySQL to parquet files is inspired by the procedure at https://estuary.dev/blog/mysql-to-parquet/."""

from nolcat.nolcat_glue_job import *

log = logging.getLogger(__name__)


#SECTION: Break Down SQL Files
#ToDo: Repeat this section for each production file
query = "SELECT statistics_source_ID, report_type, report_creation_date FROM COUNTERData GROUP BY statistics_source_ID, report_type, report_creation_date;"
df = query_database(
    query=query,
    engine=db.engine,
)
log.info(df)