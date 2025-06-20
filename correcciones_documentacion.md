# CORRECCIONES NECESARIAS PARA LA DOCUMENTACIÓN

## 1. CORRECCIÓN EN PARÁMETROS (ELIMINAR)

**ELIMINAR** de la sección de parámetros:
```latex
\item $\zeta_{zt}$: Variable continua que representa el déficit diario acumulado de la zona $z$ el día $t$ (suma de peligrosidad de los 3 turnos).
```

**RAZÓN:** ζ_{zt} es una VARIABLE, no un parámetro.

## 2. CORRECCIÓN EN NATURALEZA DE VARIABLES

**CAMBIAR:**
```latex
u_{zmt}\in \mathbb{Z}_{\geq 0}, \quad \forall z \in Z,\ m \in M,\ t \in T
```

**POR:**
```latex
u_{zmt} \in \mathbb{R}_{\geq 0}, \quad \forall z \in Z,\ m \in M,\ t \in T
```

**RAZÓN:** u_{zmt} debe ser continua (no entera) para representar niveles de peligrosidad.

## 3. AGREGAR RESTRICCIÓN R14

**AGREGAR** después de R13:

```latex
\item \textbf{Definición de peligrosidad por turno}:  
La peligrosidad por turno $u_{zmt}$ se define como la fracción de la peligrosidad diaria de la zona que no es cubierta por las patrullas asignadas a ese turno específico.

\begin{align*}
u_{zmt} \geq \frac{\zeta_{zt}}{3} - \sum_{p \in P} x_{pzmt} \quad \forall z \in Z,\ m \in M,\ t \in T
\end{align*}

\begin{align*}
u_{zmt} \geq 0 \quad \forall z \in Z,\ m \in M,\ t \in T
\end{align*}

Esta restricción distribuye la peligrosidad diaria entre los tres turnos y calcula el déficit remanente después de considerar la cobertura de patrullas en cada turno.
```

## 4. MEJORAR DEFINICIÓN DE VARIABLE u_{zmt}

**CAMBIAR:**
```latex
\item $u_{zmt}$: Variable continua no negativa que representa el nivel de peligrosidad de la zona $z$ durante el turno $m$ del día $t$.
```

**POR:**
```latex
\item $u_{zmt}$: Variable continua no negativa que representa el déficit de cobertura (peligrosidad remanente) de la zona $z$ durante el turno $m$ del día $t$, después de considerar las patrullas asignadas a ese turno.
```

## 5. ACLARAR DEFINICIÓN DE ζ_{zt}

**CAMBIAR:**
```latex
\item $\zeta_{zt}$: Variable continua entre 0 y 1 que representa el nivel de peligrosidad de la zona $z$ el día $t$.
```

**POR:**
```latex
\item $\zeta_{zt}$: Variable continua entre 0 y 1 que representa el nivel de peligrosidad agregado de la zona $z$ el día $t$, resultado de la evolución dinámica que considera la criminalidad base, los déficits de turnos anteriores, y el efecto de la cobertura de patrullas.
```

## RESUMEN DE CAMBIOS:

1. ✅ Eliminar ζ_{zt} de parámetros
2. ✅ Cambiar u_{zmt} de entero a continuo  
3. ✅ Agregar restricción R14 para definir u_{zmt}
4. ✅ Mejorar definiciones de variables u_{zmt} y ζ_{zt}

Con estos cambios, la documentación estará 100% alineada con el código Python y será matemáticamente consistente. 