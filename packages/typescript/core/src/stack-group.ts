import { IConstruct } from 'constructs';
import { ConfigLoader } from './config/loader';
import * as glob from 'glob';
import { InfraRuntimeError } from './error/infra-runtime-error';
import { dirname, join, relative, resolve } from 'path';
import * as _ from 'lodash';

type GenericStackGroup<
  TApp extends IConstruct,
  TStackGroup extends StackGroup
> = {
  new (app: TApp, loader: StackGroupLoader, module: string): TStackGroup;
  getFilePath(): string;
};

export class StackGroupLoader {
  stackGroups: { [name: string]: StackGroup } = {};
  public stacksDir: string;

  constructor(public app: IConstruct) {
    this.stacksDir = this.app.node.tryGetContext('stacksDir') ?? 'stacks';
  }

  async synth() {
    const files = glob.sync(`${this.stacksDir}/**/*.ts`);

    for (const file of files) {
      if (this.stackGroups[file] !== undefined) {
        continue;
      }

      const absPath = resolve(file);
      await this.loadModule(absPath);
    }
  }

  private async loadModule(absPath: string): Promise<boolean> {
    const module = await import(absPath);
    const members = Object.keys(module);
    for (const memberName of members) {
      const member = module[memberName];
      if (member && member.prototype instanceof StackGroup) {
        const stackGroup = this.stackGroups[absPath];
        if (stackGroup === undefined) {
          const stackGroup = new member(this.app, this, absPath) as StackGroup;
          if (stackGroup.enabled) {
            this.stackGroups[absPath] = stackGroup;
            await stackGroup.loadStacks();
            return true;
          } else {
            return false;
          }
        }
        return stackGroup.enabled;
      }
    }
    return false;
  }

  async resolveGroup<TApp extends IConstruct, TStackGroup extends StackGroup>(
    ctor: GenericStackGroup<TApp, TStackGroup>
  ): Promise<TStackGroup> {
    const absPath = ctor.getFilePath();
    await this.loadModule(absPath);
    return this.stackGroups[resolve(absPath)] as TStackGroup;
  }
}

export type BaseConfig = {
  env: string;
  region: string;
  account: string;
  shortRegion?: string;
}

export class StackGroup<
  AppType extends IConstruct = IConstruct,
  ConfigType extends BaseConfig = BaseConfig
> {
  dependencies: StackGroup[] = [];
  env: string;
  region: string;
  config: Record<string, unknown>;
  enabled: boolean;
  data: ConfigType;

  constructor(
    public app: AppType,
    public loader: StackGroupLoader,
    public module: string
  ) {
    this.env = app.node.tryGetContext('env');
    this.region = process.env['CDK_ENV'] ?? app.node.tryGetContext('region');

    const configLoader = new ConfigLoader(this.app, this.env, this.region);

    const { config, enabled } = configLoader.loadConfig(this.module);
    if (_.isNil(config['env'])) {
      throw new InfraRuntimeError(
        `The 'env' key is missing in the config`
      )
    }

    if (_.isNil(config['region'])) {
      config['region'] = process.env['CDK_DEFAULT_REGION']
    }

    if (_.isNil(config['account'])) {
      config['account'] = process.env['CDK_DEFAULT_ACCOUNT']
    }

    this.config = config;
    this.enabled = enabled;
    this.data = this.config as ConfigType;
  }

  async loadStacks(): Promise<void> {
    throw new InfraRuntimeError("'loadStacks' is not implemented");
  }

  async resolveGroup<TApp extends IConstruct, TStackGroup extends StackGroup>(
    ctor: GenericStackGroup<TApp, TStackGroup>
  ): Promise<TStackGroup> {
    const instance = await this.loader.resolveGroup(ctor);
    if (!this.dependencies.includes(instance)) {
      this.dependencies.push(instance);
    }

    return instance as TStackGroup;
  }

  public static getFilePath(): string {
    const nodeModule = this.getNodeModule();
    return nodeModule ? nodeModule.filename : '';
  }

  private static getNodeModule(): NodeModule | undefined {
    const nodeModule = Object.values(require.cache)
      .filter((chl) => Object.values(chl?.exports).includes(this))
      .shift();
    return nodeModule;
  }

  public getStackName(name?: string, ignoreModulePath = false): string {
    const moduleName = this.normalizeModuleName();
    let stackName = '';

    const env = this.config['env'] as string;
    const region = (this.config['region'] as string) || 'us-east-1';
    if (!ignoreModulePath) {
      stackName += `${moduleName}-`;
    }

    if (!_.isNil(name)) {
      stackName += `${name.toLowerCase()}-`;
    }

    stackName += `${region.toLowerCase()}-${env.toLowerCase()}`;

    return stackName;
  }

  public getResourceName(
    name?: string,
    namespace = false,
    database = false,
    useRegion = true,
    useShortRegion = false,
    ignoreModulePath = false
  ): string {
    const separator = namespace ? '/' : database ? '_' : '-';
    const moduleName = this.normalizeModuleName();
    let resourceName = '';

    if (!ignoreModulePath) {
      resourceName += `${moduleName}${separator}`;
    }

    const env = this.config['env'] as string;
    const region = (this.config['region'] as string) || 'us-east-1';

    if (!_.isNil(name)) {
      resourceName += `${name.toLowerCase()}-`;
    }

    if (database) {
      resourceName += `${env.toLowerCase()}`;
    } else {
      if (useRegion) {
        if (useShortRegion) {
          const shortRegion = (this.config['shortRegion'] as string) || 'use1';
          resourceName += `${shortRegion.toLowerCase()}`;
        } else {
          resourceName += `${region.toLowerCase()}${separator}${env.toLowerCase()}`;
        }
      }
    }

    return resourceName;
  }

  public normalizeModuleName() {
    return dirname(
      relative(join(process.cwd(), this.loader.stacksDir), this.module)
    )
      .replace('/_/g', '-')
      .toLowerCase();
  }
}
