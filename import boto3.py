from pyspark.sql import SparkSession
from pyspark.sql.functions import col, lit, max as spark_max, array_join, concat, array, when, coalesce, current_timestamp, date_format, to_date, to_timestamp
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, ArrayType
import boto3
from io import StringIO
import datetime
from botocore.exceptions import ClientError
from dateutil.tz import *
import awswrangler as wr

# Initialize Spark session
spark = SparkSession.builder \
    .appName("AWS Data Processing") \
    .config("spark.sql.legacy.timeParserPolicy", "LEGACY") \
    .getOrCreate()

def assume_role(role_arn, session_name):
    sts_client = boto3.client('sts')
    response = sts_client.assume_role(
        RoleArn=role_arn,
        RoleSessionName=session_name
    )
    
    credentials = response['Credentials']
    return credentials

role_arn = 'arn:aws:iam::680865984329:role/AWSGlueServiceRole'
session_name = 'glue_session'
# Assume role in the target account
credentials = assume_role(role_arn, session_name)

# Create a dynamodb connection
dynamodb = boto3.resource('dynamodb', aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name='us-east-1')  # getting the Dynamodb serivce resource

role_arn2 = f'arn:aws:iam::673781949024:role/nasc-de'
session_name2 = 'awswrangler_session'
credentials2 = assume_role(role_arn2, session_name2)

# Create a session with the assumed role credentials
boto3_session = boto3.Session(
    aws_access_key_id=credentials2['AccessKeyId'],
    aws_secret_access_key=credentials2['SecretAccessKey'],
    aws_session_token=credentials2['SessionToken'],
)

# SQL query for Athena
query = '''
with lastrefresh as (
SELECT MAX(dw_run_hour) as maxdate
FROM \"bdt_analytics_prod.d_andes_tables_schema_attributes\"
WHERE  table_lifecycle_state = 'ACTIVE')
,cte as (SELECT distinct table_name, provider_id, MAX(created_by) as created_by, MAX(description) as description, MAX(snapshot_day) as LastRefreshDate
FROM  \"bdt_subscriptions.subscriptionsv3\"
WHERE subscription_target_id = '50c61b87-16bf-a571-9669-decc396fa437'
group by table_name, provider_id)
,cte2 as(
select provider_name, provider_id, A.table_name, version_number, array_agg(attribute) as columns
FROM "bdt_analytics_prod.d_andes_tables_schema_attributes"   A
where
date(dw_run_hour) = (SELECT DATE(maxdate) FROM lastrefresh)
and
table_name in (select DISTINCT table_name from cte)
and table_lifecycle_state = 'ACTIVE'
group by 1,2,3,4
), cte3 as (
SELECT MAX(version_number) as version_number, table_name FROM cte2
GROUP BY table_name
), cte4 AS (
SELECT table_name, MAX(revision) as revision FROM \"booker.ANDES_JOB_PROFILES\"
group by table_name
), cte5 as (
SELECT a.table_name, MAX(a.load_type) as load_type, MAX(a.load_option) as load_option
FROM \"booker.ANDES_JOB_PROFILES\" a
JOIN cte4 b
on a.table_name = b.table_name
and a.revision = b.revision
GROUP BY a.table_name
)

SELECT distinct a.provider_name as Provider, a.provider_id, CONCAT('https://datacentral.a2z.com/hoot/providers/', a.provider_id, '/', a.table_name) as Pipeline, a.version_number , a.table_name as TableName, c.created_by as DatasetPOC, c.description as Description, c.LastRefreshDate as LastRefreshDate,
       d.load_type as loadtype,
       a.columns as Columns
FROM cte2 a
join cte3 b
on a.table_name = b.table_name
and a.version_number = b.version_number
join cte c
on c.table_name = a.table_name
and c.provider_id = a.provider_id
left JOIN cte5 d
on a.table_name = d.table_name
'''

# Read from Athena and convert to Spark DataFrame
# First, read with awswrangler
andesdf_pd = wr.athena.read_sql_query(
    sql=query,
    database = 'andes',
    workgroup = 'nasc-de',
    boto3_session=boto3_session,
    ctas_approach=True)

