# Conversational Agent Reflex App

### Main Dashboard
![](./assets/crud_app_dashboard.png)

### Refunds Page
![](./assets/crud_app_refunds.png)

### Chat LLM Interface
![](./assets/crud_app_chat.png)

This repository demonstrates how to build custom Databricks Apps applications using [Reflex](https://reflex.dev/), integrating Databricks' Lakebase (OLTP database) and querying Foundation Model LLM APIs on Databricks, allowing users to securely add, edit and delete and run LLM queries on records stored in Databricks.

## Prerequisites

- A Databricks workspace with a [Lakebase database instance](https://docs.databricks.com/aws/en/oltp/instances/about)
- [Databricks CLI](https://docs.databricks.com/aws/en/dev-tools/cli/install) installed and authenticated
- [uv](https://docs.astral.sh/uv/getting-started/installation/) (recommended) or pip
- Python 3.11+

## Local Development

1. Create a virtual environment and install dependencies:

   ```bash
   uv venv --python 3.11
   source .venv/bin/activate
   uv pip install -r requirements.txt
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

This app is designed to be deployed to [Databricks Apps](https://docs.databricks.com/aws/en/dev-tools/databricks-apps/) directly from a Git repository. You can point your Databricks App to this repository directly, or fork it to customize the app and deploy from your own repo.

1. **Create the app and add a Lakebase database resource**:
   - Via UI: go to **Compute > Apps > Create app**. During app creation, add a Lakebase database resource under **App resources > Add resource > Database**. Select your database instance and database.
   - Or via CLI: `databricks apps create <your-app-name>`
   - For an existing app, go to **Compute > Apps > your app** and click **Edit** to add the database resource.
   - Adding a Lakebase resource automatically sets the PG* environment variables (`PGHOST`, `PGDATABASE`, `PGPORT`, `PGUSER`, `PGSSLMODE`) and grants the app's service principal `CONNECT` and `CREATE` privileges on the database.
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
