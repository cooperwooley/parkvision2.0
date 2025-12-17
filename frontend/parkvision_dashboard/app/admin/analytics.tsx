// app/admin/analytics.tsx
import { useState, useEffect } from "react";
import {
  View,
  Text,
  ScrollView,
  ActivityIndicator,
  RefreshControl,
  Dimensions,
} from "react-native";
import { api, ParkingLot, LotStatus } from "../../src/api";

export default function AnalyticsPage() {
  const [lots, setLots] = useState<ParkingLot[]>([]);
  const [lotStatuses, setLotStatuses] = useState<{ [key: number]: LotStatus }>({});
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch data
  const fetchAnalytics = async (isRefresh = false) => {
    try {
      if (isRefresh) setRefreshing(true);
      else setLoading(true);

      const lotsData = await api.lots.getAll();
      setLots(lotsData);

      // Fetch status for each lot
      const statuses: { [key: number]: LotStatus } = {};
      await Promise.all(
        lotsData.map(async (lot: ParkingLot) => {
          try {
            const statusResponse = await api.lots.getStatus(lot.id);
            // Handle the response format: {lot_id, summary}
            const summary = statusResponse.summary || {};
            const spotStatuses = Object.values(summary);
            
            statuses[lot.id] = {
              lot_id: lot.id,
              total_spots: spotStatuses.length,
              vacant: spotStatuses.filter((s: any) => s === "vacant").length,
              occupied: spotStatuses.filter((s: any) => s === "occupied").length,
              reserved: spotStatuses.filter((s: any) => s === "reserved").length,
              occupancy_rate:
                spotStatuses.length > 0
                  ? spotStatuses.filter((s: any) => s === "occupied").length /
                    spotStatuses.length
                  : 0,
              last_updated: new Date().toISOString(),
            };
          } catch (err) {
            console.error(`Failed to fetch status for lot ${lot.id}`, err);
          }
        })
      );
      setLotStatuses(statuses);
    } catch (err: any) {
      console.error("Analytics error:", err);
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  useEffect(() => {
    fetchAnalytics();
  }, []);

  const onRefresh = () => {
    fetchAnalytics(true);
  };

  // Calculate overall statistics
  const calculateOverallStats = () => {
    const statuses = Object.values(lotStatuses);
    if (statuses.length === 0) {
      return {
        totalSpots: 0,
        totalOccupied: 0,
        totalVacant: 0,
        totalReserved: 0,
        averageOccupancy: 0,
      };
    }

    const totalSpots = statuses.reduce((sum, s) => sum + s.total_spots, 0);
    const totalOccupied = statuses.reduce((sum, s) => sum + s.occupied, 0);
    const totalVacant = statuses.reduce((sum, s) => sum + s.vacant, 0);
    const totalReserved = statuses.reduce((sum, s) => sum + s.reserved, 0);
    const averageOccupancy =
      statuses.reduce((sum, s) => sum + s.occupancy_rate, 0) / statuses.length;

    return {
      totalSpots,
      totalOccupied,
      totalVacant,
      totalReserved,
      averageOccupancy,
    };
  };

  const overallStats = calculateOverallStats();

  // Get top performing lots
  const getTopLots = () => {
    return Object.entries(lotStatuses)
      .map(([id, status]) => ({
        id: parseInt(id),
        name: lots.find((l) => l.id === parseInt(id))?.name || "Unknown",
        occupancy: status.occupancy_rate,
        occupied: status.occupied,
        total: status.total_spots,
      }))
      .sort((a, b) => b.occupancy - a.occupancy)
      .slice(0, 5);
  };

  if (loading) {
    return (
      <View style={{ flex: 1, justifyContent: "center", alignItems: "center" }}>
        <ActivityIndicator size="large" color="#1a73e8" />
      </View>
    );
  }

  return (
    <ScrollView
      style={{ flex: 1 }}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} />
      }
    >
      <Text style={{ fontSize: 24, fontWeight: "bold", marginBottom: 20 }}>
        Analytics Dashboard
      </Text>

      {lots.length === 0 ? (
        <View
          style={{
            padding: 40,
            alignItems: "center",
            backgroundColor: "white",
            borderRadius: 8,
          }}
        >
          <Text style={{ fontSize: 16, color: "#666" }}>
            No parking lots to analyze yet
          </Text>
        </View>
      ) : (
        <>
          {/* Overall Stats Cards */}
          <View
            style={{
              flexDirection: "row",
              flexWrap: "wrap",
              gap: 12,
              marginBottom: 24,
            }}
          >
            {/* Total Spots */}
            <View
              style={{
                flex: 1,
                minWidth: 150,
                backgroundColor: "white",
                padding: 20,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: "#e0e0e0",
              }}
            >
              <Text style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
                Total Spots
              </Text>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#1a73e8" }}>
                {overallStats.totalSpots}
              </Text>
            </View>

            {/* Occupied */}
            <View
              style={{
                flex: 1,
                minWidth: 150,
                backgroundColor: "white",
                padding: 20,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: "#e0e0e0",
              }}
            >
              <Text style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
                Occupied
              </Text>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#ef4444" }}>
                {overallStats.totalOccupied}
              </Text>
            </View>

            {/* Vacant */}
            <View
              style={{
                flex: 1,
                minWidth: 150,
                backgroundColor: "white",
                padding: 20,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: "#e0e0e0",
              }}
            >
              <Text style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
                Vacant
              </Text>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#10b981" }}>
                {overallStats.totalVacant}
              </Text>
            </View>

            {/* Reserved */}
            <View
              style={{
                flex: 1,
                minWidth: 150,
                backgroundColor: "white",
                padding: 20,
                borderRadius: 8,
                borderWidth: 1,
                borderColor: "#e0e0e0",
              }}
            >
              <Text style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
                Reserved
              </Text>
              <Text style={{ fontSize: 32, fontWeight: "bold", color: "#f59e0b" }}>
                {overallStats.totalReserved}
              </Text>
            </View>
          </View>

          {/* Average Occupancy */}
          <View
            style={{
              backgroundColor: "white",
              padding: 20,
              borderRadius: 8,
              marginBottom: 24,
              borderWidth: 1,
              borderColor: "#e0e0e0",
            }}
          >
            <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 16 }}>
              Average Occupancy Rate
            </Text>
            <View
              style={{
                height: 40,
                backgroundColor: "#f3f4f6",
                borderRadius: 8,
                overflow: "hidden",
              }}
            >
              <View
                style={{
                  height: "100%",
                  width: `${overallStats.averageOccupancy * 100}%`,
                  backgroundColor: "#1a73e8",
                  justifyContent: "center",
                  paddingLeft: 12,
                }}
              >
                <Text style={{ color: "white", fontWeight: "bold" }}>
                  {Math.round(overallStats.averageOccupancy * 100)}%
                </Text>
              </View>
            </View>
          </View>

          {/* Top Performing Lots */}
          <View
            style={{
              backgroundColor: "white",
              padding: 20,
              borderRadius: 8,
              marginBottom: 24,
              borderWidth: 1,
              borderColor: "#e0e0e0",
            }}
          >
            <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 16 }}>
              Lot Performance
            </Text>
            {getTopLots().map((lot, index) => (
              <View
                key={lot.id}
                style={{
                  marginBottom: 16,
                  paddingBottom: 16,
                  borderBottomWidth:
                    index < getTopLots().length - 1 ? 1 : 0,
                  borderBottomColor: "#e5e7eb",
                }}
              >
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    marginBottom: 8,
                  }}
                >
                  <Text style={{ fontSize: 16, fontWeight: "500" }}>
                    {lot.name}
                  </Text>
                  <Text style={{ fontSize: 16, fontWeight: "600", color: "#1a73e8" }}>
                    {Math.round(lot.occupancy * 100)}%
                  </Text>
                </View>
                <Text style={{ fontSize: 14, color: "#666", marginBottom: 8 }}>
                  {lot.occupied} / {lot.total} spots occupied
                </Text>
                <View
                  style={{
                    height: 8,
                    backgroundColor: "#f3f4f6",
                    borderRadius: 4,
                    overflow: "hidden",
                  }}
                >
                  <View
                    style={{
                      height: "100%",
                      width: `${lot.occupancy * 100}%`,
                      backgroundColor:
                        lot.occupancy > 0.8
                          ? "#ef4444"
                          : lot.occupancy > 0.5
                          ? "#f59e0b"
                          : "#10b981",
                    }}
                  />
                </View>
              </View>
            ))}
          </View>

          {/* Status Distribution */}
          <View
            style={{
              backgroundColor: "white",
              padding: 20,
              borderRadius: 8,
              marginBottom: 24,
              borderWidth: 1,
              borderColor: "#e0e0e0",
            }}
          >
            <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 16 }}>
              Status Distribution
            </Text>
            <View style={{ gap: 12 }}>
              {/* Occupied Bar */}
              <View>
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    marginBottom: 6,
                  }}
                >
                  <Text style={{ fontSize: 14, color: "#666" }}>Occupied</Text>
                  <Text style={{ fontSize: 14, fontWeight: "600" }}>
                    {overallStats.totalOccupied} (
                    {overallStats.totalSpots > 0
                      ? Math.round(
                          (overallStats.totalOccupied / overallStats.totalSpots) *
                            100
                        )
                      : 0}
                    %)
                  </Text>
                </View>
                <View
                  style={{
                    height: 24,
                    backgroundColor: "#fee2e2",
                    borderRadius: 4,
                  }}
                >
                  <View
                    style={{
                      height: "100%",
                      width: `${
                        overallStats.totalSpots > 0
                          ? (overallStats.totalOccupied / overallStats.totalSpots) *
                            100
                          : 0
                      }%`,
                      backgroundColor: "#ef4444",
                      borderRadius: 4,
                    }}
                  />
                </View>
              </View>

              {/* Vacant Bar */}
              <View>
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    marginBottom: 6,
                  }}
                >
                  <Text style={{ fontSize: 14, color: "#666" }}>Vacant</Text>
                  <Text style={{ fontSize: 14, fontWeight: "600" }}>
                    {overallStats.totalVacant} (
                    {overallStats.totalSpots > 0
                      ? Math.round(
                          (overallStats.totalVacant / overallStats.totalSpots) * 100
                        )
                      : 0}
                    %)
                  </Text>
                </View>
                <View
                  style={{
                    height: 24,
                    backgroundColor: "#d1fae5",
                    borderRadius: 4,
                  }}
                >
                  <View
                    style={{
                      height: "100%",
                      width: `${
                        overallStats.totalSpots > 0
                          ? (overallStats.totalVacant / overallStats.totalSpots) * 100
                          : 0
                      }%`,
                      backgroundColor: "#10b981",
                      borderRadius: 4,
                    }}
                  />
                </View>
              </View>

              {/* Reserved Bar */}
              <View>
                <View
                  style={{
                    flexDirection: "row",
                    justifyContent: "space-between",
                    marginBottom: 6,
                  }}
                >
                  <Text style={{ fontSize: 14, color: "#666" }}>Reserved</Text>
                  <Text style={{ fontSize: 14, fontWeight: "600" }}>
                    {overallStats.totalReserved} (
                    {overallStats.totalSpots > 0
                      ? Math.round(
                          (overallStats.totalReserved / overallStats.totalSpots) *
                            100
                        )
                      : 0}
                    %)
                  </Text>
                </View>
                <View
                  style={{
                    height: 24,
                    backgroundColor: "#fef3c7",
                    borderRadius: 4,
                  }}
                >
                  <View
                    style={{
                      height: "100%",
                      width: `${
                        overallStats.totalSpots > 0
                          ? (overallStats.totalReserved / overallStats.totalSpots) *
                            100
                          : 0
                      }%`,
                      backgroundColor: "#f59e0b",
                      borderRadius: 4,
                    }}
                  />
                </View>
              </View>
            </View>
          </View>

          {/* All Lots Summary */}
          <View
            style={{
              backgroundColor: "white",
              padding: 20,
              borderRadius: 8,
              marginBottom: 24,
              borderWidth: 1,
              borderColor: "#e0e0e0",
            }}
          >
            <Text style={{ fontSize: 18, fontWeight: "600", marginBottom: 16 }}>
              All Lots Summary
            </Text>
            {lots.map((lot) => {
              const status = lotStatuses[lot.id];
              if (!status) return null;

              return (
                <View
                  key={lot.id}
                  style={{
                    marginBottom: 16,
                    paddingBottom: 16,
                    borderBottomWidth: 1,
                    borderBottomColor: "#e5e7eb",
                  }}
                >
                  <Text style={{ fontSize: 16, fontWeight: "500", marginBottom: 8 }}>
                    {lot.name}
                  </Text>
                  <View style={{ flexDirection: "row", gap: 16 }}>
                    <View>
                      <Text style={{ fontSize: 12, color: "#666" }}>Total</Text>
                      <Text style={{ fontSize: 18, fontWeight: "600" }}>
                        {status.total_spots}
                      </Text>
                    </View>
                    <View>
                      <Text style={{ fontSize: 12, color: "#10b981" }}>Vacant</Text>
                      <Text style={{ fontSize: 18, fontWeight: "600", color: "#10b981" }}>
                        {status.vacant}
                      </Text>
                    </View>
                    <View>
                      <Text style={{ fontSize: 12, color: "#ef4444" }}>Occupied</Text>
                      <Text style={{ fontSize: 18, fontWeight: "600", color: "#ef4444" }}>
                        {status.occupied}
                      </Text>
                    </View>
                    <View>
                      <Text style={{ fontSize: 12, color: "#f59e0b" }}>Reserved</Text>
                      <Text style={{ fontSize: 18, fontWeight: "600", color: "#f59e0b" }}>
                        {status.reserved}
                      </Text>
                    </View>
                    <View>
                      <Text style={{ fontSize: 12, color: "#666" }}>Rate</Text>
                      <Text style={{ fontSize: 18, fontWeight: "600", color: "#1a73e8" }}>
                        {Math.round(status.occupancy_rate * 100)}%
                      </Text>
                    </View>
                  </View>
                </View>
              );
            })}
          </View>
        </>
      )}
    </ScrollView>
  );
}