print("andesdf", andesdf_pd)

# Convert pandas DataFrame to Spark DataFrame
andesdf = spark.createDataFrame(andesdf_pd)
print("andesdf (Spark)", andesdf.show(5))

# Add columns using Spark methods
andesdf = andesdf.withColumn("DatabaseName", lit("andes")) \
                .withColumn("ExpectedRefreshRate", lit("Daily")) \
                .withColumn("TeamName", lit("NA")) \
                .withColumn("TableSize", lit("NA")) \
                .withColumn("recordCount", lit("NA")) \
                .withColumn("Type", lit("NA")) \
                .withColumn("business_line", lit("NA")) \
                .withColumn("DescriptionQ", lit("NA"))

# Replace loadtype values using when/otherwise
andesdf = andesdf.withColumn("loadtype", 
                           when(col("loadtype") == "REPLACE", "Full Load")
                          .when(col("loadtype") == "APPEND", "append")
                          .when(col("loadtype").isNull(), "Full Load")
                          .otherwise(col("loadtype")))

# Select and rename columns
andesdf = andesdf.select(
    col("provider").alias("Provider"),
    col("DatabaseName"),
    col("tablename").alias("TableName"),
    col("lastrefreshdate").alias("LastRefreshDate"),
    col("columns").alias("Columns"),
    col("datasetpoc").alias("DatasetPOC"),
    col("description").alias("Description"),
    col("ExpectedRefreshRate"),
    col("pipeline").alias("Pipeline"),
    col("loadtype").alias("LoadType"),
    col("business_line").alias("TeamName"),
    col("TableSize"),
    col("recordCount").alias("# of Records"),
    col("Type")
)

print("andesdf (after transformation)", andesdf.show(5))

# Write the DataFrame to S3
andesdf.write.mode("overwrite").option("header", "true").csv("s3://nasc-udc/test/andes.csv")

# Process DynamoDB data
# Create empty Spark DataFrame with schema matching DynamoDB data
dyn_schema = StructType([
    StructField("team_name", StringType(), True),
    StructField("dataset_name", StringType(), True),
    StructField("dataset_poc", StringType(), True),
    StructField("description", StringType(), True),
    StructField("expected_latency", StringType(), True),
    StructField("pipeline", StringType(), True),
    StructField("provider", StringType(), True),
    StructField("load_type", StringType(), True),
    StructField("business_line", StringType(), True),
    StructField("descriptionq", StringType(), True)
])

# Since Spark can't scan DynamoDB directly, we need boto3 first, then convert
# Scan DynamoDB table
table = dynamodb.Table("huron_datasets")
response = table.scan()
dynamo_items = []

for item in response["Items"]:
    dynamo_row = {}
    for colname, colvalue in item.items():
        if colname in ('dataset_name', 'dataset_poc', 'description', 'expected_latency', 'pipeline', 'provider', 'load_type', 'business_line', 'team_name', 'descriptionq'):
            dynamo_row[colname] = colvalue
    
    # Only add rows with required data
    if dynamo_row:
        dynamo_items.append(dynamo_row)

# Convert to Spark DataFrame
dfdyn = spark.createDataFrame(dynamo_items, schema=dyn_schema)

# Select and rename columns
dfdyn = dfdyn.select(
    col("team_name").alias("DatabaseName"),
    col("dataset_name").alias("TableName"),
    col("dataset_poc"),
    col("description").alias("Description"),
    col("expected_latency").alias("ExpectedRefreshRate"),
    col("pipeline").alias("Pipeline"),
    col("provider").alias("Provider"),
    col("load_type").alias("LoadType"),
    col("business_line"),
    col("descriptionq").alias("DescriptionQ")
)

print("dfdyn", dfdyn.show(5))

