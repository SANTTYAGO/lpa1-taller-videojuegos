# main.py
import sys
from models.personaje import Personaje # <--- NUEVO
from core.escenario import Escenario
from ui.pantalla import MotorGrafico

def main():
    try:
        # Iniciamos con un personaje temporal, lo reemplazaremos en la pantalla de clases
        heroe_base = Personaje("Aventurero", puntos_vida=100, puntos_magia=50, ataque=10, defensa=5)
        
        # Generar Escenario
        mundo = Escenario()
        
        # Iniciar Motor Gráfico
        motor = MotorGrafico(heroe_base, mundo)
        
        # Bucle Principal del Juego
        while motor.corriendo:
            motor.manejar_eventos()
            motor.actualizar()
            motor.dibujar()
            
        motor.salir()
        
    except Exception as e:
        print(f"\nError fatal en el juego: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()