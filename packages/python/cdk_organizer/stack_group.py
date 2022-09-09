"""Base Stack Group module."""

import abc
import dataclasses
import importlib
import inspect
import logging
import os
import sys
from pathlib import Path
from typing import Dict, Generic, Optional, Type, TypeVar, get_args

from cdk_organizer.decorators.catch_exceptions import InfraRuntimeException, catch_exceptions
from cdk_organizer.loaders.config_loader import ConfigLoader
from constructs import IConstruct
from dacite import from_dict

CDK_APP_TYPE = TypeVar('CDK_APP_TYPE', bound=IConstruct)
CDK_CONFIG_TYPE = TypeVar('CDK_CONFIG_TYPE', covariant=True)
CDK_STACK_GROUP_TYPE = TypeVar('CDK_STACK_GROUP_TYPE')


LOGGER = logging.getLogger(__name__)


class StackGroupLoader:
    """
    Loads the stack groups from the stacks directory and synthesizes them into the CDK app.

    This class is passed to all the stack groups and they can use it to load other stacks.

    Args:
        app (CDK_APP_TYPE): The CDK app.

    Attributes:
        app (CDK_APP_TYPE): The CDK app.
        stack_groups (Dict[str, CDK_STACK_GROUP_TYPE]): The stack groups.
    """

    def __init__(self, app: CDK_APP_TYPE) -> None:
        """Stack group loader constructor."""
        self.app = app
        self.stack_groups: Dict[str, CDK_STACK_GROUP_TYPE] = {}
        self._stack_dir = app.node.try_get_context("stacksDirectory") or "stacks"

    def _fullname(self, obj: Type[CDK_STACK_GROUP_TYPE]) -> str:
        """Return the fully qualified name of a class."""
        module = obj.__module__
        if module == 'builtins':
            return obj.__qualname__  # avoid outputs like 'builtins.str'
        return module + '.' + obj.__qualname__

    def synth(self) -> None:
        """Load all the python files from the stacks directory, filters the classes that are `StackGroup` and load the stacks into the CDK app."""
        for file in Path(f'{self._stack_dir}/').rglob("**/*.py"):
            module_name = str(file).replace("/", ".").replace(".py", "")
            spec = importlib.util.spec_from_file_location(module_name, str(file))
            stack_group_module = importlib.util.module_from_spec(spec)
            sys.modules[module_name] = stack_group_module
            spec.loader.exec_module(stack_group_module)

            for _, obj in inspect.getmembers(stack_group_module):
                if not inspect.isabstract(obj) and inspect.isclass(obj) and obj.__base__.__base__ is StackGroup:
                    stack_group_name = self._fullname(obj)
                    if stack_group_name not in self.stack_groups:
                        module_instance = obj(self.app, self)
                        if module_instance.enabled:
                            self.stack_groups[stack_group_name] = module_instance
                            module_instance._load_stacks()

    def resolve_group(self, stack_group_type: Type[CDK_STACK_GROUP_TYPE]) -> CDK_STACK_GROUP_TYPE:
        """
        Resolve a stack group by its type.

        Usage:

        ```python
        self.resolve_group(MyStackGroup)
        ```

        Args:
            stack_group_type (Type[CDK_STACK_GROUP_TYPE]): The stack group type.

        Returns:
            The stack group.
        """
        stack_group_name = self._fullname(stack_group_type)

        if stack_group_name not in self.stack_groups:
            stack_group_instance = stack_group_type(self.app, self)
            self.stack_groups[stack_group_name] = stack_group_instance
            if stack_group_instance.enabled:
                stack_group_instance._load_stacks()

        return self.stack_groups[self._fullname(stack_group_type)]


