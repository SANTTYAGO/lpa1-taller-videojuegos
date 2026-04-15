# main.py
from models.personaje import Personaje

def main():
    print("--- Iniciando prueba del motor del juego ---")
    
    # Instanciamos nuestro primer personaje (R1.1)
    heroe = Personaje(nombre="Jugador 1", puntos_vida=100, ataque=15, defensa=10)
    
    # Verificamos que los atributos y métodos funcionan
    heroe.mostrar_estadisticas()
    
    print("\n¿El personaje está vivo?", heroe.esta_vivo())

if __name__ == "__main__":
    main()