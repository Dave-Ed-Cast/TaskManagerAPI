document.getElementById("loginForm")?.addEventListener("submit", async function (e) {
    e.preventDefault();

    const formData = new FormData(e.target);
    const body = new URLSearchParams();
    body.append("username", formData.get("username"));
    body.append("password", formData.get("password"));


    try {
        const res = await fetch("/users/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: body
        });

        const json = await res.json();

        if (res.ok) {
            localStorage.setItem("token", json.access_token);
            // DO NOT store admin status in local storage for security reasons.
            // localStorage.setItem("is_admin", json.is_admin);
            localStorage.setItem("username", formData.get("username"));
            localStorage.setItem("created_at", json.created_at || "Unknown");

            window.location.href = "/user";
        } else {
            document.getElementById("msg").innerText = json.detail;
        }
    } catch {
        document.getElementById("msg").innerText = "Login failed. Try again.";
    }
});
