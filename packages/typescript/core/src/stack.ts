import * as _ from 'lodash';
import { StackGroup } from './stack-group';


export class BaseStack {
  config: Record<string, unknown>;
  getResourceName: typeof StackGroup.prototype.getResourceName;

  constructor(public stackGroup: StackGroup) {
    this.config = this.stackGroup.config;

    this.getResourceName = this.stackGroup.getResourceName.bind(this.stackGroup)
  }

  getBucketName(name?: string, includePathNaming = true): string {
    let bucketName = `${!_.isNil(this.config['baseBucket']) ? `${this.config['baseBucket']}-` : ''}`
    const moduleName = this.stackGroup.normalizeModuleName();

    const { env, region } = this.stackGroup

    if (includePathNaming) {
      bucketName += `${moduleName}-`
    }

    if (!_.isNil(name)) {
      bucketName += `${name.toLowerCase()}-`
    }

    bucketName += `${region}-${env}`

    return bucketName
  }
}
