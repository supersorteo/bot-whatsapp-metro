from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

app = Flask(__name__)

# Configurar OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    """
    Endpoint que recibe mensajes de WhatsApp desde Twilio
    y responde usando ChatGPT
    """
    try:
        # Obtener datos del mensaje entrante
        incoming_msg = request.values.get('Body', '').strip()
        sender = request.values.get('From', '')
        sender_name = request.values.get('ProfileName', 'Cliente')
        
        # Log para debugging
        print(f"{'='*60}")
        print(f"📱 Nuevo mensaje")
        print(f"De: {sender}")
        print(f"Nombre: {sender_name}")
        print(f"Mensaje: {incoming_msg}")
        print(f"{'='*60}")
        
        # Obtener respuesta de ChatGPT
        respuesta = obtener_respuesta_gpt(incoming_msg, sender_name)
        
        print(f"🤖 Respuesta enviada: {respuesta}\n")
        
        # Crear respuesta de Twilio
        resp = MessagingResponse()
        resp.message(respuesta)
        
        return str(resp)
    
    except Exception as e:
        print(f"❌ Error en whatsapp_reply: {e}")
        resp = MessagingResponse()
        resp.message("Disculpa, hubo un error técnico. Por favor intenta de nuevo.")
        return str(resp)

def obtener_respuesta_gpt(mensaje, nombre_usuario="Cliente"):
    """
    Envía el mensaje a ChatGPT y obtiene una respuesta personalizada
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Cambia a "gpt-3.5-turbo" si quieres ahorrar costos
            messages=[
                {
                    "role": "system",
                    "content": f"""Eres un asistente virtual de Metro, una aplicación innovadora 
                    que brinda información y asesoramiento experto sobre materiales de construcción.
                    
                    Tu personalidad:
                    - Amigable, profesional y servicial
                    - Experto en construcción y materiales
                    - Das respuestas concisas pero completas
                    - Usas un tono cercano pero profesional
                    
                    El usuario se llama {nombre_usuario}.
                    
                    Tus funciones principales:
                    1. Asesorar sobre qué materiales usar para diferentes proyectos
                    2. Ayudar con cálculos de cantidades (cemento, arena, varillas, etc.)
                    3. Recomendar marcas y calidades
                    4. Orientar sobre presupuestos aproximados
                    5. Resolver dudas técnicas de construcción
                    
                    Si no sabes algo específico, sé honesto y recomienda consultar con un ingeniero.
                    """
                },
                {
                    "role": "user",
                    "content": mensaje
                }
            ],
            max_tokens=400,  # Respuestas un poco más largas para ser útil
            temperature=0.7
        )
        
        return response.choices[0].message.content
        
    except openai.error.AuthenticationError:
        print("❌ Error: API key de OpenAI inválida")
        return "Lo siento, hay un problema con la configuración. Por favor contacta al administrador."
    
    except openai.error.RateLimitError:
        print("❌ Error: Límite de rate excedido en OpenAI")
        return "Estoy recibiendo muchas consultas en este momento. Por favor intenta de nuevo en unos segundos."
    
    except openai.error.APIError as e:
        print(f"❌ Error de API de OpenAI: {e}")
        return "Disculpa, no pude procesar tu consulta en este momento. ¿Podrías intentar de nuevo?"
    
    except Exception as e:
        print(f"❌ Error inesperado en obtener_respuesta_gpt: {e}")
        return "Hubo un problema al procesar tu mensaje. Por favor intenta reformularlo."

@app.route('/', methods=['GET'])
def home():
    """
    Página de inicio para verificar que el bot está funcionando
    """
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Metro Bot - WhatsApp</title>
        <style>
            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                text-align: center;
                padding: 50px;
                margin: 0;
            }
            .container {
                background: rgba(255,255,255,0.1);
                border-radius: 20px;
                padding: 40px;
                max-width: 600px;
                margin: 0 auto;
                backdrop-filter: blur(10px);
            }
            h1 { font-size: 3em; margin: 0; }
            .status { 
                background: #10b981; 
                padding: 10px 20px; 
                border-radius: 50px;
                display: inline-block;
                margin: 20px 0;
                font-weight: bold;
            }
            code {
                background: rgba(0,0,0,0.3);
                padding: 5px 10px;
                border-radius: 5px;
                font-family: 'Courier New', monospace;
            }
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🏗️ Metro Bot</h1>
            <div class="status">✅ ACTIVO</div>
            <p style="font-size: 1.2em;">Bot de WhatsApp para asesoramiento en materiales de construcción</p>
            <hr style="border: 1px solid rgba(255,255,255,0.3); margin: 30px 0;">
            <p><strong>Endpoint de WhatsApp:</strong> <code>/whatsapp</code></p>
            <p><strong>Health check:</strong> <code>/health</code></p>
        </div>
    </body>
    </html>
    """

@app.route('/health', methods=['GET'])
def health():
    """
    Endpoint para verificar el estado del servicio
    """
    return {
        "status": "healthy",
        "service": "Metro WhatsApp Bot",
        "version": "1.0.0"
    }, 200

@app.route('/test', methods=['GET'])
def test():
    """
    Endpoint de prueba para verificar OpenAI
    """
    try:
        respuesta = obtener_respuesta_gpt("Hola, esto es una prueba")
        return {
            "status": "success",
            "openai_connected": True,
            "test_response": respuesta
        }, 200
    except Exception as e:
        return {
            "status": "error",
            "openai_connected": False,
            "error": str(e)
        }, 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("\n" + "="*70)
    print("🚀 METRO BOT - WHATSAPP INICIANDO")
    print("="*70)
    print(f"📍 Puerto: {port}")
    print(f"🌐 Ambiente: {'Producción (Railway)' if port != 5000 else 'Desarrollo (Local)'}")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)