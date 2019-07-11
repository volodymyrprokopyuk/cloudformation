set -eux

function create_s3_bucket_if_not_exists {
    local s3_bucket_name=${1?ERROR: mandatory S3 bucket name is not provided}

    if aws s3 ls s3://$s3_bucket_name 2>&1 | grep -q 'NoSuchBucket'; then
        aws s3 mb s3://$s3_bucket_name
    fi
}

function get_cf_export_value {
    local export_name=${1?ERROR: mandatory CloudFormation export name is not provided}
    local jq_pattern=".Exports[] | select(.Name | contains(\"$export_name\")).Value"

    aws cloudformation list-exports | jq -r "${jq_pattern}"
}

function get_cf_stack_status {
    local stack_name=${1?ERROR: mandatory stack name is not provided}

    aws cloudformation describe-stacks --stack-name $stack_name \
        | jq -r '.Stacks[0] | .StackStatus'
}

function cf_stack_does_not_exist {
    set +u
    local stack_status=$1
    set -u
    [[ -z $stack_status ]]
}

function is_cf_stack_failed {
    set +u
    local stack_status=$1
    set -u
    [[ $stack_status == *FAILED ]]
}

function is_cf_stack_create_update_complete {
    set +u
    local stack_status=$1
    set -u
    [[ $stack_status == CREATE_COMPLETE || $stack_status == UPDATE_COMPLETE ]]
}

function wait_for_cf_desired_stack_status {
    local stack_name=${1?ERROR: mandatory stack name is not provided}
    local is_cf_stack_in_desired_status=${2?ERROR: mandatory desired stack status is not provided}
    set +u
    # number of attempts before failure
    local attempts=$3
    attempts=${attempts:=60}
    # wait interval in seconds between attempts
    local interval=$4
    interval=${interval:=60}
    set -u

    sleep $interval
    local stack_status=$(get_cf_stack_status $stack_name)
    if is_cf_stack_failed $stack_status; then
        return 1
    fi
    if $is_cf_stack_in_desired_status $stack_status; then
        return 0
    fi
    while [[ $stack_status == *IN_PROGRESS ]] && (( $attempts > 0 )); do
        sleep $interval
        stack_status=$(get_cf_stack_status $stack_name)
        if is_cf_stack_failed $stack_status; then
            return 1
        fi
        if $is_cf_stack_in_desired_status $stack_status; then
            return 0
        fi
        attempts=$(( $attempts - 1 ))
    done
    echo "ERROR: timeout after $attempts attempts with $interval interwal when waiting for desired stack status: $stack_name" >&2
    return 1
}

function delete_cf_stack {
    local stack_name=${1?ERROR: mandatory stack name is not provided}

    local stack_status=$(get_cf_stack_status $stack_name)
    if cf_stack_does_not_exist $stack_status; then
        echo "WARNING: $stack_name stack does not exist. Skipping delete action" >&2
        return 0
    fi
    if is_cf_stack_failed $stack_status; then
        echo "ERROR: $stack_name stack is FAILED: $stack_status. Delete action aborted" >&2
        return 1
    fi
    if is_cf_stack_create_update_complete $stack_status; then
        aws cloudformation delete-stack --stack-name $stack_name
        wait_for_cf_desired_stack_status $stack_name cf_stack_does_not_exist
    fi
}