# Function to get Lake Formation table details (remains similar)
def get_lake_formation_table_details(client, catalog_id, database_name, table_name):
    try:
        response = client.get_table_versions(
            CatalogId=catalog_id,
            DatabaseName=database_name,
            TableName=table_name
        )
        if 'TableVersions' in response and response['TableVersions']:
            latest_version = response['TableVersions'][0]
            return latest_version.get('VersionId'), latest_version.get('UpdateTime')
    except Exception as e:
        print(f"Error getting Lake Formation details: {str(e)}")
    return None, None

# Function to get S3 last modified (remains similar)
def get_s3_last_modified(location):
    try:
        s3_client = boto3.client('s3',
            aws_access_key_id=credentials2['AccessKeyId'],
            aws_secret_access_key=credentials2['SecretAccessKey'],
            aws_session_token=credentials2['SessionToken'],
            region_name='us-east-1')
        
        path = location.replace('s3://', '')
        bucket = path.split('/')[0]
        prefix = '/'.join(path.split('/')[1:])
        
        response = s3_client.list_objects_v2(
            Bucket=bucket,
            Prefix=prefix,
            MaxKeys=1000
        )
        
        if 'Contents' in response:
            last_modified_dates = [obj['LastModified'] for obj in response['Contents']]
            return max(last_modified_dates)
        return None
    except Exception as e:
        print(f"Error getting S3 metadata: {str(e)}")
        return None

# Create AWS clients
crawlerH1 = boto3.client('glue', aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'],
    region_name='us-east-1')

client = boto3.client('glue', region_name='us-east-1')
responseGetDatabases = client.get_databases()
databaseList = responseGetDatabases['DatabaseList']

# Create schema for table data
table_schema = StructType([
    StructField("Account", StringType(), True),
    StructField("DatabaseName", StringType(), True),
    StructField("TableName", StringType(), True),
    StructField("LastRefreshDate", StringType(), True),
    StructField("ColumnName", StringType(), True),
    StructField("sizeKey", StringType(), True),
    StructField("recordCount", StringType(), True),
    StructField("classification", StringType(), True),
    StructField("DescriptionQ", StringType(), True),
    StructField("Description", StringType(), True),
    StructField("ExpectedRefreshRate", StringType(), True),
    StructField("Pipeline", StringType(), True),
    StructField("Provider", StringType(), True),
    StructField("LoadType", StringType(), True),
    StructField("TeamName", StringType(), True)
])

# Create schema for column data
col_schema = StructType([
    StructField("Account", StringType(), True),
    StructField("DatabaseName", StringType(), True),
    StructField("TableName", StringType(), True),
    StructField("LastRefreshDate", StringType(), True),
    StructField("ColumnName", StringType(), True),
    StructField("sizeKey", StringType(), True),
    StructField("recordCount", StringType(), True),
    StructField("classification", StringType(), True),
    StructField("DescriptionQ", StringType(), True),
    StructField("Description", StringType(), True),
    StructField("ExpectedRefreshRate", StringType(), True),
    StructField("Pipeline", StringType(), True),
    StructField("Provider", StringType(), True),
    StructField("LoadType", StringType(), True),
    StructField("TeamName", StringType(), True)
])

# Initialize empty lists to collect rows
table_rows = []
column_rows = []

