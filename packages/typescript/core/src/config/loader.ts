import { IConstruct } from 'constructs';
import { dirname, join, relative } from 'path';
import { existsSync, readdirSync, readFileSync } from 'fs';
import { load } from 'js-yaml';
import * as _ from 'lodash';

type LoadResult = {
  config: Record<string, unknown>;
  enabled: boolean;
};

export class ConfigLoader {
  stacksDir: string;
  configDir: string;

  constructor(
    private readonly app: IConstruct,
    private readonly env: string,
    private readonly region: string
  ) {
    this.stacksDir = this.app.node.tryGetContext('stacksDir') ?? 'stacks';
    this.configDir = this.app.node.tryGetContext('configDir') ?? 'config';
  }

  private loadConfigRecursive(
    path: string,
    config: Record<string, unknown>
  ): Record<string, unknown> {
    if (!existsSync(path)) {
      return this.loadConfigRecursive(dirname(path), config);
    }
    readdirSync(path).forEach((file) => {
      if (file.endsWith('.yaml')) {
        const fileContent = readFileSync(join(path, file), 'utf-8')
        const fileData = load(fileContent) as Record<string, unknown>;

        config = _.merge(config, fileData);
      }
    });
    if (path !== '.') {
      config = this.loadConfigRecursive(dirname(path), config);
    }

    return config;
  }

  loadConfig(module: string): LoadResult {
    const modulePath = relative(process.cwd(), dirname(module));

    const configModule = join(
      this.configDir,
      this.env,
      this.region,
      modulePath.replace(this.stacksDir, '')
    );
    const configPath = join(configModule, 'config.yaml');

    const config = this.loadConfigRecursive(configModule, {});

    return { config, enabled: existsSync(configPath) };
  }
}
