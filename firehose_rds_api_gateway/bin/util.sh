# shellcheck disable=SC2148
set $SETOPTS

function setup_virtual_environment {
    local pyvenv=${1?ERROR: mandatory virtual environment name is not provided}
    local install_test_deps=${2:-}

    if [[ ! -d $pyvenv ]]; then
        python -m venv $pyvenv
        set +x
        # shellcheck disable=SC1090
        source $pyvenv/bin/activate
        set -x
        pip install -r requirements.txt
        if [[ -n $install_test_deps ]]; then
           pip install -r requirements.test.txt
        fi
    else
        set +x
        # shellcheck disable=SC1090
        source $pyvenv/bin/activate
        set -x
    fi
}

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
    [[ $stack_status == CREATE_COMPLETE || $stack_status == UPDATE_COMPLETE \
        || $stack_status == UPDATE_ROLLBACK_COMPLETE ]]
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

    sleep 5
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
    echo "ERROR: $stack_name is not in the desired status" >&2
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

function create_ssh_tunnel {
    local local_port=${1?ERROR: mandatory local port is not provided}
    local remote_host=${2?ERROR: mandatory remote host is not provided}
    local remote_port=${3?ERROR: mandatory remote port is not provided}
    local bastion_user=${4?ERROR: mandatory bastion user is not provided}
    local bastion_host=${5?ERROR: mandatory bastion host is not provided}

    # ssh -A -f -N -L $local_port:$remote_host:$remote_port $bastion_user@$bastion_host
    ssh -A -f -N -L $local_port:$remote_host:$remote_port -J 85.184.254.193 $bastion_user@$bastion_host
}


function destroy_ssh_tunnel {
    local local_port=${1?ERROR: mandatory local port is not provided}
    local remote_host=${2?ERROR: mandatory remote host is not provided}
    local remote_port=${3?ERROR: mandatory remote port is not provided}
    local bastion_user=${4?ERROR: mandatory bastion user is not provided}
    local bastion_host=${5?ERROR: mandatory bastion host is not provided}

    local ssh_tunnel_pattern="ssh.*$local_port:$remote_host:$remote_port.*$bastion_user@$bastion_host"
    pkill -f "${ssh_tunnel_pattern}"
}

function is_ssh_tunnel_created {
    local local_port=${1?ERROR: mandatory local port is not provided}
    local remote_host=${2?ERROR: mandatory remote host is not provided}
    local remote_port=${3?ERROR: mandatory remote port is not provided}
    local bastion_user=${4?ERROR: mandatory bastion user is not provided}
    local bastion_host=${5?ERROR: mandatory bastion host is not provided}

    local ssh_tunnel_pattern="ssh.*$local_port:$remote_host:$remote_port.*$bastion_user@$bastion_host"
    pgrep -f "${ssh_tunnel_pattern}"
}

function create_ssh_tunnel_if_not_exists {
    local local_port=${1?ERROR: mandatory local port is not provided}
    local remote_host=${2?ERROR: mandatory remote host is not provided}
    local remote_port=${3?ERROR: mandatory remote port is not provided}
    local bastion_user=${4?ERROR: mandatory bastion user is not provided}
    local bastion_host=${5?ERROR: mandatory bastion host is not provided}

    if ! is_ssh_tunnel_created \
        $local_port $remote_host $remote_port $bastion_user $bastion_host; then
        create_ssh_tunnel $local_port $remote_host $remote_port $bastion_user $bastion_host
    fi
}

function destroy_ssh_tunnel_if_exists {
    local local_port=${1?ERROR: mandatory local port is not provided}
    local remote_host=${2?ERROR: mandatory remote host is not provided}
    local remote_port=${3?ERROR: mandatory remote port is not provided}
    local bastion_user=${4?ERROR: mandatory bastion user is not provided}
    local bastion_host=${5?ERROR: mandatory bastion host is not provided}

    if is_ssh_tunnel_created \
        $local_port $remote_host $remote_port $bastion_user $bastion_host; then
        destroy_ssh_tunnel $local_port $remote_host $remote_port $bastion_user $bastion_host
    fi
}
