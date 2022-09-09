# CDK Organizer Python Library

This library contains the core features to handle CDK projects including:

- Logging
- Configuration Resolver
- Stack Groups Loader
- Naming Utils

## Installation

```bash
pip install cdk-organizer
```

## Project Structure

To apply the pattern purposed in this library for CDK projects, the following structure is required:

```text
.
+-- cdk.json
+-- app.py
```

### Stack Structure

the stack class needs to inherit from class `cdk_organizer.aws.stack.Stack` for AWS CDK and `cdk_organizer.terraform.stack.Stack` for Terraform CDK.

#### AWS CDK

```python
from constructs import Construct
from cdk_organizer.aws.stack import Stack
from cdk_organizer.aws.stack_group import StackGroup


class MyStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_group: StackGroup,
        **kwargs
    ) -> None:
        super().__init__(scope, id, stack_group, **kwargs)
```

#### Terraform CDK

```python
from constructs import Construct
from cdk_organizer.terraform.stack import Stack
from cdk_organizer.terraform.stack_group import StackGroup


class MyStack(Stack):
    def __init__(
        self,
        scope: Construct,
        id: str,
        stack_group: StackGroup,
        **kwargs
    ) -> None:
        super().__init__(scope, id, stack_group, **kwargs)
```

#### Using S3 Backend

To use S3 terraform backend, the following resources are required:

- S3 Bucket
- DynamoDB Table

Modify the `cdktf.json` to add the following object:

```json
{
  ...
  "context": {
    ...
    "s3Backend": {
      "bucket": "<bucket-name>",
      "region": "<aws-region>",
      "dynamodb_table": "<dynamodb-table-name>"
    }
    ...
  }
  ...
}
```

### Stack Group Structure

Create a `stacks` folder in the root of the project and structure it as follows:

```text
.
+-- cdk.json
+-- app.py
+-- stacks/
| +-- <groupName>/
|   +-- stacks.py
```

The stack groups files follow this pattern:

#### AWS CDK

```python
import aws_cdk as cdk
from dataclasses import dataclass
from cdk_organizer.aws.stack_group import StackGroup

@dataclass
class MyStackGroupConfig:
    domain: str
    ipv6: bool = True


class MyStackGroup(StackGroup[MyStackGroupConfig]):
    def _load_stacks(self) -> None:
        MyStack(
            self.app,
            self.get_stack_name('my-stack'),
            stack_group=self,
            parameters=MyStackParameters(
                domain=self.data.domain,
                ipv6=self.data.ipv6
            )
        )
```

#### Terraform

```python
import cdktf
from dataclasses import dataclass
from cdk_organizer.terraform.stack_group import StackGroup

@dataclass
class MyStackGroupConfig:
    domain: str
    ipv6: bool = True


class MyStackGroup(StackGroup[MyStackGroupConfig]):
    def _load_stacks(self) -> None:
        MyStack(
            self.app,
            self.get_stack_name('my-stack'),
            stack_group=self,
            parameters=MyStackParameters(
                domain=self.data.domain,
                ipv6=self.data.ipv6
            )
        )
```

#### Using Stack Attributes from Other Stack Groups

In some cases, you may want to use the attributes of another stack group. For example, refer the DNS Hosted Zone created by a shared stack group.

To resolve the group use the `self.resolve_group` function in the stack group class, like the example below:

```python
import aws_cdk as cdk
from dataclasses import dataclass
from cdk_organizer.aws.stack_group import StackGroup
from stacks.dns import DNSStackGroup

@dataclass
class MyStackGroupConfig:
    domain: str
    ipv6: bool = True


class MyStackGroup(StackGroup[MyStackGroupConfig]):
    def _load_stacks(self) -> None:
        MyStack(
            self.app,
            self.get_stack_name('my-stack'),
            stack_group=self,
            parameters=MyStackParameters(
                domain=self.data.domain,
                zone=self.resolve_group(DNSStackGroup).zone
                ipv6=self.data.ipv6
            )
        )
```

The function `get_stack_name` generates the stack name based on following pattern.

**Pattern**: `{module_path}-{name}-{region}-{env}`

Consider the following example:

**module_path**: `myproject.myapp.www`
**name**: `spa`
**region**: `us-east-1`
**env**: `dev`

Stack name will be:

- `myproject-myapp-www-spa-us-east-1-dev`.

### Config Structure

Create a `config` folder in the root of the project and structure it as follows:

```text
.
+-- cdk.json
+-- app.py
+-- config/
| +-- <env>/
|   +-- config.yaml
|   +-- <region>/
|     +-- config.yaml
|     +-- <groupName>/
|         +-- config.yaml
```

The first two levels are reserved to the environment name and the region name, the next levels needs to match the stack group structure.

Example:

```text
.
+-- cdk.json
+-- app.py
+-- config/
| +-- config.yaml
| +-- dev/
|   +-- config.yaml
|   +-- us-east-1/
|     +-- config.yaml
|     +-- app1/
|       +-- config.yaml
+-- stacks/
| +-- app1/
|   +-- stacks.py
+-- templates/
|   +-- stacks/
```

### Examples

- [AWS CDK](https://github.com/lucasvieirasilva/cdk-organizer/tree/main/examples/python/aws-cdk)
- [CDK for Terraform](https://github.com/lucasvieirasilva/cdk-organizer/tree/main/examples/python/cdktf)