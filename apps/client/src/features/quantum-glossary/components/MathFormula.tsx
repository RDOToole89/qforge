import React, { useState } from "react";
import { View, Text, StyleSheet, Platform, ScrollView } from "react-native";
import { WebView } from "react-native-webview";

import { chrome } from "@/src/design";
import UnifiedBlochSphere from "@/src/features/bloch-sphere/components/UnifiedBlochSphere";
import { STATE_BLOCH_CONFIGS } from "@/src/features/bloch-sphere/data/stateBlochConfigs";

interface MathFormulaProps {
  latex: string;
  fontSize?: number;
  symbolAnnotations?: Record<string, string>;
  /** Glossary term ID — used to look up the Bloch sphere config */
  termId?: string;
}

const KATEX_CSS_CDN =
  "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.css";
const KATEX_JS_CDN =
  "https://cdn.jsdelivr.net/npm/katex@0.16.21/dist/katex.min.js";

function buildHtml(
  latex: string,
  fontSize: number,
  annotations?: Record<string, string>,
): string {
  const escaped = latex.replace(/\\/g, "\\\\").replace(/'/g, "\\'");
  const annotationsJson = annotations
    ? JSON.stringify(annotations).replace(/'/g, "\\'")
    : "null";

  return `<!DOCTYPE html>
<html>
<head>
  <meta name="viewport" content="width=device-width,initial-scale=1,maximum-scale=1">
  <link rel="stylesheet" href="${KATEX_CSS_CDN}">
  <style>
    * { margin: 0; padding: 0; box-sizing: border-box; }
    html, body {
      background: transparent;
      display: flex;
      align-items: center;
      justify-content: center;
      min-height: 70px;
      overflow: visible;
    }
    #formula {
      color: ${chrome.text.primary};
      font-size: ${fontSize}px;
      padding: 20px 16px;
      line-height: 1.5;
      text-align: center;
    }
    .katex-display { margin: 0; }
    .katex .mord, .katex .mbin, .katex .mrel,
    .katex .mopen, .katex .mclose, .katex .mpunct,
    .katex .mop, .katex .minner { color: ${chrome.text.primary}; }

    .sym-hover {
      cursor: pointer;
      border-radius: 3px;
      padding: 1px 2px;
      transition: background-color 0.15s ease, color 0.15s ease;
    }
    .sym-hover:hover {
      background-color: rgba(99, 102, 241, 0.2);
    }
    .sym-hover.active {
      background-color: rgba(99, 102, 241, 0.35);
      color: ${chrome.accent.light};
    }

    #tooltip {
      display: none;
      position: fixed;
      background: ${chrome.bg.elevated};
      color: ${chrome.text.primary};
      padding: 6px 10px;
      border-radius: 6px;
      font-size: 11px;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      max-width: 200px;
      line-height: 1.4;
      pointer-events: none;
      z-index: 1000;
      box-shadow: 0 4px 14px rgba(0,0,0,0.5);
      border: 1px solid rgba(99, 102, 241, 0.35);
    }
  </style>
</head>
<body>
  <div id="formula"></div>
  <div id="tooltip"></div>
  <script src="${KATEX_JS_CDN}"></script>
  <script>
    try {
      katex.render('${escaped}', document.getElementById('formula'), {
        throwOnError: false, displayMode: true, trust: true,
      });
    } catch(e) {
      document.getElementById('formula').textContent = '${escaped}';
    }

    var annotations = JSON.parse('${annotationsJson}');
    var activeSpan = null;
    var tip = document.getElementById('tooltip');

    function closeTip() {
      tip.style.display = 'none';
      if (activeSpan) { activeSpan.classList.remove('active'); activeSpan = null; }
    }

    if (annotations) {
      var formula = document.getElementById('formula');
      var spans = formula.querySelectorAll('.mord, .mop, .mbin, .mrel, .mopen, .mclose, .minner');
      var annoKeys = Object.keys(annotations);

      spans.forEach(function(span) {
        var text = span.textContent.trim();
        if (!text) return;
        for (var i = 0; i < annoKeys.length; i++) {
          var key = annoKeys[i];
          var isMatch = (text === key) ||
            (key.length >= 2 && text.length >= 2 && (text.indexOf(key) !== -1 || key.indexOf(text) !== -1));
          if (!isMatch) continue;
          if (span.classList.contains('sym-hover')) break;

          span.classList.add('sym-hover');
          span.setAttribute('data-key', key);

          span.addEventListener('click', function(e) {
            e.stopPropagation();
            var k = this.getAttribute('data-key');

            // Toggle: click same symbol again to close
            if (activeSpan === this) { closeTip(); return; }

            closeTip();
            activeSpan = this;
            this.classList.add('active');
            tip.textContent = annotations[k];
            tip.style.display = 'block';

            var rect = this.getBoundingClientRect();
            var tipW = tip.offsetWidth;
            var left = rect.left + rect.width/2 - tipW/2;
            left = Math.max(4, Math.min(left, window.innerWidth - tipW - 4));
            tip.style.left = left + 'px';
            tip.style.top = Math.max(2, rect.top - tip.offsetHeight - 8) + 'px';
          });
          break;
        }
      });

      // Click anywhere else to dismiss
      document.addEventListener('click', function(e) {
        if (activeSpan && !activeSpan.contains(e.target)) closeTip();
      });
    }

    setTimeout(function() {
      var h = document.getElementById('formula').scrollHeight + 4;
      window.ReactNativeWebView && window.ReactNativeWebView.postMessage(JSON.stringify({ height: Math.max(h, 70) }));
    }, 200);
  </script>
</body>
</html>`;
}

export function MathFormula({
  latex,
  fontSize = 18,
  symbolAnnotations,
  termId,
}: MathFormulaProps) {
  const [height, setHeight] = useState(90);
  const hasAnnotations = symbolAnnotations && Object.keys(symbolAnnotations).length > 0;
  const blochConfig = termId ? STATE_BLOCH_CONFIGS[termId] : undefined;
  const html = buildHtml(latex, fontSize, symbolAnnotations);

  const formulaView = Platform.OS === "web" ? (
    <WebMathFormula html={html} />
  ) : (
    <View style={{ height }}>
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
            if (data.height && data.height > 20) setHeight(data.height);
          } catch {}
        }}
      />
    </View>
  );

  if (!hasAnnotations && !blochConfig) {
    return <View style={styles.container}>{formulaView}</View>;
  }

  return (
    <View style={styles.containerWithLegend}>
      <View style={styles.formulaSide}>{formulaView}</View>
      {blochConfig && (
        <View style={styles.blochColumn}>
          <UnifiedBlochSphere
            mode="glossary"
            dots={blochConfig.dots}
            caption={blochConfig.caption}
            size={120}
          />
        </View>
      )}
      {hasAnnotations && <SymbolLegend annotations={symbolAnnotations!} />}
    </View>
  );
}

