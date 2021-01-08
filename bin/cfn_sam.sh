#!/usr/bin/env sh

# Use this script to run a sam local lambda serving CFN resource provider handlers
# run `cfn test` in a separate window to run contract tests against the local lambda
# note: you can run `cfn test -- -k <test-name>` to run a single test, e.g. `cfn test -- -k contract_delete_list`

printf "\r\n ~ Validating and generating json, then preparing and starting cfn lambda for local testing ~ \r\n"

if [ $# -eq 1 ]
then
  PATH_TO_RP="$1"
  cd "$PATH_TO_RP" || exit
  printf "\r\nvalidating resource provider json ...\r\n"
  cfn validate
  printf "\r\ngenerating code from resource provider json ...\r\n"
  cfn generate
  printf "\r\nrunning pre-commit ...\r\n"
  pre-commit run --all-files
  printf "\r\nrunning pre-commit again ...\r\n"
  pre-commit run --all-files
  printf "\r\nsubmitting cfn dry run ...\r\n"
  cfn submit --dry-run
  printf "\r\nstarting sam local lambda ...\r\n"
  sam local start-lambda
else
  printf "\r\nYou need to supply the path to the resource provider you'd like to start for testing, "
  printf "as well as the name of the resource.\r\n"
  printf "\r\nexample command if you are in this package's root directory:\r\nbash ./bin/cfn_sam.sh "
  printf "aws-frauddetector-outcome\r\n\r\n"
fi
