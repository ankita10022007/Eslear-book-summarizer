document.addEventListener("DOMContentLoaded", () => {
  const fileInput = document.getElementById("file");
  const fileName = document.getElementById("file-name");
  if (fileInput && fileName) {
    fileInput.addEventListener("change", () => {
      fileName.textContent = fileInput.files.length ? fileInput.files[0].name : "No file selected";
    });
  }

  document.querySelectorAll(".flashcard").forEach(card => {
    card.addEventListener("click", () => {
      const flipped = card.classList.toggle("flipped");
      card.setAttribute("aria-pressed", String(flipped));
    });
  });

  const speakButton = document.getElementById("speak-summary");
  const stopButton = document.getElementById("stop-speech");
  if (speakButton && "speechSynthesis" in window) {
    speakButton.addEventListener("click", () => {
      window.speechSynthesis.cancel();
      const utterance = new SpeechSynthesisUtterance(speakButton.dataset.text || "");
      utterance.rate = 0.95;
      window.speechSynthesis.speak(utterance);
    });
  } else if (speakButton) {
    speakButton.disabled = true;
    speakButton.title = "Speech synthesis is not supported by this browser.";
  }
  if (stopButton) stopButton.addEventListener("click", () => window.speechSynthesis?.cancel());

  const downloadButton = document.getElementById("download-summary");
  const dataNode = document.getElementById("download-data");
  if (downloadButton && dataNode) {
    downloadButton.addEventListener("click", () => {
      const data = JSON.parse(dataNode.textContent);
      const body = `${data.title}\n\nSUMMARY\n${data.summary}\n\nIMPORTANT POINTS\n${data.points.map((p, i) => `${i + 1}. ${p}`).join("\n")}\n\nMY NOTES\n${data.notes || ""}`;
      const blob = new Blob([body], {type: "text/plain;charset=utf-8"});
      const url = URL.createObjectURL(blob);
      const link = document.createElement("a");
      link.href = url; link.download = `${data.title.replace(/[^a-z0-9-_]+/gi, "_") || "eslear-summary"}.txt`;
      link.click(); URL.revokeObjectURL(url);
    });
  }
});