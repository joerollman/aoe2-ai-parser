import fs from 'node:fs';
import path from 'node:path';
import process from 'node:process';
import { parse, lint } from 'aoe2-rms-parser';

const args = process.argv.slice(2);

if (args.length === 0 || args.includes('--help') || args.includes('-h')) {
  console.log('usage: npm run lint:rms -- <file-or-dir> [more-files-or-dirs]');
  process.exit(args.length === 0 ? 1 : 0);
}

function collectRmsFiles(target) {
  const stat = fs.statSync(target);
  if (stat.isFile()) {
    return target.toLowerCase().endsWith('.rms') ? [target] : [];
  }
  if (!stat.isDirectory()) {
    return [];
  }
  return fs.readdirSync(target, { withFileTypes: true }).flatMap((entry) => {
    const child = path.join(target, entry.name);
    if (entry.isDirectory()) {
      return collectRmsFiles(child);
    }
    return entry.isFile() && entry.name.toLowerCase().endsWith('.rms') ? [child] : [];
  });
}

function formatIssue(kind, file, issue) {
  const line = issue.line ?? issue.start?.line ?? '?';
  const column = issue.column ?? issue.start?.column ?? '?';
  const message = issue.message ?? String(issue);
  return `${file}:${line}:${column}: ${kind}: ${message}`;
}

const files = [...new Set(args.flatMap(collectRmsFiles))].sort();
let issueCount = 0;

for (const file of files) {
  const source = fs.readFileSync(file, 'utf8');
  const result = parse(source);
  const parseErrors = result.errors ?? [];

  if (parseErrors.length > 0) {
    issueCount += parseErrors.length;
    for (const error of parseErrors) {
      console.error(formatIssue('parse', file, error));
    }
    continue;
  }

  const lintErrors = lint(result.ast);
  issueCount += lintErrors.length;
  for (const error of lintErrors) {
    console.error(formatIssue('lint', file, error));
  }
}

if (files.length === 0) {
  console.error(`no .rms files found in: ${args.join(', ')}`);
  process.exit(1);
}

if (issueCount > 0) {
  console.error(`rms lint failed: ${issueCount} issue(s) in ${files.length} file(s)`);
  process.exit(1);
}

console.log(`rms lint passed: ${files.length} file(s)`);
