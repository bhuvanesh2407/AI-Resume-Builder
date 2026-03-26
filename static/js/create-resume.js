// -------------------------
// IndexedDB Setup
// -------------------------
let dbRequest = indexedDB.open("ResumeDB", 1);

dbRequest.onupgradeneeded = function (e) {
  let db = e.target.result;
  if (!db.objectStoreNames.contains("resumes")) {
    db.createObjectStore("resumes", { keyPath: "id", autoIncrement: true });
  }
};

dbRequest.onsuccess = function (e) {
  window.db = e.target.result;
  console.log("Database ready!");
};

dbRequest.onerror = function (e) {
  console.error("Database error:", e.target.errorCode);
};

// -------------------------
// Save Resume
// -------------------------
function saveResume(resumeData) {
  let transaction = db.transaction("resumes", "readwrite");
  let store = transaction.objectStore("resumes");
  store.add(resumeData);
  transaction.oncomplete = function () {
    console.log("Resume saved!");
  };
  transaction.onerror = function (e) {
    console.error("Save error", e.target.error);
  };
}

function removeBlock(button) {
  $(button).parent().remove();
}

function addSimpleField(containerId, fieldName) {
  const $container = $("#" + containerId);
  const index = $container.children().length;

  const html = `
    <div class="block">
        <button type="button" class="delete-btn" onclick="removeBlock(this)">Delete</button>
        <input type="text" name="${fieldName}[${index}]">
    </div>
  `;

  $container.append(html);
}

function addComplexBlock(containerId, template) {
  const $container = $("#" + containerId);
  const index = $container.children().length;

  const html = template.replace(/INDEX/g, index);

  const block = `
    <div class="block">
        <button type="button" class="delete-btn" onclick="removeBlock(this)">Delete</button>
        ${html}
    </div>
  `;

  $container.append(block);
}

// -------------------------
// Collect Form Data
// -------------------------
function getFormData($form) {
  let data = {};

  // Simple fields
  const simpleFields = [
    "name",
    "designation",
    "place",
    "nationality",
    "dob",
    "visa_status",
    "notice_period",
    "profile_description",
    "professional_summary",
    "technical_skills",
  ];

  simpleFields.forEach(
    (f) => (data[f] = $form.find(`[name="${f}"]`).val() || ""),
  );

  // Dynamic lists: emails, mobiles, links
  data.emails = $form
    .find('[name="emails[]"]')
    .map(function () {
      return $(this).val();
    })
    .get();
  data.mobile_numbers = $form
    .find('[name="mobile_numbers[]"]')
    .map(function () {
      return $(this).val();
    })
    .get();
  data.links = $form
    .find('[name="links[]"]')
    .map(function () {
      return $(this).val();
    })
    .get();

  // Complex blocks helper
  function getComplexBlock(id, fields) {
    return $form
      .find(`#${id} > div`)
      .map(function () {
        let obj = {};
        fields.forEach((field) => {
          let val = $(this).find(`[name*="[${field}]"]`).val() || "";
          obj[field] = val;
        });
        return obj;
      })
      .get();
  }

  data.experience = getComplexBlock("experience", [
    "job_title",
    "company_name",
    "place",
    "from_date",
    "to_date",
    "description",
  ]);
  data.projects = getComplexBlock("projects", ["project_name", "description"]);
  data.education = getComplexBlock("education", [
    "degree_name",
    "college_name",
    "place",
    "completed_on",
    "result",
    "description",
  ]);
  data.certifications = getComplexBlock("certifications", [
    "title",
    "issuing_company",
    "completion_date",
  ]);

  return data;
}

// -------------------------
// Form Submission
// -------------------------
$(document).ready(function () {
  $("form").on("submit", function (e) {
    e.preventDefault();
    let resumeData = getFormData($(this));
    saveResume(resumeData);
    alert("Resume saved locally!");
    $(this)[0].reset();
  });
});

// -------------------------
// Retrieve All Resumes
// -------------------------
function listAllResumes() {
  let transaction = db.transaction("resumes", "readonly");
  let store = transaction.objectStore("resumes");
  let request = store.getAll();
  request.onsuccess = function () {
    console.log("All resumes:", request.result);
  };
  request.onerror = function (e) {
    console.error("Error fetching resumes:", e.target.error);
  };
}

// Example usage: listAllResumes();
