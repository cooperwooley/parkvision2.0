// app/admin/lots.tsx
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
import { api, ParkingLot, LotStatus } from "../../src/api";
import { useRouter } from "expo-router";

export default function LotsPage() {
  const router = useRouter();
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [lotStatuses, setLotStatuses] = useState<{ [key: number]: LotStatus }>({});
  const [loading, setLoading] = useState(true);
  const [modalVisible, setModalVisible] = useState(false);
  const [deleteModalVisible, setDeleteModalVisible] = useState(false);
  const [editingLot, setEditingLot] = useState<ParkingLot | null>(null);
  const [deletingLotId, setDeletingLotId] = useState<number | null>(null);
  
  // Form states
  const [name, setName] = useState("");
  const [address, setAddress] = useState("");
  const [totalSpaces, setTotalSpaces] = useState("");
  const [description, setDescription] = useState("");

  // Fetch all lots
  const fetchLots = async () => {
    try {
      const data = await api.lots.getAll();
      setLots(data);
      
      // Fetch status for each lot
      const statuses: { [key: number]: LotStatus } = {};
      await Promise.all(
        data.map(async (lot: ParkingLot) => {
          try {
            const status = await api.lots.getStatus(lot.id);
            statuses[lot.id] = status;
          } catch (err) {
            console.error(`Failed to fetch status for lot ${lot.id}`, err);
          }
        })
      );
      setLotStatuses(statuses);
    } catch (err: any) {
      console.error(err);
      Alert.alert("Error", err.message || "Could not load lots");
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLots();
  }, []);

  // Create new lot
  const handleCreateLot = async () => {
    if (!name || !totalSpaces) {
      Alert.alert("Error", "Lot name and total spaces are required");
      return;
    }

    try {
      await api.lots.create({
        name,
        total_spaces: parseInt(totalSpaces),
        address: address || undefined,
        description: description || undefined,
      });
      Alert.alert("Success", "Parking lot created successfully");
      resetForm();
      fetchLots();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  // Update lot
  const handleUpdateLot = async () => {
    if (!editingLot || !name || !totalSpaces) {
      Alert.alert("Error", "Lot name and total spaces are required");
      return;
    }

    try {
      await api.lots.update(editingLot.id, {
        name,
        total_spaces: parseInt(totalSpaces),
        address: address || undefined,
        description: description || undefined,
      });
      Alert.alert("Success", "Parking lot updated successfully");
      resetForm();
      fetchLots();
    } catch (err: any) {
      Alert.alert("Error", err.message);
    }
  };

  // Delete lot
  const handleDeleteLot = (lotId: number) => {
    setDeletingLotId(lotId);
    setDeleteModalVisible(true);
  };

  const confirmDelete = async () => {
    if (!deletingLotId) return;
    
    try {
      await api.lots.delete(deletingLotId);
      setDeleteModalVisible(false);
      setDeletingLotId(null);
      await fetchLots();
      Alert.alert("Success", "Parking lot deleted successfully");
    } catch (err: any) {
      console.error("Delete error:", err);
      Alert.alert("Error", err.message || "Failed to delete parking lot");
    }
  };

  // Open modal for editing
  const openEditModal = (lot: ParkingLot) => {
    setEditingLot(lot);
    setName(lot.name);
    setAddress(lot.address || "");
    setTotalSpaces(lot.total_spaces?.toString() || "");
    setDescription(lot.description || "");
    setModalVisible(true);
  };

  // Open modal for creating
  const openCreateModal = () => {
    resetForm();
    setModalVisible(true);
  };

  // Reset form
  const resetForm = () => {
    setEditingLot(null);
    setName("");
    setAddress("");
    setTotalSpaces("");
    setDescription("");
    setModalVisible(false);
  };

  // Navigate to lot detail
  const viewLotDetails = (lotId: number) => {
    router.push(`/admin/lots/${lotId}`);
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
          Parking Lots Management
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
          <Text style={{ color: "white", fontWeight: "600" }}>Add Lot</Text>
        </TouchableOpacity>
      </View>

      {lots.length === 0 ? (
        <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
          <Text style={{ fontSize: 16, color: "#666", marginBottom: 16 }}>
            No parking lots yet
          </Text>
          <TouchableOpacity
            onPress={openCreateModal}
            style={{
              backgroundColor: "#1a73e8",
              paddingHorizontal: 20,
              paddingVertical: 12,
              borderRadius: 6,
            }}
          >
            <Text style={{ color: "white", fontWeight: "600" }}>
              Create First Lot
            </Text>
          </TouchableOpacity>
        </View>
      ) : (
        <FlatList
          data={lots}
          keyExtractor={(item) => item.id.toString()}
          renderItem={({ item }) => {
            const status = lotStatuses[item.id];
            return (
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
                    <Text style={{ fontSize: 20, fontWeight: "600" }}>
                      {item.name}
                    </Text>
                    {item.address && (
                      <Text style={{ color: "#666", marginTop: 4 }}>
                        📍 {item.address}
                      </Text>
                    )}
                    
                    {/* Status Summary */}
                    {status ? (
                      <View style={{ marginTop: 12 }}>
                        <View
                          style={{
                            flexDirection: "row",
                            gap: 12,
                            marginBottom: 8,
                          }}
                        >
                          <View style={{ flexDirection: "row", alignItems: "center" }}>
                            <View
                              style={{
                                width: 12,
                                height: 12,
                                borderRadius: 6,
                                backgroundColor: "#10b981",
                                marginRight: 6,
                              }}
                            />
                            <Text style={{ fontSize: 14 }}>
                              {status.vacant} Vacant
                            </Text>
                          </View>
                          <View style={{ flexDirection: "row", alignItems: "center" }}>
                            <View
                              style={{
                                width: 12,
                                height: 12,
                                borderRadius: 6,
                                backgroundColor: "#ef4444",
                                marginRight: 6,
                              }}
                            />
                            <Text style={{ fontSize: 14 }}>
                              {status.occupied} Occupied
                            </Text>
                          </View>
                        </View>
                        <View
                          style={{
                            backgroundColor: "#f3f4f6",
                            padding: 8,
                            borderRadius: 4,
                          }}
                        >
                          <Text style={{ fontSize: 12, color: "#666" }}>
                            Occupancy: {Math.round(status.occupancy_rate * 100)}% •{" "}
                            Total Spots: {status.total_spots}
                          </Text>
                        </View>
                      </View>
                    ) : (
                      <Text style={{ color: "#999", marginTop: 8, fontSize: 14 }}>
                        Total Spaces: {item.total_spaces || "Not set"}
                      </Text>
                    )}
                  </View>

                  <View style={{ flexDirection: "column", gap: 8 }}>
                    <TouchableOpacity
                      onPress={() => viewLotDetails(item.id)}
                      style={{
                        backgroundColor: "#1a73e8",
                        paddingHorizontal: 12,
                        paddingVertical: 8,
                        borderRadius: 4,
                      }}
                    >
                      <Text style={{ color: "white", fontWeight: "500" }}>
                        View Details
                      </Text>
                    </TouchableOpacity>
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
                      onPress={() => handleDeleteLot(item.id)}
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
            );
          }}
        />
      )}

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
                {editingLot ? "Edit Parking Lot" : "Create New Parking Lot"}
              </Text>

              <Text style={{ marginBottom: 6, fontWeight: "500" }}>
                Lot Name *
              </Text>
              <TextInput
                value={name}
                onChangeText={setName}
                placeholder="e.g. Main Parking Lot"
                style={{
                  borderWidth: 1,
                  borderColor: "#d1d5db",
                  borderRadius: 6,
                  padding: 12,
                  marginBottom: 16,
                }}
              />

              <Text style={{ marginBottom: 6, fontWeight: "500" }}>Address</Text>
              <TextInput
                value={address}
                onChangeText={setAddress}
                placeholder="e.g. 123 Main Street"
                style={{
                  borderWidth: 1,
                  borderColor: "#d1d5db",
                  borderRadius: 6,
                  padding: 12,
                  marginBottom: 16,
                }}
              />

              <Text style={{ marginBottom: 6, fontWeight: "500" }}>
                Total Spaces *
              </Text>
              <TextInput
                value={totalSpaces}
                onChangeText={setTotalSpaces}
                placeholder="e.g. 100"
                keyboardType="numeric"
                style={{
                  borderWidth: 1,
                  borderColor: "#d1d5db",
                  borderRadius: 6,
                  padding: 12,
                  marginBottom: 16,
                }}
              />

              <Text style={{ marginBottom: 6, fontWeight: "500" }}>
                Description
              </Text>
              <TextInput
                value={description}
                onChangeText={setDescription}
                placeholder="Optional description"
                multiline
                numberOfLines={3}
                style={{
                  borderWidth: 1,
                  borderColor: "#d1d5db",
                  borderRadius: 6,
                  padding: 12,
                  marginBottom: 24,
                  textAlignVertical: "top",
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
                  onPress={editingLot ? handleUpdateLot : handleCreateLot}
                  style={{
                    flex: 1,
                    backgroundColor: "#1a73e8",
                    padding: 14,
                    borderRadius: 6,
                    alignItems: "center",
                  }}
                >
                  <Text style={{ color: "white", fontWeight: "600" }}>
                    {editingLot ? "Update" : "Create"}
                  </Text>
                </TouchableOpacity>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>

      {/* Delete Confirmation Modal */}
      <Modal
        visible={deleteModalVisible}
        animationType="fade"
        transparent={true}
        onRequestClose={() => {
          setDeleteModalVisible(false);
          setDeletingLotId(null);
        }}
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
              maxWidth: 400,
              borderRadius: 12,
              padding: 24,
            }}
          >
            <Text style={{ fontSize: 20, fontWeight: "bold", marginBottom: 12 }}>
              Confirm Delete
            </Text>
            <Text style={{ fontSize: 16, color: "#666", marginBottom: 24 }}>
              Are you sure you want to delete this parking lot? All associated spots
              will be removed. This action cannot be undone.
            </Text>

            <View style={{ flexDirection: "row", gap: 12 }}>
              <TouchableOpacity
                onPress={() => {
                  setDeleteModalVisible(false);
                  setDeletingLotId(null);
                }}
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
                onPress={confirmDelete}
                style={{
                  flex: 1,
                  backgroundColor: "#dc2626",
                  padding: 14,
                  borderRadius: 6,
                  alignItems: "center",
                }}
              >
                <Text style={{ color: "white", fontWeight: "600" }}>Delete</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </View>
  );
}