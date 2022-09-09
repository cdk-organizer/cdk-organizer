import {
  BaseConfig,
  StackGroup as BaseStackGroup,
  StackGroupLoader,
} from '@awslv/cdk-organizer-core';
import { App } from 'cdktf';

export class StackGroup<
  ConfigType extends BaseConfig = BaseConfig
> extends BaseStackGroup<App, ConfigType> {
  constructor(app: App, loader: StackGroupLoader, module: string) {
    super(app, loader, module);
  }
}
