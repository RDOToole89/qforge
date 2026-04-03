import React, { useState } from "react";
import { View, StyleSheet, Platform } from "react-native";
import { WebView } from "react-native-webview";

interface MathFormulaProps {
  /** LaTeX string to render */
  latex: string;
  /** Font size in px (default 18) */
  fontSize?: number;
}

const KATEX_CSS_CDN =
  "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css";
const KATEX_JS_CDN =
  "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js";

function buildHtml(latex: string, fontSize: number): string {
  // Escape backslashes and quotes for safe JS embedding
  const escaped = latex.replace(/\\/g, "\\\\").replace(/'/g, "\\'");

  return `<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
  <link rel="stylesheet" href="${KATEX_CSS_CDN}">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      background: transparent;
      overflow: hidden;
      display: flex;
      align-items: center;
      justify-content: center;
    }
    #formula {
      color: #e2e8f0;
      font-size: ${fontSize}px;
      padding: 8px 4px;
      line-height: 1.4;
    }
    .katex .mord, .katex .mbin, .katex .mrel,
    .katex .mopen, .katex .mclose, .katex .mpunct,
    .katex .mop, .katex .minner { color: #e2e8f0; }
  </style>
</head>
<body>
  <div id="formula"></div>
  <script src="${KATEX_JS_CDN}"></script>
  <script>
    try {
      katex.render('${escaped}', document.getElementById('formula'), {
        throwOnError: false,
        displayMode: true,
        trust: true,
      });
    } catch(e) {
      document.getElementById('formula').textContent = '${escaped}';
    }
    // Send the rendered height back to React Native
    setTimeout(function() {
      var h = document.getElementById('formula').offsetHeight + 16;
      window.ReactNativeWebView && window.ReactNativeWebView.postMessage(JSON.stringify({ height: h }));
    }, 100);
  </script>
</body>
</html>`;
}

export function MathFormula({ latex, fontSize = 18 }: MathFormulaProps) {
  const [height, setHeight] = useState(60);

  const html = buildHtml(latex, fontSize);

  if (Platform.OS === "web") {
    return <WebMathFormula html={html} />;
  }

  return (
    <View style={[styles.container, { height }]}>
      <WebView
        source={{ html }}
        style={styles.webview}
        scrollEnabled={false}
        showsHorizontalScrollIndicator={false}
        showsVerticalScrollIndicator={false}
        originWhitelist={["*"]}
        javaScriptEnabled
        onMessage={(event) => {
          try {
            const data = JSON.parse(event.nativeEvent.data);
            if (data.height && data.height > 20) {
              setHeight(data.height);
            }
          } catch {}
        }}
      />
    </View>
  );
}

/** Web platform: render as an iframe via dangerouslySetInnerHTML */
function WebMathFormula({ html }: { html: string }) {
  return (
    <View style={styles.container}>
      <iframe
        srcDoc={html}
        style={{
          border: "none",
          width: "100%",
          minHeight: 60,
          background: "transparent",
        }}
        scrolling="no"
        sandbox="allow-scripts"
      />
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    overflow: "hidden",
    borderRadius: 8,
    backgroundColor: "#0f172a",
  },
  webview: {
    flex: 1,
    backgroundColor: "transparent",
  },
});
