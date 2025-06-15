import express from "express";
import cors from "cors";

const app = express();
app.use(cors());
app.use(express.json());

// Sheets API route
import sheetsRoutes from "./routes/sheetsRoutes.js";
app.use("/sheets", sheetsRoutes);

// WebSocket server
import "./ws.js";

const PORT = 8085;
app.listen(PORT, () => {
  console.log(`🚀 Full Fault Status Server running at http://localhost:${PORT}`);
});
