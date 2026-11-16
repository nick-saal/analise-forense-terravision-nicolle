"""
Análise Forense TerraVision x Google Earth
Tema: Formações Insulares e Ilhas Isoladas no Oceano — Arquipélago de Fernando de Noronha

Instituição: Colégio Estadual Rodolpho Zaninelli
Curso: Técnico em Desenvolvimento de Sistemas | Turma: 3ºD
Disciplina: Computação Gráfica e Ciência de Dados
Professora: Angélica Neckel
Estudante: Nicolle Alves dos Santos
"""

import os
import math
import random
import tkinter as tk
from tkinter import ttk

try:
    from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageDraw
    PIL_DISPONIVEL = True
except ImportError:
    PIL_DISPONIVEL = False

# Limites de altitude (em metros) exigidos pelo trabalho
LIMITE_BAIXA = 10000
LIMITE_ALTA = 1000
LIMITE_PROCEDURAL = 200  # Abaixo de 200m ativa a síntese procedural de micro-relevo costeiro
MINIMO_ALTITUDES = 5


def carregar_camada_satelite(lista_altitudes):
    """
    Função obrigatória do trabalho: recebe no mínimo 5 altitudes (metros)
    e classifica cada uma usando Level of Detail (LoD).
    """
    if not isinstance(lista_altitudes, (list, tuple)):
        raise TypeError("A entrada deve ser uma lista de altitudes.")
    if len(lista_altitudes) < MINIMO_ALTITUDES:
        raise ValueError(f"Informe no mínimo {MINIMO_ALTITUDES} altitudes.")

    camadas = []
    for altitude in lista_altitudes:
        if altitude < 0:
            raise ValueError(f"Altitude inválida: {altitude} m.")

        if altitude > LIMITE_BAIXA:
            nivel = "Baixa Resolução"
            descricao = "Mosaico oceânico global (Fernando de Noronha e Ilha Rata isolados no Atlântico)"
            ajuste_espectro = False
        elif altitude >= LIMITE_ALTA:
            nivel = "Média Resolução"
            descricao = "Contorno insular, pista do aeroporto, Trilha do Piquinho e artefatos de costura (stitching)"
            ajuste_espectro = False
        else:
            nivel = "Alta Resolução"
            descricao = "Detalhes urbanos e costeiros (Vila dos Remédios, Igreja N. Sra. dos Remédios e enseada)"
            ajuste_espectro = True

        camadas.append({
            "altitude_m": altitude,
            "nivel": nivel,
            "descricao": descricao,
            "ajuste_espectro": ajuste_espectro,
        })
        print(f"Altitude: {altitude:>7} m | {nivel} -> {descricao}")

    return camadas


