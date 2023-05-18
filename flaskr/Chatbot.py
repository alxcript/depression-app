import openai

class Chatbot:
    def __init__(self):
        openai.api_key = "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"
        self.modelName = "davinci:ft-personal-2023-05-06-00-25-56"

    
    def generateResponse(self, query):
        """ response =#openai.Completion.create(
            model=self.modelName,
            prompt="La siguiente es una conversación con un terapeuta y un usuario. El terapeuta es JOY, que usa la escucha compasiva para tener conversaciones útiles y significativas con los usuarios. JOY es empático y amable. El objetivo de JOY es hacer que el usuario se sienta mejor al sentirse escuchado. Con cada respuesta, JOY ofrece preguntas de seguimiento para fomentar la apertura y trata de continuar la conversación de forma natural. \n\nJOY -> Hola, soy tu asistente personal de salud mental. ¿Qué tienes en mente hoy?\nUser ->"+query+"JOY ->",
            temperature=0.89,
            max_tokens=80,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0.6,
            stop=["\n"]) """


        result = "Respuesta desde la API de Openai" #response.get('choices')[0].get('text')
        return result