function getImageUrls(selector = "body") {
  const elements = document.querySelectorAll(selector);
  const urls = [];
  elements.forEach((element) => {
    const images = element.getElementsByTagName("img");
    for (let i = 0; i < images.length; i++) {
      urls.push(images[i].src);
    }
  });
  return urls;
}

function downloadUrlsAsJson(selector = "body") {
  const elements = document.querySelectorAll(selector);
  const urls = [];
  elements.forEach((element) => {
    const images = element.getElementsByTagName("img");
    for (let i = 0; i < images.length; i++) {
      urls.push(images[i].src);
    }
  });

  const json = JSON.stringify(urls);
  const blob = new Blob([json], { type: "application/json" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "image-urls.json";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

async function downloadUrlsAsZip(selector = "body") {
  // Load JSZip
  await loadScript(
    "https://cdnjs.cloudflare.com/ajax/libs/jszip/3.6.0/jszip.min.js"
  );

  const elements = document.querySelectorAll(selector);
  const urls = [];
  for (let i = 0; i < elements.length; i++) {
    const images = elements[i].getElementsByTagName("img");
    for (let j = 0; j < images.length; j++) {
      const response = await fetch(images[j].src);
      const blob = await response.blob();
      const url = URL.createObjectURL(blob);
      const img = document.createElement("img");
      img.src = url;
      await new Promise((resolve) => {
        img.onload = resolve;
      });
      const canvas = document.createElement("canvas");
      canvas.width = img.naturalWidth;
      canvas.height = img.naturalHeight;
      const context = canvas.getContext("2d");
      context.drawImage(img, 0, 0);
      canvas.toBlob((blob) => {
        const url = URL.createObjectURL(blob);
        urls.push(url);
      }, "image/jpeg");
    }
  }

  const zip = new JSZip();
  const promises = [];
  for (let i = 0; i < urls.length; i++) {
    const response = await fetch(urls[i]);
    const blob = await response.blob();
    const filename = `image-${i + 1}.jpg`;
    zip.file(filename, blob);
  }
  const blob = await zip.generateAsync({ type: "blob" });
  const url = URL.createObjectURL(blob);

  const link = document.createElement("a");
  link.href = url;
  link.download = "image-files.zip";
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

// Helper function to load a script dynamically
function loadScript(url) {
  return new Promise((resolve, reject) => {
    const script = document.createElement("script");
    script.src = url;
    script.addEventListener("load", () => {
      resolve();
    });
    script.addEventListener("error", () => {
      reject(new Error(`Failed to load script ${url}`));
    });
    document.head.appendChild(script);
  });
}

function injectScript(url) {
  var script = document.createElement("script");
  script.src = url;
  document.body.appendChild(script);
}
