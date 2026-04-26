# core/escenario.py
import random
from models.enemigo import Enemigo
from models.objeto import Tesoro, Trampa, Consumible, Equipamiento 

class Zona:
    def __init__(self, nombre, enemigo=None, objetos=None, es_tienda=False):
        self.nombre = nombre
        self.enemigo = enemigo
        self.objetos = objetos if objetos is not None else []
        self.es_tienda = es_tienda
        # --- NUEVO: Catálogo de la tienda ---
        self.mercancia = []
        if self.es_tienda:
            self.mercancia = [
                Consumible("Poción de Vida", "HP", 50, 30),
                Consumible("Poción de Maná", "MP", 50, 30),
                Equipamiento("Hacha de Combate", "arma", 12, 0, 100, 50),
                Equipamiento("Cota de Malla", "armadura", 0, 10, 120, 60),
                Equipamiento("Espada Demoniaca", "arma", 25, -2, 300, 150)
            ]

class Escenario:
    def __init__(self):
        self.zonas = self._generar_mundo()

    def _generar_mundo(self):
        zonas = []
        for i in range(20):
            es_tienda = False
            enemigo_zona = None
            objetos_zona = [] 
            nombre = f"Área {i + 1}"

            if i in [4, 9, 14]:
                es_tienda = True
                nombre = "Refugio del Mercader"
            elif i == 19:
                enemigo_zona = Enemigo("Rey Demonio", puntos_vida=150, ataque=25, defensa=10, tipo="terrestre")
                nombre = "Guarida del Rey Demonio"
            else:
                if random.random() < 0.6:
                    enemigo_zona = Enemigo("Orco", puntos_vida=40 + i*2, ataque=10 + i, defensa=5, tipo="terrestre")
                
                if random.random() < 0.4:
                    rand_obj = random.random()
                    if rand_obj < 0.4:
                        obj = Tesoro("Girasol Dorado", valor_monetario=50 + i*10)
                    elif rand_obj < 0.6:
                        obj = Trampa("Espinas Ocultas", dano_explosion=15 + i*2, alcance_explosion=1)
                    elif rand_obj < 0.8:
                        obj = Consumible("Poción Menor de Vida", "HP", 30)
                    else:
                        obj = Equipamiento("Armadura Ligera", "armadura", 0, 5, 50, 25) # Drop de armadura
                    
                    obj.x = random.randint(100, 600)
                    obj.y = random.randint(100, 400)
                    objetos_zona.append(obj)

            zonas.append(Zona(nombre, enemigo_zona, objetos_zona, es_tienda))
        return zonas