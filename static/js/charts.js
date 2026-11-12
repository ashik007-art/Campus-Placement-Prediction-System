/**
 * Chart.js Visualization Helpers for Campus Placement System
 */

const PlacementCharts = {
  colors: {
    primary: "#2563eb",
    primaryLight: "rgba(37, 99, 235, 0.2)",
    success: "#10b981",
    successLight: "rgba(16, 185, 129, 0.2)",
    warning: "#f59e0b",
    warningLight: "rgba(245, 158, 11, 0.2)",
    danger: "#ef4444",
    purple: "#8b5cf6",
    cyan: "#06b6d4",
    palette: ["#2563eb", "#10b981", "#f59e0b", "#8b5cf6", "#06b6d4", "#ec4899", "#64748b"]
  },

  createDepartmentBarChart(canvasId, labels, totalStudents, selectedStudents) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === "undefined") return null;

    return new Chart(ctx, {
      type: "bar",
      data: {
        labels: labels,
        datasets: [
          {
            label: "Total Students",
            data: totalStudents,
            backgroundColor: "#93c5fd",
            borderRadius: 6
          },
          {
            label: "Selected in Drives",
            data: selectedStudents,
            backgroundColor: "#2563eb",
            borderRadius: 6
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "top" }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  },

  createStatusDoughnut(canvasId, labels, counts) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === "undefined") return null;

    return new Chart(ctx, {
      type: "doughnut",
      data: {
        labels: labels,
        datasets: [
          {
            data: counts,
            backgroundColor: [
              "#3b82f6", // Applied
              "#f59e0b", // Shortlisted
              "#8b5cf6", // Interview
              "#10b981", // Selected
              "#ef4444"  // Rejected
            ],
            borderWidth: 2,
            borderColor: "#ffffff"
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { position: "right" }
        },
        cutout: "68%"
      }
    });
  },

  createReadinessRadar(canvasId, labels, values) {
    const ctx = document.getElementById(canvasId);
    if (!ctx || typeof Chart === "undefined") return null;

    return new Chart(ctx, {
      type: "radar",
      data: {
        labels: labels,
        datasets: [{
          label: "Candidate Metric Distribution",
          data: values,
          fill: true,
          backgroundColor: "rgba(37, 99, 235, 0.2)",
          borderColor: "#2563eb",
          pointBackgroundColor: "#2563eb",
          pointBorderColor: "#fff",
          pointHoverBackgroundColor: "#fff",
          pointHoverBorderColor: "#2563eb"
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { display: true },
            suggestedMin: 0,
            suggestedMax: 100
          }
        }
      }
    });
  }
};
