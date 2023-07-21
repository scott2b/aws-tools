# aws-tools
Tools that I use for working with AWS during development

This codebase serves as a reference library and basic toolbox for getting things done in
AWS with Python. As just a command-line toolkit, if that is what you need, you will be
better served by [the AWS CLI](https://aws.amazon.com/cli/) which is designed for that
purpose.

This also does not replace provisioning, infrastructure-as-code, and cloud resource
management tools. For those things, I highly recommend [HashiCorp's Terraform](https://www.terraform.io/).

The purpose here is more along the lines of exposing the things I do regularly in Python
projects as tools, while also providing a reference implementation for using AWS with
Python and boto3.


## Getting started

To use localstack for development:

```
docker compose up
```

### Using Localstack Pro

**Note:** Cognito is a **pro** feature for localstack. Localstack Pro starts at
[$35 per month](https://localstack.cloud/pricing/) for a single-user license.


Set these environment variables:

 - `LOCALSTACK_IMAGE=localstack-pro`
 - `LOCALSTACK_API_KEY=<your-api-key>`

Then bring up localstack as usual:

```
docker compose up
```

### Using AWS

Alternatively, just use a real AWS account. There is a pretty good free tier for a lot of things.

Config stuff TBD


## The toolkit

 - **Cognito** This is the primary focus of what is currently in development

Hopefully, more to come. S3 is the most likely thing on deck.


## Using the toolkit

Install dependencies:

```
pip install -r requirements.txt
```

Put `src` on your `PYTHONPATH`

```
export PYTHONPATH=src:PYTHONPATH
```

### General help

```
python -m awstools --help
```

### cognito

```
python -m awstools cognito --help
```

## Contributing

Install development dependencies

```
pip install -r requirements-dev.txt
```

Run tests

```
tox
```
