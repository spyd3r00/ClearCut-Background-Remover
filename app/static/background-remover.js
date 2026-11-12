const form = document.querySelector("#upload-form");
const input = document.querySelector("#image");
const selection = document.querySelector("#selection");
const sourcePreview = document.querySelector("#source-preview");
const originalImage = document.querySelector("#original-image");
const resultImage = document.querySelector("#result-image");
const resultSection = document.querySelector("#result");
const downloadLink = document.querySelector("#download-link");
const submitButton = document.querySelector("#submit-button");
const statusMessage = document.querySelector("#status");
const dropZone = document.querySelector(".drop-zone");

let sourceUrl;
let resultUrl;

function clearResult() {
  if (resultUrl) {
    URL.revokeObjectURL(resultUrl);
    resultUrl = undefined;
  }
  resultSection.hidden = true;
}

function updateSelection() {
  const file = input.files[0];
  statusMessage.textContent = "";
  clearResult();

  if (!file) {
    selection.hidden = true;
    if (sourceUrl) {
      URL.revokeObjectURL(sourceUrl);
      sourceUrl = undefined;
    }
    return;
  }

  if (sourceUrl) {
    URL.revokeObjectURL(sourceUrl);
  }
  sourceUrl = URL.createObjectURL(file);
  sourcePreview.src = sourceUrl;
  document.querySelector("#file-name").textContent = file.name;
  selection.hidden = false;
}

input.addEventListener("change", updateSelection);

document.querySelector("#clear-button").addEventListener("click", () => {
  input.value = "";
  updateSelection();
});

for (const eventName of ["dragenter", "dragover"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.add("is-dragging");
  });
}

for (const eventName of ["dragleave", "drop"]) {
  dropZone.addEventListener(eventName, (event) => {
    event.preventDefault();
    dropZone.classList.remove("is-dragging");
  });
}

dropZone.addEventListener("drop", (event) => {
  const [file] = event.dataTransfer.files;
  if (!file) return;

  const transfer = new DataTransfer();
  transfer.items.add(file);
  input.files = transfer.files;
  updateSelection();
});

form.addEventListener("submit", async (event) => {
  event.preventDefault();
  statusMessage.textContent = "";
  clearResult();

  if (!input.files.length) {
    statusMessage.textContent = "Choose an image before continuing.";
    return;
  }

  submitButton.disabled = true;
  submitButton.classList.add("is-loading");

  try {
    const response = await fetch("/remove", {
      method: "POST",
      body: new FormData(form),
    });

    if (!response.ok) {
      const responseText = await response.text();
      let errorMessage;
      try {
        errorMessage = JSON.parse(responseText).error;
      } catch {
        errorMessage = responseText
          .replace(/<[^>]*>/g, " ")
          .replace(/\s+/g, " ")
          .trim()
          .slice(0, 200);
      }
      throw new Error(
        errorMessage || `Request failed with status ${response.status}.`,
      );
    }

    const result = await response.blob();
    if (!result.type.startsWith("image/")) {
      throw new Error("The server returned an invalid image. Please try again.");
    }

    resultUrl = URL.createObjectURL(result);
    originalImage.src = sourceUrl;
    resultImage.src = resultUrl;
    downloadLink.href = resultUrl;
    resultSection.hidden = false;
    resultSection.scrollIntoView({ behavior: "smooth", block: "start" });
  } catch (error) {
    statusMessage.textContent = error.message || "Could not process this image. Please try again.";
  } finally {
    submitButton.disabled = false;
    submitButton.classList.remove("is-loading");
  }
});

window.addEventListener("pagehide", () => {
  if (sourceUrl) URL.revokeObjectURL(sourceUrl);
  if (resultUrl) URL.revokeObjectURL(resultUrl);
});
