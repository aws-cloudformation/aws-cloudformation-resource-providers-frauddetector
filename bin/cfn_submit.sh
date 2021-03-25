#!/usr/bin/env sh

# Use this script to submit a CFN resource provider

printf "\r\n ~ Validating resouce provider json and submitting to CFN registry ~ \r\n"

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
  if [ $? -ne 0 ]
  then
    printf "\r\nERROR - pre-commit needs to pass!\r\n"
    exit 1
  fi
  printf "\r\nsubmitting cfn and setting to default for this resource provider ...\r\n"
  cfn submit --set-default
else
  printf "\r\nYou need to supply the path to the resource provider you'd like to submit, "
  printf "as well as the name of the resource.\r\n"
  printf "\r\nexample command if you are in this package's root directory:\r\nbash ./bin/cfn_submit.sh "
  printf "aws-frauddetector-outcome\r\n\r\n"
fi
