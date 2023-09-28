# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.10.0] - 2023-09-28

### Added

- Added `!include_pattern` YAML tag to support including multiple YAML files using glob patterns.

`a.yaml`

```yaml
b: !include_pattern '*.yaml'
```

`b.yaml`

```yaml
key: value
```

`a.yaml` will be rendered as:

```yaml
b:
  - key: value
```

The `!include_pattern` also supports `params` to pass to the included YAML files.

```yaml
b: !include_pattern
  pattern: '*.yaml'
  params:
    KEY: VALUE
```

## [1.9.0] - 2023-09-25

### Changed

- Changed `!include` YAML tag to support Jinja2 templating.

`a.yaml`

```yaml
b: !include
  path: b.yaml
  params:
    key: value
```

`b.yaml`

```yaml
key: {{ key }}
```

`a.yaml` will be rendered as:

```yaml
b:
  key: value
```

## [1.8.2] - 2023-09-25

### Fixed

- Fix `!merge` YAML tag to work with nested YAML anchors and aliases from `!include` YAML tag.

## [1.8.1] - 2023-09-25

### Fixed

- Support recursive `!include` YAML tag.

## [1.8.0] - 2023-09-25

### Added

- Preserve the YAML anchors and aliases when using `!include` YAML tag.

## [1.7.0] - 2023-09-22

### Added

- Added `!include` YAML tag to include YAML files from other YAML config files.

## [1.6.0] - 2023-08-02

### Changed

- Add python 3.10 support.
- Update CDKTF version to `^0.17.0`.

## [1.5.0] - 2023-06-02

### Changed

- Update `normalized_module_name` to parameterize to ignore or not the stacks module prefix, default to `false`.

## [1.4.0] - 2023-03-16

### Changed

- Update CDKTF version to 0.15.5 (latest).

## [1.3.1] - 2022-09-13

### Fixed

- Fix terraform S3 backend documentation.

## [1.3.0] - 2022-09-13

### Changed

- Move S3 Backend properties from context to config.

## [1.2.0] - 2022-09-09

### Nonfunctional

- Update documentation to include package extras and context variables.

## [1.1.0] - 2022-09-09

### Nonfunctional

- Update documentation to include CDK start script example.

## [1.0.0] - 2022-08-29

### Added

- Initial project version.
