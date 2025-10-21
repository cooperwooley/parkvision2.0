// app/admin/index.tsx
import { View, Text } from "react-native";

export default function AdminDashboard() {
  return (
    <View style={{ flex: 1 }}>
      <Text style={{ fontSize: 28, fontWeight: "bold", marginBottom: 16 }}>
        Welcome to the Admin Dashboard
      </Text>

      <Text style={{ fontSize: 18, marginBottom: 8 }}>
        Overview of your parking lots, occupancy, and analytics.
      </Text>

      <Text>Use the sidebar to navigate to different admin pages.</Text>
    </View>
  );
}
