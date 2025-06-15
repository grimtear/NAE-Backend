import { WebSocketServer } from 'ws';
import net from 'net';

// Ports to try
const tryPorts = [8085, 8086, 8087];

// Find a free port from the list
function findFreePort(ports) {
  return new Promise((resolve, reject) => {
    const checkNext = (i) => {
      if (i >= ports.length) return reject(new Error("❌ No free ports found"));

      const server = net.createServer()
        .once("error", () => {
          server.close();
          checkNext(i + 1);
        })
        .once("listening", () => {
          const port = ports[i];
          server.close(() => resolve(port));
        })
        .listen(ports[i]);
    };

    checkNext(0);
  });
}

// Start the WebSocket server
async function startWebSocket() {
  try {
    const freePort = await findFreePort(tryPorts);
    const wss = new WebSocketServer({ port: freePort });

    wss.on("connection", (socket) => {
      console.log(`[ONLINE] WebSocket connected on port ${freePort}`);
      socket.send(JSON.stringify({ 
        type: "connected", 
        data: "WebSocket connection established",
        timestamp: new Date().toISOString()
      }));

      socket.on("message", (message) => {
        try {
          const parsedMessage = JSON.parse(message.toString());
          console.log("📩 Message received:", parsedMessage);
          
          // Echo back processing updates
          if (parsedMessage.type === 'processingStart') {
            broadcast({
              type: 'processingUpdate',
              data: {
                status: 'processing',
                fileType: parsedMessage.data.fileType,
                message: 'Processing file...'
              },
              timestamp: new Date().toISOString()
            });
          }
        } catch (error) {
          console.error("Error parsing message:", error);
        }
      });

      socket.on("close", () => {
        console.log("🔌 WebSocket client disconnected");
      });

      socket.on("error", (err) => {
        console.error("⚠️ WebSocket error:", err);
      });
    });

    // Broadcast function
    function broadcast(message) {
      const json = JSON.stringify(message);
      wss.clients.forEach((client) => {
        if (client.readyState === 1) { // WebSocket.OPEN
          client.send(json);
        }
      });
    }

    // Make broadcast globally available
    global.broadcast = broadcast;

    console.log(`📡 WebSocket server is actively listening on ws://localhost:${freePort}`);
    
    // Simulate periodic data updates
    setInterval(() => {
      broadcast({
        type: 'dataUpdate',
        data: {
          timestamp: new Date().toISOString(),
          message: 'Data sync completed'
        },
        timestamp: new Date().toISOString()
      });
    }, 30000); // Every 30 seconds

  } catch (err) {
    console.error("❌ Could not start WebSocket server:", err);
  }
}

startWebSocket();