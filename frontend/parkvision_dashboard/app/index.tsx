import { Link } from "expo-router";
import { View, Text, TouchableOpacity } from "react-native";

export default function Home() {
  return (
    <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
      <Text style={{ fontSize: 24, marginBottom: 20 }}>ParkVision 2.0</Text>
      <Link href="/admin" asChild>
        <TouchableOpacity style={{ padding: 12, backgroundColor: "#007AFF", borderRadius: 6 }}>
          <Text style={{ color: "white", fontWeight: "bold" }}>Go to Admin Dashboard</Text>
        </TouchableOpacity>
      </Link>
    </View>
  );
}
