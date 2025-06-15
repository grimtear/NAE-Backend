
import { useEffect, useState } from "react";
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from "recharts";
import axios from "axios";

export default function StatusGraph() {
  const [data, setData] = useState([]);

  const fetchData = async () => {
    try {
      const res = await axios.get("/api/assets");
      const rows = res.data || [];

      const counts = rows.reduce(
        (acc, item) => {
          if (item.status === "Working") acc.working++;
          else if (item.status === "Faulty") acc.faulty++;
          else acc.unknown++;
          return acc;
        },
        { working: 0, faulty: 0, unknown: 0 }
      );

      setData([
        { name: "Working", value: counts.working },
        { name: "Faulty", value: counts.faulty },
        { name: "Unknown", value: counts.unknown },
      ]);
    } catch (err) {
      console.error("Failed to fetch asset data", err);
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 900000); // 15 min
    return () => clearInterval(interval);
  }, []);

  return (
    <ResponsiveContainer width="100%" height={300}>
      <BarChart data={data}>
        <XAxis dataKey="name" />
        <YAxis />
        <Tooltip />
        <Bar dataKey="value" />
      </BarChart>
    </ResponsiveContainer>
  );
}
