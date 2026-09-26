/**
 * Civic Task Navigator - Client Application Logic
 * Queries PostgreSQL backend and dynamically renders verified statutory roadmaps.
 */

document.addEventListener("DOMContentLoaded", () => {
  const searchForm = document.getElementById("searchForm");
  const queryInput = document.getElementById("queryInput");
  const locationInput = document.getElementById("locationInput");
  const loadingState = document.getElementById("loadingState");
  const notFoundContainer = document.getElementById("notFoundContainer");
  const notFoundTitle = document.getElementById("notFoundTitle");
  const availableServicesList = document.getElementById("availableServicesList");
  const resultContainer = document.getElementById("resultContainer");

  // Results elements
  const serviceIdBadge = document.getElementById("serviceIdBadge");
  const serviceSlaBadge = document.getElementById("serviceSlaBadge");
  const serviceNameDisplay = document.getElementById("serviceNameDisplay");
  const serviceLocationDisplay = document.getElementById("serviceLocationDisplay");
  const serviceDepartmentDisplay = document.getElementById("serviceDepartmentDisplay");
  const serviceDescriptionDisplay = document.getElementById("serviceDescriptionDisplay");
  const roadmapTimeline = document.getElementById("roadmapTimeline");

  // Metadata elements
  const metaDepartment = document.getElementById("metaDepartment");
  const metaLocation = document.getElementById("metaLocation");
  const metaProcessingTime = document.getElementById("metaProcessingTime");
  const metaFee = document.getElementById("metaFee");
  const metaEligibility = document.getElementById("metaEligibility");
  const metaAppMethod = document.getElementById("metaAppMethod");
  const metaAppUrl = document.getElementById("metaAppUrl");
  const metaSourceUrl = document.getElementById("metaSourceUrl");
  const metaVerifiedDate = document.getElementById("metaVerifiedDate");

  // Bind example chips
  document.querySelectorAll(".chip-btn").forEach((btn) => {
    btn.addEventListener("click", () => {
      const q = btn.getAttribute("data-query");
      const loc = btn.getAttribute("data-location");
      if (q) queryInput.value = q;
      if (loc) locationInput.value = loc;
      executeSearch(q, loc);
    });
  });

  // Handle search form submission
  searchForm.addEventListener("submit", (e) => {
    e.preventDefault();
    const q = queryInput.value.trim();
    const loc = locationInput.value.trim();
    if (q) {
      executeSearch(q, loc);
    }
  });

  async function executeSearch(query, location) {
    // UI state updates
    loadingState.classList.remove("hidden");
    resultContainer.classList.add("hidden");
    notFoundContainer.classList.add("hidden");

    // Update URL query parameters for bookmarking/sharing
    const url = new URL(window.location);
    url.searchParams.set("q", query);
    if (location) {
      url.searchParams.set("location", location);
    } else {
      url.searchParams.delete("location");
    }
    window.history.pushState({}, "", url);

    try {
      const apiUrl = `/api/search?q=${encodeURIComponent(query)}&location=${encodeURIComponent(location || "")}`;
      const response = await fetch(apiUrl);
      const data = await response.json();

      loadingState.classList.add("hidden");

      if (data.found && data.data) {
        renderServiceResult(data.data, data.location);
      } else {
        renderNotFound(data.message, data.available_services);
      }
    } catch (err) {
      loadingState.classList.add("hidden");
      renderNotFound("Error connecting to the database server. Please verify PostgreSQL is running.");
      console.error("Search request failed:", err);
    }
  }

  function renderServiceResult(serviceData, location) {
    const s = serviceData.service;

    // Header values
    serviceIdBadge.textContent = `Official Service ID: ${s.id}`;
    const slaText = s.processing_time_days ? `${s.processing_time_days} Days SLA` : (s.processing_time_raw || "Statutory SLA");
    serviceSlaBadge.textContent = `Statutory SLA: ${slaText}`;
    serviceNameDisplay.textContent = s.service_name;
    serviceLocationDisplay.textContent = serviceData.display_location || location || "Maharashtra State";
    serviceDepartmentDisplay.textContent = serviceData.department_name || s.department_name || "Government of Maharashtra";
    serviceDescriptionDisplay.textContent = s.description || "Official notified public service under Maharashtra Right to Public Services Act.";

    // Render Roadmap
    renderRoadmap(serviceData.roadmap);

    // Render Metadata
    metaDepartment.textContent = serviceData.department_name || s.department_name || "Government Department";
    metaLocation.textContent = serviceData.display_location || location || "Maharashtra State (Statewide / Municipal Jurisdiction)";
    metaProcessingTime.textContent = s.processing_time_days ? `${s.processing_time_days} statutory working days (RTS Act)` : (s.processing_time_raw || "Statutory timeline");
    
    // Fee
    if (serviceData.fee && serviceData.fee.amount !== null && serviceData.fee.amount !== undefined) {
      metaFee.textContent = `₹${serviceData.fee.amount.toFixed(2)} (${serviceData.fee.currency || 'INR'}) - ${serviceData.fee.description || 'Statutory Fee'}`;
    } else if (serviceData.fee && serviceData.fee.description) {
      metaFee.textContent = serviceData.fee.description;
    } else {
      metaFee.textContent = "Statutory application and facilitation fee per Maharashtra RTS Rules";
    }

    metaEligibility.textContent = s.eligibility || "Citizen/Resident meeting statutory documentation criteria.";
    metaAppMethod.textContent = s.application_method || "Online via Aaple Sarkar Portal or In-Person at Aaple Sarkar Seva Kendra (CSC)";

    // Links
    if (s.application_url) {
      metaAppUrl.href = s.application_url;
      metaAppUrl.style.display = "inline-flex";
    } else {
      metaAppUrl.style.display = "none";
    }

    if (s.source_url) {
      metaSourceUrl.href = s.source_url;
      metaSourceUrl.style.display = "inline-flex";
    } else {
      metaSourceUrl.style.display = "none";
    }

    if (s.last_verified_at) {
      const d = new Date(s.last_verified_at);
      metaVerifiedDate.textContent = isNaN(d) ? s.last_verified_at : d.toLocaleDateString("en-IN", { dateStyle: "long" });
    } else {
      metaVerifiedDate.textContent = "Current Active RTS Notification";
    }

    resultContainer.classList.remove("hidden");
    resultContainer.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  function renderRoadmap(steps) {
    roadmapTimeline.innerHTML = "";

    steps.forEach((step, index) => {
      // Step Card
      const stepCard = document.createElement("div");
      stepCard.className = "roadmap-step-card";

      // Step Header
      const headerDiv = document.createElement("div");
      headerDiv.className = "step-card-header";

      const titleDiv = document.createElement("div");
      titleDiv.className = "step-number-title";
      titleDiv.innerHTML = `
        <div class="step-circle">${step.step_number}</div>
        <h4 class="step-title">${step.title}</h4>
      `;

      const badgeSpan = document.createElement("span");
      badgeSpan.className = "step-badge";
      badgeSpan.textContent = step.badge || `Step ${step.step_number}`;

      headerDiv.appendChild(titleDiv);
      headerDiv.appendChild(badgeSpan);
      stepCard.appendChild(headerDiv);

      // Step Description
      const descP = document.createElement("p");
      descP.className = "step-desc";
      descP.textContent = step.description;
      stepCard.appendChild(descP);

      // Specific step details
      // Step 1 Prerequisites list
      if (step.details && step.details.length > 0) {
        const prereqList = document.createElement("ul");
        prereqList.className = "doc-items-list";
        step.details.forEach(item => {
          const li = document.createElement("li");
          li.className = "doc-item";
          li.innerHTML = `<span class="doc-bullet">•</span> <span><strong>${item}</strong></span>`;
          prereqList.appendChild(li);
        });
        stepCard.appendChild(prereqList);
      }

      // Step 2 Document groups
      if (step.doc_groups && step.doc_groups.length > 0) {
        step.doc_groups.forEach(group => {
          const groupBlock = document.createElement("div");
          groupBlock.className = "doc-category-block";

          const groupHeader = document.createElement("div");
          groupHeader.className = "doc-category-title";
          groupHeader.innerHTML = `
            <span>${group.category}</span>
            <span class="doc-rule-tag">${group.rule || 'Select 1'}</span>
          `;
          groupBlock.appendChild(groupHeader);

          const docList = document.createElement("ul");
          docList.className = "doc-items-list";
          group.documents.forEach(docName => {
            const li = document.createElement("li");
            li.className = "doc-item";
            li.innerHTML = `<span class="doc-bullet">•</span> <span>${docName}</span>`;
            docList.appendChild(li);
          });

          groupBlock.appendChild(docList);
          stepCard.appendChild(groupBlock);
        });
      }

      // Step 3 Application link button
      if (step.official_url) {
        const linkBtn = document.createElement("a");
        linkBtn.href = step.official_url;
        linkBtn.target = "_blank";
        linkBtn.rel = "noopener noreferrer";
        linkBtn.className = "btn btn-primary";
        linkBtn.style.marginTop = "0.75rem";
        linkBtn.style.fontSize = "0.875rem";
        linkBtn.style.padding = "0.6rem 1.2rem";
        linkBtn.innerHTML = `
          <span>${step.official_url_label || 'Official Portal Link'}</span>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path>
            <polyline points="15 3 21 3 21 9"></polyline>
            <line x1="10" y1="14" x2="21" y2="3"></line>
          </svg>
        `;
        stepCard.appendChild(linkBtn);
      }

      roadmapTimeline.appendChild(stepCard);

      // Add Downward Connector Arrow between steps
      if (index < steps.length - 1) {
        const connector = document.createElement("div");
        connector.className = "roadmap-connector";
        connector.innerHTML = `
          <div class="arrow-icon">↓</div>
        `;
        roadmapTimeline.appendChild(connector);
      }
    });
  }

  function renderNotFound(message, suggestions) {
    notFoundTitle.textContent = message || "We could not find sufficient verified information for this service in our current database.";
    availableServicesList.innerHTML = "";

    if (suggestions && suggestions.length > 0) {
      suggestions.forEach(sName => {
        const chip = document.createElement("button");
        chip.type = "button";
        chip.className = "chip-btn";
        chip.textContent = sName;
        chip.addEventListener("click", () => {
          queryInput.value = sName;
          executeSearch(sName, locationInput.value);
        });
        availableServicesList.appendChild(chip);
      });
    }

    notFoundContainer.classList.remove("hidden");
    notFoundContainer.scrollIntoView({ behavior: "smooth", block: "start" });
  }

  // Auto-search on initial load if query is provided in inputs
  const initialQ = queryInput.value.trim();
  const initialLoc = locationInput.value.trim();
  if (initialQ) {
    executeSearch(initialQ, initialLoc);
  }
});
