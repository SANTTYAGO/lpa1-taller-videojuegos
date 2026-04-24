# core/escenario.py
import random
from models.enemigo import Enemigo
from models.objeto import Tesoro, Trampa, Consumible # <-- Importamos Consumible

class Zona:
    def __init__(self, nombre, enemigo=None, objeto=None, es_tienda=False):
        self.nombre = nombre
        self.enemigo = enemigo
        self.objeto = objeto
        self.es_tienda = es_tienda

class Escenario:
    def __init__(self):
        self.zonas = self._generar_mundo()

    def _generar_mundo(self):
        zonas = []
        for i in range(20):
            es_tienda = False
            enemigo_zona = None
            objeto_zona = None
            nombre = f"Área {i + 1}"

            # Zonas de descanso/tienda
            if i in [4, 9, 14]:
                es_tienda = True
                nombre = "Refugio del Mercader"
            # Zona final
            elif i == 19:
                enemigo_zona = Enemigo("Rey Demonio", puntos_vida=150, ataque=25, defensa=10, tipo="terrestre")
                nombre = "Guarida del Rey Demonio"
            # Zonas normales de exploración
            else:
                if random.random() < 0.6:
                    enemigo_zona = Enemigo("Orco", puntos_vida=40 + i*2, ataque=10 + i, defensa=5, tipo="terrestre")
                
                if random.random() < 0.4:
                    rand_obj = random.random()
                    # --- NUEVO: Distribución probabilística de loot ---
                    if rand_obj < 0.4:
                        objeto_zona = Tesoro("Girasol Dorado", valor_monetario=50 + i*10)
                    elif rand_obj < 0.6:
                        objeto_zona = Trampa("Espinas Ocultas", dano_explosion=15 + i*2, alcance_explosion=1)
                    elif rand_obj < 0.8:
                        objeto_zona = Consumible("Poción Menor de Vida", "HP", 30)
                    else:
                        objeto_zona = Consumible("Poción Menor de Maná", "MP", 30)

            zonas.append(Zona(nombre, enemigo_zona, objeto_zona, es_tienda))
        return zonas