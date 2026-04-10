#!/usr/bin/env python3
"""
Gera um artigo via Claude API e adiciona ao artigos.json.
Corre automaticamente via GitHub Actions.
Artigos: 1400-1800 palavras, estrutura SEO completa.
"""

import anthropic
import json
import os
import random
from datetime import datetime, timezone

# ── Configuração ──────────────────────────────────────────────
CATEGORIAS = [
    "Perda Auditiva",
    "Sinais de Alerta",
    "Prevenção",
    "Família",
    "Diagnóstico",
    "Aparelhos",
]

TEMAS_POR_CATEGORIA = {
    "Perda Auditiva": [
        "Os diferentes tipos de perda auditiva e o que os causa",
        "Perda auditiva neurossensorial: o que é e como se trata",
        "Como a perda auditiva afecta a memória e o cérebro",
        "Perda auditiva súbita: quando é urgência médica",
        "A relação entre diabetes e perda auditiva",
        "Presbiacusia: a perda auditiva associada ao envelhecimento",
        "Perda auditiva congénita: causas e abordagens terapêuticas",
    ],
    "Sinais de Alerta": [
        "Os 10 sinais de que precisa de uma consulta auditiva urgente",
        "Zumbidos no ouvido: quando devem preocupar",
        "Por que razão as vozes femininas são mais difíceis de perceber",
        "O que significa precisar de legendas na televisão",
        "Dificuldade ao telefone: sinal de alerta ou hábito?",
        "Sensação de ouvido tapado: causas e quando consultar",
        "Hipersensibilidade a sons: o que é a hiperacusia",
    ],
    "Prevenção": [
        "Como proteger a audição no local de trabalho",
        "Auscultadores e audição: o que a ciência diz",
        "Os medicamentos que podem danificar a audição",
        "Exercício físico e saúde auditiva: a ligação surpreendente",
        "Alimentação e audição: o que comer para proteger os ouvidos",
        "Ruído urbano e perda auditiva: riscos do quotidiano",
        "Protectores auditivos: como escolher os mais eficazes",
    ],
    "Família": [
        "Como convencer um familiar a fazer a consulta auditiva",
        "Viver com alguém com perda auditiva: guia para familiares",
        "Como comunicar melhor com pais ou avós com dificuldades auditivas",
        "O impacto da perda auditiva nos relacionamentos",
        "Como explicar a perda auditiva a crianças pequenas",
        "Perda auditiva e isolamento social: como ajudar",
        "Cuidar de um familiar com aparelho auditivo",
    ],
    "Diagnóstico": [
        "O audiograma explicado em linguagem simples",
        "Quanto tempo demora o diagnóstico de perda auditiva?",
        "O que esperar na primeira consulta auditiva",
        "Os diferentes testes de audição e o que medem",
        "Como ler e interpretar o seu audiograma",
        "Audiologista vs otorrinolaringologista: a quem recorrer?",
        "Rastreio auditivo: por que fazer mesmo sem sintomas",
    ],
    "Aparelhos": [
        "Aparelhos auditivos modernos: o que mudou nos últimos 5 anos",
        "Aparelhos auditivos invisíveis: valem o preço?",
        "Como adaptar-se a um aparelho auditivo novo",
        "A diferença entre aparelhos auditivos e amplificadores de som",
        "Aparelhos auditivos recarregáveis: prós e contras",
        "Inteligência artificial nos aparelhos auditivos modernos",
        "Aparelhos auditivos e Bluetooth: ligar ao smartphone",
    ],
}

IMAGENS_UNSPLASH = {
    "Perda Auditiva": "photo-1559757148-5c350d0d3c56",
    "Sinais de Alerta": "photo-1576091160550-2173dba999ef",
    "Prevenção": "photo-1571019613454-1cb2f99b2d8b",
    "Família": "photo-1529156069898-49953e39b3ac",
    "Diagnóstico": "photo-1584308666744-24d5c474f2ae",
    "Aparelhos": "photo-1516549655169-df83a0774514",
}


def escolher_categoria_e_tema():
    categoria_input = os.environ.get("CATEGORIA_INPUT", "auto")
    
    if categoria_input == "auto":
        try:
            with open("artigos.json", "r", encoding="utf-8") as f:
                existentes = json.load(f)
            cats_recentes = [a.get("cat") for a in existentes[:6]]
            categorias_disponiveis = [c for c in CATEGORIAS if c not in cats_recentes]
            if not categorias_disponiveis:
                categorias_disponiveis = CATEGORIAS
        except Exception:
            categorias_disponiveis = CATEGORIAS
        
        categoria = random.choice(categorias_disponiveis)
    else:
        categoria = categoria_input if categoria_input in CATEGORIAS else random.choice(CATEGORIAS)
    
    try:
        with open("artigos.json", "r", encoding="utf-8") as f:
            existentes = json.load(f)
        titulos_existentes = [a.get("titulo", "").lower() for a in existentes[:20]]
        temas_disponiveis = [
            t for t in TEMAS_POR_CATEGORIA[categoria]
            if not any(palavra in t.lower() for titulo in titulos_existentes 
                      for palavra in titulo.split() if len(palavra) > 5)
        ]
        if not temas_disponiveis:
            temas_disponiveis = TEMAS_POR_CATEGORIA[categoria]
    except Exception:
        temas_disponiveis = TEMAS_POR_CATEGORIA[categoria]
    
    tema = random.choice(temas_disponiveis)
    return categoria, tema


