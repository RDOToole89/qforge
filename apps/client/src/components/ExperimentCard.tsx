import React from "react";

import { Button, Card, Row, Stack, Text } from "@/src/design";

interface Props {
  name: string;
  description: string;
  onRun: () => void;
  onCustomize: () => void;
}

export default function ExperimentCard({
  name,
  description,
  onRun,
  onCustomize,
}: Props) {
  return (
    <Card variant="elevated" padding="lg" className="mb-md">
      <Stack gap="xs">
        <Text variant="headingSm" weight="bold" mono tone="primary">
          {name}
        </Text>
        <Text variant="bodyLg" tone="secondary">
          {description}
        </Text>
      </Stack>
      <Row gap="sm" className="mt-md">
        <Button variant="primary" size="md" onPress={onRun}>
          Run
        </Button>
        <Button
          variant="outline"
          size="md"
          onPress={onCustomize}
          className="border-accent"
        >
          <Text variant="label" weight="semibold" tone="accent">
            Customize
          </Text>
        </Button>
      </Row>
    </Card>
  );
}
