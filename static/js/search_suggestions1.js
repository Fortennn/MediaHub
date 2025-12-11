(() => {
  const supportsAbort = typeof window !== 'undefined' && 'AbortController' in window;
  const isMobile = () => window.matchMedia('(max-width: 768px)').matches;

  const debounce = (fn, delay = 220) => {
    let timeoutId;
    return (...args) => {
      clearTimeout(timeoutId);
      timeoutId = setTimeout(() => fn(...args), delay);
    };
  };

  const typeFallback = (type) => {
    const map = {
      movie: 'Movie',
      series: 'Series',
      anime: 'Anime',
    };
    return map[type] || 'Media';
  };

  const createDropdown = (wrapper) => {
    let dropdown = wrapper.querySelector('.search-suggestions');
    if (!dropdown) {
      dropdown = document.createElement('div');
      dropdown.className = 'search-suggestions';
      wrapper.appendChild(dropdown);
    }
    return dropdown;
  };

  const addSeparator = (meta) => {
    const separator = document.createElement('span');
    separator.className = 'dot';
    separator.textContent = '|';
    meta.appendChild(separator);
  };

  const renderSuggestions = (dropdown, items) => {
    dropdown.innerHTML = '';

    if (!items.length) {
      dropdown.classList.remove('show');
      return;
    }

    items.forEach((item) => {
      const link = document.createElement('a');
      link.className = 'search-suggestion-item';
      link.href = item.url;

      const thumb = document.createElement('div');
      thumb.className = 'suggestion-thumb';
      if (item.poster) {
        const img = document.createElement('img');
        img.src = item.poster;
        img.alt = item.title;
        thumb.appendChild(img);
      } else {
        const initial = document.createElement('span');
        const source = item.type_label || typeFallback(item.type);
        initial.textContent = (source || '?').slice(0, 1).toUpperCase();
        thumb.appendChild(initial);
      }

      const body = document.createElement('div');
      body.className = 'suggestion-body';

      const title = document.createElement('div');
      title.className = 'suggestion-title';
      title.textContent = item.title;

      const meta = document.createElement('div');
      meta.className = 'suggestion-meta';

      const typeLabel = document.createElement('span');
      typeLabel.textContent = item.type_label || typeFallback(item.type);
      meta.appendChild(typeLabel);

      if (item.release_year) {
        addSeparator(meta);
        const year = document.createElement('span');
        year.textContent = item.release_year;
        meta.appendChild(year);
      }

      if (typeof item.avg_rating !== 'undefined') {
        addSeparator(meta);
        const rating = document.createElement('span');
        rating.textContent = Number(item.avg_rating).toFixed(1);
        meta.appendChild(rating);
      }

      body.appendChild(title);
      body.appendChild(meta);

      link.appendChild(thumb);
      link.appendChild(body);
      dropdown.appendChild(link);
    });

    dropdown.classList.add('show');
  };

  const renderEmpty = (dropdown) => {
    dropdown.innerHTML = '<div class="search-suggestion-empty">Нічого не знайдено</div>';
    dropdown.classList.add('show');
  };

  const setupInput = (input) => {
    const url = input.dataset.suggestionsUrl;
    if (!url) return;

    const wrapper = input.closest('.search-form-sakura') || input.parentElement;
    if (!wrapper) return;

    const dropdown = createDropdown(wrapper);
    let abortController = null;

    const fetchSuggestions = debounce(async () => {
      const query = input.value.trim();

      if (!query) {
        renderSuggestions(dropdown, []);
        return;
      }

      if (supportsAbort && abortController) {
        abortController.abort();
      }

      abortController = supportsAbort ? new AbortController() : null;

      try {
        const response = await fetch(
          `${url}?q=${encodeURIComponent(query)}`,
          {
            signal: abortController ? abortController.signal : undefined,
            headers: { 'X-Requested-With': 'XMLHttpRequest' },
          }
        );

        if (!response.ok) {
          renderSuggestions(dropdown, []);
          return;
        }

        const data = await response.json();

        if (input.value.trim() !== query) {
          return;
        }

        const items = data.results || [];
        if (!items.length) {
          renderEmpty(dropdown);
          return;
        }

        renderSuggestions(dropdown, items);
      } catch (error) {
        if (error.name !== 'AbortError') {
          console.warn('Search suggestions failed', error);
        }
      }
    });

    input.addEventListener('input', fetchSuggestions);
    input.addEventListener('focus', () => {
      if (dropdown.childElementCount) {
        dropdown.classList.add('show');
      }
    });

    input.addEventListener('keydown', (event) => {
      if (event.key === 'Escape') {
        dropdown.classList.remove('show');
      }
    });

    document.addEventListener('click', (event) => {
      if (!wrapper.contains(event.target)) {
        dropdown.classList.remove('show');
      }
    });

    input.addEventListener('blur', () => {
      setTimeout(() => dropdown.classList.remove('show'), 120);
    });

    input.addEventListener('touchstart', () => {
      dropdown.classList.remove('show');
    });

    if (isMobile()) {
      dropdown.classList.add('mobile');
    }
  };

  document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('[data-suggestions-url]').forEach(setupInput);
  });
})();
