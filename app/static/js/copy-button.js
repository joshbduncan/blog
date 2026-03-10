// Add copy code buttons to all `.codehilite` divs
document.addEventListener("DOMContentLoaded", function () {
    const blocks = document.querySelectorAll(".codehilite");
    const copyIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" stroke-width="2" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" class="clipboard"><path d="M8 8m0 2a2 2 0 0 1 2 -2h8a2 2 0 0 1 2 2v8a2 2 0 0 1 -2 2h-8a2 2 0 0 1 -2 -2z"></path><path d="M16 8v-2a2 2 0 0 0 -2 -2h-8a2 2 0 0 0 -2 2v8a2 2 0 0 0 2 2h2"></path></svg>`;
    const copiedIcon = `<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" stroke-width="3" stroke="currentColor" fill="none" stroke-linecap="round" stroke-linejoin="round" class="check"><style>
          path#check-icon {
            stroke-dasharray: 22px;
            stroke-dashoffset: 22px;
            animation: check 0.2s ease-out forwards;
          }

          @keyframes check {
            from {
              stroke-dashoffset: 22px;
            }
            to {
              stroke-dashoffset: 0;
            }
          }
</style><path id="check-icon" d="M5 12l5 5l10 -10"></path></svg>`;

    blocks.forEach((block) => {
        const button = document.createElement("a");
        let resetTimer = null;

        button.className = "secondary copy-to-clipboard";
        button.innerHTML = copyIcon;
        button.setAttribute("aria-label", "Copy to clipboard");
        button.setAttribute("data-tooltip", "Copy to clipboard");
        button.setAttribute("data-placement", "left");

        block.appendChild(button);

        button.addEventListener("click", async () => {
            try {
                // Get the code element inside the block for cleaner text
                const code = block.querySelector("pre") || block;
                await navigator.clipboard.writeText(code.textContent.trim());

                if (resetTimer) {
                    clearTimeout(resetTimer);
                }

                button.innerHTML = copiedIcon;
                button.classList.add("success");
                button.setAttribute("aria-label", "Copied");
                button.setAttribute("data-tooltip", "Copied");

                resetTimer = setTimeout(() => {
                    button.innerHTML = copyIcon;
                    button.classList.remove("success");
                    button.setAttribute("aria-label", "Copy to clipboard");
                    button.setAttribute("data-tooltip", "Copy to clipboard");
                }, 2000);
            } catch (err) {
                console.error("Failed to copy code:", err);
            }
        });
    });
});
