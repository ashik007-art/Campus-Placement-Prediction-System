/**
 * Placement Prediction and Skill Gap Interactive Handlers
 */
document.addEventListener("DOMContentLoaded", () => {
  const roleSelect = document.getElementById("job-role-select");
  const gapContainer = document.getElementById("skill-gap-results");

  if (roleSelect && gapContainer) {
    roleSelect.addEventListener("change", async () => {
      const roleId = roleSelect.value;
      if (!roleId) return;

      const studentId = roleSelect.getAttribute("data-student-id");
      try {
        const response = await fetch(`/recommendations/skill-gap-api?job_role_id=${roleId}&student_id=${studentId}`);
        if (!response.ok) throw new Error("Network error fetching skill gap analysis");
        const data = await response.json();

        // Update Skill Gap UI
        const progressBar = document.getElementById("skill-match-progress");
        const matchPctText = document.getElementById("skill-match-percentage");
        const matchedList = document.getElementById("matched-skills-list");
        const missingList = document.getElementById("missing-skills-list");
        const summaryText = document.getElementById("skill-gap-summary");

        if (progressBar) progressBar.style.width = `${data.match_percentage}%`;
        if (matchPctText) matchPctText.innerText = `${data.match_percentage}%`;
        if (summaryText) summaryText.innerText = data.recommendation_summary;

        if (matchedList) {
          matchedList.innerHTML = data.matched_skills.length
            ? data.matched_skills.map(s => `<span class="badge badge-success" style="margin: 2px;">${s.name}</span>`).join(" ")
            : '<span class="text-muted" style="font-size: 0.85rem;">None</span>';
        }

        if (missingList) {
          missingList.innerHTML = data.missing_skills.length
            ? data.missing_skills.map(s => `<span class="badge badge-danger" style="margin: 2px;">${s.name}</span>`).join(" ")
            : '<span class="text-muted" style="font-size: 0.85rem;">None (Full match!)</span>';
        }

        gapContainer.style.display = "block";
      } catch (err) {
        console.error("Error running skill gap analysis:", err);
      }
    });
  }
});
