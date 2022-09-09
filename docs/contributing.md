# Contributing

This repository is a monorepo for AWS CDK Project Framework projects.

## Requirements

Install the following softwares

- [node.js 16.x](https://nodejs.org/en/download/)
- [poetry](https://pypi.org/project/poetry/1.2.0/)

```shell
pip install poetry==1.2.0
```

> Installation using [pipx](https://pypa.github.io/pipx/installation/) is strongly recommended.

## Install dependencies

```shell
npm install
```

```shell
poetry install
```

## Terminal virtual environment

```shell
poetry shell
```

## Run Flake8 Linting

```shell
npx nx affected:lint
```

or for a specific project

```shell
npx nx lint <appName>
```

## Add new dependency

```shell
npx nx run <appName>:add --name <dependencyName>==<dependencyVersion>
```

Example:

```shell
npx nx run core:add --name requests=2.27.1
```

Using the Nx wrapper to adding a dependency ensure that both root `poetry.lock` and project `poetry.lock` are updated.