def gerar_textura_procedural_costeira(largura, altura, semente=42):
    """
    Gera um mapa procedural de granulometria de areia, copas de árvores e espuma
    de arrebentação para simular detalhes em altitudes ultra-baixas (< 200 m).
    """
    rng = random.Random(semente)
    ruido_fino = Image.effect_noise((largura, altura), 34).convert("L")
    ruido_macro = Image.effect_noise((largura // 5, altura // 5), 50).convert("L")
    ruido_macro = ruido_macro.resize((largura, altura), Image.Resampling.BICUBIC)

    mapa_altura = Image.blend(ruido_macro, ruido_fino, 0.48)

    # Simula linhas de arrebentação na enseada e rugosidade do solo/vegetação
    draw = ImageDraw.Draw(mapa_altura)
    for _ in range(40):
        x = rng.randint(0, largura)
        y = rng.randint(0, altura)
        angulo = rng.uniform(-0.4, 0.4)
        pontos = [(x, y)]
        for _ in range(rng.randint(6, 14)):
            passo = rng.randint(18, 48)
            angulo += rng.uniform(-0.28, 0.28)
            x += int(math.cos(angulo) * passo)
            y += int(math.sin(angulo) * passo)
            pontos.append((x, y))
        draw.line(pontos, fill=rng.randint(175, 235), width=rng.randint(1, 2))

    mapa_altura = mapa_altura.filter(ImageFilter.GaussianBlur(0.85))
    return mapa_altura.convert("RGB")


class AbaFernandoDeNoronha(tk.Frame):
    """Aba principal de Fernando de Noronha com 5 camadas reais + síntese procedural."""

    def __init__(self, parent):
        super().__init__(parent, bg="#0d1b2a")
        self.pasta_base = os.path.dirname(os.path.abspath(__file__))
        self.imagens_carregadas = []
        self.largura_tela = 840
        self.altura_tela = 460

        self.descricoes_camadas = [
            "Camada 1 — Visão Orbital do Arquipélago (Ilha Principal e Ilha Rata): halo de costura sobre o oceano",
            "Camada 2 — Aproximação Regional (Mirante dos Golfinhos e Pista): contraste batimétrico costeiro",
            "Camada 3 — Setor Leste (Trilha do Piquinho e Ponta da Atalaia): falha radiométrica (faixa cinza) entre tiles",
            "Camada 4 — Vila dos Remédios e Dipta Point (BR-363): transição entre área urbana, mata e mar turquesa",
            "Camada 5 — Zoom Máximo Satélite (Igreja N. Sra. dos Remédios): telhados, trilhas e linha de arrebentação",
            "SÍNTESE PROCEDURAL (< 200 m) — Micro-relevo de areia, copas de vegetação e espuma gerados matematicamente",
        ]

        if not PIL_DISPONIVEL:
            tk.Label(
                self,
                text="Biblioteca 'pillow' não instalada.\nRode 'pip install pillow' no terminal.",
                fg="#ffcc00", bg="#0d1b2a", font=("Arial", 12), pady=80
            ).pack()
            return

        # Mapeia os 5 ficheiros fornecidos (aceita .jpg, .jpg.jpg, .png e variações de grafia)
        candidatos_por_camada = [
            ["fernando_noronha", "fernando_noronha1", "673329776-34a71aed-a8de-4b45-819e-36988a750918"],
            ["fernando_noronha2"],
            ["fernado_noronha3", "fernando_noronha3"],
            ["fernado_noronha4", "fernando_noronha4"],
            ["fernando_noronha5", "fernado_noronha5"],
        ]
        extensoes = (".jpg.jpg", ".jpg", ".png", ".jpeg", ".webp")

        for lista_nomes in candidatos_por_camada:
            img_encontrada = None
            for nome in lista_nomes:
                for ext in extensoes:
                    caminho = os.path.join(self.pasta_base, f"{nome}{ext}")
                    if os.path.exists(caminho):
                        img_encontrada = Image.open(caminho).convert("RGB").resize(
                            (self.largura_tela, self.altura_tela), Image.Resampling.LANCZOS
                        )
                        break
                if img_encontrada is not None:
                    break
            self.imagens_carregadas.append(img_encontrada)

        self.mapa_procedural = gerar_textura_procedural_costeira(self.largura_tela, self.altura_tela)

        self.lbl_mapa = tk.Label(self, bg="#061019", bd=2, relief="sunken", width=self.largura_tela, height=self.altura_tela)
        self.lbl_mapa.pack(padx=15, pady=(12, 6))

        self.lbl_status = tk.Label(
            self, text="", fg="white", bg="#1b263b",
            font=("Consolas", 10), justify="left", padx=15, pady=10, width=98
        )
        self.lbl_status.pack(pady=6)

        frame_ctrl = tk.Frame(self, bg="#0d1b2a")
        frame_ctrl.pack(pady=8, fill="x", padx=30)

        tk.Label(
            frame_ctrl, text="Altitude da Câmera (Zoom):",
            fg="#38bdf8", bg="#0d1b2a", font=("Arial", 10, "bold")
        ).pack(side="left")

        self.slider = tk.Scale(
            frame_ctrl, from_=10, to=35000, orient="horizontal",
            length=540, bg="#0d1b2a", fg="white", troughcolor="#1b263b",
            highlightthickness=0, command=self.atualizar_camada
        )
        self.slider.set(35000)
        self.slider.pack(side="right")

        self.atualizar_camada(35000)

    def processar_imagem(self, img_base, altitude):
        img_proc = img_base.copy()

        # Síntese procedural em altitudes ultra-baixas (< 200 m) sobre a Camada 5
        if altitude < LIMITE_PROCEDURAL:
            progresso = (LIMITE_PROCEDURAL - altitude) / (LIMITE_PROCEDURAL - 10)
            escala = 1.0 + (progresso * 1.8)

            nw = int(self.largura_tela / escala)
            nh = int(self.altura_tela / escala)
            left = (self.largura_tela - nw) // 2
            top = (self.altura_tela - nh) // 2

            img_zoom = img_proc.crop((left, top, left + nw, top + nh)).resize(
                (self.largura_tela, self.altura_tela), Image.Resampling.BILINEAR
            )

            intensidade_procedural = min(0.38, 0.10 + progresso * 0.28)
            img_proc = Image.blend(img_zoom, self.mapa_procedural, intensidade_procedural)

            img_proc = img_proc.filter(ImageFilter.UnsharpMask(radius=2.0, percent=155, threshold=2))
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.30)
            img_proc = ImageEnhance.Color(img_proc).enhance(1.20)
            return img_proc

        # Realce de nitidez para bordas costeiras, falésias e edificações
        img_proc = img_proc.filter(ImageFilter.UnsharpMask(radius=1.8, percent=135, threshold=3))

        if altitude > LIMITE_BAIXA:
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.08)
        elif altitude >= LIMITE_ALTA:
            # Destaca artefatos de costura (stitching) e diferenças batimétricas
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.18)
            img_proc = ImageEnhance.Color(img_proc).enhance(1.16)
        else:
            # Realça vegetação da APA/Parque Marinho, faixa de areia e Vila dos Remédios
            img_proc = ImageEnhance.Contrast(img_proc).enhance(1.26)
            img_proc = ImageEnhance.Brightness(img_proc).enhance(0.95)
            img_proc = ImageEnhance.Color(img_proc).enhance(1.24)

        return img_proc

    def atualizar_camada(self, valor):
        altitude = int(valor)

        if altitude > 14000:
            idx_img, idx_desc = 0, 0
        elif altitude > 6000:
            idx_img, idx_desc = 1, 1
        elif altitude >= 1000:
            idx_img, idx_desc = 2, 2
        elif altitude > 500:
            idx_img, idx_desc = 3, 3
        elif altitude >= LIMITE_PROCEDURAL:
            idx_img, idx_desc = 4, 4
        else:
            idx_img, idx_desc = 4, 5

        if altitude > LIMITE_BAIXA:
            nivel = "BAIXA RESOLUÇÃO (> 10.000 m)"
            render_txt = "Desativado (visão orbital — contraste entre oceano profundo e halo insular)"
        elif altitude >= LIMITE_ALTA:
            nivel = "MÉDIA RESOLUÇÃO (1.000 m a 10.000 m)"
            render_txt = "Moderado (evidencia costura/stitching e diferença radiométrica entre faixas)"
        elif altitude >= LIMITE_PROCEDURAL:
            nivel = "ALTA RESOLUÇÃO SATÉLITE (200 m a 1.000 m)"
            render_txt = "ATIVADO (Realce de linha costeira, Vila dos Remédios e vegetação nativa)"
        else:
            nivel = "MICRO-ESCALA PROCEDURAL (< 200 m)"
            render_txt = "SÍNTESE PROCEDURAL ATIVA (Detail Texturing de areia, copas e arrebentação)"

        img_base = self.imagens_carregadas[idx_img]

        if img_base is None:
            nomes_esperados = [
                "fernando_noronha.jpg",
                "fernando_noronha2.jpg.jpg",
                "fernado_noronha3.jpg.jpg",
                "fernado_noronha4.jpg.jpg",
                "fernando_noronha5.jpg.jpg",
            ]
            self.lbl_mapa.config(
                image="",
                text=f"[Fernando de Noronha — Camada {idx_img + 1}/5 aguardando '{nomes_esperados[idx_img]}']\n"
                     f"Salve as 5 imagens na mesma pasta do script.py",
                fg="#94a3b8", font=("Arial", 12)
            )
        else:
            img_final = self.processar_imagem(img_base, altitude)
            self.foto_tk = ImageTk.PhotoImage(img_final)
            self.lbl_mapa.config(image=self.foto_tk, text="")

        camada_label = "PROCEDURAL" if altitude < LIMITE_PROCEDURAL else f"{idx_img + 1}/5"
        self.lbl_status.config(
            text=f"REGIÃO: FERNANDO DE NORONHA (PE)  |  ALTITUDE: {altitude} m  |  CAMADA {camada_label}: {nivel}\n"
                 f"CENA: {self.descricoes_camadas[idx_desc]}\n"
                 f"MODO DE RENDERIZAÇÃO: {render_txt}"
        )


