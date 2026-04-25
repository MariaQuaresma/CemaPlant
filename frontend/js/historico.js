function $(id) {
    return document.getElementById(id);
}

const TIMEZONE_BRASILIA = "America/Sao_Paulo";

function parseDataBackend(valor) {
    if (valor instanceof Date) {
        return valor;
    }
    if (typeof valor === "string") {
        const texto = valor.trim();
        const temFuso = /([zZ]|[+-]\d{2}:?\d{2})$/.test(texto);
        if (temFuso) {
            return new Date(texto.replace(" ", "T"));
        }
        const m = texto.match(
            /^(\d{4})-(\d{2})-(\d{2})(?:[ T](\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,6}))?)?)?$/
        );
        if (m) {
            const ano = Number(m[1]);
            const mes = Number(m[2]) - 1;
            const dia = Number(m[3]);
            const hora = Number(m[4] || 0);
            const minuto = Number(m[5] || 0);
            const segundo = Number(m[6] || 0);
            const micros = m[7] || "0";
            const ms = Number(micros.slice(0, 3).padEnd(3, "0"));
            return new Date(Date.UTC(ano, mes, dia, hora, minuto, segundo, ms));
        }
        return new Date(`${texto.replace(" ", "T")}Z`);
    }
    return new Date(valor);
}

function formatarData(valor) {
    if (!valor) {
        return "-";
    }

    const data = parseDataBackend(valor);
    if (Number.isNaN(data.getTime())) {
        return valor;
    }

    return new Intl.DateTimeFormat("pt-BR", {
        dateStyle: "short",
        timeStyle: "short",
        timeZone: TIMEZONE_BRASILIA
    }).format(data);
}

function criarItem(titulo, subtitulo, detalhes = []) {
    const li = document.createElement("li");
    li.className = "data-item";

    const head = document.createElement("div");
    head.className = "data-item__header";

    const strong = document.createElement("strong");
    strong.textContent = titulo;
    head.appendChild(strong);

    if (subtitulo) {
        const span = document.createElement("span");
        span.textContent = subtitulo;
        head.appendChild(span);
    }

    li.appendChild(head);

    detalhes.forEach((linha) => {
        if (!linha) {
            return;
        }

        const p = document.createElement("p");
        p.textContent = linha;
        li.appendChild(p);
    });

    return li;
}

function renderizarLista(id, dados, mensagemVazia, renderFn) {
    const lista = $(id);
    if (!lista) {
        return;
    }
    lista.innerHTML = "";
    if (!Array.isArray(dados) || dados.length === 0) {
        const vazio = document.createElement("li");
        vazio.className = "empty-state";
        vazio.textContent = mensagemVazia;
        lista.appendChild(vazio);
        return;
    }
    dados.forEach((item) => {
        lista.appendChild(renderFn(item));
    });
}

function setStatus(texto, tipo = "") {
    const status = $("historicoStatus");
    if (!status) {
        return;
    }
    status.textContent = texto;
    if (tipo) {
        status.dataset.state = tipo;
    }
}

async function carregarHistoricoPage() {
    if (!exigirAutenticacao()) {
        return;
    }
    setStatus("Carregando dados do usuário...", "info");
    const respostas = await Promise.allSettled([
        apiGet("/plantas/usuario"),
        apiGet("/doencas/usuario"),
        apiGet("/recomendacoes/usuario"),
        apiGet("/imagens/usuario")
    ]);
    const [plantas, doencas, recomendacoes, imagens] = respostas.map((r) => {
        if (r.status !== "fulfilled") {
            return [];
        }
        return Array.isArray(r.value) ? r.value : [];
    });
    renderizarLista("plantasUsuario", plantas, "Nenhuma planta encontrada.", (item) =>
        criarItem(
            item.nome,
            item.nome_cientifico || "",
            [item.descricao || "Sem descrição"]
        )
    );
    renderizarLista("doencasUsuario", doencas, "Nenhuma doença encontrada.", (item) =>
        criarItem(
            item.nome,
            item.nome_cientifico || "",
            [
                item.descricao || "Sem descrição",
                item.nivel !== null && item.nivel !== undefined ? `Nível: ${item.nivel}` : ""
            ]
        )
    );
    renderizarLista("recomendacoesUsuario", recomendacoes, "Nenhuma recomendação encontrada.", (item) =>
        criarItem(
            `Detecção #${item.deteccao_id}`,
            formatarData(item.data_criacao),
            [item.texto_recomendacao]
        )
    );
    renderizarLista("imagensUsuario", imagens, "Nenhuma imagem encontrada.", (item) =>
        criarItem(
            `Imagem #${item.id}`,
            formatarData(item.data_upload),
            [item.url_imagem]
        )
    );
    const teveFalha = respostas.some((r) => r.status !== "fulfilled");
    if (teveFalha) {
        setStatus("Algumas listas não puderam ser carregadas.", "warning");
        return;
    }
    setStatus("Dados carregados com sucesso.", "success");
}

window.carregarHistoricoPage = carregarHistoricoPage;

window.addEventListener("DOMContentLoaded", () => {
    const root = $("historicoPage");
    if (!root) {
        return;
    }

    carregarHistoricoPage().catch((erro) => {
        setStatus(erro.message || "Erro ao carregar histórico.", "error");
    });
});
