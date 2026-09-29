const api = axios.create({
    baseURL: "/api",
    headers: { "Content-Type": "application/json" },
});

const state = {
    gamesPage: 1,
    gamesPageSize: 9,
    gamesPages: 0,
    editingId: null,
    editingType: null,
};

const $ = (selector) => document.querySelector(selector);

function showFeedback(selector, message, type = "") {
    const element = $(selector);
    element.textContent = message;
    element.className = `feedback ${type}`;
}

function getErrorMessage(error) {
    const detail = error?.response?.data?.detail;

    if (Array.isArray(detail)) {
        return detail.map((item) => item.msg).join(". ");
    }

    return detail || "Se ha producido un error inesperado.";
}

async function loadCategories() {
    try {
        const { data } = await api.get("/categories", {
            params: { page: 1, page_size: 100 },
        });

        const filter = $("#category-filter");
        const currentValue = filter.value;

        filter.innerHTML = '<option value="">Todas</option>';

        data.items.forEach((category) => {
            filter.insertAdjacentHTML(
                "beforeend",
                `<option value="${category.id}">${escapeHtml(category.name)}</option>`
            );
        });

        filter.value = currentValue;
        renderCategories(data.items);
    } catch (error) {
        showFeedback("#category-feedback", getErrorMessage(error), "error");
    }
}

async function loadGames() {
    const feedback = "#game-feedback";
    showFeedback(feedback, "Cargando...");

    try {
        const params = {
            page: state.gamesPage,
            page_size: state.gamesPageSize,
            search: $("#search-input").value.trim() || undefined,
            category_id: $("#category-filter").value || undefined,
        };

        const { data } = await api.get("/games", { params });

        state.gamesPages = data.pages;
        renderGames(data.items);

        $("#page-info").textContent =
            `Página ${data.page} de ${Math.max(data.pages, 1)}`;

        $("#previous-page").disabled = data.page <= 1;
        $("#next-page").disabled = data.pages === 0 || data.page >= data.pages;

        showFeedback(feedback, `${data.total} videojuego(s) encontrado(s).`, "success");
    } catch (error) {
        showFeedback(feedback, getErrorMessage(error), "error");
    }
}

function renderGames(games) {
    const container = $("#games-list");

    if (!games.length) {
        container.innerHTML = '<div class="card"><p>No hay videojuegos para mostrar.</p></div>';
        return;
    }

    container.innerHTML = games.map((game) => `
        <article class="card">
            <h3>${escapeHtml(game.title)}</h3>
            <div class="card-meta">
                <span class="badge">${escapeHtml(game.category.name)}</span>
                ${game.platform ? `<span class="badge">${escapeHtml(game.platform)}</span>` : ""}
                ${game.release_year ? `<span class="badge">${game.release_year}</span>` : ""}
            </div>
            <p>${escapeHtml(game.description || "Sin descripción.")}</p>
            ${game.developer ? `<p><strong>Desarrollador:</strong> ${escapeHtml(game.developer)}</p>` : ""}
            <div class="card-actions">
                <button class="button secondary" onclick="editGame(${game.id})">Editar</button>
                <button class="button danger" onclick="removeGame(${game.id})">Eliminar</button>
            </div>
        </article>
    `).join("");
}

function renderCategories(categories) {
    const container = $("#categories-list");

    if (!categories.length) {
        container.innerHTML = '<div class="card"><p>No hay categorías.</p></div>';
        return;
    }

    container.innerHTML = categories.map((category) => `
        <article class="card">
            <h3>${escapeHtml(category.name)}</h3>
            <p>${escapeHtml(category.description || "Sin descripción.")}</p>
            <div class="card-meta">
                <span class="badge">${category.games_count} videojuego(s)</span>
            </div>
            <div class="card-actions">
                <button class="button secondary" onclick="editCategory(${category.id})">Editar</button>
                <button class="button danger" onclick="removeCategory(${category.id})">Eliminar</button>
            </div>
        </article>
    `).join("");
}

function openModal(title, fields, type, id = null) {
    state.editingId = id;
    state.editingType = type;

    $("#modal-title").textContent = title;
    $("#form-fields").innerHTML = fields;
    $("#modal").classList.remove("hidden");
}

function closeModal() {
    $("#modal").classList.add("hidden");
    $("#entity-form").reset();
    state.editingId = null;
    state.editingType = null;
}

async function openGameForm(game = null) {
    let categories = [];

    try {
        const { data } = await api.get("/categories", {
            params: { page: 1, page_size: 100 },
        });
        categories = data.items;
    } catch (error) {
        showFeedback("#game-feedback", getErrorMessage(error), "error");
        return;
    }

    const categoryOptions = categories.map((category) =>
        `<option value="${category.id}" ${game?.category.id === category.id ? "selected" : ""}>
            ${escapeHtml(category.name)}
        </option>`
    ).join("");

    openModal(
        game ? "Editar videojuego" : "Nuevo videojuego",
        `
        <label>Título<input name="title" required maxlength="150" value="${escapeAttribute(game?.title || "")}"></label>
        <label>Descripción<input name="description" maxlength="1000">${escapeHtml(game?.description || "")}</label>
        <label>Año de lanzamiento<input name="release_year" type="number" min="1950" max="2100" value="${game?.release_year || ""}"></label>
        <label>Desarrollador<input name="developer" maxlength="120" value="${escapeAttribute(game?.developer || "")}"></label>
        <label>Plataforma<input name="platform" maxlength="80" value="${escapeAttribute(game?.platform || "")}"></label>
        <label>Categoría<select name="category_id" required>${categoryOptions}</select></label>
        `,
        "game",
        game?.id ?? null
    );
}

