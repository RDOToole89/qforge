module.exports = function (api) {
  api.cache(true);
  return {
    presets: [
      ["babel-preset-expo", { jsxImportSource: "nativewind" }],
      "nativewind/babel",
    ],
    // NOTE: react-native-worklets/plugin (the Reanimated v4 babel plugin) is
    // added automatically by babel-preset-expo when react-native-worklets is
    // installed, so it is intentionally NOT listed here to avoid duplication.
  };
};