class MiniGoogleEarthApp:
    """Janela principal do simulador."""

    def __init__(self, root):
        self.root = root
        self.root.title("TerraVision vs. Google Earth — Análise Forense LoD (Fernando de Noronha)")
        self.root.configure(bg="#0d1b2a")

        tk.Label(
            root,
            text="SIMULADOR DE RENDERIZAÇÃO GEOESPACIAL (LoD) — FORMAÇÕES INSULARES",
            fg="#38bdf8", bg="#0d1b2a", font=("Arial", 13, "bold"), pady=8
        ).pack()

        style = ttk.Style()
        style.theme_use("default")
        style.configure("TNotebook", background="#0d1b2a", borderwidth=0)
        style.configure("TNotebook.Tab", background="#1b263b", foreground="white", padding=[18, 6], font=("Arial", 10, "bold"))
        style.map("TNotebook.Tab", background=[("selected", "#0284c7")], foreground=[("selected", "white")])

        self.notebook = ttk.Notebook(root)
        self.notebook.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        aba_ilha = AbaFernandoDeNoronha(self.notebook)
        self.notebook.add(aba_ilha, text="  🏝️ Fernando de Noronha (5 Camadas + Procedural)  ")


if __name__ == "__main__":
    print("=== EXECUÇÃO DA FUNÇÃO OBRIGATÓRIA (LoD) ===")
    carregar_camada_satelite([35000, 12000, 5000, 800, 350])

    janela = tk.Tk()
    app = MiniGoogleEarthApp(janela)
    janela.mainloop()
