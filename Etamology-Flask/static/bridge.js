/* bridge.js - Modular Script Bridge */
(function() {
    // Wait for the original applet's renderRes function to exist
    const patch = () => {
        const _origRenderRes = window.renderRes;
        if (typeof _origRenderRes !== 'function') return setTimeout(patch, 50);

        window.renderRes = function(rows) {
            _origRenderRes(rows); // Run the Python-generated UI first

            document.querySelectorAll('.entry-card').forEach(card => {
                const lang = card.dataset.lang || '';
                const form = card.dataset.form || '';
                
                // Create the Historical/Modern side-by-side container
                const sideBySide = document.createElement('div');
                sideBySide.className = 'script-comparison';

                // 1. Handle Cree (Canada Tribes)
                if (lang.startsWith('cre') && window.Kilahkwaani) {
                    const ucas = Kilahkwaani.sroToSyllabics(form);
                    sideBySide.innerHTML += `<div class="mode"><span>UCAS</span><span class="cree">${ucas}</span></div>`;
                }

                // 2. Handle GLAS (Archives: Kickapoo, Fox, Potawatomi)
                if (['kic', 'sac', 'pot'].includes(lang) && window.Kilahkwaani) {
                    const glas = Kilahkwaani.romanToGlas(form, lang);
                    sideBySide.innerHTML += `<div class="mode"><span>GLAS</span><span class="glas">${glas}</span></div>`;
                }

                if (sideBySide.childNodes.length > 0) {
                    card.querySelector('.hw').after(sideBySide);
                }
            });
        };
    };
    patch();
})();
