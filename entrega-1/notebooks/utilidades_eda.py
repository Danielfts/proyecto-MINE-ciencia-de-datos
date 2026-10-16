"""Funciones reutilizables del notebook de entendimiento de los datos.

Parten de las del primer parcial del curso (análisis univariado, inspección de
atípicos, t-test de Welch con tamaño de efecto) y agregan lo que pidió la
retroalimentación de ese parcial: una bitácora de calidad que se llena desde el
código, pruebas que verifican sus supuestos y comparaciones dentro de grupos
comparables.

Las gráficas usan el estilo que el notebook carga con plt.style.use
(identidad/graficas.mplstyle): aquí solo se fijan los colores de cada elemento.
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import scipy.stats as stats
from IPython.display import display

# Colores de la identidad visual (ver identidad/README.md#gráficas)
AMARILLO = "#FFFF00"
NEGRO = "#000000"
GRIS = "#666666"
GRIS_CLARO = "#BDBDBD"


# --- Bitácora de calidad -------------------------------------------------------
class BitacoraCalidad:
    """Registra cada problema de calidad y la estrategia elegida, con conteos reales.

    Sus columnas son las de la tabla de resumen del tutorial 2 (problema, tabla y
    atributo, dimensión, nivel y estrategia), más las filas afectadas. La tabla se
    genera con `tabla()`, así que lo que dice coincide con lo que hizo el código.
    """

    def __init__(self):
        self.registros = []

    def registrar(self, problema, tabla_atributo, dimension, nivel, filas_afectadas, estrategia,
                  filas_antes=None, filas_despues=None):
        self.registros.append({
            "problema": problema,
            "tabla y atributo": tabla_atributo,
            "dimensión": dimension,
            "nivel": nivel,
            "filas afectadas": int(filas_afectadas),
            "estrategia": estrategia,
            "filas antes": filas_antes,
            "filas después": filas_despues,
        })

    def filtrar(self, df, mascara_excluir, problema, tabla_atributo, dimension, nivel, estrategia):
        """Excluye las filas marcadas por `mascara_excluir` y deja el registro."""
        antes = len(df)
        resultado = df.loc[~mascara_excluir].copy()
        self.registrar(problema, tabla_atributo, dimension, nivel, mascara_excluir.sum(), estrategia,
                       antes, len(resultado))
        return resultado

    def tabla(self):
        return pd.DataFrame(self.registros).rename_axis("#").rename(index=lambda i: i + 1)


# --- Resumen general -----------------------------------------------------------
def resumen_columnas(df):
    """Tipo, nulos y cardinalidad por columna (tolera columnas con listas)."""
    def n_unicos(s):
        try:
            return s.nunique()
        except TypeError:
            return s.astype(str).nunique()

    return pd.DataFrame({
        "tipo": df.dtypes.astype(str),
        "nulos": df.isna().sum(),
        "% nulos": (df.isna().mean() * 100).round(2),
        "únicos": [n_unicos(df[c]) for c in df.columns],
    }).sort_values("% nulos", ascending=False)


# --- Univariado no gráfico -----------------------------------------------------
def limites_outliers(s, k=1.5):
    """Cercos de Tukey (Q1-k*IQR, Q3+k*IQR) y de z-score (media +- 3*std)."""
    q1, q3 = s.quantile(0.25), s.quantile(0.75)
    iqr = q3 - q1
    media, std = s.mean(), s.std()
    return {
        "q1": q1, "q3": q3, "iqr": iqr,
        "iqr_low": q1 - k * iqr, "iqr_high": q3 + k * iqr,
        "z_low": media - 3 * std, "z_high": media + 3 * std,
    }


def interpretar_forma(asimetria, curtosis):
    """Texto corto para la asimetría y la curtosis (exceso)."""
    if abs(asimetria) < 0.5:
        a = "casi simétrica"
    elif abs(asimetria) < 1:
        a = "sesgo moderado " + ("a la derecha" if asimetria > 0 else "a la izquierda")
    else:
        a = "sesgo fuerte " + ("a la derecha" if asimetria > 0 else "a la izquierda")
    c = ("colas pesadas" if curtosis > 0.5 else "colas ligeras" if curtosis < -0.5 else "colas como la normal")
    return f"{a}; {c}"


def preparar_serie(df, col, log=False):
    """La serie sin nulos; con `log=True`, log10 de los valores positivos."""
    s = df[col].dropna()
    if log:
        return np.log10(s[s > 0]), f"log10({col})", int((s <= 0).sum())
    return s, col, 0


def resumen_numerico(df, columnas):
    """Medidas de tendencia central, dispersión, posición y forma, una fila por variable.

    `columnas` es una lista de (columna, log). Con log=True la variable se resume en
    escala log10 (excluyendo los valores <= 0, que se cuentan aparte). El coeficiente
    de variación solo se reporta en escala de razón y sin logaritmo.
    """
    filas = {}
    for col, log in columnas:
        s, etiqueta, excluidos = preparar_serie(df, col, log)
        lim = limites_outliers(s)
        atipicos = ((s < lim["iqr_low"]) | (s > lim["iqr_high"])).mean() * 100
        asim, curt = s.skew(), s.kurtosis()
        filas[etiqueta] = {
            "n": len(s), "excluidos <= 0": excluidos,
            "media": s.mean(), "mediana": s.median(), "moda": s.mode().iloc[0],
            "desv. est.": s.std(), "MAD": (s - s.median()).abs().median(),
            "CV %": s.std() / s.mean() * 100 if not log and s.mean() > 0 else np.nan,
            "mín": s.min(), "p1": s.quantile(0.01), "Q1": lim["q1"], "Q3": lim["q3"],
            "p99": s.quantile(0.99), "máx": s.max(), "IQR": lim["iqr"],
            "asimetría": asim, "curtosis": curt, "% atípicos Tukey": atipicos,
            "forma": interpretar_forma(asim, curt),
        }
    return pd.DataFrame(filas).T


def frecuencias(serie, top=None):
    """Frecuencia absoluta, relativa y acumulada; incluye los nulos."""
    conteo = serie.value_counts(dropna=False)
    tabla = pd.DataFrame({
        "frecuencia": conteo,
        "%": (conteo / conteo.sum() * 100).round(2),
        "% acumulado": (conteo.cumsum() / conteo.sum() * 100).round(2),
    })
    return tabla.head(top) if top else tabla


def inspeccionar_outliers(df, col, id_col, k=1.5, n=8, extra_cols=None):
    """Registros atípicos de `col` (cercos de Tukey), para juzgar si son errores o datos reales."""
    s = df[col].dropna()
    lim = limites_outliers(s, k)
    mask_low, mask_high = df[col] < lim["iqr_low"], df[col] > lim["iqr_high"]
    print(f"=== Atípicos de {col} (k={k}) ===")
    print(f"Rango observado: [{s.min():,.2f}, {s.max():,.2f}] | "
          f"cercos: [{lim['iqr_low']:,.2f}, {lim['iqr_high']:,.2f}]")
    print(f"Por debajo: {int(mask_low.sum())} | por encima: {int(mask_high.sum())}")
    cols = [c for c in [id_col, col, *(extra_cols or [])] if c in df.columns]
    out = df.loc[mask_low | mask_high, cols].sort_values(col)
    if mask_low.any():
        print(f"\n--- {min(n, int(mask_low.sum()))} valores más bajos"); display(out.head(n))
    if mask_high.any():
        print(f"\n--- {min(n, int(mask_high.sum()))} valores más altos"); display(out.tail(n))
    return out


# --- Univariado gráfico --------------------------------------------------------
def graficar_numerico(df, col, log=False, bins=40):
    """Histograma con media y mediana, y diagrama de caja."""
    s, etiqueta, _ = preparar_serie(df, col, log)
    media, mediana = s.mean(), s.median()
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 3.6))
    ax1.hist(s, bins=bins, color=AMARILLO, edgecolor=NEGRO, linewidth=0.5)
    ax1.axvline(media, color=NEGRO, linestyle="--", linewidth=1.5, label=f"media = {media:,.2f}")
    ax1.axvline(mediana, color=GRIS, linestyle=":", linewidth=2, label=f"mediana = {mediana:,.2f}")
    ax1.set_title(f"Histograma de {etiqueta}"); ax1.set_xlabel(etiqueta); ax1.set_ylabel("Frecuencia")
    ax1.legend()
    ax2.boxplot(s, vert=False, showmeans=True, patch_artist=True, widths=0.5,
                boxprops={"facecolor": AMARILLO, "edgecolor": NEGRO},
                medianprops={"color": NEGRO}, whiskerprops={"color": NEGRO}, capprops={"color": NEGRO},
                meanprops={"marker": "D", "markerfacecolor": NEGRO, "markeredgecolor": NEGRO, "markersize": 4},
                flierprops={"marker": "o", "markersize": 2, "markerfacecolor": GRIS, "markeredgecolor": GRIS})
    ax2.set_title(f"Diagrama de caja de {etiqueta}"); ax2.set_xlabel(etiqueta); ax2.set_yticks([])
    plt.tight_layout(); plt.show()


def graficar_categorico(df, col, top=None):
    """Barras de frecuencia con la curva de Pareto (porcentaje acumulado)."""
    conteo = df[col].value_counts(dropna=False)
    total = conteo.sum()
    if top:
        conteo = conteo.head(top)
    acum = conteo.cumsum() / total * 100
    etiquetas = conteo.index.astype(str)
    fig, ax1 = plt.subplots(figsize=(11, 3.8))
    ax1.bar(etiquetas, conteo.values, color=AMARILLO, edgecolor=NEGRO, linewidth=0.6)
    ax1.set_ylabel("Frecuencia"); ax1.set_title(f"Distribución de {col}" + (f" (los {top} más frecuentes)" if top else ""))
    ax1.tick_params(axis="x", rotation=45)
    for e in ax1.get_xticklabels():
        e.set_ha("right")
    ax2 = ax1.twinx()
    ax2.plot(etiquetas, acum.values, color=NEGRO, marker="o", markersize=4, linewidth=1.5)
    ax2.axhline(80, color=GRIS, linestyle="--", linewidth=1)
    ax2.set_ylabel("% acumulado"); ax2.set_ylim(0, 105); ax2.grid(False)
    ax2.spines["right"].set_visible(True)
    plt.tight_layout(); plt.show()


# --- Pruebas de hipótesis ------------------------------------------------------
def cohen_d(x, y):
    """d de Cohen con la desviación agrupada (con varianzas distintas, solo orientativa)."""
    n1, n2 = len(x), len(y)
    s1, s2 = np.std(x, ddof=1), np.std(y, ddof=1)
    sp = np.sqrt(((n1 - 1) * s1 ** 2 + (n2 - 1) * s2 ** 2) / (n1 + n2 - 2))
    return (np.mean(x) - np.mean(y)) / sp


def revisar_supuestos(grupos, nombres, titulo=""):
    """QQ-plot por grupo y prueba de Levene de igualdad de varianzas.

    Con muestras grandes las pruebas formales de normalidad rechazan casi siempre,
    así que la normalidad se juzga con el QQ-plot.
    """
    fig, axes = plt.subplots(1, len(grupos), figsize=(4.5 * len(grupos), 3.6))
    for ax, g, nombre in zip(np.atleast_1d(axes), grupos, nombres):
        stats.probplot(g, dist="norm", plot=ax)
        ax.get_lines()[0].set(color=NEGRO, markersize=2, alpha=0.4)
        ax.get_lines()[1].set(color=GRIS)
        ax.set_title(f"QQ-plot: {nombre} (n={len(g)})")
        ax.set_xlabel("Cuantiles teóricos (normal)"); ax.set_ylabel("Cuantiles observados")
    if titulo:
        fig.suptitle(titulo)
    plt.tight_layout(); plt.show()
    lev = stats.levene(*grupos, center="median")
    print(f"Levene (centrado en la mediana): W={lev.statistic:.3f}, p={lev.pvalue:.4g} -> "
          + ("varianzas distintas" if lev.pvalue <= 0.05 else "no se rechaza igualdad de varianzas"))
    return lev


def comparar_dos_grupos(data, grupo_col, g1, g2, valor, alpha=0.05):
    """Welch (sobre `valor`) y Mann-Whitney como alternativa no paramétrica, con sus supuestos."""
    a = data.loc[data[grupo_col] == g1, valor].dropna()
    b = data.loc[data[grupo_col] == g2, valor].dropna()
    revisar_supuestos([a, b], [str(g1), str(g2)], titulo=f"{valor} por {grupo_col}")

    welch = stats.ttest_ind(a, b, equal_var=False)
    ci = welch.confidence_interval(1 - alpha)
    mw = stats.mannwhitneyu(a, b, alternative="two-sided")
    # Probabilidad de superioridad: P(valor de g1 > valor de g2), tamaño de efecto de Mann-Whitney
    prob_sup = mw.statistic / (len(a) * len(b))

    print(f"\n=== {valor}: {g1} vs {g2} ===")
    print(f"{g1}: n={len(a)}, media={a.mean():.3f}, mediana={a.median():.3f}")
    print(f"{g2}: n={len(b)}, media={b.mean():.3f}, mediana={b.median():.3f}")
    print(f"Welch: t={welch.statistic:.3f}, p={welch.pvalue:.4g}, "
          f"IC{int((1 - alpha) * 100)}% de la diferencia=[{ci.low:.3f}, {ci.high:.3f}], "
          f"d de Cohen={cohen_d(a.values, b.values):.3f}")
    print(f"Mann-Whitney: U={mw.statistic:.0f}, p={mw.pvalue:.4g}, P({g1} > {g2})={prob_sup:.3f}")
    return {"welch": welch, "ic": ci, "mann_whitney": mw, "prob_superioridad": prob_sup,
            "d": cohen_d(a.values, b.values), "n": (len(a), len(b))}


def cramers_v(tabla):
    """V de Cramér a partir de una tabla de contingencia (tamaño de efecto del chi-cuadrado)."""
    chi2 = stats.chi2_contingency(tabla)[0]
    n = tabla.to_numpy().sum()
    r, k = tabla.shape
    return np.sqrt(chi2 / (n * (min(r, k) - 1)))