function SymbolLegend({ annotations }: { annotations: Record<string, string> }) {
  return (
    <ScrollView style={styles.legend} contentContainerStyle={styles.legendContent}>
      <Text style={styles.legendTitle}>Symbols</Text>
      {Object.entries(annotations).map(([sym, desc]) => (
        <View key={sym} style={styles.legendItem}>
          <Text style={styles.legendSym}>{sym}</Text>
          <Text style={styles.legendDesc} numberOfLines={2}>{desc}</Text>
        </View>
      ))}
    </ScrollView>
  );
}

function WebMathFormula({ html }: { html: string }) {
  return (
    <iframe
      srcDoc={html}
      style={{
        border: "none",
        width: "100%",
        minHeight: 90,
        height: "100%",
        background: "transparent",
      }}
      scrolling="no"
      sandbox="allow-scripts"
    />
  );
}

const styles = StyleSheet.create({
  container: {
    width: "100%",
    overflow: "hidden",
    borderRadius: 8,
    backgroundColor: chrome.bg.primary,
  },
  containerWithLegend: {
    width: "100%",
    flexDirection: "row",
    borderRadius: 8,
    backgroundColor: chrome.bg.primary,
    overflow: "hidden",
  },
  formulaSide: {
    flex: 1,
    minHeight: 90,
  },
  blochColumn: {
    width: 135,
    alignItems: "center",
    justifyContent: "center",
    borderLeftWidth: 1,
    borderLeftColor: chrome.bg.surface,
    backgroundColor: "rgba(15, 23, 42, 0.3)",
  },
  legend: {
    width: 140,
    maxHeight: 180,
    borderLeftWidth: 1,
    borderLeftColor: chrome.bg.surface,
    backgroundColor: "rgba(15, 23, 42, 0.5)",
  },
  legendContent: {
    padding: 6,
  },
  legendTitle: {
    color: chrome.accent.base,
    fontSize: 8,
    fontWeight: "700",
    textTransform: "uppercase",
    letterSpacing: 0.8,
    marginBottom: 4,
  },
  legendItem: {
    flexDirection: "row",
    alignItems: "flex-start",
    gap: 4,
    marginBottom: 4,
  },
  legendSym: {
    color: chrome.accent.light,
    fontSize: 10,
    fontWeight: "700",
    minWidth: 16,
  },
  legendDesc: {
    flex: 1,
    color: chrome.text.secondary,
    fontSize: 9,
    lineHeight: 12,
  },
  webview: {
    flex: 1,
    backgroundColor: "transparent",
  },
});