async function editGame(id) {
    try {
        const { data } = await api.get(`/games/${id}`);
        await openGameForm(data);
    } catch (error) {
        showFeedback("#game-feedback", getErrorMessage(error), "error");
    }
}

function openCategoryForm(category = null) {
    openModal(
        category ? "Editar categoría" : "Nueva categoría",
        `
        <label>Nombre<input name="name" required minlength="2" maxlength="80" value="${escapeAttribute(category?.name || "")}"></label>
        <label>Descripción<input name="description" maxlength="500">${escapeHtml(category?.description || "")}</label>
        `,
        "category",
        category?.id ?? null
    );
}

async function editCategory(id) {
    try {
        const { data } = await api.get(`/categories/${id}`);
        openCategoryForm(data);
    } catch (error) {
        showFeedback("#category-feedback", getErrorMessage(error), "error");
    }
}

async function submitForm(event) {
    event.preventDefault();

    const formData = new FormData(event.target);
    const payload = Object.fromEntries(formData.entries());

    if (state.editingType === "game") {
        payload.release_year = payload.release_year ? Number(payload.release_year) : null;
        payload.category_id = Number(payload.category_id);

        try {
            if (state.editingId) {
                await api.put(`/games/${state.editingId}`, payload);
                showFeedback("#game-feedback", "Videojuego actualizado correctamente.", "success");
            } else {
                await api.post("/games", payload);
                showFeedback("#game-feedback", "Videojuego creado correctamente.", "success");
            }

            closeModal();
            await loadCategories();
            await loadGames();
        } catch (error) {
            showFeedback("#game-feedback", getErrorMessage(error), "error");
        }
        return;
    }

    try {
        if (state.editingId) {
            await api.put(`/categories/${state.editingId}`, payload);
            showFeedback("#category-feedback", "Categoría actualizada correctamente.", "success");
        } else {
            await api.post("/categories", payload);
            showFeedback("#category-feedback", "Categoría creada correctamente.", "success");
        }

        closeModal();
        await loadCategories();
        await loadGames();
    } catch (error) {
        showFeedback("#category-feedback", getErrorMessage(error), "error");
    }
}

async function removeGame(id) {
    if (!window.confirm("¿Seguro que quieres eliminar este videojuego?")) return;

    try {
        await api.delete(`/games/${id}`);
        showFeedback("#game-feedback", "Videojuego eliminado correctamente.", "success");
        await loadCategories();
        await loadGames();
    } catch (error) {
        showFeedback("#game-feedback", getErrorMessage(error), "error");
    }
}

async function removeCategory(id) {
    if (!window.confirm(
        "¿Eliminar esta categoría? Solo podrá eliminarse si no tiene videojuegos asociados."
    )) return;

    try {
        await api.delete(`/categories/${id}`);
        showFeedback("#category-feedback", "Categoría eliminada correctamente.", "success");
        await loadCategories();
        await loadGames();
    } catch (error) {
        showFeedback("#category-feedback", getErrorMessage(error), "error");
    }
}

function escapeHtml(value) {
    return String(value)
        .replaceAll("&", "&amp;")
        .replaceAll("<", "&lt;")
        .replaceAll(">", "&gt;")
        .replaceAll('"', "&quot;")
        .replaceAll("'", "&#039;");
}

function escapeAttribute(value) {
    return escapeHtml(value);
}

$("#new-game-button").addEventListener("click", () => openGameForm());
$("#new-category-button").addEventListener("click", () => openCategoryForm());
$("#search-button").addEventListener("click", () => {
    state.gamesPage = 1;
    loadGames();
});
$("#previous-page").addEventListener("click", () => {
    if (state.gamesPage > 1) {
        state.gamesPage -= 1;
        loadGames();
    }
});
$("#next-page").addEventListener("click", () => {
    if (state.gamesPage < state.gamesPages) {
        state.gamesPage += 1;
        loadGames();
    }
});
$("#modal-close").addEventListener("click", closeModal);
$("#cancel-button").addEventListener("click", closeModal);
$("#entity-form").addEventListener("submit", submitForm);

$("#search-input").addEventListener("keydown", (event) => {
    if (event.key === "Enter") {
        state.gamesPage = 1;
        loadGames();
    }
});

$("#category-filter").addEventListener("change", () => {
    state.gamesPage = 1;
    loadGames();
});

loadCategories().then(loadGames);
