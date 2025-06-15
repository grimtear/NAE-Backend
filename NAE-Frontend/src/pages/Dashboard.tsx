
import StatusGraph from "../components/StatusGraph";

export default function Dashboard() {
  return (
    <div className="p-6">
      <h1 className="text-2xl font-bold mb-4">📊 Asset Health Dashboard</h1>
      <StatusGraph />
    </div>
  );
}
