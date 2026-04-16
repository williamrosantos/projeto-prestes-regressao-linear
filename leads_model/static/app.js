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

    console.log("App.js carregado. Iniciando campos estáticos...");

    // ── Determinar URL da API ────────────────────────────
    // Usar caminhos relativos para funcionar em qualquer porta (ex: 3001)
    const API_BASE = ''; 
    console.log(`Usando Base da API: ${API_BASE || 'Mesma porta do Frontend'}`);

    // ── 1. Inicializar Campos Estáticos ──────────────────
    MONTHS.forEach((m, i) => {
        const opt = document.createElement('option');
        opt.value = i + 1;
        opt.textContent = m;
        monthSelect.appendChild(opt);
    });
    monthSelect.selectedIndex = 2; // Março

    // Inicializar selects com "Carregando..."
    pracaSelect.innerHTML = '<option value="">Carregando...</option>';
    projectSelect.innerHTML = '<option value="">Aguardando praça...</option>';

    // ── 1.1 Modal e Ciclo ────────────────────────────────
    const modalOverlay = document.getElementById('modal-empreendimento');
    const modalBody = document.getElementById('modal-body');

    document.getElementById('btn-modal-emp').addEventListener('click', async () => {
        if (modalBody.innerHTML === '') {
            const resp = await fetch(`${API_BASE}/api/historico-empreendimentos`);
            const data = await resp.json();
            data.forEach(row => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${row.empreendimento}</td>
                    <td>${row.praca}</td>
                    <td>R$ ${row.cpl_medio.toLocaleString('pt-BR', {minimumFractionDigits: 2})}</td>
                    <td>${(row.taxa_qualif * 100).toFixed(0)}%</td>
                    <td>${(row.taxa_visita * 100).toFixed(0)}%</td>
                    <td>${(row.taxa_reserva * 100).toFixed(0)}%</td>
                    <td>${row.meses}</td>
                `;
                modalBody.appendChild(tr);
            });
        }
        modalOverlay.classList.remove('hidden');
    });

    document.getElementById('btn-modal-close').addEventListener('click', () => {
        modalOverlay.classList.add('hidden');
    });

    modalOverlay.addEventListener('click', (e) => {
        if (e.target === modalOverlay) modalOverlay.classList.add('hidden');
    });

    async function updateCiclo(empreendimento) {
        if (!empreendimento) return;
        try {
            const resp = await fetch(`${API_BASE}/api/ciclo?empreendimento=${encodeURIComponent(empreendimento)}`);
            const data = await resp.json();
            document.getElementById('ciclo-valor').textContent = data.mes_ciclo;
            document.getElementById('meta-ciclo').style.display = 'block';
        } catch (err) {
            console.error("Erro ao carregar ciclo:", err);
        }
    }

    // ── 2. Carregar Metadados da API ──────────────────────
    async function loadMetadata() {
        console.log(`Buscando metadados em ${API_BASE}/api/metadata...`);
        showLoader(true);
        try {
            const resp = await fetch(`${API_BASE}/api/metadata`);
            console.log("Resposta do servidor:", resp.status, resp.statusText);
            
            if (!resp.ok) {
                const errorText = await resp.text();
                throw new Error(`Erro na API (${resp.status}): ${errorText}`);
            }

            const data = await resp.json();
            console.log("Dados recebidos:", data);

            pracaMapping = data.mapping || {};

            // Popular Praças
            pracaSelect.innerHTML = '';
            if (data.pracas && data.pracas.length > 0) {
                data.pracas.forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p;
                    opt.textContent = p;
                    pracaSelect.appendChild(opt);
                });
                // Trigger inicial de Empreendimentos
                updateProjects(data.pracas[0]);
            } else {
                pracaSelect.innerHTML = '<option value="">Nenhuma praça encontrada</option>';
            }

            // Popular Tabela de Histórico
            if (data.historico) {
                populateHistory(data.historico);
            }

            // Resumo do Rodapé
            if (data.summary) {
                document.getElementById('db-summary').innerHTML = `
                    <div class="meta-item"><span>Total Registros:</span> ${data.summary.total_registros}</div>
                    <div class="meta-item"><span>Período:</span> ${data.summary.periodo}</div>
                `;
            }

        } catch (err) {
            console.error('Erro crítico no loadMetadata:', err);
            notification(`ERRO DE CONEXÃO: Certifique-se de que o servidor Python está rodando e acesse via http://localhost:8000\n\nDetalhe: ${err.message}`, 'error');
            pracaSelect.innerHTML = '<option value="">Erro ao carregar</option>';
        } finally {
            showLoader(false);
        }
    }

    function updateProjects(praca) {
        console.log("Atualizando projetos para praça:", praca);
        projectSelect.innerHTML = '';
        const projects = pracaMapping[praca] || [];
        if (projects.length > 0) {
            projects.forEach(p => {
                const opt = document.createElement('option');
                opt.value = p;
                opt.textContent = p;
                projectSelect.appendChild(opt);
            });
        } else {
            projectSelect.innerHTML = '<option value="">Nenhum empreendimento</option>';
        }
        // Atualizar ciclo para o primeiro projeto da lista
        if (projectSelect.value) updateCiclo(projectSelect.value);
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
    projectSelect.addEventListener('change', (e) => updateCiclo(e.target.value));

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
            const resp = await fetch(`${API_BASE}/api/predict`, {
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
