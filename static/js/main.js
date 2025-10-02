const form = document.getElementById('email-form');
const loadingEl = document.getElementById('loading');
const resultEl = document.getElementById('result');
const errorEl = document.getElementById('error');
const categoriaEl = document.getElementById('categoria');
const motivoEl = document.getElementById('motivo');
const respostaEl = document.getElementById('resposta');
const historyEl = document.getElementById('history');
const countProdutivoEl = document.getElementById('count-produtivo');
const countImprodutivoEl = document.getElementById('count-improdutivo');

function setLoading(isLoading) {
  loadingEl.classList.toggle('d-none', !isLoading);
}

function setError(message) {
  if (message) {
    errorEl.textContent = message;
    errorEl.classList.remove('d-none');
  } else {
    errorEl.classList.add('d-none');
    errorEl.textContent = '';
  }
}

function updateResult(data) {
  resultEl.classList.remove('d-none');
  const cat = data.categoria || 'Improdutivo';
  categoriaEl.textContent = cat;
  categoriaEl.className = 'badge ' + (cat === 'Produtivo' ? 'bg-success' : 'bg-secondary');

  motivoEl.textContent = data.motivo || '';
  respostaEl.value = data.resposta_sugerida || '';
}

function updateDashboardAndHistory(data) {
  if (data.counts) {
    countProdutivoEl.textContent = data.counts.Produtivo || 0;
    countImprodutivoEl.textContent = data.counts.Improdutivo || 0;
  }
  if (Array.isArray(data.history)) {
    historyEl.innerHTML = '';
    if (data.history.length === 0) {
      const li = document.createElement('li');
      li.className = 'list-group-item text-muted';
      li.textContent = 'Sem itens ainda.';
      historyEl.appendChild(li);
      return;
    }
    data.history.forEach(item => {
      const li = document.createElement('li');
      li.className = 'list-group-item';
      const badge = document.createElement('span');
      badge.className = 'badge me-2 ' + (item.categoria === 'Produtivo' ? 'bg-success' : 'bg-secondary');
      badge.textContent = item.categoria;
      li.appendChild(badge);
      li.appendChild(document.createTextNode(item.preview || ''));
      historyEl.appendChild(li);
    });
  }
}

form.addEventListener('submit', async (e) => {
  e.preventDefault();
  setError('');
  resultEl.classList.add('d-none');
  setLoading(true);

  try {
    const formData = new FormData(form);
    const res = await fetch('/process', {
      method: 'POST',
      body: formData,
    });
    const data = await res.json();
    if (!res.ok) {
      throw new Error(data.error || 'Erro ao processar');
    }
    updateResult(data);
    updateDashboardAndHistory(data);
  } catch (err) {
    setError(err.message || String(err));
  } finally {
    setLoading(false);
  }
});