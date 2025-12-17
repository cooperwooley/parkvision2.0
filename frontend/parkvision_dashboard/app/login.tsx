//app/login.tsx
import { useState } from "react";
import { View, Text, TextInput, TouchableOpacity, Alert } from "react-native";
import { authStorage } from "../src/auth-storage";
import { useRouter } from "expo-router";

export default function LoginPage() {
  const [username, setUsername] = useState(""); // Changed from email
  const [password, setPassword] = useState("");
  const router = useRouter();

  const handleLogin = async () => {
    try {
      const res = await fetch("http://localhost:8000/auth/login", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ username, password }), // Changed from email
      });

      if (!res.ok) {
        const data = await res.json();
        Alert.alert("Login failed", data.detail || "Unknown error");
        return;
      }

      const data = await res.json();
      await authStorage.save(data.access_token);
      router.replace("/admin");
    } catch (err) {
      console.error(err);
      Alert.alert("Login error", "Could not connect to server");
    }
  };

  return (
    <View style={{ padding: 20 }}>
      <TextInput
        placeholder="Username" // Changed from "Email"
        value={username} // Changed from email
        onChangeText={setUsername} // Changed from setEmail
        style={{ borderWidth: 1, marginBottom: 12, padding: 8 }}
      />
      <TextInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        secureTextEntry
        style={{ borderWidth: 1, marginBottom: 12, padding: 8 }}
      />
      <TouchableOpacity
        onPress={handleLogin}
        style={{ backgroundColor: "#1a73e8", padding: 12 }}
      >
        <Text style={{ color: "white", textAlign: "center" }}>Log In</Text>
      </TouchableOpacity>
    </View>
  );
}