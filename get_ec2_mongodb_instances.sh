curr_date_time=$(date +'%Y-%m-%d-%H-%M-%S')
file_name="ssm_send_command_output_${curr_date_time}"
sh_command_id=$(aws ssm send-command \
    --targets "Key=tag:YOUR_TAG_KEY,Values=YOUR_TAG_VALUE" \
    --document-name "AWS-RunShellScript" \
    --comment "MongoDB find version script on Linux Instances" \
    --parameters '{"executionTimeout":["3600"],"commands":["mongod --version"]}' \
    --timeout-seconds 3600 --max-concurrency "50" --max-errors "50" \
    --output text \
    --query "Command.CommandId"
 )

echo "send-command id=${sh_command_id}"
echo "send-command output will be stored in file = ${file_name}"

# sleep for 120 seconds so ssm_send command gets completed
sleep 120

aws ssm list-command-invocations \
    --command-id $sh_command_id \
    --details \
    --query "[CommandInvocations[]]">$file_name


python3 mongo-parse-ssm-json-new.py $file_name