class StackGroup(
    Generic[CDK_APP_TYPE, CDK_CONFIG_TYPE]
):
    """
    Base Stack Group class.

    This class expects two types as generic arguments:

    - **CDK_APP_TYPE**: The CDK App Type
        - For `aws-cdk` stack group classes, the `app` parameter is the `cdk.App` class.
        - For `cdktf` stack group classes, the `app` parameter is the `cdktf.App` class.

    - **CDK_CONFIG_TYPE**: The Config Dataclass Type

    This class is also a singleton class.

    Usage:
        ### AWS CDK
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
        ### Terraform

        ```python
        import cdktf
        from dataclasses import dataclass
        from cdk_organizer.aws.stack_group import StackGroup

        @dataclass
        class MyStackGroupConfig:
            domain: str
            ipv6: bool = True


        class MyStackGroup(StackGroup[cdktf.App, MyStackGroupConfig]):
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
    """

    @catch_exceptions
    def __init__(
        self,
        app: CDK_APP_TYPE,
        loader: StackGroupLoader
    ) -> None:
        """Initialize the Stack Group."""
        self.app = app
        self._loader = loader
        self.dependencies = []
        self.env = os.getenv("CDK_ENV", None) or app.node.try_get_context("env")
        self.region = app.node.try_get_context("region")
        normalized_module_name = self.__module__.replace(".py", "")
        self.module_name = '.'.join(normalized_module_name.split('.')[:-1])
        self.config, self.enabled = ConfigLoader(self.app, self.env, self.region).load_config(self.module_name)

        config_type = self._resolve_config_type()
        if self.enabled and config_type is not None and dataclasses.is_dataclass(config_type):
            self.data = self._get_data(config_type)

    def resolve_group(self, stack_group_type: Type[CDK_STACK_GROUP_TYPE]) -> CDK_STACK_GROUP_TYPE:
        """
        Resolve a dependent stack group instance.

        Args:
            stack_group_type (Type[CDK_STACK_GROUP_TYPE]): The stack group type.

        Returns:
            The stack group.
        """
        stack_group_instance = self._loader.resolve_group(stack_group_type)
        if stack_group_instance not in self.dependencies:
            self.dependencies.append(stack_group_instance)

        return stack_group_instance

    def _resolve_config_type(self) -> Optional[Type[CDK_CONFIG_TYPE]]:
        if hasattr(self.__class__, '__orig_bases__'):
            bases = self.__class__.__orig_bases__
            if isinstance(bases, tuple) and bases:
                type_args = get_args(bases[0])
                if type_args:
                    return type_args[0]

        return None

    def _get_data(self, config_type: Type[CDK_CONFIG_TYPE]) -> CDK_CONFIG_TYPE:
        try:
            return from_dict(
                data_class=config_type,
                data=self.config
            )
        except Exception as e:
            raise InfraRuntimeException(f"Error on parsing config YAML data for stack group '{self.module_name}', {str(e)}")

    def get_stack_name(self, name: Optional[str] = None, ignore_module_path: bool = False) -> str:
        """
        Generate a stack name based on following pattern.

        **Pattern**: `{module_path}-{name}-{region}-{env}`

        Consider the following example:

        **module_path**: `myproject.myapp.www`
        **name**: `spa`
        **region**: `us-east-1`
        **env**: `dev`

        Stack name will be:

        - `myproject-myapp-www-spa-us-east-1-dev`

        Args:
            name (str, optional): string value to be added between the module path and region + env name.
            ignore_module_path (bool, optional): If True, the module path will be ignored. Defaults to False.

        Returns:
            The stack name.
        """
        module_name = self.normalized_module_name()
        stack_name = ''

        env = self.config.get('env', '')
        region = self.config.get('region', 'us-east-1')
        if not ignore_module_path:
            stack_name = f'{module_name}-'

        if name:
            stack_name += f'{name.lower()}-'

        stack_name += f'{region.lower()}-{env.lower()}'
        return stack_name

    def get_resource_name(
        self,
        name: Optional[str] = None,
        namespace: bool = False,
        database: bool = False,
        use_region: bool = True,
        use_short_region: bool = False,
        ignore_module_path: bool = False
    ) -> str:
        """
        Generate a resource name based on following patterns.

        ### Namespace

        **Pattern**: `{module_path}/{name}/{region}/{env}`

        Consider the following example:

        **module_path**: `myproject.myapp.www`
        **name**: `spa`
        **region**: `us-east-1`
        **env**: `dev`

        The resource name will be:

        - `myproject/myapp/www/spa/us-east-1/dev`

        ### Database

        **Pattern**: `{module_path}_{name}_{env}`

        Consider the following example:

        **module_path**: `myproject.myapp`
        **name**: `raw`
        **env**: `dev`

        The resource name will be:

        - `myproject_myapp_raw_dev`

        Args:
            name (str): string value to be used as the base of the bucket name
            namespace (bool): Use the separator `/` to generate the resource name
            database (bool): Use the separator `_` to generate the resource name
            use_region (bool): Use the region in the resource name, default `true`
            use_short_region (bool): Use the short region in the resource name, default `false`
            ignore_module_path (bool): Ignore the module path in the resource name, default `false`

        Returns:
            resource name
        """
        separator = '-'
        resource_name = ''
        if namespace:
            separator = '/'
        elif database:
            separator = '_'

        module_name = self.normalized_module_name(separator)
        if not ignore_module_path:
            resource_name = f'{module_name.lower()}{separator}'

        env = self.config.get('env')
        region = self.config.get('region')

        if name:
            resource_name += f'{name.lower()}{separator}'

        if database:
            resource_name += f'{env}'
            resource_name = resource_name.replace('-', separator)
        else:
            if use_region:
                if use_short_region:
                    region = self.config.get('short_region')
                resource_name += f'{region}{separator}{env}'
            else:
                resource_name += f'{env}'

        return resource_name

    def normalized_module_name(self, separator: str = '-') -> str:
        """
        Normalize the module name by removing the `stacks` prefix and replacing all dots with a separator.

        Args:
            separator (str): The separator to use, default value: `-`

        Returns:
            The normalized module name.
        """
        return self.module_name.replace("stacks.", "").replace(".", separator).replace("_", '-').lower()

    @abc.abstractmethod
    def _load_stacks(self) -> None:
        """Load stacks."""
