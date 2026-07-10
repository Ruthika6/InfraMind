export const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

// Derive WebSocket URL from HTTP URL (e.g. http://api... -> ws://api... or https://api... -> wss://api...)
export const WS_BASE_URL = API_BASE_URL.replace(/^http/, "ws");
