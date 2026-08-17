(function () {
    const form = document.getElementById("qr-form");
    const urlInput = document.getElementById("url-input");
    const restartBtn = document.getElementById("restart-btn");
    const errorMessage = document.getElementById("error-message");
    const qrcodeContainer = document.getElementById("qrcode");
    const downloadGroup = document.getElementById("download-group");
    const downloadDropdown = document.getElementById("download-dropdown");
    const downloadPng = document.getElementById("download-btn");
    const downloadJpeg = document.getElementById("download-jpeg");
    const downloadGif = document.getElementById("download-gif");
    const downloadSvg = document.getElementById("download-svg");

    const IMAGE_SIZE = 500;
    // Quiet-zone margin, in QR module widths (not pixels) — scale by cellSize
    // before passing to the library so every format gets the same margin.
    const MARGIN_MODULES = 2;

    let currentSvgUrl = null;

    const SCHEME_RE = /^[a-z][a-z0-9+.-]*:/i;

    // Bare domains like "google.com" have no scheme, so assume https://
    // rather than encoding them as a relative/unusable URL in the QR code.
    // Returns the normalized URL, or null if the input isn't usable: inputs
    // with an explicit scheme (http:, mailto:, tel:, ...) are trusted as-is
    // (via the URL constructor), but bare domains we prepend https:// to are
    // also required to look like a real host (has a dot, or is localhost) so
    // plain typos/garbage don't silently turn into a QR code for nonsense.
    function normalizeUrl(value) {
        const hadScheme = SCHEME_RE.test(value);
        const candidate = hadScheme ? value : "https://" + value;

        let parsed;
        try {
            parsed = new URL(candidate);
        } catch (err) {
            return null;
        }

        if (
            !hadScheme &&
            parsed.hostname !== "localhost" &&
            !parsed.hostname.includes(".")
        ) {
            return null;
        }

        return candidate;
    }

    function showError(message) {
        errorMessage.textContent = message;
        errorMessage.hidden = false;
    }

    function clearError() {
        errorMessage.textContent = "";
        errorMessage.hidden = true;
    }

    function closeDropdown() {
        downloadDropdown.open = false;
    }

    function clearDownloadLinks() {
        [downloadPng, downloadJpeg, downloadGif, downloadSvg].forEach(function (link) {
            link.removeAttribute("href");
        });
        if (currentSvgUrl) {
            URL.revokeObjectURL(currentSvgUrl);
            currentSvgUrl = null;
        }
    }

    function clearQrCode() {
        qrcodeContainer.innerHTML = "";
        downloadGroup.hidden = true;
        closeDropdown();
        clearDownloadLinks();
    }

    // Modules-per-side is data-dependent, so pick a cell size that renders
    // close to IMAGE_SIZE; the <img> width/height attributes plus
    // image-rendering: pixelated (in CSS) square up any small remainder.
    function cellSizeFor(moduleCount) {
        return Math.max(1, Math.round(IMAGE_SIZE / (moduleCount + MARGIN_MODULES * 2)));
    }

    function buildSvgDataUrl(qr) {
        const svgCellSize = 10;
        let svg = qr.createSvgTag({
            cellSize: svgCellSize,
            margin: MARGIN_MODULES * svgCellSize,
            scalable: true,
        });
        svg = svg.replace(
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg"',
            '<svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="' +
                IMAGE_SIZE +
                '" height="' +
                IMAGE_SIZE +
                '"',
        );
        const blob = new Blob([svg], { type: "image/svg+xml" });
        return URL.createObjectURL(blob);
    }

    function generateQrCode(url) {
        const qr = qrcode(0, "M");
        qr.addData(url);
        qr.make();

        const cellSize = cellSizeFor(qr.getModuleCount());
        const gifDataUrl = qr.createDataURL(cellSize, MARGIN_MODULES * cellSize);

        const img = document.createElement("img");
        img.src = gifDataUrl;
        img.width = IMAGE_SIZE;
        img.height = IMAGE_SIZE;
        img.alt = `QR code for ${url}`;
        qrcodeContainer.innerHTML = "";
        qrcodeContainer.appendChild(img);

        downloadGif.href = gifDataUrl;
        currentSvgUrl = buildSvgDataUrl(qr);
        downloadSvg.href = currentSvgUrl;

        // Render from a 1px/module source onto a 500x500 canvas (nearest-neighbor)
        // for crisp PNG/JPEG output; canvas conversion is async, so reveal the
        // download controls only once both are ready.
        const sourceImg = new Image();
        sourceImg.onload = function () {
            const canvas = document.createElement("canvas");
            canvas.width = IMAGE_SIZE;
            canvas.height = IMAGE_SIZE;
            const ctx = canvas.getContext("2d");
            ctx.imageSmoothingEnabled = false;
            ctx.drawImage(sourceImg, 0, 0, IMAGE_SIZE, IMAGE_SIZE);

            downloadPng.href = canvas.toDataURL("image/png");
            downloadJpeg.href = canvas.toDataURL("image/jpeg", 0.92);

            downloadGroup.hidden = false;
        };

        sourceImg.onerror = function () {
            showError("Could not generate a QR code for that URL.");
        };

        sourceImg.src = qr.createDataURL(1, MARGIN_MODULES);
    }

    form.addEventListener("submit", function (event) {
        event.preventDefault();
        clearError();
        clearQrCode();

        const url = urlInput.value.trim();
        if (!url) {
            return;
        }

        const normalizedUrl = normalizeUrl(url);
        if (!normalizedUrl) {
            showError("Enter a valid URL, like example.com or https://example.com.");
            return;
        }

        urlInput.value = normalizedUrl;

        try {
            generateQrCode(normalizedUrl);
        } catch (err) {
            showError("Could not generate a QR code for that URL.");
        }
    });

    restartBtn.addEventListener("click", function () {
        form.reset();
        clearError();
        clearQrCode();
        urlInput.focus();
    });

    [downloadJpeg, downloadGif, downloadSvg].forEach(function (link) {
        link.addEventListener("click", closeDropdown);
    });

    document.addEventListener("click", function (event) {
        if (downloadDropdown.open && !downloadDropdown.contains(event.target)) {
            closeDropdown();
        }
    });
})();
