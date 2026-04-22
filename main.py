# main.py
from models.personaje import Personaje
from core.escenario import Escenario
from ui.pantalla import MotorGrafico

def main():
    print("Iniciando 'La Leyenda de los 17 Girasoles'...")
    
    # 1. Creamos al héroe
    heroe_principal = Personaje(nombre="Santi", puntos_vida=100, ataque=20, defensa=15)
    
    # 2. Generamos el mundo de 20 zonas
    mundo_procedural = Escenario()
    
    # 3. Lanzamos el Motor Gráfico
    juego = MotorGrafico(heroe=heroe_principal, mundo=mundo_procedural)

    # Ciclo de Vida del Juego
    while juego.corriendo:
        juego.manejar_eventos() 
        juego.actualizar()      
        juego.dibujar()         
        
    juego.salir()
    print("Gracias por jugar. ¡Hasta la próxima!")

if __name__ == "__main__":
    main()