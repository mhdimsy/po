export type HealthResponse = {
  status: string;
};

export type ImportValidationReport = {
  import_ready: boolean;
  total_rows: number;
  files: Array<{
    file_name: string;
    row_count: number;
    errors: Array<{
      file_name: string;
      row_number: number | null;
      severity: string;
      code: string;
      message: string;
      field_name?: string | null;
      raw_value?: string | null;
    }>;
    warnings: Array<{
      file_name: string;
      row_number: number | null;
      severity: string;
      code: string;
      message: string;
      field_name?: string | null;
      raw_value?: string | null;
    }>;
  }>;
  issues: Array<{
    file_name: string;
    row_number: number | null;
    severity: string;
    code: string;
    message: string;
  }>;
};

export type RebuildDemoResponse = {
  import_report: {
    import_batch_id: number;
    import_ready: boolean;
    total_rows: number;
    imported_rows_by_file: Record<string, number>;
    created_entity_counts: Record<string, number>;
    issues: Array<{
      file_name: string;
      row_number: number | null;
      severity: string;
      code: string;
      message: string;
    }>;
  };
  scenario_id: number;
  scenario_name: string;
  orders_seeded: number;
  operations_seeded: number;
  machines_seeded: number;
};

export type Scenario = {
  id: number;
  name: string;
  status: string;
  parent_scenario_id: number | null;
  base_snapshot_id: number | null;
  base_import_batch_id: number | null;
};

export type ScenarioSeedResponse = {
  scenario_id: number;
  import_batch_id: number;
  orders_seeded: number;
  operations_seeded: number;
  machines_seeded: number;
  skipped_orders_without_routing: number;
  max_orders: number;
};

export type ProductTreeOperationSummary = {
  total: number;
  queued: number;
  setup: number;
  running: number;
  finished: number;
  blocked: number;
  other: number;
};

export type ProductTreeNode = {
  order_id: string;
  order_code: string | null;
  product_code: string | null;
  status: string;
  computed_status: string;
  assignment_status: string | null;
  operation_summary: ProductTreeOperationSummary;
  children: ProductTreeNode[];
};

export type ProductTreeResponse = {
  scenario_id: number;
  root_count: number;
  total_orders_in_scope: number;
  max_depth: number;
  roots: ProductTreeNode[];
};

export type Operator = {
  id: number;
  code: string;
  full_name: string;
  home_work_center_id: number | null;
  primary_shift_id: number | null;
  status: string;
};

export type InventoryItem = {
  id: number;
  bom_id: number;
  code: string;
  title: string;
  unit: string;
};

export type InventoryBalance = {
  id: number;
  inventory_item_id: number;
  warehouse_id: number;
  on_hand_qty: number;
  reserved_qty: number;
  safety_stock_qty: number;
  preset: string;
};

export type SimulationRun = {
  id: number;
  scenario_id: number;
  status: string;
  speed_factor: number;
  current_sim_time: number;
  started_at?: string;
  paused_at?: string | null;
  stopped_at?: string | null;
};

export type SimulationStepResponse = {
  run: SimulationRun;
  events_created: number;
  operation_transition: {
    operation_id: string;
    machine_id?: string | null;
    operator_id?: string | null;
    previous_status: string;
    next_status: string;
    event_type: string;
  } | null;
  operation_transitions?: Array<{
    operation_id: string;
    machine_id?: string | null;
    operator_id?: string | null;
    previous_status: string;
    next_status: string;
    event_type: string;
  }>;
};

export type FactoryEvent = {
  event_id: number;
  event_type: string;
  aggregate_type: string;
  aggregate_id: string;
  scenario_id: number | null;
  payload_json: Record<string, unknown>;
  simulation_time: number | null;
  created_at: string;
};

export type OptimizationRun = {
  id: number;
  scenario_id: number;
  status: string;
  score: number;
  changed_operations_count: number;
};

export type ScheduleOperation = {
  id: number;
  operation_id: string;
  order_id: string | null;
  machine_id: string | null;
  operator_id: string | null;
  start_time: number;
  end_time: number;
  status: string;
  score: number;
  reason_json: {
    blocked_reason?: string | null;
    constraints_checked?: string[];
    [key: string]: unknown;
  };
};

export type CurrentOperationState = {
  id: number;
  scenario_id: number | null;
  operation_id: string;
  order_id: string | null;
  machine_id: string | null;
  operator_id: string | null;
  status: string;
  simulation_time: number | null;
  payload_json: Record<string, unknown>;
};

export type CurrentMachineState = {
  id: number;
  scenario_id: number | null;
  machine_id: string;
  status: string;
  current_operation_id: string | null;
  simulation_time: number | null;
  payload_json: Record<string, unknown>;
};

export type RiskSettings = {
  delay_risk_weight: number;
  material_shortage_risk_weight: number;
  machine_failure_risk_weight: number;
  qc_ncr_risk_weight: number;
  schedule_instability_weight: number;
  low_threshold: number;
  medium_threshold: number;
  high_threshold: number;
};

export type RiskScore = {
  id: number;
  scenario_id: number;
  aggregate_type: string;
  aggregate_id: string;
  total_score: number;
  level: string;
  components_json: Record<string, number>;
  calculated_at: string;
};

export type RiskCalculationResponse = {
  scenario_id: number;
  scores_created: number;
  scenario_risk: RiskScore;
  scores: RiskScore[];
};

export type ManagerDashboard = {
  scenario_id: number | null;
  delivery: {
    total_orders: number;
    completed_orders: number;
    delayed_orders: number;
    on_time_rate_percent: number;
  };
  delay: {
    delayed_operations: number;
    waiting_material_operations: number;
    waiting_machine_operations: number;
    waiting_qc_operations: number;
  };
  production_progress: {
    total_operations: number;
    finished_operations: number;
    active_operations: number;
    queued_operations: number;
    completion_percent: number;
  };
  capacity: {
    total_machines: number;
    busy_machines: number;
    unavailable_machines: number;
    machine_utilization_percent: number;
    total_operators: number;
    busy_operators: number;
    operator_utilization_percent: number;
  };
  bottleneck: Array<{
    resource_id: string;
    queued_operations: number;
  }>;
  material_shortage: {
    shortage_items: number;
    reserved_items: number;
    open_purchase_requests: number;
    top_shortages: Array<Record<string, unknown>>;
  };
  ncr_rework: {
    open_ncrs: number;
    high_severity_ncrs: number;
    active_rework_orders: number;
    estimated_delay_min: number;
  };
  optimizer_performance: {
    latest_run_id: number | null;
    status: string | null;
    score: number | null;
    changed_operations_count: number;
    suggested_operations: number;
    accepted_operations: number;
  };
  risk: RiskScore[];
};
