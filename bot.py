from flask import Flask, request, jsonify
import openai
from twilio.twiml.messaging_response import MessagingResponse
from openai import OpenAI
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
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
    Envía el mensaje a ChatGPT y obtiene una respuesta
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Cambia a "gpt-3.5-turbo" si quieres ahorrar costos
            messages=[
                {
                    "role": "system", 
                    "content": """Eres un asistente de atención al cliente amigable y profesional. 
                    Respondes de manera concisa y útil. Siempre mantén un tono cordial y profesional."""
                },
                {
                    "role": "user", 
                    "content": mensaje
                }
            ],
            max_tokens=400,  # Respuestas un poco más largas para ser útil
            temperature=0.7
        )
        
        # Extraer y retornar el texto de la respuesta
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
    Ruta de prueba para verificar que el servidor está funcionando
    """
    return """
    <html>
        <head>
            <title>Bot WhatsApp - Metro</title>
        </head>
        <body style="font-family: Arial; text-align: center; padding: 50px;">
            <h1>✅ Bot de WhatsApp funcionando correctamente</h1>
            <p>El servidor está activo y listo para recibir mensajes.</p>
            <p>Endpoint de WhatsApp: <code>/whatsapp</code></p>
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
    Endpoint de prueba para verificar la conexión con OpenAI
    """
    if not openai_client:
        return jsonify({
            "status": "error",
            "openai_connected": False,
            "error": "OpenAI client not initialized - check OPENAI_API_KEY"
        }), 500
    
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
    print("=" * 50)
    print("🚀 Servidor del Bot de WhatsApp iniciando...")
    print(f"📍 Puerto: {port}")
    print(f"🌐 Ambiente: {'Producción (Railway)' if port != 5000 else 'Desarrollo (Local)'}")
    print("="*70 + "\n")
    
    app.run(host='0.0.0.0', port=port, debug=False)