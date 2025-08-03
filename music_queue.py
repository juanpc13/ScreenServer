
class MusicQueue:
    import datetime

    def __init__(self, log_file='music_queue.log'):
        self.queue = []
        self.log_file = log_file

    def _log(self, accion, cancion):
        fecha = self.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{fecha}] {accion}: {cancion}\n")

    def agregar(self, cancion):
        """Agrega una canción al final de la cola."""
        self.queue.append(cancion)
        self._log('Agregada', cancion)

    def eliminar(self, cancion):
        """Elimina la primera aparición de una canción de la cola."""
        if cancion in self.queue:
            self.queue.remove(cancion)
            self._log('Eliminada', cancion)

    def mostrar_cola(self):
        """Devuelve la lista completa de canciones en la cola."""
        return list(self.queue)

    def mostrar_ultimas_5(self):
        """Devuelve las últimas 5 canciones de la cola (o menos si hay menos de 5)."""
        return self.queue[-5:]

    def reproducida(self):
        """Saca y devuelve la canción actual (la primera de la cola)."""
        if self.queue:
            cancion = self.queue.pop(0)
            self._log('Reproducida', cancion)
            return cancion
        return None