for databaseDict in databaseList:
    # Get the correct database name and catalog ID
    if 'TargetDatabase' in databaseDict:
        databaseName = databaseDict['TargetDatabase']['DatabaseName']
        catalogId = databaseDict['TargetDatabase']['CatalogId']
    else:
        databaseName = databaseDict['Name']
        catalogId = databaseDict['CatalogId']
    
    # Skip if it's just a numeric account ID
    if databaseName.isdigit():
        continue
    
    # Special handling for qm_nohrsc_snow_noc
    if databaseDict['Name'] == 'qm_nohrsc_snow_noc':
        responseGetTables = client.get_tables(
            CatalogId='144103666967',
            DatabaseName='qm_nohrsc_snow'
        )
        for table in responseGetTables['TableList']:
            table_name = table['Name']
            _, update_time = get_lake_formation_table_details(client, '144103666967', 'qm_nohrsc_snow', table_name)
            
            if update_time:
                table['LastUpdateTime'] = update_time
            
            if not update_time:
                try:
                    table_metadata = client.get_table(
                        CatalogId='144103666967',
                        DatabaseName='qm_nohrsc_snow',
                        Name=table_name
                    )
                    
                    if 'Table' in table_metadata and 'UpdateTime' in table_metadata['Table']:
                        table['LastUpdateTime'] = table_metadata['Table']['UpdateTime']
                except Exception as e:
                    print(f"Error getting table metadata: {str(e)}")
    else:
        responseGetTables = client.get_tables(
            CatalogId=catalogId,
            DatabaseName=databaseName
        )
    
    tableList = responseGetTables['TableList']
    
    if not any(db in databaseName for db in ["andes", "gcfsbi_2", "robotics", "_dev", "audit_datawarehouse_log", "_silver"]):
        for tableDict in tableList:
            tableName = tableDict['Name']
            excluded_tables = ['engineering_retrofits_tracker', 'fleets', 'hqe_dynamolog_cross_accnt', 
                              'package_flix_athena_log', 'epc_nasc_mapping', 'swa_manifested_packages',
                              'o_slam_pkg_monetary_details', 'o_pickup_based_caps_report', 'o_slam_package_leg_details',
                              'd_perfectmile_package_items_v2_na', 'd_perfectmile_pkg_attributes_v2_na',
                              'a_perfectmile_gdea_int_pdd_na', 'd_perfectmile_gdea_int_pdd_na', 'packageflix_audit',
                              'packscan_lumos_sites', 'sort_testsc_sort_schedule', 'd_ltp_swa_sumry_netcore_18a_test',
                              'd_ltp_topline_netcore_1a_test', 'd_ltp_zip_demand_netcore_3a_test', 'r_pkg_load_summary',
                              'r_pkg_plan_ibv', 'de_slam_packages', 'r_pkg_recve_dvrt_view', 'r_pkg_summary',
                              'r_nasc_pflix_data_hist', 'r_pkg_volume_trend_ibv', 'report_repository',
                              'rs_nasc_vet_vto_opportunities_amt', 'sc_grant_rate_attrition_fcst', 'd_ltp_topline_netcore_1a',
                              'pflix_vs_ssp_summary', 'pflix_vs_pmile_summary', 'na_elm_tracker', 'weather_promise_pads',
                              'd_ltp_ira_netcore_5b_test', 'd_ltp_manual_inputs_hub_test', 'container_state_change_event_na_v1',
                              'dat_sc_ppa_15min_job_roles_employees_v1', 'dat_sc_ppa_15min_job_roles_v1', 'dat_sc_ppa_15min_v1',
                              'errorsformat_conversion_failed', 'ib_vrid_topic_525fb1484a1d70a0121716447087d650',
                              'partition_date_2025_02_05', 'partition_date_2025_02_07',
                              'partition_date_2025_02_07_b01938737a89d519516000778aad6412',
                              'stamp_d_artemis_reg_ira_9664e0697c56b2ddc24a1cc04591cd80', 
                              'vrid_eta_prediction_na_1584b330580dae224d6fb36d0b3b5bef',
                              'lf_testml_test', 'vrid_eta_prediction_na_1584b330580dae224d6fb36d0b3b5bef']
            
            if tableName not in excluded_tables:
                columnList = tableDict['StorageDescriptor']['Columns']
                columnNames = ''
                tagList = tableDict['Parameters']
                
                # Get LastUpdateTime or default to 4 days ago
                if 'LastUpdateTime' in tableDict:
                    MaxRefreshDate = tableDict['LastUpdateTime']
                else:
                    MaxRefreshDate = datetime.datetime.now(tzlocal()) - datetime.timedelta(days=4)
                
                # Try to get crawler info
                try:
                    responseGetCrawlers = crawlerH1.get_crawler(Name=tableName)
                    if 'LastCrawl' in responseGetCrawlers['Crawler']:
                        MaxRefreshDate = responseGetCrawlers['Crawler']['LastCrawl']['StartTime']
                except ClientError:
                    pass
                
                # Try to get partition info
                partitions = ''
                pardate = []
                try:
                    partitions = client.get_partitions(DatabaseName=databaseName, TableName=tableName)
                    partitions = partitions['Partitions']
                except ClientError:
                    pass
                
                # Get max refresh date from partitions
                MaxRefreshDateFromPartition = datetime.datetime(2024, 2, 14, 23, 8, 19, tzinfo=tzlocal())
                if len(partitions) > 0:
                    for par in partitions:
                        pardate.append(par['CreationTime'])
                    
                    if pardate:
                        MaxRefreshDateFromPartition = max(pardate)
                    
                    if MaxRefreshDateFromPartition > MaxRefreshDate:
                        MaxRefreshDate = MaxRefreshDateFromPartition
                
                # Try to get S3 last modified
                try:
                    table_details = client.get_table(DatabaseName=databaseName, Name=tableName)
                    s3_location = table_details['Table']['StorageDescriptor']['Location']
                    
                    s3_last_modified = get_s3_last_modified(s3_location)
                    if s3_last_modified and s3_last_modified > MaxRefreshDate:
                        MaxRefreshDate = s3_last_modified
                except Exception as e:
                    print(f"Error checking S3 metadata for table {tableName}: {str(e)}")
                
                # Format MaxRefreshDate as string
                MaxRefreshDate_str = MaxRefreshDate.strftime("%m/%d/%Y, %H:%M:%S")
                
                # Handle special case for hoot database
                if 'hoot' in databaseName:
                    databaseName = 'andes'
                
                # Process columns
                for column in columnList:
                    columnName = column['Name']
                    columnNames += columnName + ', '
                    
                    # Create column row
                    col_row = ['Huron H2', databaseName, tableName, MaxRefreshDate_str, columnName]
                    for tags, value in tagList.items():
                        if tags in ('sizeKey', 'UPDATED_BY_CRAWLER', 'recordCount', 'classification',
                                   'DescriptionQ', 'Description', 'ExpectedRefreshRate', 'Pipeline', 
                                   'Provider', 'LoadType', 'TeamName'):
                            col_row.append(value)
                    
                    # Add column row
                    column_rows.append(col_row)
                
                # Create table row
                table_row = ['Huron H2', databaseName, tableName, MaxRefreshDate_str, columnNames]
                for tags, value in tagList.items():
                    if tags in ('sizeKey', 'UPDATED_BY_CRAWLER', 'recordCount', 'classification',
                               'DescriptionQ', 'Description', 'ExpectedRefreshRate', 'Pipeline', 
                               'Provider', 'LoadType', 'TeamName'):
                        table_row.append(value)
                
                # Add table row
                table_rows.append(table_row)

