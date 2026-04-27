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
        
        self.mercancia = []
        self.armas_por_clase = {}
        
        if self.es_tienda:
            self.mercancia = [
                Consumible("Pocion de Vida", "HP", 50, 30),
                Consumible("Pocion de Mana", "MP", 50, 30)
            ]
            # La tienda se adaptara inteligentemente segun la clase del heroe en el EstadoTienda
            self.armas_por_clase = {
                "Knight": [Equipamiento("Espada Larga", "arma", 15, 0, 100, 50)],
                "Wizard": [Equipamiento("Baston Arcano", "arma", 18, 0, 110, 55)],
                "Archer": [Equipamiento("Arco Elfico", "arma", 16, 0, 105, 52)],
                "Soldier": [Equipamiento("Espada Oxidada", "arma", 5, 0, 50, 25)]
                # (Puedes agregar mercancia para el resto de clases aqui)
            }

class Escenario:
    def __init__(self):
        self.zonas = self._generar_mundo()

    def _generar_mundo(self):
        zonas = []
        
        # LISTA DE TUS NUEVOS ENEMIGOS
        lista_enemigos = [
            "Armored Orc", "Armored Skeleton", "Elite Orc", 
            "Greatsword Skeleton", "Orc", "Orc rider", 
            "Skeleton", "Skeleton Archer", "Slime", "Werebear", "Werewolf"
        ]

        for i in range(20):
            es_tienda = False
            enemigo_zona = None
            objetos_zona = [] 
            nombre = f"Area {i + 1}"

            if i in [4, 9, 14]:
                es_tienda = True
                nombre = "Refugio del Mercader"

            elif i == 19:
                enemigo_zona = Enemigo("Rey Demonio", puntos_vida=300, ataque=35, defensa=15, tipo="terrestre")
                nombre = "Guarida del Rey Demonio"
            else:
                if random.random() < 0.6:
                    enemigo_aleatorio = random.choice(lista_enemigos)
                    # Stats escalan un poco con el avance de nivel (i)
                    enemigo_zona = Enemigo(enemigo_aleatorio, puntos_vida=40 + i*5, ataque=10 + i*2, defensa=5 + i, tipo="terrestre")
                
                if random.random() < 0.4:
                    rand_obj = random.random()
                    if rand_obj < 0.4: obj = Tesoro("Girasol Dorado", valor_monetario=50 + i*10)
                    elif rand_obj < 0.6: obj = Trampa("Espinas Ocultas", dano_explosion=15 + i*2, alcance_explosion=1)
                    elif rand_obj < 0.8: obj = Consumible("Pocion Menor de Vida", "HP", 30)
                    else: obj = Equipamiento("Armadura Ligera", "armadura", 0, 5, 50, 25)
                    
                    obj.x = random.randint(100, 600)
                    obj.y = random.randint(100, 400)
                    objetos_zona.append(obj)

            zonas.append(Zona(nombre, enemigo_zona, objetos_zona, es_tienda))
        return zonas