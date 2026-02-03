
CREATE TABLE databricks_auth_metrics (
	metric STRING, 
	enum_name STRING, 
	enum_value STRING, 
	bucket_le DOUBLE, 
	value DOUBLE
) USING DELTA
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'enabled')



CREATE TABLE databricks_list_roles (
	role_name STRING, 
	identity_type STRING
) USING DELTA
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'enabled')



CREATE TABLE databricks_synced_table_managers (
	schema_name STRING, 
	table_name STRING, 
	user_name STRING
) USING DELTA
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'enabled')



CREATE TABLE help_ticket (
	ticket_id STRING, 
	customer_id STRING, 
	subject STRING, 
	status STRING, 
	created_at TIMESTAMP, 
	resolved_at TIMESTAMP
) USING DELTA
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'enabled')



CREATE TABLE refund_requests (
	refund_id STRING, 
	ticket_id STRING, 
	payment_id STRING, 
	sku STRING, 
	request_date TIMESTAMP, 
	approved BOOLEAN, 
	approval_date TIMESTAMP
) USING DELTA
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'enabled')



CREATE TABLE stripe_payments (
	payment_id STRING, 
	customer_id STRING, 
	amount_cents INT, 
	currency STRING, 
	payment_status STRING, 
	payment_date TIMESTAMP
) USING DELTA
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'enabled')



CREATE TABLE warehouse_inventory (
	sku STRING, 
	warehouse_id STRING, 
	quantity INT, 
	last_updated TIMESTAMP
) USING DELTA
TBLPROPERTIES('delta.feature.allowColumnDefaults' = 'enabled')

