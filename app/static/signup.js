document.getElementById("signupForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();

    const msg = document.getElementById("msg");
    const formData = new FormData(e.target);

    // Clear previous messages
    msg.innerText = "";
    msg.style.color = "";

    // Extract form values
    const username = formData.get("username")?.trim();
    const email = formData.get("email")?.trim();
    const password = formData.get("password");
    const confirmPassword = formData.get("confirmPassword");

    // === Comprehensive Client-side validation ===

    // Username validation
    if (!username) {
        msg.innerText = "Username is required.";
        msg.style.color = "red";
        return;
    }

    if (username.length < 3) {
        msg.innerText = "Username must be at least 3 characters long.";
        msg.style.color = "red";
        return;
    }

    if (username.length > 20) {
        msg.innerText = "Username must be less than 20 characters.";
        msg.style.color = "red";
        return;
    }

    // Check for valid username characters (alphanumeric and underscores only)
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        msg.innerText = "Username can only contain letters, numbers, and underscores.";
        msg.style.color = "red";
        return;
    }

    // Email validation
    if (!email) {
        msg.innerText = "Email is required.";
        msg.style.color = "red";
        return;
    }

    // Basic email format validation
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!emailRegex.test(email)) {
        msg.innerText = "Please enter a valid email address.";
        msg.style.color = "red";
        return;
    }

    // Password validation
    if (!password) {
        msg.innerText = "Password is required.";
        msg.style.color = "red";
        return;
    }

    if (password.length < 8) {
        msg.innerText = "Password must be at least 8 characters long.";
        msg.style.color = "red";
        return;
    }

    if (password.length > 128) {
        msg.innerText = "Password must be less than 128 characters.";
        msg.style.color = "red";
        return;
    }

    // Check for password strength
    const hasUpperCase = /[A-Z]/.test(password);
    const hasLowerCase = /[a-z]/.test(password);
    const hasNumbers = /\d/.test(password);
    const hasSpecialChar = /[!@#$%^&*(),.?":{}|<>]/.test(password);

    if (!hasUpperCase || !hasLowerCase || !hasNumbers) {
        msg.innerText = "Password must contain at least one uppercase letter, one lowercase letter, and one number.";
        msg.style.color = "red";
        return;
    }

    // Optional: require special characters
    // if (!hasSpecialChar) {
    //     msg.innerText = "Password must contain at least one special character.";
    //     msg.style.color = "red";
    //     return;
    // }

    // Confirm password validation
    if (!confirmPassword) {
        msg.innerText = "Please confirm your password.";
        msg.style.color = "red";
        return;
    }

    if (password !== confirmPassword) {
        msg.innerText = "Passwords do not match.";
        msg.style.color = "red";
        return;
    }

    // Show loading state
    msg.innerText = "Creating account...";
    msg.style.color = "blue";

    const data = JSON.stringify({
        username: username,
        password: password,
        is_admin: false  // or get from form if needed
    });

    try {
        const res = await fetch("/users/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: data
        });

        // Try to parse JSON, but fallback to text if parsing fails
        let responseBody;
        try {
            responseBody = await res.json();
        } catch {
            responseBody = await res.text();
        }

        if (res.ok) {
            msg.innerText = "Registration successful! Redirecting...";
            msg.style.color = "green";

            // Optionally auto-login if backend sends token
            if (responseBody.access_token) {
                localStorage.setItem("token", responseBody.access_token);
                localStorage.setItem("is_admin", responseBody.is_admin || false);
                localStorage.setItem("username", username);
                localStorage.setItem("created_at", responseBody.created_at || new Date().toISOString());
            }

            setTimeout(() => {
                window.location.href = "/user";
            }, 1500);
        } else {
            // Handle different types of server errors
            let errorMessage = "Registration failed.";

            if (typeof responseBody === "string") {
                errorMessage = responseBody;
            } else if (responseBody?.detail) {
                const detail = responseBody.detail.toLowerCase();

                // Specific error handling based on server response
                if (detail.includes("username") && (detail.includes("already exists") || detail.includes("taken"))) {
                    errorMessage = "This username is already taken. Please choose another.";
                } else if (detail.includes("email") && (detail.includes("already exists") || detail.includes("taken"))) {
                    errorMessage = "This email is already registered. Please use another email or try logging in.";
                } else if (detail.includes("invalid email")) {
                    errorMessage = "Please enter a valid email address.";
                } else if (detail.includes("password")) {
                    errorMessage = "Password does not meet requirements.";
                } else if (detail.includes("validation")) {
                    errorMessage = "Please check your input and try again.";
                } else {
                    errorMessage = responseBody.detail;
                }
            } else if (responseBody?.message) {
                errorMessage = responseBody.message;
            } else if (responseBody?.error) {
                errorMessage = responseBody.error;
            }

            // Handle specific HTTP status codes
            switch (res.status) {
                case 400:
                    if (errorMessage === "Registration failed.") {
                        errorMessage = "Invalid input. Please check your information and try again.";
                    }
                    break;
                case 409:
                    if (errorMessage === "Registration failed.") {
                        errorMessage = "Username or email already exists.";
                    }
                    break;
                case 422:
                    if (errorMessage === "Registration failed.") {
                        errorMessage = "Please check that all fields are filled out correctly.";
                    }
                    break;
                case 500:
                    errorMessage = "Server error. Please try again later.";
                    break;
                default:
                    if (errorMessage === "Registration failed.") {
                        errorMessage = `Registration failed (Error ${res.status}). Please try again.`;
                    }
            }

            msg.innerText = errorMessage;
            msg.style.color = "red";
        }
    } catch (err) {
        console.error("Registration error:", err);

        // Handle network errors
        if (err.name === "TypeError" && err.message.includes("fetch")) {
            msg.innerText = "Network error. Please check your internet connection and try again.";
        } else {
            msg.innerText = "Registration failed. Please try again later.";
        }
        msg.style.color = "red";
    }
});