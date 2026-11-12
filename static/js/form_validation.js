/**
 * Client-Side Form Validation and Real-Time Feedback
 */
document.addEventListener("DOMContentLoaded", () => {
  // Validate CGPA inputs
  document.querySelectorAll("input[name='cgpa'], input[name='min_cgpa']").forEach((input) => {
    input.addEventListener("input", () => {
      const val = parseFloat(input.value);
      if (isNaN(val) || val < 0.0 || val > 10.0) {
        input.setCustomValidity("CGPA must be a valid number between 0.0 and 10.0");
      } else {
        input.setCustomValidity("");
      }
    });
  });

  // Validate Percentage inputs
  document.querySelectorAll("input[name*='percentage']").forEach((input) => {
    input.addEventListener("input", () => {
      const val = parseFloat(input.value);
      if (isNaN(val) || val < 0.0 || val > 100.0) {
        input.setCustomValidity("Percentage must be between 0.0 and 100.0");
      } else {
        input.setCustomValidity("");
      }
    });
  });

  // Validate Backlogs (non-negative)
  document.querySelectorAll("input[name='backlogs'], input[name='max_backlogs']").forEach((input) => {
    input.addEventListener("input", () => {
      const val = parseInt(input.value, 10);
      if (isNaN(val) || val < 0) {
        input.setCustomValidity("Backlogs must be a non-negative integer (0 or more)");
      } else {
        input.setCustomValidity("");
      }
    });
  });

  // Confirm password matching
  const pwd = document.querySelector("input[name='password']");
  const confirmPwd = document.querySelector("input[name='confirm_password']");
  if (pwd && confirmPwd) {
    const checkMatch = () => {
      if (confirmPwd.value && pwd.value !== confirmPwd.value) {
        confirmPwd.setCustomValidity("Passwords do not match");
      } else {
        confirmPwd.setCustomValidity("");
      }
    };
    pwd.addEventListener("input", checkMatch);
    confirmPwd.addEventListener("input", checkMatch);
  }
});
