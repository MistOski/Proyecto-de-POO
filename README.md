Funciones actuales

El siguiente proyecto es un videojuego desarrollado en Pygame enfocado en la estrategia.

Los jugadores deben elegir una ciudad y administrarla conforme a sus preferencias, realizar progresos significativos y conquistar las ciudades vecinas, lo cual es el propósito final del juego: conquistar la Región de los Lagos comenzando por una ciudad.

Actualmente, el juego es ejecutable con el comando de "python main.py"; posterior a eso aparece la pantalla de inicio, a la cual se accede con la tecla INTRO. Los jugadores empiezan eligiendo su ciudad, la cual, al realizar una nueva partida, obtendrá una clase aleatoria.

Existen 3 clases: 

Conquistador: +20% de poder de ataque inicial.

Comerciante: +20$ de ganancias al comerciar.

Recolector: +20$ de ganancias al recolectar recursos.

Actualmente solo se encuentran disponibles esos beneficios.

Cada 30 segundos, cada ciudad realizará una acción aleatoria; podrá comerciar, recolectar o intentar conquistar otras ciudades (actualmente deshabilitado). El sistema de conquista permite ganar monedas y territorios; dichos territorios deben estar cerca de la ciudad inicial del jugador para poder ser conquistados; si una ciudad se encuentra lejos y este no se ha expandido con las ciudades vecinas, no podrá realizar la conquista.

El juego actualmente carece de interfaz, pero cuenta con sus respectivas opciones funcionales, tales como la pestaña de notificaciones que se encuentra en la esquina inferior izquierda de la pantalla, la cual envía mensajes de las acciones del jugador y las otras ciudades. A su vez, con las teclas 1, 2 y 3, el jugador podrá elegir las opciones de acción que tiene disponibles: atacar, comerciar, recolectar (se abre una pestaña para elegir qué ciudad atacar).


