#!/usr/bin/env node
import 'tsconfig-paths/register'

import * as cdk from 'aws-cdk-lib';
import { StackGroupLoader } from "@awslv/cdk-organizer-core";

const app = new cdk.App();
const loader = new StackGroupLoader(app)

loader.synth().then(() => console.log("Stack Groups Synthesized"));
