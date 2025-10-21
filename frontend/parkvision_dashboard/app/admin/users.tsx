// app/admin/users.tsx
import { View, Text } from "react-native";

export default function UsersPage() {
  return (
    <View style={{ flex: 1 }}>
      <Text style={{ fontSize: 24, fontWeight: "bold", marginBottom: 16 }}>
        Users Management
      </Text>
      <Text>Manage admin accounts here.</Text>
    </View>
  );
}
