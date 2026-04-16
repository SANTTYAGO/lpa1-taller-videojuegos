# main.py
from models.personaje import Personaje
from models.enemigo import Enemigo
from models.objeto import Tesoro
from core.combate import SistemaCombate

def main():
    # Instanciamos entidades
    heroe = Personaje(nombre="Caballero", puntos_vida=50, ataque=18, defensa=10)
    gargola = Enemigo(nombre="Gárgola Oscura", puntos_vida=30, ataque=12, defensa=8, tipo="volador")
    moneda_oro = Tesoro(nombre="Cáliz Antiguo", valor_monetario=250)

    print("--- FASE DE EXPLORACIÓN ---")
    heroe.mostrar_estadisticas()
    
    # Probamos la recolección (R3.2)
    print("\nEl héroe encuentra algo brillante en el suelo...")
    heroe.recolectar_objeto(moneda_oro)
    
    # Probamos el combate (R5.1 y R5.2)
    print("\n¡Una sombra desciende del cielo!")
    SistemaCombate.iniciar_combate(heroe, gargola)
    
    print("\n--- ESTADO FINAL ---")
    heroe.mostrar_estadisticas()

if __name__ == "__main__":
    main()