// app/admin/lots.tsx
import { View, Text } from "react-native";

export default function LotsPage() {
  return (
    <View style={{ flex: 1 }}>
      <Text style={{ fontSize: 24, fontWeight: "bold", marginBottom: 16 }}>
        Lots Management
      </Text>
      <Text>Manage parking lots, add/remove spots, and view status.</Text>
    </View>
  );
}
