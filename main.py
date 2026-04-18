# main.py
from models.personaje import Personaje
from core.escenario import Escenario
from ui.pantalla import MotorGrafico

def main():
    print("Iniciando Aventura 16-Bits...")
    
    # 1. Instanciamos a nuestro héroe
    heroe_principal = Personaje(nombre="Santi", puntos_vida=100, ataque=20, defensa=15)
    
    # 2. Generamos el mundo completo (20 cuartos con enemigos y objetos aleatorios)
    mundo_generado = Escenario()
    
    # 3. Le pasamos el héroe y el mundo al motor gráfico
    juego = MotorGrafico(heroe=heroe_principal, mundo=mundo_generado)

    while juego.corriendo:
        juego.manejar_eventos() 
        juego.dibujar()         
        juego.actualizar()      
        
    juego.salir()
    print("Juego cerrado correctamente.")

if __name__ == "__main__":
    main()