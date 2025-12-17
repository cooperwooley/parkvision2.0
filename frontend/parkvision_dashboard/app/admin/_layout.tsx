// app/admin/_layout.tsx
import { Slot, Link, useRouter } from "expo-router";
import { View, Text, TouchableOpacity, ScrollView } from "react-native";
import { useEffect } from "react";
import { authStorage } from "../../src/auth-storage";

export default function AdminLayout() {
  const router = useRouter();

  // Check authentication on mount
  useEffect(() => {
    const checkAuth = async () => {
      try {
        const token = await authStorage.get(); // uses your existing method
        if (!token) {
          router.replace("/login"); // redirect if no token
        }
      } catch (err) {
        console.error("Auth check failed", err);
        router.replace("/login");
      }
    };

    checkAuth();
  }, []);

  return (
    <View style={{ flex: 1, flexDirection: "row" }}>
      {/* Sidebar */}
      <ScrollView
        style={{ 
          flex: 0.06, // Sidebar takes 15% of width (was likely 0.2 or larger by default)
          backgroundColor: "#1a1a1a", 
          padding: 16 
        }}
        contentContainerStyle={{ flexGrow: 1 }}
      >
        <Text style={{ color: "white", fontSize: 20, marginBottom: 24 }}>
          Admin
        </Text>

        <Link href="/admin" asChild>
          <TouchableOpacity style={{ marginBottom: 16 }}>
            <Text style={{ color: "white" }}>Dashboard</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/admin/analytics" asChild>
          <TouchableOpacity style={{ marginBottom: 16 }}>
            <Text style={{ color: "white" }}>Analytics</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/admin/lots" asChild>
          <TouchableOpacity style={{ marginBottom: 16 }}>
            <Text style={{ color: "white" }}>Lots</Text>
          </TouchableOpacity>
        </Link>

        <Link href="/admin/users" asChild>
          <TouchableOpacity>
            <Text style={{ color: "white" }}>Users</Text>
          </TouchableOpacity>
        </Link>
      </ScrollView>

      {/* Main content */}
      <View style={{ flex: 1, padding: 20 }}>
        <View
          style={{
            borderBottomWidth: 1,
            borderBottomColor: "#ccc",
            marginBottom: 20,
          }}
        >
          <Text style={{ fontSize: 22, fontWeight: "bold" }}>Admin Header</Text>
        </View>

        <Slot /> {/* renders child page content */}
      </View>
    </View>
  );
}
