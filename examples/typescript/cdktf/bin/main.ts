#!/usr/bin/env node
import 'tsconfig-paths/register';

import { App } from 'cdktf';
import { StackGroupLoader } from '@awslv/cdk-organizer-core';

const app = new App();
const loader = new StackGroupLoader(app);

loader.synth().then(() => {
  app.synth();
});
