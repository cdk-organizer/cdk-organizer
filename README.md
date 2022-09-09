# AWS CDK Project Framework

Nx Monorepo for CDK Infra projects.

- Flake8 linting
- Python import sorting
- Poetry

Documentation: <https://cdk-organizer.github.io/>

## Getting Started

This repository is a monorepo for AWS CDK Project Framework projects.

### Requirements

Install the following softwares

- [node.js 16.x](https://nodejs.org/en/download/)
- [poetry](https://pypi.org/project/poetry/1.2.0/)

```shell
pip install poetry==1.2.0
```

> Installation using [pipx](https://pypa.github.io/pipx/installation/) is strongly recommended.

### Install dependencies

```shell
npm install
```

```shell
poetry install
```

### Terminal virtual environment

```shell
poetry shell
```

### Run Flake8 Linting

```shell
npx nx affected:lint
```

or for a specific project

```shell
npx nx lint <appName>
```

### Add new dependency

```shell
npx nx run <appName>:add --name <dependencyName>==<dependencyVersion>
```

Using the Nx wrapper to adding a dependency ensure that both root `poetry.lock` and project `poetry.lock` are updated.

### Packages

- [CDK Organizer for Python](packages/python/README.md)
- [AWS CDK Organizer for TypeScript](packages/typescript/aws/README.md)
- [Terraform for CDK Organizer for TypeScript](packages/typescript/terraform/README.md)

### Examples

#### Python

- [AWS CDK](packages/examples/python/aws-cdk/README.md)
- [Terraform for CDK](packages/examples/python/cdktf/README.md)

#### TypeScript

- [AWS CDK](packages/examples/typescript/aws-cdk/README.md)
- [Terraform for CDK](packages/examples/typescript/cdktf/README.md)

### [Changelog](CHANGELOG.md)
