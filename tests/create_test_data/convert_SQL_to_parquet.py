"""This procedure for changing in MySQL to parquet files is inspired by the procedure at https://estuary.dev/blog/mysql-to-parquet/."""

log = logging.getLogger(__name__)

try:
    from nolcat.nolcat_glue_job import *
    log.info("`from nolcat.nolcat_glue_job import *` successful.")
except:
    try:
        from ..nolcat.nolcat_glue_job import *
        log.info("`from ..nolcat.nolcat_glue_job import *` successful.")
    except:
        try:
            from ..nolcat_glue_job import *
            log.info("`from ..nolcat_glue_job import *` successful.")
        except:
            try:
                from ..nolcat import nolcat_glue_job
                log.info("`from ..nolcat import nolcat_glue_job` successful.")
            except:
                try:
                    from nolcat import nolcat_glue_job
                    log.info("`from nolcat import nolcat_glue_job` successful.")
                except:
                    try:
                        from .. import nolcat_glue_job
                        log.info("`from .. import nolcat_glue_job` successful.")
                    except:
                        try:
                            from nolcat.nolcat.nolcat_glue_job import *
                            log.info("`from nolcat.nolcat.nolcat_glue_job import *` successful.")
                        except:
                            try:
                                from nolcat.nolcat import nolcat_glue_job
                                log.info("`from nolcat.nolcat import nolcat_glue_job` successful.")
                            except:
                                log.warning("None of the import statements worked")


#SECTION: Break Down SQL Files
#ToDo: Repeat this section for each production file
query = "SELECT statistics_source_ID, report_type, report_creation_date FROM COUNTERData GROUP BY statistics_source_ID, report_type, report_creation_date;"
df = query_database(
    query=query,
    engine=db.engine,
)
log.info(df)