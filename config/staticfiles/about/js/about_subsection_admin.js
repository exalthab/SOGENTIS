document.addEventListener('DOMContentLoaded', function () {
    const wrappers = document.querySelectorAll('.smart-tabs-wrapper');

    wrappers.forEach(wrapper => {
        const fields = Array.from(wrapper.querySelectorAll('.form-row'));

        // Créer onglets
        const tabContainer = document.createElement('div');
        tabContainer.classList.add('smart-tabs');

        const contentContainer = document.createElement('div');
        contentContainer.classList.add('smart-tab-contents');

        const tabs = [];
        const contents = [];

        // Grouper par section a/b/c...
        const sections = ['a', 'b', 'c', 'd', 'e', 'f'];

        sections.forEach(section => {
            // Tab
            const tab = document.createElement('div');
            tab.classList.add('smart-tab');
            tab.textContent = wrapper.querySelector(`#id_${section}_title`).previousSibling.textContent || section.toUpperCase();
            tabContainer.appendChild(tab);
            tabs.push(tab);

            // Content wrapper
            const contentDiv = document.createElement('div');
            contentDiv.classList.add('smart-tab-content');

            ['title', 'content', 'image'].forEach(field => {
                const row = wrapper.querySelector(`.form-row.field-${section}_${field}`);
                if (row) contentDiv.appendChild(row);
            });

            contentContainer.appendChild(contentDiv);
            contents.push(contentDiv);
        });

        wrapper.prepend(tabContainer);
        wrapper.appendChild(contentContainer);

        // Activer premier onglet
        tabs[0].classList.add('active');
        contents[0].classList.add('active');

        // Click event
        tabs.forEach((tab, idx) => {
            tab.addEventListener('click', () => {
                tabs.forEach(t => t.classList.remove('active'));
                contents.forEach(c => c.classList.remove('active'));
                tab.classList.add('active');
                contents[idx].classList.add('active');
            });
        });
    });
});
