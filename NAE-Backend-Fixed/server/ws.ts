import { WebSocketServer } from "ws";

const wss = new WebSocketServer({ port: 8085 });
console.log("📡 WebSocket server listening on ws://localhost:8085");

wss.on("connection", (socket) => {
  console.log("⚡ WebSocket client connected");
  socket.send(JSON.stringify({ event: "welcome", payload: "🦊 Connected to Fault Status Server" }));
});
