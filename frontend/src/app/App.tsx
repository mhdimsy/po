import { Layout } from '../components/Layout';
import { useHashRoute } from '../hooks/useHashRoute';
import { FactoryPage } from '../pages/FactoryFloor/FactoryPage';
import { SchedulePage } from '../pages/GanttSchedule/SchedulePage';
import { ImportPage } from '../pages/ImportWizard/ImportPage';
import { MachineLinesPage } from '../pages/MachineLines/MachineLinesPage';
import { DashboardPage } from '../pages/ManagerDashboard/DashboardPage';
import { ProductTreePage } from '../pages/ProductTree/ProductTreePage';
import { ScenarioPage } from '../pages/ScenarioManager/ScenarioPage';
import { SimulationPage } from '../pages/SimulationControl/SimulationPage';
import { InventoryPage } from '../pages/SyntheticData/InventoryPage';
import { OperatorsPage } from '../pages/SyntheticData/OperatorsPage';

const pageByRoute = {
  dashboard: <DashboardPage />,
  factory: <FactoryPage />,
  lines: <MachineLinesPage />,
  productTree: <ProductTreePage />,
  import: <ImportPage />,
  scenarios: <ScenarioPage />,
  operators: <OperatorsPage />,
  inventory: <InventoryPage />,
  simulation: <SimulationPage />,
  schedule: <SchedulePage />
};

export function App() {
  const { route, navigate } = useHashRoute();
  const page = pageByRoute[route as keyof typeof pageByRoute] ?? <DashboardPage />;

  return (
    <Layout activeRoute={route} onNavigate={navigate}>
      {page}
    </Layout>
  );
}