# Create Spark DataFrames from collected rows
df = spark.createDataFrame(table_rows, schema=table_schema)
coldf = spark.createDataFrame(column_rows, schema=col_schema)

# Join with dfdyn
df = df.join(dfdyn, df["TableName"] == dfdyn["TableName"], "left").select(
    df["DatabaseName"].alias("DatabaseName_1"),
    df["TableName"],
    df["LastRefreshDate"],
    df["ColumnName"],
    dfdyn["dataset_poc"],
    coalesce(df["Description"], dfdyn["Description"]).alias("Description"),
    coalesce(df["DescriptionQ"], dfdyn["DescriptionQ"]).alias("DescriptionQ"),
    coalesce(df["ExpectedRefreshRate"], dfdyn["ExpectedRefreshRate"]).alias("ExpectedRefreshRate"),
    dfdyn["Pipeline"].alias("pipeline"),
    coalesce(df["Provider"], dfdyn["Provider"]).alias("Provider"),
    coalesce(df["LoadType"], dfdyn["LoadType"]).alias("LoadType"),
    dfdyn["business_line"],
    df["sizeKey"],
    df["recordCount"],
    df["classification"]
)

coldf = coldf.join(dfdyn, coldf["TableName"] == dfdyn["TableName"], "left").select(
    coldf["DatabaseName"].alias("DatabaseName_1"),
    coldf["TableName"],
    coldf["LastRefreshDate"],
    coldf["ColumnName"],
    dfdyn["dataset_poc"],
    coalesce(coldf["Description"], dfdyn["Description"]).alias("Description"),
    coalesce(coldf["DescriptionQ"], dfdyn["DescriptionQ"]).alias("DescriptionQ"),
    coalesce(coldf["ExpectedRefreshRate"], dfdyn["ExpectedRefreshRate"]).alias("ExpectedRefreshRate"),
    dfdyn["Pipeline"].alias("pipeline"),
    coalesce(coldf["Provider"], dfdyn["Provider"]).alias("Provider"),
    coalesce(coldf["LoadType"], dfdyn["LoadType"]).alias("LoadType"),
    dfdyn["business_line"],
    coldf["sizeKey"],
    coldf["recordCount"],
    coldf["classification"]
)

