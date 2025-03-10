let currentImageIndex = 0;
let currentGalleryImages = [];

document.addEventListener("DOMContentLoaded", () => {
  // Global variable for CAPTCHA verification data
  window.captchaVerification = null;
  // Cross-browser theme detection
  function detectSystemTheme() {
    // First check localStorage
    const storedTheme = localStorage.getItem("preferred-theme");
    if (storedTheme) {
      return storedTheme;
    }

    // Then check media query
    if (
      window.matchMedia &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
    ) {
      return "dark";
    }

    // Default to light
    return "light";
  }

  // Apply theme
  function applyTheme(theme) {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("preferred-theme", theme);
  }

  // Set initial theme
  applyTheme(detectSystemTheme());

  // Listen for system theme changes
  if (window.matchMedia) {
    window
      .matchMedia("(prefers-color-scheme: dark)")
      .addEventListener("change", (e) => {
        const newTheme = e.matches ? "dark" : "light";
        applyTheme(newTheme);
      });
  }

  // DOM Elements
  const landingSection = document.getElementById("landing");
  const searchSection = document.getElementById("search");
  const statusMessage = document.getElementById("status");
  const statusIcon = document.getElementById("status-icon");
  const statusText = document.getElementById("status-text");
  const resultsSection = document.getElementById("results");
  const startButton = document.getElementById("start-btn");
  const findButton = document.getElementById("find-btn");
  const searchInput = document.getElementById("search-input");
  const modal = document.getElementById("image-modal");
  const modalImg = document.getElementById("modal-img");
  const closeModal = modal.querySelector(".modal-close");

  // User's location
  let userLocation = null;

  // Start button click handler
  startButton.addEventListener("click", () => {
    landingSection.classList.add("hidden");
    searchSection.classList.remove("hidden");
  });

  // Find button click handler
  findButton.addEventListener("click", () => {
    const searchQuery = searchInput.value.trim();

    if (!searchQuery) {
      showStatus("alert", "Please enter what you're looking for.");
      return;
    }

    // Show CAPTCHA before proceeding
    showCaptcha(() => {
      // This function runs after successful CAPTCHA verification

      // Ask for location permission
      showStatus(
        "info",
        "To find places near you, we need your location permission."
      );

      if (navigator.geolocation) {
        navigator.geolocation.getCurrentPosition(
          // Success callback
          (position) => {
            userLocation = {
              latitude: position.coords.latitude,
              longitude: position.coords.longitude,
            };

            showStatus("loading", "Finding places near you...");
            searchForPlaces(searchQuery);
          },
          // Error callback
          (error) => {
            showStatus(
              "error",
              "We need your location to help you find places nearby. Please enable location permissions and try again."
            );
          }
        );
      } else {
        showStatus(
          "error",
          "Your browser doesn't support geolocation. Please try using a different browser."
        );
      }
    });
  });

  // Show status message
  function showStatus(type, message) {
    statusText.textContent = message;

    // Set icon based on status type
    switch (type) {
      case "error":
        statusIcon.innerHTML = '<i class="ri-error-warning-line icon-red"></i>';
        break;
      case "success":
        statusIcon.innerHTML = '<i class="ri-check-line icon-green"></i>';
        break;
      case "info":
        statusIcon.innerHTML = '<i class="ri-information-line icon-blue"></i>';
        break;
      case "loading":
        statusIcon.innerHTML =
          '<i class="ri-loader-4-line icon-blue animate-spin"></i>';
        break;
      case "alert":
        statusIcon.innerHTML = '<i class="ri-alert-line icon-yellow"></i>';
        break;
    }

    statusMessage.classList.remove("hidden");

    if (type === "error") {
      resultsSection.classList.add("hidden");
    }
  }

  // Search for places function
  async function searchForPlaces(query) {
    try {
      // Format the location string
      const locationString = `${userLocation.latitude},${userLocation.longitude}`;

      // Make the API request to the process endpoint
      const response = await fetch("/process", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          query: query,
          location: locationString,
          captcha_id: window.captchaVerification.captcha_id,
          captcha_answer: window.captchaVerification.captcha_answer,
        }),
      });

      // Clear the stored CAPTCHA data
      window.captchaVerification = null;

      if (!response.ok) {
        // Get error message from the response if possible
        let errorMessage;
        try {
          const errorData = await response.json();
          errorMessage = errorData.message || "Unknown error occurred";
        } catch (e) {
          errorMessage = `Server error: ${response.status}`;
        }

        // Handle CAPTCHA-specific errors
        if (response.status === 403 && errorMessage.includes("CAPTCHA")) {
          showStatus(
            "error",
            "CAPTCHA verification failed. Please try your search again."
          );
          return;
        }

        // Creative error messages based on status codes
        if (response.status === 404) {
          showStatus(
            "error",
            "Hmm, our AI explorer seems to have wandered off the map. Please try again later!"
          );
        } else if (response.status === 429) {
          showStatus(
            "error",
            "Whoa there! Our AI is catching its breath. Please wait a moment before searching again."
          );
        } else if (response.status >= 500) {
          showStatus(
            "error",
            "Our servers are having a coffee break. Please try again when they're properly caffeinated!"
          );
        } else {
          showStatus("error", `Something unexpected happened: ${errorMessage}`);
        }
        return;
      }

      // Parse the JSON response
      const data = await response.json();

      // Check if the data has the expected format
      if (!data || !data.places || !Array.isArray(data.places)) {
        showStatus(
          "error",
          "We received a mysterious response from our AI. Please try again later!"
        );
        return;
      }

      // Display the results
      displayResults(data.places);
    } catch (error) {
      console.error("Search error:", error);
      showStatus(
        "error",
        "Looks like our AI got lost in the digital wilderness. Please check your connection and try again!"
      );
    }
  }

  // Display results
  function displayResults(places) {
    if (!places || places.length === 0) {
      showStatus(
        "alert",
        "No places found matching your search. Please try a different keyword."
      );
      return;
    }

    statusMessage.classList.add("hidden");
    resultsSection.classList.remove("hidden");
    resultsSection.innerHTML = "";

    // Add results heading
    const resultsHeading = document.createElement("h2");
    resultsHeading.className = "results-heading";
    resultsHeading.textContent = "Places near you";
    resultsSection.appendChild(resultsHeading);

    places.forEach((place) => {
      const placeCard = document.createElement("div");
      placeCard.className = "place-card";

      // Create image gallery if images exist
      let imageGallery = "";
      if (place.images && place.images.length > 0) {
        imageGallery = `
          <div class="image-gallery">
            ${place.images
              .map(
                (img) =>
                  `<img src="${img}" class="gallery-image" alt="${place.name}">`
              )
              .join("")}
          </div>
        `;
      }

      placeCard.innerHTML = `
        <div class="place-content">
          <div class="place-header">
            <h3 class="place-name">${place.name}</h3>
            <span class="place-rating">
              <i class="ri-star-fill"></i>
              ${place.rating.toFixed(1)} <span class="rating-count">(${
        place.ratingCount || 0
      })</span>
            </span>
          </div>
          <div class="place-address">
            <i class="ri-map-pin-line"></i>
            <span>${place.address}</span>
          </div>
          <div>
            <h4 class="review-heading">AI Review Summary</h4>
            <p class="review-summary">${place.reviewSummary}</p>
          </div>
        </div>
        ${imageGallery}
        <div class="card-actions">
          <button class="btn btn-primary btn-full">
            <i class="ri-map-2-line"></i>
            <span>Open in Google Maps</span>
          </button>
        </div>
      `;

      // Add click event to open in Google Maps
      const mapButton = placeCard.querySelector(".btn");
      mapButton.addEventListener("click", () => {
        const mapsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(
          place.name + " " + place.address
        )}`;
        window.open(mapsUrl, "_blank");
      });

      resultsSection.appendChild(placeCard);
    });

    // Add click events to all gallery images
    document.querySelectorAll(".gallery-image").forEach((img) => {
      img.addEventListener("click", (e) => {
        // Find all images in this gallery
        const gallery = e.target.closest(".image-gallery");
        currentGalleryImages = Array.from(
          gallery.querySelectorAll(".gallery-image")
        );

        // Set current index to the clicked image
        currentImageIndex = currentGalleryImages.indexOf(e.target);

        // Update modal image and counter
        updateModalImage();
        openModal();
      });
    });
  }

  function openModal() {
    modal.classList.add("active");
  }

  function closeImageModal() {
    modal.classList.remove("active");
  }

  // Add these new functions for navigation
  function updateModalImage() {
    modalImg.src = currentGalleryImages[currentImageIndex].src;

    // Update counter
    document.querySelector(".modal-counter").textContent = `${
      currentImageIndex + 1
    } / ${currentGalleryImages.length}`;

    // Hide prev/next buttons if at the beginning/end
    document.querySelector(".modal-prev").style.visibility =
      currentImageIndex === 0 ? "hidden" : "visible";

    document.querySelector(".modal-next").style.visibility =
      currentImageIndex >= currentGalleryImages.length - 1
        ? "hidden"
        : "visible";
  }

  function prevImage() {
    if (currentImageIndex > 0) {
      currentImageIndex--;
      updateModalImage();
    }
  }

  function nextImage() {
    if (currentImageIndex < currentGalleryImages.length - 1) {
      currentImageIndex++;
      updateModalImage();
    }
  }

  // Close modal when clicking on X
  closeModal.addEventListener("click", closeImageModal);

  // Close modal when clicking outside the image
  modal.addEventListener("click", (event) => {
    if (event.target === modal) {
      closeImageModal();
    }
  });

  // CAPTCHA implementation
  async function showCaptcha(onSuccess) {
    const captchaContainer = document.getElementById("captcha-container");
    const captchaChallenge = document.getElementById("captcha-challenge");
    const verifyButton = document.getElementById("verify-captcha");

    // Show the CAPTCHA container
    captchaContainer.classList.remove("hidden");

    // Hide the status message
    statusMessage.classList.add("hidden");

    try {
      // Fetch a new CAPTCHA from the server
      const response = await fetch("/get-captcha");
      if (!response.ok) {
        throw new Error("Failed to get CAPTCHA");
      }

      const captchaData = await response.json();
      const captchaId = captchaData.captcha_id;
      const challenge = captchaData.challenge;

      // Create the CAPTCHA challenge HTML
      captchaChallenge.innerHTML = `
        <div class="text-center">
          <p class="mb-2">Please solve this math problem to verify you're human:</p>
          <p class="text-xl font-bold mb-4">${challenge} = ?</p>
          <input type="number" id="captcha-answer" class="search-input" placeholder="Enter your answer">
          <input type="hidden" id="captcha-id" value="${captchaId}">
        </div>
      `;

      // Add event listener to the verify button
      verifyButton.onclick = () => {
        const userAnswer = parseInt(
          document.getElementById("captcha-answer").value,
          10
        );
        const storedCaptchaId = document.getElementById("captcha-id").value;

        // Store the CAPTCHA data to use with the actual API call
        window.captchaVerification = {
          captcha_id: storedCaptchaId,
          captcha_answer: userAnswer,
        };

        // Hide the CAPTCHA container
        captchaContainer.classList.add("hidden");

        // Call the success callback
        onSuccess();
      };

      // Also verify on Enter key press in the input field
      document
        .getElementById("captcha-answer")
        .addEventListener("keyup", (event) => {
          if (event.key === "Enter") {
            verifyButton.click();
          }
        });
    } catch (error) {
      console.error("Error getting CAPTCHA:", error);
      captchaChallenge.innerHTML = `
        <div class="text-center">
          <p>Error loading CAPTCHA. Please try again.</p>
          <button id="retry-captcha" class="btn btn-primary mt-4">Try Again</button>
        </div>
      `;

      document.getElementById("retry-captcha").addEventListener("click", () => {
        showCaptcha(onSuccess);
      });
    }
  }

  // Navigation event listeners
  document.querySelector(".modal-prev").addEventListener("click", prevImage);
  document.querySelector(".modal-next").addEventListener("click", nextImage);

  // Keyboard navigation
  document.addEventListener("keydown", (e) => {
    if (!modal.classList.contains("active")) return;

    if (e.key === "ArrowLeft") prevImage();
    else if (e.key === "ArrowRight") nextImage();
    else if (e.key === "Escape") closeImageModal();
  });
});
