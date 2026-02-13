from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import openai
import os
from dotenv import load_dotenv

# Cargar variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Configurar API key de OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

@app.route('/whatsapp', methods=['POST'])
def whatsapp_reply():
    """
    Endpoint que recibe mensajes de WhatsApp desde Twilio
    y responde usando ChatGPT
    """
    
    # Obtener el mensaje entrante y el número del remitente
    incoming_msg = request.values.get('Body', '').strip()
    sender = request.values.get('From', '')
    
    # Mostrar en consola para debugging
    print(f"📱 Mensaje recibido de {sender}: {incoming_msg}")
    
    # Obtener respuesta de ChatGPT
    respuesta = obtener_respuesta_gpt(incoming_msg)
    
    # Mostrar respuesta en consola
    print(f"🤖 Respuesta enviada: {respuesta}")
    
    # Crear respuesta de WhatsApp con Twilio
    resp = MessagingResponse()
    resp.message(respuesta)
    
    return str(resp)

def obtener_respuesta_gpt(mensaje):
    """
    Envía el mensaje a ChatGPT y obtiene una respuesta
    """
    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",  # Puedes cambiar a "gpt-3.5-turbo" para ahorrar costos
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
            max_tokens=300,
            temperature=0.7
        )
        
        # Extraer y retornar el texto de la respuesta
        return response.choices[0].message.content
        
    except Exception as e:
        # Manejar errores y mostrar en consola
        print(f"❌ Error con OpenAI: {e}")
        return "Disculpa, tuve un problema al procesar tu mensaje. ¿Podrías intentar de nuevo en un momento?"

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

@app.route('/test', methods=['GET'])
def test():
    """
    Endpoint de prueba para verificar la conexión con OpenAI
    """
    try:
        respuesta = obtener_respuesta_gpt("Hola, esto es una prueba")
        return f"✅ Conexión con OpenAI funcionando. Respuesta: {respuesta}"
    except Exception as e:
        return f"❌ Error: {str(e)}"

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print("=" * 50)
    print("🚀 Servidor del Bot de WhatsApp iniciando...")
    print(f"📍 Puerto: {port}")
    print("=" * 50)
    
    # Para producción en Railway
    app.run(host='0.0.0.0', port=port)