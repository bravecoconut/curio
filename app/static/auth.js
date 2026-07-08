// client/static/auth.js

const auth = async (email, password) => {
    try {
        const response = await fetch("api/auth_service", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
            },
            credentials: "include",
            body: JSON.stringify({ email, password }),
        });

        const result = await response.json();

        if (!response.ok || !result.status) {
            console.error("Auth failed:", result.data?.error || "Unknown error");
            return { success: false, error: result.data?.error || "Something went wrong" };
        }

        console.log("Auth successful:", result.data);
        return { success: true, data: result.data };

    } catch (error) {
        console.error("Network or unexpected error:", error);
        return { success: false, error: "Could not reach the server" };
    }
};

const errorModal = (error) => {
    // remove any existing modal first, so errors don't stack
    const existing = document.getElementById("errorModal");
    if (existing) existing.remove();

    const modal = document.createElement("div");
    modal.id = "errorModal";
    modal.innerHTML = `
        <h3>Error</h3>
        <p id="errorDescription">${error}</p>
    `;

    document.getElementById('authContainer').appendChild(modal);

    // auto-dismiss after 4 seconds
    setTimeout(() => {
        modal.classList.add("hidden");
        setTimeout(() => modal.remove(), 300);
    }, 4000);
};

// errorModal("dass")


async function handleContinue() {
    const emailInput = document.getElementById("emailInput");
    const passwordInput = document.getElementById("passwordInput");
    const continueBtn = document.getElementById("authContinue");

    const email = emailInput.value.trim();
    const password = passwordInput.value.trim();


    if (!email || !password) {
        errorModal("Please enter both email and password.");
        return;
    }

    const originalText = continueBtn.textContent;
    continueBtn.textContent = "Please wait...";

    const result = await auth(email, password);

    continueBtn.textContent = originalText;

    if (!result.success) {
        errorModal(result.error);
        return;
    }

    // success — redirect wherever your app should go next
    window.location.href = "/home";
}

document.addEventListener("DOMContentLoaded", () => {
    const continueBtn = document.getElementById("authContinue");
    const passwordInput = document.getElementById("passwordInput");

    continueBtn.addEventListener("click", handleContinue);

    // allow pressing Enter in the password field to submit
    passwordInput.addEventListener("keydown", (e) => {
        if (e.key === "Enter") {
            handleContinue();
        }
    });
});


