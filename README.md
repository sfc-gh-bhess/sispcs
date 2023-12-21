# Example Streamlit in Snowpark Conatiner Services
This is a simple Streamlit that can be deployed in 
Snowpark Container Services. It queries the TPC-H 100 
data set and returns the top sales clerks. The Streamlit
provides date pickers to restrict the range of the sales
data and a slider to determine how many top clerks to display.
The data is presented in a table sorted by highest seller
to lowest.

This service will mount 2 stages into the container:
* A directory that has the source code of your Streamlit app. 
  This allows you to make changes to the stage files and have
  the Streamlit app immediately update itself.
* A directory that will host Python packages that you install
  with `pip install`. This allows you to save installed packages
  even if the service is restarted.


# Setup
This example requires importing the `SNOWFLAKE_SAMPLE_DATA`
data share, and an account with Snowpark Container Services
enabled.

## Common Setup
Run the following steps as `ACCOUNTADMIN`.
1. Create a `ROLE` that will be used for Snowpark Container Services administration.
```
CREATE ROLE spcs_role;
GRANT ROLE spcs_role TO ACCOUNTADMIN;
GRANT BIND SERVICE ENDPOINT ON ACCOUNT TO ROLE spcs_role;
```
2. Create a `COMPUTE POOL`.
```
CREATE COMPUTE POOL pool1
    MIN_NODES = 1
    MAX_NODES = 1
    INSTANCE_FAMILY = standard_1;
GRANT USAGE, MONITOR ON COMPUTE POOL pool1 TO ROLE spcs_role;
```
3. Create a `WAREHOUSE` that we'll use in our `SERVICE`.
```
CREATE OR REPLACE WAREHOUSE wh_xs WITH
    WAREHOUSE_SIZE = 'X-SMALL'
    AUTO_SUSPEND = 180
    AUTO_RESUME = TRUE
    INITIALLY_SUSPENDED = FALSE;
GRANT ALL ON WAREHOUSE wh_xs TO ROLE spcs_role;
```
4. Create the necessary `SECURITY INTEGRATION` for Snowpark Container Services.
```
CREATE SECURITY INTEGRATION snowservices_ingress_oauth
    TYPE=oauth
    OAUTH_CLIENT=snowservices_ingress
    ENABLED=true;
```

## Project Setup
1. Use the `SPCS_ROLE`
```
USE ROLE spcs_role;
```
2. Create a `DATABASE` and `SCHEMA` for this use. You can, of course use
  an existing `DATABASE` and `SCHEMA`.
```
CREATE DATABASE sandbox;
CREATE SCHEMA spcs;
USE SCHEMA sandbox.spcs;
```
3. Create the `IMAGE REPOSITORY` and `STAGES` we will need. 
  The `PYTHON_PACKAGES` stage will hold the installed packages. The
  `STREAMLIT_SRC` stage will hold the Jupyter working directory files.
```
CREATE IMAGE REPOSITORY repo1;
CREATE STAGE python_packages 
    DIRECTORY = ( ENABLE = true ) 
    ENCRYPTION = ( TYPE = 'SNOWFLAKE_SSE' );
CREATE STAGE streamlit_src 
    DIRECTORY = ( ENABLE = true ) 
    ENCRYPTION = ( TYPE = 'SNOWFLAKE_SSE' );
```
4. You will need the repository URL for the `IMAGE REPOSITORY`. Run
  the following command and note the value for `repository_url`.
```
SHOW IMAGE REPOSITORIES;
```

## Build the Docker image and upload to Snowflake
1. In the root directory of this repository, run the following command.
```
bash ./configure.sh
```

