function create_s3_bucket_if_not_exists {
    local s3_bucket_name=${1?ERROR: mandatory S3 bucket name is not provided}

    if aws s3 ls s3://$s3_bucket_name 2>&1 | grep -q 'NoSuchBucket'; then
        aws s3 mb s3://$s3_bucket_name
    fi
}

function get_cf_export_value {
    local export_name=${1?ERROR: mandatory export name is not provided}
    local jq_pattern=".Exports[] | select(.Name | contains(\"$export_name\")).Value"

    aws cloudformation list-exports | jq -r "${jq_pattern}"
}
