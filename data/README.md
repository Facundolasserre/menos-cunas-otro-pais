# Datos

## Política

`raw/` contiene descargas originales e inmutables y está ignorado por Git.
`interim/` contiene resultados temporales regenerables y está ignorado por Git.
`processed/` contendrá únicamente tablas derivadas pequeñas, documentadas y
necesarias para reproducir la obra.

Cada script de descarga deberá registrar origen, fecha, tamaño y checksum. Cada
tabla procesada deberá poder regenerarse desde las fuentes crudas.

