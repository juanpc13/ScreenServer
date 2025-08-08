import uuid

class MusicQueue:
    import datetime

    def __init__(self, log_file='music_queue.log'):
        self.items = {}  # id -> item
        self.order = []  # lista de ids en orden de la cola
        self.log_file = log_file

    def _log(self, accion, cancion):
        fecha = self.datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(f"[{fecha}] {accion}: {cancion}\n")

    def agregar(self, cancion, metadata=""):
        """Agrega una canción y su metadata al final de la cola, asignando un id único."""
        item_id = str(uuid.uuid4())
        item = {'id': item_id, 'cancion': cancion, 'metadata': metadata}
        self.items[item_id] = item
        self.order.append(item_id)
        self._log('Agregada', f"{cancion} | {metadata} | {item_id}")
        return item_id

    def eliminar(self, id):
        """Elimina la canción de la cola por id."""
        if id in self.items:
            item = self.items.pop(id)
            self.order.remove(id)
            self._log('Eliminada', f"{item['cancion']} | {item['metadata']} | {id}")

    def mover_arriba(self, id):
        """Mueve la canción una posición arriba en la cola usando su id (si es posible)."""
        idx = self.order.index(id) if id in self.order else -1
        if idx > 0:
            self.order[idx], self.order[idx-1] = self.order[idx-1], self.order[idx]
            item = self.items[id]
            self._log('Movida arriba', f"{item['cancion']} | {item['metadata']} | {id}")
            return True
        return False

    def mover_abajo(self, id):
        """Mueve la canción una posición abajo en la cola usando su id (si es posible)."""
        idx = self.order.index(id) if id in self.order else -1
        if 0 <= idx < len(self.order)-1:
            self.order[idx], self.order[idx+1] = self.order[idx+1], self.order[idx]
            item = self.items[id]
            self._log('Movida abajo', f"{item['cancion']} | {item['metadata']} | {id}")
            return True
        return False

    def mostrar_cola(self):
        """Devuelve la lista completa de canciones y metadata en la cola."""
        return [self.items[id] for id in self.order]

    def mostrar_ultimas_5(self):
        """Devuelve las últimas 5 canciones (y metadata) de la cola (o menos si hay menos de 5)."""
        return [self.items[id] for id in self.order[-5:]]

    def reproducida(self):
        """Saca y devuelve la canción actual (la primera de la cola)."""
        if self.order:
            id = self.order.pop(0)
            item = self.items.pop(id)
            self._log('Reproducida', f"{item['cancion']} | {item['metadata']} | {id}")
            return item
        return None
