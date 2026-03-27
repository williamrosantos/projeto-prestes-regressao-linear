document.addEventListener('DOMContentLoaded', () => {
    const pracaSelect = document.getElementById('praca');
    const projectSelect = document.getElementById('empreendimento');
    const monthSelect = document.getElementById('mes');
    const form = document.getElementById('simulation-form');
    const resultsGrid = document.getElementById('results-display');
    const historyBody = document.getElementById('history-body');
    const loader = document.getElementById('loader');

    let pracaMapping = {};

    const MONTHS = [
        "Janeiro", "Fevereiro", "Março", "Abril", "Maio", "Junho",
        "Julho", "Agosto", "Setembro", "Outubro", "Novembro", "Dezembro"
    ];

    // ── 1. Inicializar Campos Estáticos ──────────────────
    MONTHS.forEach((m, i) => {
        const opt = document.createElement('option');
        opt.value = i + 1;
        opt.textContent = m;
        monthSelect.appendChild(opt);
    });
    // Marcar Março como default (index 2)
    monthSelect.selectedIndex = 2;

    // ── 2. Carregar Metadados da API ──────────────────────
    async function loadMetadata() {
        showLoader(true);
        try {
            const resp = await fetch('/api/metadata');
            const data = await resp.json();

            pracaMapping = data.mapping;

            // Popular Praças
            pracaSelect.innerHTML = '';
            data.pracas.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p;
                opt.textContent = p;
                pracaSelect.appendChild(opt);
            });

            // Trigger inicial de Empreendimentos
            updateProjects(data.pracas[0]);

            // Popular Tabela de Histórico
            populateHistory(data.historico);

            // Resumo do Rodapé
            document.getElementById('db-summary').innerHTML = `
                <div class="meta-item"><span>Total Registros:</span> ${data.summary.total_registros}</div>
                <div class="meta-item"><span>Período:</span> ${data.summary.periodo}</div>
            `;

        } catch (err) {
            console.error('Erro ao carregar metadados:', err);
            notification('Erro de conexão com o servidor.', 'error');
        } finally {
            showLoader(false);
        }
    }

    function updateProjects(praca) {
        projectSelect.innerHTML = '';
        const projects = pracaMapping[praca] || [];
        projects.forEach(p => {
            const opt = document.createElement('option');
            opt.value = p;
            opt.textContent = p;
            projectSelect.appendChild(opt);
        });
    }

    function populateHistory(history) {
        historyBody.innerHTML = '';
        history.forEach(row => {
            const tr = document.createElement('tr');
            tr.innerHTML = `
                <td><strong>${row.praca}</strong></td>
                <td>R$ ${row.cpl_medio.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                <td>${(row.taxa_qualif * 100).toFixed(0)}%</td>
                <td>${(row.taxa_visita * 100).toFixed(0)}%</td>
                <td>${(row.taxa_reserva * 100).toFixed(0)}%</td>
                <td>${row.meses}</td>
            `;
            historyBody.appendChild(tr);
        });
    }

    // ── 3. Eventos ───────────────────────────────────────
    pracaSelect.addEventListener('change', (e) => updateProjects(e.target.value));

    form.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const payload = {
            praca: pracaSelect.value,
            empreendimento: projectSelect.value,
            investimento: parseFloat(document.getElementById('investimento').value),
            mes_calendario: parseInt(monthSelect.value),
            taxa_manual: document.getElementById('taxa-manual').value ? parseFloat(document.getElementById('taxa-manual').value) / 100 : null
        };

        showLoader(true);
        try {
            const resp = await fetch('/api/predict', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            });

            if (!resp.ok) throw new Error('Falha na predição');
            
            const results = await resp.json();
            renderResults(results);

        } catch (err) {
            console.error(err);
            notification('Erro ao calcular predição.', 'error');
        } finally {
            showLoader(false);
        }
    });

    function renderResults(res) {
        resultsGrid.innerHTML = `
            <div class="result-card card animate-in">
                <span class="res-label">Leads Estimados</span>
                <div class="res-value">${res.leads_estimados.toLocaleString('pt-BR')}</div>
                <div class="res-sub">Captação total projetada</div>
            </div>
            <div class="result-card card animate-in" style="animation-delay: 0.1s">
                <span class="res-label">Qualificados (Modelo)</span>
                <div class="res-value">${res.leads_qualificados_modelo.toLocaleString('pt-BR')}</div>
                <div class="res-sub">Performance estatística</div>
            </div>
            <div class="result-card card animate-in" style="animation-delay: 0.2s">
                <span class="res-label">Qualificados (Taxa)</span>
                <div class="res-value">${res.leads_qualificados_taxa.toLocaleString('pt-BR')}</div>
                <div class="res-sub">Fonte: ${res.origem_taxa || 'Histórico'}</div>
            </div>
            <div class="result-card card animate-in" style="animation-delay: 0.3s">
                <span class="res-label">CPL Implícito</span>
                <div class="res-value">R$ ${res.cpl.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</div>
                <div class="res-sub">Custo médio por lead</div>
            </div>
        `;
    }

    // ── Helpers ──────────────────────────────────────────
    function showLoader(show) {
        loader.classList.toggle('hidden', !show);
        form.querySelector('button').disabled = show;
    }

    function notification(msg, type) {
        // Simples alert por enquanto, poderia ser um toast
        alert(msg);
    }

    // Início
    loadMetadata();
});
