// app/admin/analytics.tsx
import { View, Text } from "react-native";

export default function AnalyticsPage() {
  return (
    <View style={{ flex: 1 }}>
      <Text style={{ fontSize: 24, fontWeight: "bold", marginBottom: 16 }}>
        Analytics
      </Text>
      <Text>Charts and graphs of parking lot usage will go here.</Text>
    </View>
  );
}
