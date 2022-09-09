"""AWS CDK Startup Module."""


import aws_cdk as cdk
from cdk_organizer.miscellaneous.logging import setup_logging
from cdk_organizer.stack_group import StackGroupLoader

app = cdk.App()
logger = setup_logging(__name__, app.node.try_get_context("loglevel") or "INFO")
loader = StackGroupLoader(app)

loader.synth()
app.synth()
