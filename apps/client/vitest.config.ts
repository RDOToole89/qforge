import { fileURLToPath, URL } from "node:url";
import { defineConfig } from "vitest/config";

export default defineConfig({
  resolve: {
    alias: [
      // Mirror tsconfig "paths": { "@/*": ["./*"] } so re-exports through the
      // "@/src/..." alias resolve under Vitest's node runner.
      {
        find: /^@\//,
        replacement: fileURLToPath(new URL("./", import.meta.url)),
      },
    ],
  },
  test: {
    environment: "node",
    include: ["src/**/*.{test,spec}.{ts,tsx}"],
    server: {
      // `three` ships ESM that occasionally trips Vitest's transform pipeline.
      // Inlining it forces Vite to process it so imports resolve under node.
      deps: {
        inline: ["three"],
      },
    },
  },
});