def gerar_artigo(categoria: str, tema: str) -> dict:
    client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])
    
    prompt = f"""Escreve um artigo editorial completo em português europeu (Portugal) sobre: "{tema}"
Categoria: {categoria}

OBJECTIVO: Artigo de referência para o Google — 1400 a 1800 palavras no corpo, estrutura clara, factual e útil.

REGRAS DE LINGUAGEM:
- Português europeu rigoroso: "utilizador" não "usuário", "telemóvel" não "celular", "autocarro" não "ônibus", etc.
- Tom: informativo, empático e autorizado — como um médico de família que explica com paciência
- Nunca alarmista, nunca vago

ESTRUTURA OBRIGATÓRIA DO CORPO (campo "corpo"):
1. Parágrafo de entrada forte (2-3 frases que prendem o leitor)
2. Secção 1 com <h3> — contexto e dados
3. Secção 2 com <h3> — causas ou mecanismos
4. Secção 3 com <h3> — sinais práticos ou impacto no quotidiano
5. Um <blockquote> com uma citação ou dado marcante
6. Secção 4 com <h3> — o que fazer / soluções
7. Secção 5 com <h3> — quando consultar / próximos passos
8. Parágrafo final que menciona a consulta auditiva gratuita e sem compromisso

TAGS HTML PERMITIDAS: <p>, <h3>, <blockquote>
SEM markdown, SEM asteriscos, SEM listas, SEM outras tags HTML

Responde APENAS em JSON válido com este formato exacto:
{{
  "titulo": "Título apelativo e específico (máx 72 chars, inclui o tema central)",
  "deck": "Subtítulo de 2 frases que resume o valor do artigo (máx 180 chars)",
  "corpo": "<p>Texto completo em HTML com 1400-1800 palavras...</p>"
}}"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=4096,
        messages=[{"role": "user", "content": prompt}],
    )
    
    raw = message.content[0].text.strip()
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
    raw = raw.strip()
    
    artigo_gerado = json.loads(raw)
    
    # Validate length
    corpo = artigo_gerado.get("corpo", "")
    word_count = len(corpo.replace('<', ' <').split())
    print(f"   Palavras no corpo: ~{word_count}")
    
    now = datetime.now(timezone.utc)
    foto_id = IMAGENS_UNSPLASH.get(categoria, "photo-1559757148-5c350d0d3c56")
    
    try:
        with open("artigos.json", "r", encoding="utf-8") as f:
            existentes = json.load(f)
        data_str = now.strftime("%Y-%m-%d")
        artigos_hoje = [a for a in existentes if a.get("data") == data_str]
        seq = len(artigos_hoje) + 1
    except Exception:
        existentes = []
        seq = 1
    
    artigo_id = f"{now.strftime('%Y-%m-%d')}-{seq:02d}"
    
    # Calculate read time (avg 200 words/min in Portuguese)
    read_minutes = max(6, round(word_count / 200))
    
    return {
        "id": artigo_id,
        "data": now.strftime("%Y-%m-%d"),
        "hora": now.strftime("%H:%M"),
        "cat": categoria,
        "titulo": artigo_gerado["titulo"],
        "deck": artigo_gerado["deck"],
        "readTime": f"{read_minutes} min",
        "img": f"https://images.unsplash.com/{foto_id}?w=800&q=80",
        "corpo": artigo_gerado["corpo"],
    }, existentes


def main():
    print("🎯 A escolher categoria e tema...")
    categoria, tema = escolher_categoria_e_tema()
    print(f"   Categoria: {categoria}")
    print(f"   Tema: {tema}")
    
    print("✍️  A gerar artigo longo via Claude API (1400-1800 palavras)...")
    novo_artigo, existentes = gerar_artigo(categoria, tema)
    print(f"   Título: {novo_artigo['titulo']}")
    print(f"   Tempo de leitura: {novo_artigo.get('readTime', 'N/A')}")
    
    artigos_actualizados = [novo_artigo] + existentes
    artigos_actualizados = artigos_actualizados[:50]
    
    with open("artigos.json", "w", encoding="utf-8") as f:
        json.dump(artigos_actualizados, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Artigo publicado: {novo_artigo['id']}")
    print(f"   Total de artigos: {len(artigos_actualizados)}")


if __name__ == "__main__":
    main()
