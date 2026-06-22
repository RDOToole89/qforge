import React from "react";
import FontAwesome from "@expo/vector-icons/FontAwesome";
import { Tabs } from "expo-router";

import { chrome } from "@/src/design/tokens";

function TabBarIcon(props: {
  name: React.ComponentProps<typeof FontAwesome>["name"];
  color: string;
}) {
  return <FontAwesome size={24} style={{ marginBottom: -3 }} {...props} />;
}

export default function TabLayout() {
  return (
    <Tabs
      screenOptions={{
        tabBarActiveTintColor: chrome.text.primary,
        tabBarStyle: {
          backgroundColor: chrome.bg.primary,
          borderTopColor: chrome.bg.surface,
        },
        headerStyle: { backgroundColor: chrome.bg.primary },
        headerTintColor: chrome.text.primary,
      }}
    >
      <Tabs.Screen
        name="configure"
        options={{
          title: "Configure",
          tabBarIcon: ({ color }) => <TabBarIcon name="sliders" color={color} />,
        }}
      />
      <Tabs.Screen
        name="results"
        options={{
          title: "Results",
          tabBarIcon: ({ color }) => (
            <TabBarIcon name="bar-chart" color={color} />
          ),
        }}
      />
      <Tabs.Screen
        name="visualizer"
        options={{
          title: "Visualizer",
          tabBarIcon: ({ color }) => <TabBarIcon name="cube" color={color} />,
        }}
      />
      <Tabs.Screen
        name="circuit"
        options={{
          title: "Circuit",
          tabBarIcon: ({ color }) => <TabBarIcon name="sitemap" color={color} />,
        }}
      />
      <Tabs.Screen
        name="registry"
        options={{
          title: "Registry",
          tabBarIcon: ({ color }) => <TabBarIcon name="flask" color={color} />,
        }}
      />
      <Tabs.Screen
        name="glossary"
        options={{
          title: "Glossary",
          tabBarIcon: ({ color }) => <TabBarIcon name="book" color={color} />,
        }}
      />
    </Tabs>
  );
}