# Rename columns
df = df.select(
    col("DatabaseName_1").alias("DatabaseName"),
    col("TableName"),
    col("LastRefreshDate"),
    col("ColumnName").alias("Columns"),
    col("dataset_poc").alias("DatasetPOC"),
    col("Description"),
    col("DescriptionQ"),
    col("ExpectedRefreshRate"),
    col("pipeline").alias("Pipeline"),
    col("Provider"),
    col("LoadType"),
    col("business_line").alias("TeamName"),
    col("sizeKey").alias("TableSize"),
    col("recordCount").alias("# of Records"),
    col("classification").alias("Type")
)

coldf = coldf.select(
    col("DatabaseName_1").alias("DatabaseName"),
    col("TableName"),
    col("LastRefreshDate"),
    col("ColumnName"),
    col("dataset_poc").alias("DatasetPOC"),
    col("Description"),
    col("DescriptionQ"),
    col("ExpectedRefreshRate"),
    col("pipeline").alias("Pipeline"),
    col("Provider"),
    col("LoadType"),
    col("business_line").alias("TeamName"),
    col("sizeKey").alias("TableSize"),
    col("recordCount").alias("# of Records"),
    col("classification").alias("Type")
)

# Final dataset preparation
andesdf = andesdf.select(
    col("DatabaseName"),
    col("TableName"),
    col("LastRefreshDate"),
    col("Columns"),
    col("DatasetPOC"),
    col("Description"),
    col("ExpectedRefreshRate"),
    col("Pipeline"),
    col("Provider"),
    col("LoadType"),
    col("TeamName"),
    col("TableSize"),
    col("# of Records"),
    col("Type")
)

# Convert LastRefreshDate to timestamp if needed
andesdf = andesdf.withColumn("LastRefreshDate", to_timestamp(col("LastRefreshDate")))

# Union the andesdf and df datasets
finaldf = andesdf.union(df)

# Data cleansing
finaldf = finaldf.withColumn(
    "DatasetPOC", 
    when((col("DatabaseName") == "nasc_analytics_gold") & col("DatasetPOC").isNull(), "ajajha")
    .otherwise(col("DatasetPOC"))
)

# Fill null LoadType values
finaldf = finaldf.withColumn("LoadType", coalesce(col("LoadType"), lit("Full Load")))

# Convert ExpectedRefreshRate to lowercase
finaldf = finaldf.withColumn("ExpectedRefreshRate", 
    when(col("ExpectedRefreshRate").isNotNull(), lower(col("ExpectedRefreshRate")))
    .otherwise(col("ExpectedRefreshRate"))
)

# Drop duplicates
finaldf = finaldf.dropDuplicates(["DatabaseName", "TableName"])

# Write DataFrames to S3
finaldf.write.mode("overwrite").option("header", "true").csv("s3://nasc-de-prod-9024/gold/nasc-udc/andesmerged.csv")
coldf.write.mode("overwrite").option("header", "true").csv("s3://nasc-udc/test/H2UDC_with_columns.csv")
df.write.mode("overwrite").option("header", "true").csv("s3://nasc-udc/test/H2UDC.csv")

# Stop the Spark session
spark.stop()