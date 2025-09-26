document.addEventListener("DOMContentLoaded", async function () {
    const body = document.body;
    if (!body.classList.contains("user-page")) return;

    const username = localStorage.getItem("username");
    const is_admin = localStorage.getItem("is_admin") === "true";
    const token = localStorage.getItem("token");
    const created_at = localStorage.getItem("created_at") || "Unknown";

    const addUserBtn = document.getElementById("add-user-btn");
    const addUserModal = document.getElementById("add-user-modal");
    const cancelAddBtn = document.getElementById("cancel-add");
    const addUserForm = document.getElementById("add-user-form");
    const closeAddBtn = document.getElementById("close-add");
    const logoutBtn = document.querySelector(".logout-btn");

    if (!username || !token) {
        window.location.href = "/";
        return;
    }

    // Fill profile
    document.getElementById("username").innerText = username;
    document.getElementById("role").innerText = is_admin ? "Admin" : "User";
    document.getElementById("created_at").innerText = created_at;
    document.getElementById("task-panel").style.display = "block";

    if (is_admin) {
        document.getElementById("admin-panel").style.display = "block";
        loadUsers(token);
    }

    loadTasks();

    // --- Modal open/close ---
    addUserBtn?.addEventListener("click", () => addUserModal.classList.add("show"));
    cancelAddBtn?.addEventListener("click", () => addUserModal.classList.remove("show"));
    closeAddBtn?.addEventListener("click", () => addUserModal.classList.remove("show"));

    window.addEventListener("click", (e) => {
        if (e.target === addUserModal) addUserModal.classList.remove("show");
    });

    window.addEventListener("keydown", (e) => {
        if (e.key === "Escape") addUserModal.classList.remove("show");
    });

    // --- Add User Form Submission ---
    addUserForm?.addEventListener("submit", async (e) => {
        e.preventDefault();

        const newUsername = document.getElementById("new-username").value.trim();
        const password = document.getElementById("new-password").value;
        const isAdmin = document.getElementById("new-is-admin").checked;

        if (!newUsername || !password) return alert("Username and password are required");

        try {
            const res = await fetch("/users/register", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                    "Authorization": "Bearer " + token
                },
                body: JSON.stringify({ username: newUsername, password, is_admin: isAdmin })
            });

            const json = await res.json();
            if (!res.ok) throw new Error(json.detail || "Failed to create user");

            alert(json.msg || "User created successfully");
            addUserModal.classList.remove("show");
            addUserForm.reset();
            loadUsers(token); // refresh list
        } catch (err) {
            alert(err.message);
        }
    });

    // --- Logout handler ---
    logoutBtn?.addEventListener("click", () => {
        localStorage.clear();
        window.location.href = "/";
    });
});

async function loadUsers(token) {
    try {
        const res = await fetch("/users/all", {
            headers: { "Authorization": "Bearer " + token }
        });
        const users = await res.json();

        const container = document.getElementById("user-list");
        container.innerHTML = "";

        users.forEach(u => {
            const div = document.createElement("div");
            div.classList.add("user-item");
            div.innerHTML = `
                <span class="username">${u.username}</span>
                <span class="role">${u.is_admin ? 'Admin' : 'User'}</span>
                <button class="role-btn" data-username="${u.username}" data-role="${!u.is_admin}">
                    Make ${!u.is_admin ? 'Admin' : 'User'}
                </button>
                <button class="key-btn" data-username="${u.username}">🔑</button>
                <button class="delete-btn" data-username="${u.username}">🗑️</button>
            `;
            container.appendChild(div);
        });

        container.querySelectorAll(".key-btn").forEach(btn => {
            btn.addEventListener("click", () => {
                const username = btn.dataset.username;
                const newPass = prompt(`Enter a new password for ${username}:`);
                if (!newPass) return;
                resetPassword(username, newPass);
            });
        });

        container.querySelectorAll(".role-btn").forEach(btn => {
            btn.addEventListener("click", () => changeRole(btn.dataset.username, btn.dataset.role === "true"));
        });

        container.querySelectorAll(".delete-btn").forEach(btn => {
            btn.addEventListener("click", () => deleteUser(btn.dataset.username));
        });


    } catch (err) {
        console.error("Failed to fetch users", err);
    }
}

async function loadTasks() {
    const token = localStorage.getItem("token");
    const isAdmin = localStorage.getItem("is_admin") === "true";

    const endpoint = "/tasks"; 
    try {
        const res = await fetch(endpoint, {
            headers: { "Authorization": `Bearer ${token}` }
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Failed to load tasks");
            return;
        }

        const tasks = await res.json();
        const container = document.getElementById("task-list");
        container.innerHTML = "";

        if (tasks.length === 0) {
            container.innerHTML = `<p>No tasks found.</p>`;
            return;
        }

        tasks.forEach(t => {
            const div = document.createElement("div");
            div.classList.add("task-item");
            div.innerHTML = `
                <div class="task-header">
                    <div class="task-title"><strong>${t.title}</strong></div>
                    <div class="task-meta">
                        <span>Status: ${t.done ? "✅ Done" : "⏳ Pending"}</span>
                        ${isAdmin ? `<span class="task-owner">Owner: ${t.owner_id}</span>` : ""}
                    </div>
                </div>
                <div class="task-desc">${t.description || ""}</div>
            `;
            container.appendChild(div);
        });

        console.log("Task container:", document.getElementById("task-list"));
        console.log("Tasks loaded:", tasks);

    } catch (err) {
        console.error("Failed to fetch tasks", err);
    }
}


async function changeRole(username, is_admin) {
    const token = localStorage.getItem("token");
    try {
        const res = await fetch(`/users/${username}/role?is_admin=${is_admin}`, {
            method: "PUT",
            headers: { "Authorization": "Bearer " + token }
        });

        // Add this check to handle errors properly
        if (!res.ok) {
            const err = await res.json();
            throw new Error(err.detail || "Failed to update role");
        }

        const json = await res.json();
        alert(json.message);
        loadUsers(token);
    } catch (err) {
        alert(err.message);
    }
}

async function deleteUser(username) {
    const token = localStorage.getItem("token");
    if (!confirm(`Are you sure you want to delete user "${username}"?`)) return;

    try {
        const res = await fetch(`/users/${username}`, {
            method: "DELETE",
            headers: { "Authorization": "Bearer " + token }
        });

        if (!res.ok) {
            const err = await res.json();
            alert(err.detail || "Failed to delete user");
            return;
        }

        const json = await res.json();
        alert(json.message);
        loadUsers(token);

    } catch {
        alert("Failed to delete user");
    }
}

async function resetPassword(username, newPassword) {
    const admin_token = localStorage.getItem("token");

    try {
        const res = await fetch(`/users/${username}/password`, {
            method: "PUT",
            headers: {
                "Content-Type": "application/json",
                "Authorization": "Bearer " + admin_token
            },
            body: JSON.stringify({ new_password: newPassword })
        });

        const json = await res.json();

        if (!res.ok) throw new Error(json.detail || "Failed to update password");

        alert(json.msg || "Password updated successfully");
        loadUsers(admin_token);
    } catch (err) {
        alert(err.message);
    }
}