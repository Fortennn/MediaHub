document.addEventListener('DOMContentLoaded', function () {
    document.body.classList.add('admin-theme-ready');

    const header = document.getElementById('header');
    const toggleHeaderShadow = function () {
        if (header) {
            header.classList.toggle('is-scrolled', window.scrollY > 8);
        }
    };
    toggleHeaderShadow();
    window.addEventListener('scroll', toggleHeaderShadow);

    const ambient = document.createElement('div');
    ambient.className = 'admin-ambient';
    const glowPalette = ['var(--accent-strong)', 'var(--accent-cyan)', 'rgba(255,255,255,0.06)'];
    glowPalette.forEach((color, index) => {
        const orb = document.createElement('span');
        orb.style.setProperty('--glow-color', color);
        orb.style.setProperty('--delay', `${index * 3}s`);
        orb.style.setProperty('--size', `${38 + index * 18}vmin`);
        orb.style.left = `${12 + index * 26}%`;
        orb.style.top = `${18 + index * 16}%`;
        ambient.appendChild(orb);
    });
    document.body.appendChild(ambient);

    const highlightBlocks = document.querySelectorAll('.module, .inline-group, .selector');
    highlightBlocks.forEach(block => {
        block.addEventListener('mousemove', event => {
            const rect = block.getBoundingClientRect();
            block.style.setProperty('--mx', `${event.clientX - rect.left}px`);
            block.style.setProperty('--my', `${event.clientY - rect.top}px`);
            block.classList.add('has-cursor');
        });
        block.addEventListener('mouseleave', () => block.classList.remove('has-cursor'));
    });

    const tables = document.querySelectorAll('#changelist table');
    tables.forEach(table => {
        if (table.rows.length <= 10) {
            return;
        }
        const wrapper = table.parentElement;
        const search = document.createElement('div');
        search.className = 'table-search';
        search.innerHTML = '<input aria-label="Search rows" type="search" placeholder="Search rows..." />';
        wrapper.insertBefore(search, table);
        const input = search.querySelector('input');
        input.addEventListener('input', () => {
            const query = input.value.toLowerCase();
            Array.from(table.querySelectorAll('tbody tr')).forEach(row => {
                const text = row.textContent.toLowerCase();
                row.style.display = text.includes(query) ? '' : 'none';
            });
        });
    });

    const navSidebar = document.getElementById('nav-sidebar');
    if (navSidebar) {
        const toggle = document.createElement('button');
        toggle.type = 'button';
        toggle.className = 'sidebar-toggle';
        toggle.textContent = 'Menu';
        if (header) {
            header.appendChild(toggle);
        }
        toggle.addEventListener('click', () => navSidebar.classList.toggle('open'));
    }

    const focusables = document.querySelectorAll('input, select, textarea');
    focusables.forEach(el => {
        el.addEventListener('focus', () => el.classList.add('field-focus'));
        el.addEventListener('blur', () => el.classList.remove('field-focus'));
    });
});
