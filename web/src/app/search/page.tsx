import { AppShell } from "@/components/AppShell";
import { VehicleSearchWorkspace } from "@/components/VehicleSearchWorkspace";

export default function SearchPage() {
  return (
    <AppShell title="Vehicle Search" subtitle="Vehicle + Part · OEM · Part Name · VIN (optional)">
      <VehicleSearchWorkspace />
    </AppShell>
  );
}
