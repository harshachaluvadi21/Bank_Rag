import axios from "axios";
import { ChatRequest, ChatResponse, HealthResponse } from "@/types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL ? `${process.env.NEXT_PUBLIC_API_URL}/api` : "http://localhost:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const getHealthStatus = async (): Promise<HealthResponse> => {
  const response = await apiClient.get<HealthResponse>("/health");
  return response.data;
};

export const sendChatMessage = async (data: ChatRequest): Promise<ChatResponse> => {
  const response = await apiClient.post<ChatResponse>("/chat", data);
  return response.data;
};
