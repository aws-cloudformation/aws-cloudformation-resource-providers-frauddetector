## AWS CloudFormation Resource Provider Package for Amazon Fraud Detector

This repository contains AWS-owned resource providers for the `AWS::FraudDetector::*` namespace.

## Development

#### Requirements
1. Install docker (e.g. install on MacOS with `brew cask install docker`)
2. Install AWS SAM CLI, see [the documentation](https://docs.aws.amazon.com/serverless-application-model/latest/developerguide/serverless-sam-cli-install.html) for instructions. (./cfn_server runs `sam local start-lambda`)
3. Install a python environment (python version >= 3.6), I recommend using virtualenvwrapper
    - Optional - create new virtual env: (e.g. `mkvirtualenv frauddetector_cfn`)
4. Clone this repository and `cd` to package root
5. Install dev_requirements: `pip install -r dev_requirements.txt`


#### Creating a New Resource Provider
1. Run mkdir for the new resource provider and cd into it.
2. Run `cfn init` and fill out the prompts for the new provider. Pick python37 as the language, if you'd like to keep things consistent.
3. Edit the generated JSON to have the properties and permissions you need (you can iterate later if need be).
4. Run `cfn validate` in the new resource provider directory to ensure your JSON is valid.
5. Run `cfn generate` in the new resource provider directory to generate some code based on the JSON.
6. Implement handlers, helpers, contract test inputs, and unit tests.
7. Run `pre-commit run --all-files` to make sure the new code is good to commit.
8. Run your changes against unit tests, contract tests, and pre-commit as you iterate and develop!

#### Unit Testing
1. In the package root, run `./run_unit_tests`
2. To view coverage, run `./view_coverage`
    - If that doesn't work, use your browser to open `./htmlcov/index.html`

#### Contract Testing
1. In the package root, run `./cfn_server ${resource_provider}`, where `${resource_provider}` is the resource provider you'd like to test
    - e.g. `./cfn_server outcome`
    - this will use SAM CLI to start a local lambda containing the resource provider
2. In another terminal, cd to the resource provider directory and run `cfn test`
    - to test a single contract test, use `-- -k <test-name>` arguments, e.g. `cfn test -- -k contract_update_list_success`

#### Manual Testing
1. In the root directory, run `./cfn_submit ${resource_provider}` to register the type as a custom resource you can access via CloudFormation, e.g. `./cfn_submit outcome`
2. Use either the AWS CLI or the AWS console to interact with the new custom resource via CloudFormation

## License

This project is licensed under the Apache-2.0 License.
