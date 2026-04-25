// -------------------------
// IndexedDB Setup
// -------------------------
let db = null;
let editId = null;

let dbRequest = indexedDB.open("ResumeDB", 1);

dbRequest.onupgradeneeded = function (e) {
  let dbInstance = e.target.result;

  if (!dbInstance.objectStoreNames.contains("resumes")) {
    dbInstance.createObjectStore("resumes", {
      keyPath: "id",
      autoIncrement: true,
    });
  }
};

dbRequest.onsuccess = function (e) {
  db = e.target.result;

  console.log("Database ready!");

  const params = new URLSearchParams(window.location.search);
  editId = params.get("id");

  if (editId) {
    loadResume(Number(editId));
  }
};

dbRequest.onerror = function (e) {
  console.error("Database error:", e.target.errorCode);
};

// -------------------------
// Save / Update Resume
// -------------------------
function saveResume(resumeData) {
  let transaction = db.transaction("resumes", "readwrite");
  let store = transaction.objectStore("resumes");

  if (editId) {
    resumeData.id = Number(editId);
    store.put(resumeData);
  } else {
    store.add(resumeData);
  }

  transaction.oncomplete = function () {
    alert(editId ? "Resume updated!" : "Resume saved!");
    window.location.href = "/";
  };

  transaction.onerror = function (e) {
    console.error("Save error", e.target.error);
  };
}

// -------------------------
// UI Helpers
// -------------------------
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

  $container.append(`
    <div class="block">
        <button type="button" class="delete-btn" onclick="removeBlock(this)">Delete</button>
        ${html}
    </div>
  `);
}

// -------------------------
// Collect Form Data
// -------------------------
function getFormData($form) {
  let data = {};

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

  simpleFields.forEach((f) => {
    data[f] = $form.find(`[name="${f}"]`).val() || "";
  });

  function getList(containerId) {
    return $form.find(`#${containerId} input`).map(function () {
      return $(this).val();
    }).get();
  }

  data.emails = getList("emails");
  data.mobile_numbers = getList("mobiles");
  data.links = getList("links");

  function getComplex(id, fields) {
    return $form.find(`#${id} .block`).map(function () {
      let obj = {};
      fields.forEach((f) => {
        obj[f] = $(this).find(`[name*="[${f}]"]`).val() || "";
      });
      return obj;
    }).get();
  }

  data.experience = getComplex("experience", [
    "job_title",
    "company_name",
    "place",
    "from_date",
    "to_date",
    "description",
  ]);

  data.projects = getComplex("projects", [
    "project_name",
    "description",
  ]);

  data.education = getComplex("education", [
    "degree_name",
    "college_name",
    "place",
    "completed_on",
    "result",
    "description",
  ]);

  data.certifications = getComplex("certifications", [
    "title",
    "issuing_company",
    "completion_date",
  ]);

  return data;
}

// -------------------------
// Load Resume (EDIT MODE)
// -------------------------
function loadResume(id) {
  let transaction = db.transaction("resumes", "readonly");
  let store = transaction.objectStore("resumes");
  let request = store.get(id);

  request.onsuccess = function () {
    let data = request.result;
    if (!data) return;

    // clear dynamic containers
    $("#emails, #mobiles, #links, #experience, #projects, #education, #certifications").empty();

    // fill simple fields
    for (let key in data) {
      if (typeof data[key] !== "object") {
        $(`[name="${key}"]`).val(data[key]);
      }
    }

    function fillSimple(containerId, values, fieldName) {
      values.forEach((val) => {
        addSimpleField(containerId, fieldName);
        $(`#${containerId} input`).last().val(val);
      });
    }

    fillSimple("emails", data.emails || [], "emails");
    fillSimple("mobiles", data.mobile_numbers || [], "mobile_numbers");
    fillSimple("links", data.links || [], "links");

    function fillComplex(containerId, items, templateFn) {
      items.forEach((item) => {
        addComplexBlock(containerId, templateFn());
        let $block = $(`#${containerId} .block`).last();

        for (let key in item) {
          $block.find(`[name*="[${key}]"]`).val(item[key]);
        }
      });
    }

    fillComplex("experience", data.experience || [], experienceTemplate);

    fillComplex("projects", data.projects || [], projectsTemplate);

    fillComplex("education", data.education || [], educationTemplate);

    fillComplex("certifications", data.certifications || [], certificationsTemplate);
  };
}

// -------------------------
// Templates
// -------------------------
function experienceTemplate() {
  return `
    <label>Job Title</label>
    <input name="experience[INDEX][job_title]">

    <label>Company Name</label>
    <input name="experience[INDEX][company_name]">

    <label>Place</label>
    <input name="experience[INDEX][place]">

    <label>From Date</label>
    <input name="experience[INDEX][from_date]">

    <label>To Date</label>
    <input name="experience[INDEX][to_date]">

    <label>Description</label>
    <textarea name="experience[INDEX][description]"></textarea>
  `;
}

function projectsTemplate() {
  return `
    <label>Project Name</label>
    <input name="projects[INDEX][project_name]">

    <label>Description</label>
    <textarea name="projects[INDEX][description]"></textarea>
  `;
}

function educationTemplate() {
  return `
    <label>Degree Name</label>
    <input name="education[INDEX][degree_name]">

    <label>College Name</label>
    <input name="education[INDEX][college_name]">

    <label>Place</label>
    <input name="education[INDEX][place]">

    <label>Completed On</label>
    <input name="education[INDEX][completed_on]">

    <label>Result</label>
    <input name="education[INDEX][result]">

    <label>Description</label>
    <textarea name="education[INDEX][description]"></textarea>
  `;
}

function certificationsTemplate() {
  return `
    <label>Title</label>
    <input name="certifications[INDEX][title]">

    <label>Issuing Company</label>
    <input name="certifications[INDEX][issuing_company]">

    <label>Completion Date</label>
    <input name="certifications[INDEX][completion_date]">
  `;
}

// -------------------------
// Form Submit
// -------------------------
$(document).ready(function () {
  $("form").on("submit", function (e) {
    e.preventDefault();

    let resumeData = getFormData($(this));
    saveResume(resumeData);
  });
});