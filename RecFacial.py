from flask import Flask, render_template, Response, request
import cv2
import time
from FFEM import MonitorEmotion_From_Video

#Define o Webapp para a var app
app = Flask(__name__)


#Executa o Código abaixo quando o Webapp é acessado
@app.route("/", methods=['GET', 'POST'],)

#Define variaveis quando o Webapp é acessado e aplica o template de página a ser utilizado
def index():

    global a
    global b
    global t_end
 
    a = 0
    t_end = 0
    f = open("result.txt", 'w')
    f.write('')
    f.close()
    print(request.method)
    get_result()
    time.sleep(0.125)
    #Vefifica se o botão de Analize foi apertado e define o timer da analize facial
    if request.method == 'POST':
        if request.form.get('Analzize') == 'Analizar':
            a = 1
            b = 0
            t_end = time.time() + 5
            time.sleep(0.125)
        else:
            a = 0
            t_end = 0
            b = 0
            return render_template("index.html")
    elif request.method == 'GET':
        print("No Post Back Call")
        a = 0
        b = 0
        c = 1
        t_end = 0
    return render_template("index.html")


def get_frame(a,t_end):

    #Define e atualiza os quadros de imagem da camera para análise 
    camera=cv2.VideoCapture(0)
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('input.avi', fourcc, 20.0, (640,480))
    b = 0
    
    while True:
        
        retval, im = camera.read()
        im = cv2.resize(im, (640,480))
        imgencode=cv2.imencode('.jpg',im)[1]
        stringData=imgencode.tobytes()
        
        #Aplica a tela de "analisando..."
        if time.time() > t_end -1 and a == 1 and t_end != 0: 
            f = open("result.txt", 'w')
            f.write("Analisando")
            f.close()

        

        #Grava um video de 5 segundos e envia para a análize de emoções
        if a == 1:
            if time.time() < t_end:
                out.write(im)

                
            else:
                a = 0
                out.release()
                b = 1
                global emocoes
                emocoes = MonitorEmotion_From_Video('input.avi','output.avi')
                print(emocoes)

                result = str(max(emocoes, key=emocoes.get))
                print(str(max(emocoes, key=emocoes.get)))

        #Verifica que a analize foi concluida e envia o resultado para o Webapp para vizualização do usuário
        if b == 1:
            f = open("result.txt", 'w')
            f.write(result)
      



        yield (b'--frame\r\n'
            b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')

#Envia a solicitação pro Webapp atualizar o quadro da Camera
@app.route('/video')
def video(): 
    return Response(get_frame(a,t_end),mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/resultado')
def resultado():
    return Response(get_result(),mimetype='multipart/x-mixed-replace; boundary=frame')

def get_result():
    ok = 1
    

    while True:
        
        if ok == 1:
            f = open("result.txt", 'r')
            result = f.read()
            f.close()

        
        im = cv2.imread('blank.png')

        if result == 'Analisando':
            im = cv2.imread('analisando.png')

        if time.time() > t_end:

            if result == 'Triste':
                im = cv2.imread('triste.png')
                ok = 0 

            elif result == 'Feliz':
                im = cv2.imread('feliz.png')
                ok = 0
                
            elif result == 'Neutro':
                im = cv2.imread('neutro.png')
                ok = 0
            
            elif result == 'Bravo':
                im = cv2.imread('bravo.png')
                ok = 0
            
            elif result == 'Surpreso':
                im = cv2.imread('surpreso.png')
                ok = 0

            elif result == 'Nojo':
                im = cv2.imread('enojado.png')
                ok = 0
            
            elif result == 'Medo':
                im = cv2.imread('commedo.png')
                ok = 0
        
        im = cv2.resize(im,(640, 480))

        imgencode=cv2.imencode('.jpg',im)[1]
        stringData=imgencode.tobytes()

        
        yield (b'--frame\r\n'
               b'Content-Type: text/plain\r\n\r\n'+stringData+b'\r\n')


#Inicia o Webapp no host local
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=5000, debug=True, threaded=True)