read -p "What is the image repository URL (SHOW IMAGE REPOSITORIES IN SCHEMA)? " repository_url
read -p "What is the stage location for the Streamlit source? " streamlit_stage
read -p "What is the path to the main file for Strealmit in that stage? " streamlit_main
read -p "What is the path to the requirements file for Strealmit in that stage? " streamlit_requirements
read -p "What warehouse can the Streamlit app use? " warehouse
read -p "What is the stage location for the Python packages? " pythonpath_stage

  When prompted, enter:
  * the `repository_url` for the Image Repository URL
  * the `STAGE` name for the Streamlit source code, e.g., `@SANDBOX.SPCS.STREAMLIT_SRC`.
  * the path in the Streamlit source `STAGE` that has the main Streamlit file, e.g., `app.py`.
  * the path in the STremalit source `STAGE` that has the requirements.txt file, e.g., requirements.txt.
  * the `WAREHOUSE` name that the Streamlit can use, e.g., `wh_xs`
  * the `STAGE` name for the Python packages, e.g., `@SANDBOX.SPCS.PYTHON_PACKAGES`.

  This will create a `Makefile` that can be used to build locally and also
  to build for Snowpark Container Services, including pushing the image to
  the specified image repository. It also creates a `streamlit.yaml` file that is
  the Snowpark Container Services specification file for use when creating the `SERVICE`.
2. Build the image, tag it, and push it to Snowflake.
```
make all
```
3. The `make ddl` command will print a sample SQL DDL statement to create
  the `SERVICE`. You will need to modify the `COMPUTE POOL` name from `your_compute_pool`
  to the name of the `COMPUTE POOL` you would like to use. In our case that 
  would be `POOL1`.

## Create the Service and Grant Access
1. Use the `SPCS_ROLE` and the `DATABASE` and `SCHEMA` we created earlier.
```
USE ROLE spcs_role;
USE SCHEMA sandbox.spcs;
```
2. Use the DDL that was produced by `make ddl`, replacing `POOL1` for the 
  `COMPUTE POOL`:
```
CREATE SERVICE sispcs
    IN COMPUTE POOL pool1
    FROM SPECIFICATION $$
spec:
  containers:
    - name: streamlit
      image: sfsenorthamerica-bmh-prod3.registry.snowflakecomputing.com/sandbox/spcs/repo1/sispcs
      env:
        SNOWFLAKE_WAREHOUSE: wh_xs
        STREAMLIT_REQUIREMENTS: requirements.txt
      args:
        - app.py
      volumeMounts:
        - name: streamlit
          mountPath: /streamlit
        - name: pythonpath
          mountPath: /usr/local/lib/python3.10/site-packages

  endpoints:
    - name: streamlit
      port: 8080
      public: true
  volumes:
    - name: streamlit
      source: "@sandbox.spcs.streamlit_src"
    - name: pythonpath
      source: "@sandbox.spcs.python_packages"
  networkPolicyConfig:
    allowInternetEgress: true
$$;
```
3. See that the service has started by executing `SHOW SERVICES IN COMPUTE POOL pool1` 
  and `SELECT system$get_service_status('sispcs')`.
4. Find the public endpoint for the service by executing `SHOW ENDPOINTS IN SERVICE sispcs`.
5. Grant `USAGE` on the `SERVICE` to other `ROLES` so they can access it: 
  `GRANT USAGE ON SERVICE sispcs TO ROLE some_role`.
  Note that a user needs to have a default `ROLE` _other_ than `ACCOUNTADMIN`,
  `SECURITYADMIN`, or `ORGADMIN` to visit the endpoint for the `SERVICE`.

## Use the Streamlit
1. Navigate to the endpoint and authenticate. Note, you must use a user whose
   default role is _not_ `ACCOUNTADMIN`, `SECURITYADMIN`, or `ORGADMIN`.
2. Enjoy!


## Local Testing
This Streamlit can be tested running locally. To do that, build the
image for your local machine with `make build_local`.

In order to run the Streamlit in the container, we need to set some 
environment variables in our terminal session before running the 
container. The variables to set are:
* `SNOWFLAKE_ACCOUNT` - the account locator for the Snowflake account
* `SNOWFLAKE_USER` - the Snowflake username to use
* `SNOWFLAKE_PASSWORD` - the password for the Snowflake user
* `SNOWFLAKE_WAREHOUSE` - the warehouse to use
* `SNOWFLAKE_DATABASE` - the database to set as the current database (does not really matter that much what this is set to)
* `SNOWFLAKE_SCHEMA` - the schema in the database to set as the current schema (does not really matter that much what this is set to)

Once those have been set, run the Streamlit container with `make run`. Navigate
to `http://localhost:8080`.