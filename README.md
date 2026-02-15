# Conversational Agent App

### Main Dashboard
![](./assets/crud_app_dashboard.png)

### Refunds Page
![](./assets/crud_app_refunds.png)

### Chat LLM Interface
![](./assets/crud_app_chat.png)

This repository demonstrates how to build custom Databricks Apps applications integrating Databricks' Lakebase (OLTP database) and querying Foundation Model LLM APIs on Databricks, allowing users to securely add, edit and delete and run LLM queries on records stored in Databricks.

## Prerequisites

- A Databricks workspace with a [Lakebase database instance](https://docs.databricks.com/aws/en/database/lakebase/)
- [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install) installed and authenticated
- Python 3.11+

## Local Development

1. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

2. Authenticate with your Databricks workspace using OAuth U2M via the CLI:

   ```bash
   databricks auth login --host https://<your-workspace>.cloud.databricks.com
   ```

3. Set the required PostgreSQL environment variables to connect to your Lakebase instance:

   ```bash
   export PGHOST="<your-lakebase-host>"
   export PGDATABASE="databricks_postgres"
   export PGPORT="5432"
   export PGUSER="<your-databricks-username>"
   ```

4. Start the app:

   ```bash
   reflex run
   ```

   The required database tables (`help_ticket`, `refund_requests`, `stripe_payments`) are created automatically on first startup if they don't already exist.

## Deploy to Databricks Apps

This app is designed to be deployed to [Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/) directly from a Git repository.

1. **Create the app** in your Databricks workspace:
   - Via UI: go to **Compute > Apps > Create app**
   - Or via CLI: `databricks apps create <your-app-name>`

2. **Add a Lakebase database resource** to the app. This is required for the app to connect to the database.
   - Go to **Compute > Apps > your app > Configure > Add resource > Database**
   - Select your Lakebase database instance and database
   - This automatically sets the PG* environment variables (`PGHOST`, `PGDATABASE`, `PGPORT`, `PGUSER`, `PGSSLMODE`) and grants the app's service principal `CONNECT` and `CREATE` privileges on the database
   - See [Add a Lakebase resource to a Databricks app](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/lakebase)

3. **Configure the Git repository**:
   - In the app configuration, enter the Git repository URL and select your Git provider
   - For private repositories, configure a Git credential for the app's service principal
   - See [Deploy a Databricks app](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/deploy)

4. **Deploy**:
   - Click **Deploy > From Git**, then select the branch, tag, or commit to deploy
   - The app runs using the command defined in `app.yaml`

   Databricks authentication and PG* environment variables are handled automatically by the platform. Database tables are created on first startup.

## Project Structure

```
app/
  app.py            # Reflex app definition and page routes
  db.py             # Database connection pool and schema initialization
  components/       # UI components (sidebar, views, charts)
  states/           # Reflex state classes (dashboard, tickets, refunds, payments, chat)
assets/             # Images and static files
app.yaml            # Databricks Apps deployment configuration
rxconfig.py         # Reflex framework configuration
requirements.txt    # Python dependencies
```
