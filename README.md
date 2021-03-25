## AWS CloudFormation Resource Provider Package for Amazon Fraud Detector

This repository contains AWS-owned resource providers for the `AWS::FraudDetector::*` namespace.

## Development

#### Requirements
1. Install docker (e.g. install on MacOS with `brew cask install docker`)
2. Install a python environment (python version >= 3.6), I recommend using virtualenvwrapper
    - Optional - create new virtual env: (e.g. `mkvirtualenv frauddetector_cfn`)
3. Clone this repository and `cd` to package root
3. Install dev_requirements: `pip install -r dev_requirements.txt`

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
