#!/usr/bin/env node
/**
 * Design-token guard: fail if a raw hex color literal appears outside the token
 * source. All colors must come from `src/design/tokens.ts` (the single source of
 * truth) so the palette can't drift back into scattered hardcoded values.
 *
 * Scans `src/` and `app/` for quoted hex strings ("#rgb".."#rrggbbaa"), excluding
 * the token definitions (src/design/) and test files. Run via `pnpm lint:tokens`.
 */
import { readdirSync, readFileSync, statSync } from "node:fs";
import { join, relative } from "node:path";

const ROOT = new URL("..", import.meta.url).pathname.replace(/^\/([A-Za-z]:)/, "$1");
const SCAN_DIRS = ["src", "app"];
const QUOTED_HEX = /["'`]#[0-9a-fA-F]{3,8}["'`]/;
const SKIP_DIR = /(^|\/)(node_modules|__tests__|src\/design)(\/|$)/;
const SKIP_FILE = /\.(test|spec)\.[tj]sx?$/;

/** @param {string} dir @param {string[]} out */
function walk(dir, out) {
  for (const entry of readdirSync(dir)) {
    const full = join(dir, entry);
    const rel = relative(ROOT, full).replace(/\\/g, "/");
    if (SKIP_DIR.test(rel + "/")) continue;
    const st = statSync(full);
    if (st.isDirectory()) walk(full, out);
    else if (/\.(ts|tsx)$/.test(entry) && !SKIP_FILE.test(entry)) out.push(full);
  }
}

const files = [];
for (const d of SCAN_DIRS) {
  try {
    walk(join(ROOT, d), files);
  } catch {
    /* dir may not exist */
  }
}

const offenders = [];
for (const file of files) {
  const lines = readFileSync(file, "utf8").split(/\r?\n/);
  lines.forEach((line, i) => {
    const trimmed = line.trim();
    // skip comment lines (line `//`, block `/* … */`, JSDoc `*` continuations)
    if (trimmed.startsWith("//") || trimmed.startsWith("*") || trimmed.startsWith("/*")) return;
    // strip trailing line comments from code lines
    const code = line.replace(/\/\/.*$/, "");
    if (QUOTED_HEX.test(code)) {
      offenders.push(`${relative(ROOT, file).replace(/\\/g, "/")}:${i + 1}: ${line.trim()}`);
    }
  });
}

if (offenders.length) {
  console.error("Raw hex color literals found (use design tokens in src/design/tokens.ts):\n");
  console.error(offenders.join("\n"));
  console.error(`\n${offenders.length} offending line(s).`);
  process.exit(1);
}
console.log("OK — no raw hex outside src/design token definitions.");
