// IndexedDB Setup
// -------------------------
let dbRequest = indexedDB.open("ResumeDB", 1);

// -------------------------
// List all resumes
// -------------------------
function listAllResumes() {
  let transaction = db.transaction("resumes", "readonly");
  let store = transaction.objectStore("resumes");
  let request = store.getAll();

  request.onsuccess = function () {
    let resumes = request.result;
    let html = "";
    if (resumes.length === 0) {
      html = "<p>No resumes saved yet.</p>";
    } else {
      resumes.forEach((resume) => {
        html += `
                        <div class="resume-card" data-id="${resume.id}" style="border:1px solid #ccc; padding:10px; margin:10px;">
                            <h3>${resume.name} (${resume.designation})</h3>
                            <p>${resume.place || ""} | ${resume.nationality || ""}</p>
                            <button class="select-resume">Select Resume</button>
                            <button class="view-resume">View</button>
                            <button class="delete-resume">Delete</button>
                        </div>
                    `;
      });
    }
    $("#resume-list").html(html);
    highlightResume();
  };

  request.onerror = function (e) {
    console.error("Error fetching resumes:", e.target.error);
  };
}

function highlightResume() {
  // Get the selected resume ID from localStorage
  let selectedId = localStorage.getItem("selectedResume");

  // Remove highlight from all resumes first
  $(".resume-card").css("border", "1px solid #ccc");

  // Highlight the selected resume, if any
  if (selectedId) {
    $(`.resume-card[data-id='${selectedId}']`).css(
      "background-color",
      "#007bff",
    ); // blue border
  }
}

function selectResume() {}

dbRequest.onupgradeneeded = function (e) {
  let db = e.target.result;
  if (!db.objectStoreNames.contains("resumes")) {
    db.createObjectStore("resumes", { keyPath: "id", autoIncrement: true });
  }
};

dbRequest.onsuccess = function (e) {
  window.db = e.target.result;
  listAllResumes();
};

dbRequest.onerror = function (e) {
  console.error("Database error:", e.target.errorCode);
};

// -------------------------
// Delete Resume
// -------------------------
$(document).on("click", ".delete-resume", function () {
  let id = Number($(this).closest(".resume-card").data("id"));
  if (confirm("Are you sure you want to delete this resume?")) {
    let transaction = db.transaction("resumes", "readwrite");
    let store = transaction.objectStore("resumes");
    store.delete(id);
    transaction.oncomplete = () => {
      alert("Resume deleted!");
      listAllResumes();
    };
  }
});

// -------------------------
// Navigate to create-resume page
// -------------------------
$(document).on("click", "#create-new", function () {
  window.location.href = "/create-resume";
});

$(document).on("click", ".select-resume", function () {
  let id = Number($(this).closest(".resume-card").data("id"));

  localStorage.setItem("selectedResume", id);
  alert("Resume id " + id + " is selected.");
  highlightResume();
});

// -------------------------
// View Resume (basic alert)
// -------------------------
$(document).on("click", ".view-resume", function () {
  let id = Number($(this).closest(".resume-card").data("id"));

  let transaction = db.transaction("resumes", "readonly");
  let store = transaction.objectStore("resumes");
  let request = store.get(id);

  request.onsuccess = function () {
    let resume = request.result;

    let html = `
      <h4>${resume.name}</h4>
      <p><strong>Designation:</strong> ${resume.designation}</p>
      <p><strong>Nationality:</strong> ${resume.nationality}</p>
      <p><strong>DOB:</strong> ${resume.dob}</p>
      <p><strong>Place:</strong> ${resume.place}</p>
      <p><strong>Visa Status:</strong> ${resume.visa_status}</p>
      <p><strong>Notice Period:</strong> ${resume.notice_period}</p>

      <hr>

      <h5>Professional Summary</h5>
      <p>${resume.professional_summary}</p>

      <hr>

      <h5>Technical Skills</h5>
      <pre>${resume.technical_skills}</pre>

      <hr>

      <h5>Education</h5>
    `;

    resume.education.forEach(function (edu) {
      html += `
        <div class="mb-3">
          <strong>${edu.degree_name}</strong><br>
          ${edu.college_name}<br>
          ${edu.place}<br>
          Completed: ${edu.completed_on}
        </div>
      `;
    });

    html += `<hr><h5>Experience</h5>`;

    resume.experience.forEach(function (exp) {
      html += `
        <div class="mb-3">
          <strong>${exp.job_title}</strong><br>
          ${exp.company_name}<br>
          ${exp.place}<br>
          ${exp.from_date} - ${exp.to_date}
          <p>${exp.description}</p>
        </div>
      `;
    });

    html += `<hr><h5>Projects</h5>`;

    resume.projects.forEach(function (project) {
      html += `
        <div class="mb-3">
          <strong>${project.project_name}</strong>
          <p>${project.description}</p>
        </div>
      `;
    });

    $("#resumeContent").html(html);

    let modal = new bootstrap.Modal(document.getElementById("resumeModal"));
    modal.show();
  };
});
