// lib/api.ts
import { authStorage } from "./auth-storage";

const API_URL = "http://localhost:8000"; // Change when deployed

// Helper to get auth headers
async function getAuthHeaders() {
  const token = await authStorage.get();
  return {
    "Content-Type": "application/json",
    ...(token && { Authorization: `Bearer ${token}` }),
  };
}

// Helper for API requests
async function apiRequest(
  endpoint: string,
  options: RequestInit = {}
): Promise<any> {
  const headers = await getAuthHeaders();
  const res = await fetch(`${API_URL}${endpoint}`, {
    ...options,
    headers: { ...headers, ...options.headers },
  });

  if (!res.ok) {
    const error = await res.json().catch(() => ({ detail: "Unknown error" }));
    throw new Error(error.detail || `Request failed: ${res.status}`);
  }

  // Handle 204 No Content
  if (res.status === 204) return null;

  return res.json();
}

export const api = {
  // ============================================================================
  // AUTHENTICATION
  // ============================================================================
  auth: {
    login: async (username: string, password: string) => {
      return apiRequest("/auth/login", {
        method: "POST",
        body: JSON.stringify({ username, password }),
      });
    },

    register: async (username: string, email: string, password: string) => {
      return apiRequest("/auth/register", {
        method: "POST",
        body: JSON.stringify({ username, email, password }),
      });
    },

    getUser: async (userId: number) => {
      return apiRequest(`/auth/users/${userId}`);
    },

    getAllUsers: async () => {
      return apiRequest("/auth/users");
    },

    updateUser: async (
      userId: number,
      data: { username?: string; email?: string; password?: string }
    ) => {
      return apiRequest(`/auth/users/${userId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      });
    },

    deleteUser: async (userId: number) => {
      return apiRequest(`/auth/users/${userId}`, {
        method: "DELETE",
      });
    },
  },

  // ============================================================================
  // PARKING LOTS
  // ============================================================================
  lots: {
    // Get all parking lots
    getAll: async () => {
      return apiRequest("/lots/");
    },

    // Get specific parking lot
    get: async (lotId: number) => {
      return apiRequest(`/lots/${lotId}`);
    },

    // Create parking lot
    create: async (data: {
      name: string;
      address?: string;
      total_spaces: number;
      description?: string;
      init_frame_path?: string;
      video_path?: string;
      video_start_time?: number;
    }) => {
      return apiRequest("/lots/", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    // Update parking lot
    update: async (lotId: number, data: any) => {
      return apiRequest(`/lots/${lotId}`, {
        method: "PUT",
        body: JSON.stringify(data),
      });
    },

    // Delete parking lot
    delete: async (lotId: number) => {
      return apiRequest(`/lots/${lotId}`, {
        method: "DELETE",
      });
    },

    // Initialize lot from annotations
    initFromAnnotations: async (lotId: number, annotations: any) => {
      return apiRequest(`/lots/${lotId}/init`, {
        method: "POST",
        body: JSON.stringify(annotations),
      });
    },

    // Get lot status summary
    getStatus: async (lotId: number) => {
      return apiRequest(`/lots/${lotId}/status`);
    },

    // List spots with status
    getSpots: async (lotId: number) => {
      return apiRequest(`/lots/${lotId}/spots`);
    },

    // Bulk update spots
    bulkUpdateSpots: async (lotId: number, updates: any[]) => {
      return apiRequest(`/lots/${lotId}/bulk_update`, {
        method: "POST",
        body: JSON.stringify(updates),
      });
    },
  },

  // ============================================================================
  // PARKING SPOTS
  // ============================================================================
  spots: {
    // Update single spot
    update: async (lotId: number, spotId: number, data: any) => {
      return apiRequest(`/lots/${lotId}/spots/${spotId}/update`, {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    // Get spot latest status
    getStatus: async (lotId: number, spotId: number) => {
      return apiRequest(`/lots/${lotId}/spots/${spotId}/status`);
    },
  },

  // ============================================================================
  // COMPUTER VISION / AI
  // ============================================================================
  cv: {
    // Post spot status (standard detection)
    postSpotStatus: async (data: {
      lot_id: number;
      frame_data: any;
      timestamp?: string;
      [key: string]: any;
    }) => {
      return apiRequest("/cv/spot_status/", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },

    // Post spot status by bounding box
    postSpotStatusByBbox: async (data: {
      lot_id: number;
      bboxes: Array<{ x: number; y: number; width: number; height: number }>;
      frame_data?: any;
      timestamp?: string;
      [key: string]: any;
    }) => {
      return apiRequest("/cv/spot_status_by_bbox/", {
        method: "POST",
        body: JSON.stringify(data),
      });
    },
  },
};

// ============================================================================
// TYPE DEFINITIONS (optional but recommended)
// ============================================================================

export interface ParkingLot {
  id: number;
  name: string;
  address?: string;
  total_spaces: number;
  description?: string;
  init_frame_path?: string;
  video_path?: string;
  video_start_time?: number;
  created_at: string;
  updated_at: string;
}

export interface ParkingSpot {
  id: number;
  lot_id?: number;
  parking_lot_id?: number;
  spot_number: string;
  status?: "occupied" | "vacant" | "reserved" | "unknown";
  current_status?: "occupied" | "vacant" | "reserved" | "unknown" | null;
  last_status?: "occupied" | "vacant" | "reserved" | "unknown" | null;
  last_detected_at?: string | null;
  last_meta?: any;
  x?: number;
  y?: number;
  width?: number;
  height?: number;
  polygon?: any;
  annotation_id?: number;
  created_at?: string;
}

export interface LotStatus {
  lot_id: number;
  total_spots: number;
  occupied: number;
  vacant: number;
  reserved: number;
  occupancy_rate: number;
  last_updated: string;
}

export interface User {
  id: number;
  username: string;
  email: string;
  is_admin: boolean;
  created_at: string;
  last_login: string | null;
}