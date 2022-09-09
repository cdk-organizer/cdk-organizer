"""CDK Infrastructure Core Module."""

import yaml
from cdk_organizer.miscellaneous.yaml_tags.merge_yaml import construct_merge

yaml.add_constructor('!merge', construct_merge, yaml.SafeLoader)
