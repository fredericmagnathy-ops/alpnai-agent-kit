import {mkdir, open, readFile, rename, rmdir, unlink} from 'node:fs/promises';
import {join, resolve} from 'node:path';
import type {Journal, RecordEntry} from './client.js';

/** Single-host filesystem journal. A crash leaves a fail-closed lock for owner review. */
export class FileJournal implements Journal {
  private readonly root: string;
  constructor(directory: string) {this.root = resolve(directory);}
  private path(identity: string) {
    if (!/^[a-f0-9]{64}$/.test(identity)) throw Error('invalid_journal_identity');
    return join(this.root, identity);
  }
  async exclusive<T>(identity: string, operation: () => Promise<T>): Promise<T> {
    await mkdir(this.root, {recursive: true, mode: 0o700});
    const lock = this.path(identity) + '.lock';
    try {await mkdir(lock, {mode: 0o700});} catch {throw Error('journal_locked_owner_review_if_crashed');}
    try {return await operation();} finally {await rmdir(lock);}
  }
  async load(identity: string) {
    try {return JSON.parse(await readFile(this.path(identity) + '.json', 'utf8')) as RecordEntry;}
    catch (error) {if ((error as NodeJS.ErrnoException).code === 'ENOENT') return undefined; throw error;}
  }
  async save(identity: string, record: RecordEntry) {
    const path = this.path(identity) + '.json', temporary = path + '.tmp';
    // A previous crashed save is never silently overwritten.
    const file = await open(temporary, 'wx', 0o600);
    try {await file.writeFile(JSON.stringify(record)); await file.sync();} finally {await file.close();}
    try {await rename(temporary, path);} catch (error) {await unlink(temporary).catch(() => {}); throw error;}
    const directory = await open(this.root, 'r');
    try {await directory.sync();} finally {await directory.close();}
  }
}
