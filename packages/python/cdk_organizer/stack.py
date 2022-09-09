"""Base CDK Stack module."""

import logging
from typing import TYPE_CHECKING, Optional

if TYPE_CHECKING:
    from cdk_organizer.aws.stack_group import StackGroup

from cdk_organizer.decorators.catch_exceptions import catch_exceptions


class BaseStack(object):
    """
    Base class for any CDK Stack classes.

    Features:
        - Logging
        - Configuration in dict and dataclass formats
        - Environment properties
        - Utils for generating bucket and general resources names
    """

    @catch_exceptions
    def __init__(
        self,
        stack_name: str,
        stack_group: "StackGroup"
    ) -> None:
        """Initialize the class."""
        self._stack_name = stack_name
        self.stack_group = stack_group
        self.config = stack_group.config

        if hasattr(self.stack_group, 'data'):
            self.data = self.stack_group.data

        self.logger = logging.getLogger(__name__)
        self.env_props = self._get_aws_environment_props(self.config)

    @property
    def env_name(self) -> str:
        """Get the environment name."""
        return self.config.get('env')

    def _get_aws_environment_props(self, config: dict) -> dict:
        """
        Get AWS environment properties from the config YAML file.

        Args:
            config dict: environment config data

        Returns:
            account/region mapping
        """
        env_props = None

        if 'account' in config and 'region' in config:
            env_props = {
                'account': config['account'],
                'region': config['region']
            }

        return env_props

    def get_bucket_name(
        self,
        name: str,
        include_path_naming: bool = True
    ) -> str:
        """
        Generate a bucket name based on following pattern.

        **Pattern**: `{base_naming}-{module_path}-{name}-{region}-{env}`

        The `{base_naming}` is configured in the `config.yaml`, property `baseBucket`.

        Consider the following example:

        **base_naming**: `mycompany`
        **module_path**: `myproject.myapp.www`
        **name**: `spa`
        **region**: `us-east-1`
        **env**: `dev`

        The bucket name will be:

        - `mycompany-myproject-myapp-www-spa-us-east-1-dev`

        Args:
            name (str): string value to be used as the base of the bucket name
            include_path_naming (bool): include the module path in the bucket name

        Returns:
            bucket name
        """
        bucket_name = self.config.get('base_bucket', '')
        if bucket_name != '':
            bucket_name += '-'

        module_name = self.stack_group.normalized_module_name()

        env = self.config.get('env', None)
        region = self.config.get('region', None)

        if include_path_naming:
            bucket_name += f'{module_name}-'

        if name:
            bucket_name += f'{name.lower()}-'

        bucket_name += f"{region}-{env}"
        return bucket_name

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
        return self.stack_group.get_resource_name(
            name=name,
            namespace=namespace,
            database=database,
            use_region=use_region,
            use_short_region=use_short_region,
            ignore_module_path=ignore_module_path
        )
