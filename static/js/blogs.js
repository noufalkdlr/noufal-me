(function () {
  const PER_PAGE = 6;

  const blogs = JSON.parse(document.getElementById("blogs-data").textContent);
  const listEl = document.getElementById("blog-list");
  const emptyEl = document.getElementById("blogs-empty");
  const paginationEl = document.getElementById("pagination");
  const searchEl = document.getElementById("search-input");
  const categoryEl = document.getElementById("category-filter");

  let state = {
    query: "",
    category: "all",
    page: 1,
  };

  function filteredBlogs() {
    const q = state.query.trim().toLowerCase();
    return blogs.filter((blog) => {
      const matchesCategory =
        state.category === "all" || blog.category === state.category;
      const matchesQuery =
        !q ||
        blog.title.toLowerCase().includes(q) ||
        blog.description.toLowerCase().includes(q) ||
        (blog.tags || []).some((t) => t.toLowerCase().includes(q));
      return matchesCategory && matchesQuery;
    });
  }

  function renderCard(blog) {
    const a = document.createElement("a");
    a.href = "/blogs/" + blog.slug + "/";
    a.className = "blog-card";

    a.innerHTML =
      '<div class="blog-card-thumb"><img src="' +
      blog.thumbnail +
      '" alt="' +
      blog.title +
      '" loading="lazy" /></div>' +
      '<div class="blog-card-body">' +
      '<div class="blog-card-meta"><time>' +
      blog.formatted_date +
      "</time><span>&bull;</span><span>" +
      blog.category +
      "</span></div>" +
      "<h2>" +
      blog.title +
      "</h2>" +
      '<p class="blog-card-desc">' +
      blog.description +
      "</p>" +
      "</div>";

    return a;
  }

  function renderPagination(total) {
    paginationEl.innerHTML = "";
    const totalPages = Math.max(1, Math.ceil(total / PER_PAGE));

    if (totalPages <= 1) return;

    const prev = document.createElement("button");
    prev.className = "page-btn";
    prev.textContent = "Prev";
    prev.disabled = state.page === 1;
    prev.addEventListener("click", () => {
      state.page = Math.max(1, state.page - 1);
      render();
    });
    paginationEl.appendChild(prev);

    for (let i = 1; i <= totalPages; i++) {
      const btn = document.createElement("button");
      btn.className = "page-btn" + (state.page === i ? " is-active" : "");
      btn.textContent = String(i);
      btn.addEventListener("click", () => {
        state.page = i;
        render();
      });
      paginationEl.appendChild(btn);
    }

    const next = document.createElement("button");
    next.className = "page-btn";
    next.textContent = "Next";
    next.disabled = state.page === totalPages;
    next.addEventListener("click", () => {
      state.page = Math.min(totalPages, state.page + 1);
      render();
    });
    paginationEl.appendChild(next);
  }

  function render() {
    const results = filteredBlogs();
    const totalPages = Math.max(1, Math.ceil(results.length / PER_PAGE));
    state.page = Math.min(state.page, totalPages);

    const start = (state.page - 1) * PER_PAGE;
    const pageItems = results.slice(start, start + PER_PAGE);

    listEl.innerHTML = "";
    emptyEl.hidden = results.length > 0;

    pageItems.forEach((blog) => listEl.appendChild(renderCard(blog)));
    renderPagination(results.length);
  }

  searchEl.addEventListener("input", (e) => {
    state.query = e.target.value;
    state.page = 1;
    render();
  });

  categoryEl.addEventListener("click", (e) => {
    const btn = e.target.closest(".category-pill");
    if (!btn) return;

    categoryEl
      .querySelectorAll(".category-pill")
      .forEach((el) => el.classList.remove("is-active"));
    btn.classList.add("is-active");

    state.category = btn.dataset.category;
    state.page = 1;
    render();
  });

  // The first page of cards is already server-rendered into #blog-list at
  // build time (for crawlers / no-JS), and the pagination controls below
  // it are rebuilt here to match. We only need a full client-side render
  // once the user actually searches, filters, or paginates — not on load.
  renderPagination(filteredBlogs().length);
})();
