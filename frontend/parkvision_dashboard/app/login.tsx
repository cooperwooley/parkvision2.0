import { useState } from "react";
import { View, Text, TextInput, Button, Alert } from "react-native";
import { useRouter } from "expo-router";
import { api } from "../lib/api";
import { authStorage } from "../lib/auth-storage";

export default function Login() {
  const router = useRouter();

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");

  const handleLogin = async () => {
    try {
      const { access_token } = await api.login(username, password);
      await authStorage.save(access_token);

      router.replace("/admin"); // go to dashboard
    } catch (err: any) {
      Alert.alert("Login failed", err.message);
    }
  };

  return (
    <View style={{ padding: 30 }}>
      <Text style={{ fontSize: 28, marginBottom: 20 }}>Admin Login</Text>

      <TextInput
        placeholder="Username"
        style={{ borderWidth: 1, padding: 10, marginBottom: 10 }}
        value={username}
        onChangeText={setUsername}
      />

      <TextInput
        placeholder="Password"
        secureTextEntry
        style={{ borderWidth: 1, padding: 10, marginBottom: 20 }}
        value={password}
        onChangeText={setPassword}
      />

      <Button title="Login" onPress={handleLogin} />
    </View>
  );
}
