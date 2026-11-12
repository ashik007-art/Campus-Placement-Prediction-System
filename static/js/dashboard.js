/**
 * Dashboard Chart Initialization and Real-Time Counters
 */
document.addEventListener("DOMContentLoaded", () => {
  // Admin Department Chart
  const deptCanvas = document.getElementById("adminDeptChart");
  if (deptCanvas && typeof PlacementCharts !== "undefined" && window.DASHBOARD_DEPT_DATA) {
    const data = window.DASHBOARD_DEPT_DATA;
    const labels = data.map(d => d.department);
    const totals = data.map(d => d.total_students);
    const selected = data.map(d => d.selected_count || 0);
    PlacementCharts.createDepartmentBarChart("adminDeptChart", labels, totals, selected);
  }

  // Admin Application Status Chart
  const statusCanvas = document.getElementById("adminStatusChart");
  if (statusCanvas && typeof PlacementCharts !== "undefined" && window.DASHBOARD_STATUS_DATA) {
    const data = window.DASHBOARD_STATUS_DATA;
    const labels = data.map(s => s.status);
    const counts = data.map(s => s.count);
    PlacementCharts.createStatusDoughnut("adminStatusChart", labels, counts);
  }

  // Student Profile Radar Chart
  const studentRadarCanvas = document.getElementById("studentRadarChart");
  if (studentRadarCanvas && typeof PlacementCharts !== "undefined" && window.STUDENT_RADAR_DATA) {
    const d = window.STUDENT_RADAR_DATA;
    const labels = ["Academics (CGPA)", "Technical Skills", "Projects", "Internships", "Aptitude", "Communication"];
    const values = [
      Math.min(100, (d.cgpa / 10.0) * 100),
      Math.min(100, d.skills_count * 20),
      Math.min(100, d.projects_count * 33.3),
      Math.min(100, d.internships_count * 50),
      d.aptitude_score * 33.3,
      d.communication_score * 33.3
    ];
    PlacementCharts.createReadinessRadar("studentRadarChart", labels, values);
  }
});
