// Check for dark mode preference and store it
const isDarkMode =
  window.matchMedia &&
  window.matchMedia("(prefers-color-scheme: dark)").matches;
// Set data attribute on HTML element that we'll use for CSS selectors
document.documentElement.setAttribute(
  "data-theme",
  isDarkMode ? "dark" : "light"
);

// Store theme preference in localStorage for persistence
localStorage.setItem("preferred-theme", isDarkMode ? "dark" : "light");
