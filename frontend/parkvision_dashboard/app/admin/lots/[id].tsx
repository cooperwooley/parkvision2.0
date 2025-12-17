// app/admin/lots/[id].tsx
import { useState, useEffect } from "react";
import {
  View,
  Text,
  TouchableOpacity,
  FlatList,
  Alert,
  ActivityIndicator,
  ScrollView,
  RefreshControl,
} from "react-native";
import { useLocalSearchParams, useRouter } from "expo-router";
import { api, ParkingLot, ParkingSpot, LotStatus } from "../../../src/api";

export default function LotDetailPage() {
  const { id } = useLocalSearchParams();
  const router = useRouter();
  const lotId = parseInt(id as string);

  const [lot, setLot] = useState<ParkingLot | null>(null);
  const [spots, setSpots] = useState<ParkingSpot[]>([]);
  const [status, setStatus] = useState<LotStatus | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [filterStatus, setFilterStatus] = useState<string>("all");

  // Fetch lot details, spots, and status
  const fetchLotData = async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);

      const [lotData, spotsResponse, statusResponse] = await Promise.all([
        api.lots.get(lotId),
        api.lots.getSpots(lotId),
        api.lots.getStatus(lotId),
      ]);

      setLot(lotData);
      // Handle the response format: {lot_id: number, spots: array}
      setSpots(spotsResponse.spots || []);
      // Handle status format: {lot_id: number, summary: object}
      // Convert summary object to status counts
      const summary = statusResponse.summary || {};
      const spotStatuses = Object.values(summary);
      const statusCounts = {
        lot_id: lotId,
        total_spots: spotStatuses.length,
        vacant: spotStatuses.filter((s: any) => s === "vacant").length,
        occupied: spotStatuses.filter((s: any) => s === "occupied").length,
        reserved: spotStatuses.filter((s: any) => s === "reserved").length,
        occupancy_rate: spotStatuses.length > 0 
          ? spotStatuses.filter((s: any) => s === "occupied").length / spotStatuses.length 
          : 0,
        last_updated: new Date().toISOString(),
      };
      setStatus(statusCounts as any);
    } catch (err: any) {
      console.error(err);
      Alert.alert("Error", err.message || "Could not load lot details");
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchLotData();
  }, [lotId]);

  // Refresh data
  const onRefresh = () => {
    fetchLotData(true);
  };

  // Filter spots by status
  const filteredSpots = spots.filter((spot) => {
    if (filterStatus === "all") return true;
    // Backend returns 'current_status' or 'last_status'
    const spotStatus = spot.current_status || spot.last_status || "unknown";
    return spotStatus === filterStatus;
  });

  // Get status color
  const getStatusColor = (status: string) => {
    switch (status) {
      case "vacant":
        return "#10b981";
      case "occupied":
        return "#ef4444";
      case "reserved":
        return "#f59e0b";
      default:
        return "#6b7280";
    }
  };

  // Update spot status
  const handleUpdateSpot = (spotId: number, currentStatus: string) => {
    const statuses = ["vacant", "occupied", "reserved"];
    const currentIndex = statuses.indexOf(currentStatus);
    const nextStatus = statuses[(currentIndex + 1) % statuses.length];

    Alert.alert(
      "Update Spot Status",
      `Change spot status to ${nextStatus}?`,
      [
        { text: "Cancel", style: "cancel" },
        {
          text: "Update",
          onPress: async () => {
            try {
              await api.spots.update(lotId, spotId, { status: nextStatus });
              Alert.alert("Success", "Spot status updated");
              fetchLotData(true);
            } catch (err: any) {
              Alert.alert("Error", err.message);
            }
          },
        },
      ]
    );
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color="#1a73e8" />
      </View>
    );
  }

  if (!lot) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <Text style={{ fontSize: 16, color: "#666" }}>Lot not found</Text>
        <TouchableOpacity
          onPress={() => router.back()}
          style={{
            marginTop: 16,
            backgroundColor: "#1a73e8",
            paddingHorizontal: 20,
            paddingVertical: 12,
            borderRadius: 6,
          }}
        >
          <Text style={{ color: "white" }}>Go Back</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <View style={{ flex: 1 }}>
      {/* Header */}
      <View style={{ marginBottom: 20 }}>
        <TouchableOpacity onPress={() => router.back()} style={{ marginBottom: 12 }}>
          <Text style={{ color: "#1a73e8", fontSize: 16 }}>← Back to Lots</Text>
        </TouchableOpacity>

        <Text style={{ fontSize: 24, fontWeight: "bold", marginBottom: 8 }}>
          {lot.name}
        </Text>
        {lot.address && (
          <Text style={{ color: "#666", fontSize: 16 }}>📍 {lot.address}</Text>
        )}
      </View>

      {/* Status Overview */}
      {status && (
        <View
          style={{
            backgroundColor: "white",
            padding: 16,
            borderRadius: 8,
            marginBottom: 20,
            borderWidth: 1,
            borderColor: "#e0e0e0",
          }}
        >
          <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 12 }}>
            Live Status
          </Text>

          <View style={{ flexDirection: "row", gap: 16, marginBottom: 12 }}>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#10b981" }}>
                {status.vacant}
              </Text>
              <Text style={{ color: "#666" }}>Vacant</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#ef4444" }}>
                {status.occupied}
              </Text>
              <Text style={{ color: "#666" }}>Occupied</Text>
            </View>
            <View style={{ flex: 1 }}>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#f59e0b" }}>
                {status.reserved}
              </Text>
              <Text style={{ color: "#666" }}>Reserved</Text>
            </View>
          </View>

          {/* Occupancy Bar */}
          <View
            style={{
              height: 8,
              backgroundColor: "#e5e7eb",
              borderRadius: 4,
              overflow: "hidden",
              marginBottom: 8,
            }}
          >
            <View
              style={{
                height: "100%",
                width: `${status.occupancy_rate * 100}%`,
                backgroundColor: "#1a73e8",
              }}
            />
          </View>
          <Text style={{ fontSize: 14, color: "#666" }}>
            {Math.round(status.occupancy_rate * 100)}% Occupancy • {status.total_spots}{" "}
            Total Spots
          </Text>
          <Text style={{ fontSize: 12, color: "#999", marginTop: 4 }}>
            Last updated: {new Date(status.last_updated).toLocaleString()}
          </Text>
        </View>
      )}

      {/* Filter Buttons */}
      <ScrollView horizontal showsHorizontalScrollIndicator={false} style={{ marginBottom: 16 }}>
        <View style={{ flexDirection: "row", gap: 8 }}>
          {["all", "vacant", "occupied", "reserved"].map((filter) => (
            <TouchableOpacity
              key={filter}
              onPress={() => setFilterStatus(filter)}
              style={{
                paddingHorizontal: 16,
                paddingVertical: 8,
                borderRadius: 20,
                backgroundColor: filterStatus === filter ? "#1a73e8" : "#f3f4f6",
              }}
            >
              <Text
                style={{
                  color: filterStatus === filter ? "white" : "#374151",
                  fontWeight: "500",
                  textTransform: "capitalize",
                }}
              >
                {filter}
              </Text>
            </TouchableOpacity>
          ))}
        </View>
      </ScrollView>

      {/* Spots Grid */}
      <FlatList
        data={filteredSpots}
        keyExtractor={(item) => item.id.toString()}
        numColumns={3}
        contentContainerStyle={{ paddingBottom: 20 }}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
        }
        ListEmptyComponent={
          <View style={{ padding: 40, alignItems: "center" }}>
            <Text style={{ fontSize: 16, color: "#666" }}>
              {filterStatus === "all"
                ? "No spots in this lot yet"
                : `No ${filterStatus} spots`}
            </Text>
          </View>
        }
        renderItem={({ item }) => {
          // Backend returns current_status or last_status
          const spotStatus = item.current_status || item.last_status || "unknown";
          return (
            <TouchableOpacity
              onPress={() => handleUpdateSpot(item.id, spotStatus)}
              style={{
                flex: 1,
                margin: 4,
                aspectRatio: 1,
                backgroundColor: getStatusColor(spotStatus),
                borderRadius: 8,
                padding: 12,
                justifyContent: "center",
                alignItems: "center",
                minHeight: 100,
              }}
            >
              <Text
                style={{
                  color: "white",
                  fontSize: 20,
                  fontWeight: "bold",
                  marginBottom: 4,
                }}
              >
                {item.spot_number}
              </Text>
              <Text
                style={{
                  color: "white",
                  fontSize: 12,
                  textTransform: "capitalize",
                  opacity: 0.9,
                }}
              >
                {spotStatus}
              </Text>
            </TouchableOpacity>
          );
        }}
      />

      {/* Floating Action Button */}
      <TouchableOpacity
        onPress={onRefresh}
        style={{
          position: "absolute",
          bottom: 20,
          right: 20,
          backgroundColor: "#1a73e8",
          width: 56,
          height: 56,
          borderRadius: 28,
          justifyContent: "center",
          alignItems: "center",
          shadowColor: "#000",
          shadowOffset: { width: 0, height: 2 },
          shadowOpacity: 0.25,
          shadowRadius: 4,
          elevation: 5,
        }}
      >
        <Text style={{ color: "white", fontSize: 24 }}>↻</Text>
      </TouchableOpacity>
    </View>
  );
}