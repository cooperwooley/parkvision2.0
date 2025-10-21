// app/admin/_layout.tsx
import { Slot, Link } from "expo-router";
import { View, Text, TouchableOpacity, ScrollView, useWindowDimensions } from "react-native";

export default function AdminLayout() {
  const { width: screenWidth } = useWindowDimensions();
  const isMobile = screenWidth < 768;

  const sidebarWidth = isMobile ? "100%" : 120; // fixed width for desktop, full width for mobile

  return (
    <View style={{ flex: 1, flexDirection: isMobile ? "column" : "row", width: "100%", height: "100%" }}>
      {/* Sidebar */}
      <ScrollView
        style={{
          width: sidebarWidth,
          maxWidth: isMobile ? "100%" : 120,
          backgroundColor: "#1a1a1a",
          padding: 16,
        }}
        contentContainerStyle={{ flexGrow: 1 }}
      >
        <Text style={{ color: "white", fontSize: 22, marginBottom: 24, fontWeight: "bold" }}>
          Admin
        </Text>

        {/* Explicit links */}
        <Link href="/admin" asChild>
          <TouchableOpacity style={{ marginBottom: 16 }}>
            <Text style={{ color: "white", fontSize: 16 }}>Dashboard</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/admin/analytics" asChild>
          <TouchableOpacity style={{ marginBottom: 16 }}>
            <Text style={{ color: "white", fontSize: 16 }}>Analytics</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/admin/lots" asChild>
          <TouchableOpacity style={{ marginBottom: 16 }}>
            <Text style={{ color: "white", fontSize: 16 }}>Lots</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/admin/users" asChild>
          <TouchableOpacity style={{ marginBottom: 16 }}>
            <Text style={{ color: "white", fontSize: 16 }}>Users</Text>
          </TouchableOpacity>
        </Link>
      </ScrollView>

      {/* Main content */}
      <View style={{ flex: 1, padding: 20, minWidth: 0 }}>
        <View
          style={{
            borderBottomWidth: 1,
            borderBottomColor: "#ccc",
            paddingBottom: 12,
            marginBottom: 20,
          }}
        >
          <Text style={{ fontSize: 24, fontWeight: "bold" }}>Admin Dashboard</Text>
        </View>

        <Slot /> {/* renders child page content */}
      </View>
    </View>
  );
}
