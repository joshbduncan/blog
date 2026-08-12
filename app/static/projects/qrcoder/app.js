(function () {
  const form = document.getElementById('qr-form');
  const urlInput = document.getElementById('url-input');
  const restartBtn = document.getElementById('restart-btn');
  const errorMessage = document.getElementById('error-message');
  const qrcodeContainer = document.getElementById('qrcode');
  const downloadBtn = document.getElementById('download-btn');

  const IMAGE_SIZE = 500;

  function showError(message) {
    errorMessage.textContent = message;
    errorMessage.hidden = false;
  }

  function clearError() {
    errorMessage.textContent = '';
    errorMessage.hidden = true;
  }

  function clearQrCode() {
    qrcodeContainer.innerHTML = '';
    downloadBtn.hidden = true;
    downloadBtn.removeAttribute('href');
  }

  function generateQrCode(url) {
    const qr = qrcode(0, 'M');
    qr.addData(url);
    qr.make();

    // Render at 1px/module with a standard 4-module quiet zone, then scale
    // that source image up to an exact 500x500 PNG on a canvas.
    const sourceDataUrl = qr.createDataURL(1, 4);
    const sourceImg = new Image();

    sourceImg.onload = function () {
      const canvas = document.createElement('canvas');
      canvas.width = IMAGE_SIZE;
      canvas.height = IMAGE_SIZE;
      const ctx = canvas.getContext('2d');
      ctx.imageSmoothingEnabled = false;
      ctx.drawImage(sourceImg, 0, 0, IMAGE_SIZE, IMAGE_SIZE);

      const pngDataUrl = canvas.toDataURL('image/png');

      const img = document.createElement('img');
      img.src = pngDataUrl;
      img.width = IMAGE_SIZE;
      img.height = IMAGE_SIZE;
      img.alt = `QR code for ${url}`;
      qrcodeContainer.innerHTML = '';
      qrcodeContainer.appendChild(img);

      downloadBtn.href = pngDataUrl;
      downloadBtn.download = 'qrcode.png';
      downloadBtn.hidden = false;
    };

    sourceImg.onerror = function () {
      showError('Could not generate a QR code for that URL.');
    };

    sourceImg.src = sourceDataUrl;
  }

  form.addEventListener('submit', function (event) {
    event.preventDefault();
    clearError();
    clearQrCode();

    const url = urlInput.value.trim();
    if (!url) {
      return;
    }

    try {
      generateQrCode(url);
    } catch (err) {
      showError('Could not generate a QR code for that URL.');
    }
  });

  restartBtn.addEventListener('click', function () {
    form.reset();
    clearError();
    clearQrCode();
    urlInput.focus();
  });
})();
