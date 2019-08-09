# Infringement data import

[Documentation](https://atlassian.hq.k.grp/confluence/pages/viewpage.action?pageId=134659302)

## How to validate, unit/integration test, deploy, e2e/smoke test, use, and undeploy the aplication

```bash
# Validate Bash scripts, CloudFormation teamplates, Python code and tests
./bin/validate.sh
# Unit test transformation lambdas
./bin/unit_test.sh
# Integration test transformation lambdas
./bin/integration_test.sh
# Deploy all stacks of the infirngement data import application
./bin/deploy_application.sh infringement-all
# Create the database scheme of the infirngement data import application
./bin/create_db_schema.sh
# Migrate the database scheme of the infirngement data import application
./bin/migrate_db_schema.sh
# End-to-end test the infirngement data import application
./bin/e2e_test.sh
# Smoke test the infirngement data import application
./bin/smoke_test.sh
# Send test data to the corresponding Kinesis Firehose delivery streams
./bin/send_data_to_firehose.sh
# Undeploy the infirngement data import application
./bin/undeploy_application.sh -y
```
