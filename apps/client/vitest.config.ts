import { defineConfig } from "vitest/config";

export default defineConfig({
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
