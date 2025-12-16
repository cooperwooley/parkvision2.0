// app/admin/users.tsx
import { useState, useEffect } from "react";
import {
  View,
  Text,
  TextInput,
  TouchableOpacity,
  FlatList,
  Alert,
  Modal,
  ScrollView,
  ActivityIndicator,
} from "react-native";
import { authStorage } from "../../lib/auth-storage";

const API_URL = "http://localhost:8000";

interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}

export default function UsersPage() {
  const [users, setUsers] = useState<User[]>([]);
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [editingUser, setEditingUser] = useState<User | null>(null);
  
  // Form states
  const [username, setUsername] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  // Fetch all users
  const fetchUsers = async () => {
    try {
      const token = await authStorage.get();
      const res = await fetch(`${API_URL}/auth/users`, {
        headers: {
          Authorization: `Bearer ${token}`,
        },
      });

      if (!res.ok) throw new Error("Failed to fetch users");

      const data = await res.json();
      setUsers(data);
    } catch (err) {
      console.error(err);
      Alert.alert("Error", "Could not load users");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchUsers();
  }, []);

  // Create new user
  const handleCreateUser = async () => {
    if (!username || !email || !password) {
      Alert.alert("Error", "All fields are required");
      return;
    }

    try {
      const token = await authStorage.get();
      const res = await fetch(`${API_URL}/auth/register`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ username, email, password }),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to create user");
      }

      Alert.alert("Success", "User created successfully");
      resetForm();
      fetchUsers();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  // Update user
  const handleUpdateUser = async () => {
    if (!editingUser || !username || !email) {
      Alert.alert("Error", "Username and email are required");
      return;
    }

    try {
      const token = await authStorage.get();
      const body: any = { username, email };
      if (password) body.password = password;

      const res = await fetch(`${API_URL}/auth/users/${editingUser.id}`, {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify(body),
      });

      if (!res.ok) {
        const data = await res.json();
        throw new Error(data.detail || "Failed to update user");
      }

      Alert.alert("Success", "User updated successfully");
      resetForm();
      fetchUsers();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  // Delete user
  const handleDeleteUser = (userId: number) => {
    Alert.alert(
      "Confirm Delete",
      "Are you sure you want to delete this user?",
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Delete",
          style: "destructive",
          onPress: async () => {
            try {
              const token = await authStorage.get();
              const res = await fetch(`${API_URL}/auth/users/${userId}`, {
                method: "DELETE",
                headers: {
                  Authorization: `Bearer ${token}`,
                },
              });

              if (!res.ok) throw new Error("Failed to delete user");

              Alert.alert("Success", "User deleted successfully");
              fetchUsers();
            } catch (err) {
              Alert.alert("Error", "Could not delete user");
            }
          },
        },
      ]
    );
  };

  // Open modal for editing
  const openEditModal = (user: User) => {
    setEditingUser(user);
    setUsername(user.username);
    setEmail(user.email);
    setPassword("");
    setModalVisible(true);
  };

  // Open modal for creating
  const openCreateModal = () => {
    resetForm();
    setModalVisible(true);
  };

  // Reset form
  const resetForm = () => {
    setEditingUser(null);
    setUsername("");
    setEmail("");
    setPassword("");
    setModalVisible(false);
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color="#1a73e8" />
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      <View
        style={{
          flexDirection: "row",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: 20,
        }}
      >
        <Text style={{ fontSize: 24, fontWeight: "bold" }}>
          Users Management
        </Text>
        <TouchableOpacity
          onPress={openCreateModal}
          style={{
            backgroundColor: "#1a73e8",
            paddingHorizontal: 16,
            paddingVertical: 10,
            borderRadius: 6,
          }}
        >
          <Text style={{ color: "white", fontWeight: "600" }}>Add User</Text>
        </TouchableOpacity>
      </View>

      {/* Users List */}
      <FlatList
        data={users}
        keyExtractor={(item) => item.id.toString()}
        renderItem={({ item }) => (
          <View
            style={{
              backgroundColor: "white",
              padding: 16,
              marginBottom: 12,
              borderRadius: 8,
              borderWidth: 1,
              borderColor: "#e0e0e0",
            }}
          >
            <View
              style={{
                flexDirection: "row",
                justifyContent: "space-between",
                alignItems: "flex-start",
              }}
            >
              <View style={{ flex: 1 }}>
                <Text style={{ fontSize: 18, fontWeight: "600" }}>
                  {item.username}
                </Text>
                <Text style={{ color: "#666", marginTop: 4 }}>
                  {item.email}
                </Text>
                <View
                  style={{ flexDirection: "row", marginTop: 8, gap: 8 }}
                >
                  {item.is_admin && (
                    <View
                      style={{
                        backgroundColor: "#fef3c7",
                        paddingHorizontal: 8,
                        paddingVertical: 4,
                        borderRadius: 4,
                      }}
                    >
                      <Text style={{ fontSize: 12, color: "#92400e" }}>
                        Admin
                      </Text>
                    </View>
                  )}
                  <Text style={{ fontSize: 12, color: "#999" }}>
                    Joined: {new Date(item.created_at).toLocaleDateString()}
                  </Text>
                </View>
              </View>

              <View style={{ flexDirection: "row", gap: 8 }}>
                <TouchableOpacity
                  onPress={() => openEditModal(item)}
                  style={{
                    backgroundColor: "#f3f4f6",
                    paddingHorizontal: 12,
                    paddingVertical: 8,
                    borderRadius: 4,
                  }}
                >
                  <Text style={{ color: "#1a73e8" }}>Edit</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  onPress={() => handleDeleteUser(item.id)}
                  style={{
                    backgroundColor: "#fee",
                    paddingHorizontal: 12,
                    paddingVertical: 8,
                    borderRadius: 4,
                  }}
                >
                  <Text style={{ color: "#dc2626" }}>Delete</Text>
                </TouchableOpacity>
              </View>
            </View>
          </View>
        )}
      />

      {/* Create/Edit Modal */}
      <Modal
        visible={modalVisible}
        animationType="slide"
        transparent={true}
        onRequestClose={resetForm}
      >
        <View
          style={{
            flex: 1,
            backgroundColor: "rgba(0,0,0,0.5)",
            justifyContent: "center",
            alignItems: "center",
          }}
        >
          <View
            style={{
              backgroundColor: "white",
              width: "90%",
              maxWidth: 500,
              borderRadius: 12,
              padding: 24,
            }}
          >
            <ScrollView>
              <Text style={{ fontSize: 20, fontWeight: "bold", marginBottom: 20 }}>
                {editingUser ? "Edit User" : "Create New User"}
              </Text>

              <Text style={{ marginBottom: 6, fontWeight: "500" }}>Username</Text>
              <TextInput
                value={username}
                onChangeText={setUsername}
                placeholder="Enter username"
                style={{
                  borderWidth: 1,
                  borderColor: "#d1d5db",
                  borderRadius: 6,
                  padding: 12,
                  marginBottom: 16,
                }}
              />

              <Text style={{ marginBottom: 6, fontWeight: "500" }}>Email</Text>
              <TextInput
                value={email}
                onChangeText={setEmail}
                placeholder="Enter email"
                keyboardType="email-address"
                autoCapitalize="none"
                style={{
                  borderWidth: 1,
                  borderColor: "#d1d5db",
                  borderRadius: 6,
                  padding: 12,
                  marginBottom: 16,
                }}
              />

              <Text style={{ marginBottom: 6, fontWeight: "500" }}>
                Password {editingUser && "(leave blank to keep current)"}
              </Text>
              <TextInput
                value={password}
                onChangeText={setPassword}
                placeholder="Enter password"
                secureTextEntry
                style={{
                  borderWidth: 1,
                  borderColor: "#d1d5db",
                  borderRadius: 6,
                  padding: 12,
                  marginBottom: 24,
                }}
              />

              <View style={{ flexDirection: "row", gap: 12 }}>
                <TouchableOpacity
                  onPress={resetForm}
                  style={{
                    flex: 1,
                    backgroundColor: "#f3f4f6",
                    padding: 14,
                    borderRadius: 6,
                    alignItems: "center",
                  }}
                >
                  <Text style={{ fontWeight: "600" }}>Cancel</Text>
                </TouchableOpacity>
                <TouchableOpacity
                  onPress={editingUser ? handleUpdateUser : handleCreateUser}
                  style={{
                    flex: 1,
                    backgroundColor: "#1a73e8",
                    padding: 14,
                    borderRadius: 6,
                    alignItems: "center",
                  }}
                >
                  <Text style={{ color: "white", fontWeight: "600" }}>
                    {editingUser ? "Update" : "Create"}
                  </Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </View>
  );
}