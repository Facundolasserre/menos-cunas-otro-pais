# Revisión del prototipo v0.6

Fecha: 2026-09-25.

## Resultado

La flecha que conecta 777.012 con 413.135 ya no roza los números. Sus extremos
se calculan a partir de las cajas tipográficas renderizadas y reservan 12 puntos
de aire visual a cada lado, incluida la cabeza de flecha.

## Prevención de regresiones

El constructor detiene la exportación si la distancia efectiva entre la flecha
y cualquiera de los dos números cae por debajo de ocho puntos. La solución se
adapta a cambios futuros de cifra o tipografía sin recurrir a coordenadas
ajustadas manualmente.

## Estado

La v0.6 queda aprobada para inspección digital y conserva la marca “NO
PRESENTAR”. Continúan pendientes la impresión A3 al 100% y la lectura con tres
personas según `docs/reader-test-protocol.md`.
