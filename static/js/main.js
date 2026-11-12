/**
 * Campus Placement Prediction System - Main Interactive Controller
 */
document.addEventListener("DOMContentLoaded", () => {
  // Mobile sidebar toggle
  const mobileBtn = document.querySelector(".mobile-menu-btn");
  const sidebar = document.querySelector(".app-sidebar");
  
  if (mobileBtn && sidebar) {
    mobileBtn.addEventListener("click", () => {
      sidebar.classList.toggle("sidebar-open");
    });

    // Close when clicking outside
    document.addEventListener("click", (e) => {
      if (!sidebar.contains(e.target) && !mobileBtn.contains(e.target) && sidebar.classList.contains("sidebar-open")) {
        sidebar.classList.remove("sidebar-open");
      }
    });
  }

  // Dismiss flash alerts
  document.querySelectorAll(".alert-close").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const alert = e.target.closest(".alert");
      if (alert) {
        alert.style.opacity = "0";
        setTimeout(() => alert.remove(), 250);
      }
    });
  });

  // Generic modal openers
  document.querySelectorAll("[data-open-modal]").forEach((trigger) => {
    trigger.addEventListener("click", (e) => {
      e.preventDefault();
      const targetModalId = trigger.getAttribute("data-open-modal");
      const modal = document.getElementById(targetModalId);
      if (modal) modal.classList.add("active");
    });
  });

  // Modal closers
  document.querySelectorAll("[data-close-modal], .modal-overlay").forEach((el) => {
    el.addEventListener("click", (e) => {
      if (e.target === el || el.hasAttribute("data-close-modal")) {
        const modal = el.closest(".modal-overlay");
        if (modal) modal.classList.remove("active");
      }
    });
  });

  // Destructive action confirmation dialogs
  document.querySelectorAll("[data-confirm]").forEach((btn) => {
    btn.addEventListener("click", (e) => {
      const msg = btn.getAttribute("data-confirm") || "Are you sure you want to perform this action?";
      if (!confirm(msg)) {
        e.preventDefault();
      }
    });
  });
});
