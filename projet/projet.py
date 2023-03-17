# importation pour la bdd
import mysql.connector

import bcrypt

from datetime import datetime

import random,string
#importation liée au traitement des fichiers csv
import os
import csv

#importation socket.o
from flask_socketio import SocketIO, join_room, emit

#importation des extentions flask utilisées dans notre application web
from flask import Flask, render_template, request, redirect, url_for, session

# création de l'application flask
app=Flask('__name__')

# configuration socket.io
socketio = SocketIO(app, logger=True, engineio_logger=True)

# clé de codage pour les sessions
app.secret_key = "6a6afeba79eb205ff2b2949aaed44f13823d3ef1b2f938244edc2aa66227c2e2"

# Upload folder
UPLOAD_FOLDER = 'file'
app.config['UPLOAD_FOLDER'] =  UPLOAD_FOLDER

#   FONCTIONS
def Execute(requete,listeValeurs):
    connex = mysql.connector.connect(user='root', password='password',host='localhost', database='ProjScolaire')
    curseur = connex.cursor()
    resultat = []
    if listeValeurs=="":
        curseur.execute(requete)
    else:
        curseur.execute(requete,listeValeurs)
    if requete[0:6] == "SELECT":
        resultat = curseur.fetchall()
    else :
        connex.commit()
    connex.close()
    return resultat
def NbAtt(liste):
    if len(liste)>1 :
        valeurs ="("
        for i in range(len(liste)):
            valeurs += "%s,"
        valeurs = valeurs[:-1]+")"
    else :
        valeurs = "(%s)"
    return valeurs

def parseCSV(filePath):
    # CVS Column Names
    with open(filePath) as fic:
        csvData = csv.reader(fic)
        # parcourir les lignes
        ligne1=0
        for row in csvData:
            if ligne1 == 1 : # sauter la 1ere ligne
                print("ici")
                rowli = row[0].split(";")
                sqlE = "INSERT INTO Etudiants (NumEtu,Nom,Prenom,PASSWORD) VALUES (%s,%s,%s,%s)"
                sqlU="INSERT INTO assocEP (idU,NumEtu) VALUES (%s,%s)"
                valueU=(session['connecter'],rowli[0])
                code = rowli[0].encode('utf-8')
                code = bcrypt.hashpw(code,bcrypt.gensalt(12))
                valueE = (rowli[0],rowli[1],rowli[2],code)
                Execute(sqlE,valueE)
                Execute(sqlU,valueU)
            ligne1 = 1

# verifications des données saisies
def Inscrit(id):
    existe = Execute("SELECT mail FROM utilisateurs WHERE mail = %s ", ( id,))
    if existe == [] :
        existe = Execute("SELECT NumEtu FROM Etudiants WHERE NumEtu = %s ", ( id,))
    return existe
def codeCorrect(id,code):
    code=code.encode('utf-8')
    codeEnregistre = Execute("SELECT `PASSWORD` FROM utilisateurs WHERE mail = %s", (id, ))
    if not(codeEnregistre) :
        codeEnregistre = Execute("SELECT `PASSWORD` FROM Etudiants WHERE NumEtu = %s", (id, ))
    codeEnregistre = codeEnregistre[0][0].encode('utf-8')
    return bcrypt.checkpw(code,codeEnregistre)

# INSERT
def Insert(table,listeAttributs,listeValeurs):
    Nbvaleurs = NbAtt(listeValeurs)
    requete = f"INSERT INTO {table} {listeAttributs} VALUES {Nbvaleurs}"
    Execute(requete,listeValeurs)
def generate_id():
    id = ''.join(random.choice(string.ascii_uppercase + string.ascii_lowercase + string.digits) for _ in range(8))
    return id 

#select primary key
def getidU(mail):
    idU = Execute("SELECT idU FROM utilisateurs WHERE mail = %s", (mail,))
    if not(idU) :
        idU = [[[]]]
    return idU[0][0]
def getidQ(question,idU):
    idQ = Execute("SELECT idQ FROM questions WHERE question = %s AND idU = %s ", (question,idU))
    return idQ[0][0]
def getidR(reponse,idQ):
    idR = Execute("SELECT idR FROM reponse WHERE idQ  = %s AND reponse = %s", (idQ,reponse))
    return idR[0][0]
def getidE(etiquette):
    idE =  Execute("SELECT idE FROM etiquettes WHERE etiquette = %s", (etiquette,))
    return idE[0][0]
def getNumEtu(nom,prenom):
    return Execute("SELECT NumEtu FROM Etudiants WHERE nom = %s  AND prenom = %s ",(nom,prenom))[0][0]
def getAssocEP(idU):
    liste = Execute("SELECT NumEtu FROM assocEP WHERE idU = %s ",(idU,))
    resultat=[]
    for etu in liste :
        resultat.append(etu[0])
    return resultat
def getAssocPE(NumEtu):
    liste = Execute("SELECT idU FROM assocEP WHERE NumEtu = %s ",(NumEtu,))
    resultat=[]
    for prof in liste :
        resultat.append(prof[0])
    return resultat
def getAssocQE(idE):
    liste = Execute("SELECT idQ FROM assocQE WHERE idE = %s ",idE)
    resultat=[]
    for q in liste :
        resultat.append(q[0])
    return resultat
def getAssocEQ(idQ):
    liste = Execute("SELECT idE FROM assocQE WHERE idQ = %s ",(idQ,))
    resultat=[]
    for eti in liste :
        resultat.append(eti[0])
    return resultat
def get(att,table):
    requete = f"SELECT {att} FROM {table}"
    liste = Execute(requete,"")
    resultat=[]
    for val in liste :
        resultat.append(val[0])
    return resultat

#infosU
def getPrenomU(idU):
    return Execute("SELECT prenom FROM utilisateurs WHERE idU = %s ",(idU,))[0][0]
def getNomU(idU):
    return Execute("SELECT nom FROM utilisateurs WHERE idU = %s ",(idU,))[0][0]
def getMailU(idU):
    return Execute("SELECT mail FROM utilisateurs WHERE idU = %s ",(idU,))[0][0]

#infosQ
def getQuestion(idQ):
    return Execute("SELECT question,idQ FROM questions WHERE idQ = %s ",(idQ,))
def getTypeQ(idQ):
    return Execute("SELECT type FROM questions WHERE idQ = %s ",(idQ,))[0][0]
def getQuestions(idU):
    resultat= Execute("SELECT question,idQ FROM questions WHERE idU = %s ",(idU,))
    return resultat

# voir plus tard si on ne garde pas que getInfosQ pour utiliser a chaque fois type de la Q
def getInfosQ(idU):
    return Execute("SELECT question,type FROM questions WHERE idU = %s ",(idU,))

#infosR
def getReponse(idR):
    return Execute("SELECT reponse FROM reponses WHERE idR = %s ",(idR,))[0][0]
def getValR(idR):
    return Execute("SELECT valeur FROM reponses WHERE idR = %s ",(idR,))[0][0]
def getidQdeR(idR):
    return Execute("SELECT idQ FROM reponses WHERE idR = %s ",(idR,))[0][0]
def getReponsesdeQ(idQ):
    return Execute("SELECT reponse,valeur FROM reponses WHERE idQ = %s ",(idQ,))
def getReponsesdeQAvecidR(idQ):
    return Execute("SELECT reponse,valeur,idR FROM reponses WHERE idQ = %s ",(idQ,))

def getReponsesforEtu(idQ):
    return Execute("SELECT idR,reponse FROM reponses WHERE idQ = %s ",(idQ,))

#infosEtu
def getNomEtu(NumEtu):
    return Execute("SELECT Nom FROM Etudiants WHERE NumEtu = %s ",(NumEtu,))[0][0]
def getPrenomEtu(NumEtu):
    return Execute("SELECT Prenom FROM Etudiants WHERE NumEtu = %s ",(NumEtu,))[0][0]
def getInfosEtu(idU):
    return Execute("SELECT NumEtu,Nom,Prenom FROM Etudiants WHERE NumEtu IN (SELECT NumEtu FROM assocEP WHERE idU = %s )  ",(idU,))

#infosEti
def getEtiq(idE):
    return Execute("SELECT etiquette FROM etiquettes WHERE idE = %s ",(idE,))[0][0]

# UPDATE
def modifier_mdp_prof(idU,NewMdp):
    Execute("UPDATE utilisateurs SET PASSWORD = %s WHERE idU = %s", (NewMdp,idU))
def modifier_mdp_etu(NumEtu,NewMdp):
    Execute("UPDATE etudiants SET PASSWORD = %s WHERE NumEtu = %s", (NewMdp,NumEtu))

# DELETE
def supprimer(table,cond,val):
    requete = f"DELETE FROM {table} WHERE {cond} = %s "
    Execute(requete,val)


def getSequences(idU):
    return Execute("SELECT idS,titre FROM sequence WHERE idU = %s ",(idU,))

def getidQdeidS(idS):
    return Execute("SELECT ordre,idQ FROM assocQS WHERE idS = %s ORDER BY ordre ASC",(idS,))


#    ROUTES

# Route racine contenant la page d'acceuil
@app.route('/',methods=['POST','GET'] )
def acceuil():
    return render_template('index.html', titrePage = 'Bienvenue')

# Route vers la page d'inscription
@app.route('/signup',methods=['POST','GET'])
def signup():

    # condition valide lorsque l'utilisateur envoie le formulaire d'inscription
    if request.method == 'POST':

        # On créé des variables qui recuperent les données saisies coté client lorsque celles-ci ont été poster ('POST')
        nom = request.form.get('lastName')
        prenom = request.form.get('firstName')
        mail = request.form.get('email')
        code = request.form.get('password1')
        checkcode = request.form.get('password2')

        #on vérifie que :
        #  les 2 codes sont identiques
        #  le mail saisit n'est pas associé à un utilisateur déja existant'
        # si les 2 conditions sont vérifiées on ajoute le nouvel utilisateur à la base de données
        if code == checkcode and not(Inscrit(mail)) :
            code = code.encode('utf-8')
            code = bcrypt.hashpw(code,bcrypt.gensalt(12))
            Insert("utilisateurs","(nom,prenom,mail,PASSWORD)",(nom,prenom,mail,code))

            # on charge le cookie de session avec les données de l'utilisateur
            session['connecter']=getidU(mail)
            session['prenom']=prenom
            session['nom']=nom
            session['role']='professeur'
            # on renvoie l'utilisateur à la page d'acceuil
            return redirect(url_for('acceuil'))

        # si le mail saisit est associé à un compte utilisateur
        # on le redirige vers la page de connexion en preremplissant le mail
        elif code == checkcode :
            return redirect(url_for('log',mail=mail))
        # si les codes ne correspondent pas,
        # on lui notifie que les mot de passe ne correspondent pas
        else :
            return render_template('signup.html',titrePage= "Inscription", mail=mail, nom=nom, prenom=prenom )
    # page d'inscription par defaut
    else :
        return render_template('signup.html',titrePage= "Inscription")

@app.route('/signup/<mail>')
def sign(mail):
    return render_template('signup.html',titrePage= "Inscription", mail=mail , mailInconnu = 1 )

# Route vers la page de connexion
@app.route('/login',methods=['POST','GET'])
def login():
    # Condition valide lorsque l'utilisateur envoie le formulaire de connexion
    if request.method == 'POST':
        identifiant = request.form.get('email')
        code = request.form.get('password')
        # on verifie que le mail saisit correspond à un utilisateur existant
        if Inscrit(identifiant) :
            # on verifie si le code saisit et celui associer au mail saisit
            if codeCorrect(identifiant,code):
                # on charge le cookie de session avec les données de l'utilisateur
                if getidU(identifiant) != [] :
                    session['connecter']=getidU(identifiant)
                    session['prenom']= getPrenomU(session['connecter'])
                    session['nom']= getNomU(session['connecter'])
                    session['role'] = 'professeur'
                else :
                    session['connecter']= identifiant
                    session['prenom']= getPrenomEtu(identifiant)
                    session['nom']= getNomEtu(identifiant)
                    session['role'] = 'eleve'
                # on l'envoie vers la page d'acceuil
                return redirect(url_for('acceuil'))
            # si le code est incorrect,
            # on le lui notifie
            else:
                return render_template("login.html",titrePage= "Connexion", mdp='incorrect', login=identifiant)
        # si le mail ne correspond a aucun compte,
        # on le renvoie vers la page d'inscription
        else:
            return redirect(url_for('sign', mail=identifiant ))
    # page de connexion par defaut
    else:
        return render_template("login.html",titrePage= "Inscription")

@app.route('/login/<mail>')
def log(mail):
    return render_template('login.html',titrePage= "Inscription", login=mail)

# Route vers l'acceuil après la deconnexion
@app.route('/logout')
def logout():
    # On décharge le cookie de connexion, afin de renvoyer la bonne page d'acceuil
    session['connecter']=''
    session['prenom']=''
    session['nom']=''
    session['role']=''
    session['salon']=''
    return redirect(url_for('acceuil'))

# Route vers la page contenant les questions
@app.route('/questions', methods=['POST','GET'])
def questions():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    idU = session['connecter']
    liste_reponses =[]
    liste_assocQE = []
    questions_idU =[]
    etiquettesSelect = []
    listeEtideQ =[]
    # condition qui renvoie la page questions filtrée par des etiquettes selectionnées
    if request.method == 'POST' and request.form.get("ExamEcrit") :
        listeidq = request.form.get('listeQchoisi')
        listeidq = list(filter(None,listeidq.split(',')))
        listeidq = [int(num) for num in listeidq]
        titre= request.form.get('titre')
        data = []
        for q in listeidq:
            if getTypeQ(q) =="qcm" :
                data.append([getQuestion(q)[0][0],getReponsesdeQ(q)])
            else :
                data.append([getQuestion(q)[0][0],[]])
        return render_template("examen1.html",titrePage= "Examen à imprimer",titre=titre,data=data)
    elif  request.method == 'POST' and request.form.get("ExamLive") :
        listeidq = request.form.get('listeQchoisi')
        listeidq = list(filter(None,listeidq.split(',')))
        listeidq = [int(num) for num in listeidq]
        intitule= request.form.get('titre')
        idS=generate_id()
        Insert("sequence","(idS,titre,idU)",(idS,intitule,session['connecter']))
        for idQ in  listeidq:
            Insert("assocQS","(idS,idQ,Ordre)",(idS,idQ,listeidq.index(idQ)+1))
        return redirect(url_for('acceuil'))
    elif  request.method == 'POST' and request.form.get("supprimer") :
        idQ = (request.form.get("supprimer"))
        supprimer("questions","idQ",(idQ,))
        return redirect(url_for('questions'))
    # condition qui nous renvoie sur la page d'edition de question
    elif  request.method == 'POST' and request.form.get("modifier") :
        session['QuestionAmodifier'] = request.form.get("modifier")
        return redirect(url_for('edit_question'))
    # page question par defaut qui renvoie toutes les questions de l'utilisateur connecté
    else :
        questions_idU = getQuestions(idU)
        for question in questions_idU :
            liste_reponses.append([getReponsesdeQ(question[1]),question[1]])
            for eti in getAssocEQ(question[1]):
                listeEtideQ.append(getEtiq(eti))
            liste_assocQE.append([listeEtideQ,question[1]])
            listeEtideQ = []
        return render_template('questions.html',titrePage= "Mes Questions", questions=questions_idU, idU=idU, etiquettes = get("etiquette","etiquettes"), liste_reponses=liste_reponses, liste_assocQE=liste_assocQE)

# Route vers la page d'ajout de question
@app.route('/ajout_question',methods=['POST','GET'])
def ajout_question():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    liste_reponses = []
    liste_etiSelect = []
    idUtil = session['connecter']
    liste_etiquettes_bdd=get("etiquette","etiquettes")
    if request.method == 'POST': 
        for key, val in request.form.items():
            print((key,val))
        question = request.form.get('question')
        typeQ = request.form.get('typeQ')
        if (question,typeQ) not in getInfosQ(idUtil) :
            Insert("questions","(question,type,idU)",(question,typeQ,idUtil))
            for key, val in request.form.items():
                if key.startswith("item"):
                    liste_reponses.append((key,val))
                    print((key,val))
                if key.startswith("etiquetteSelect"):
                    liste_etiSelect.append((key,val))
            if request.form.get("typeQ")=="Num" and (request.form.get("reponse"),"1") not in getReponsesdeQ(getidQ(question,idUtil)):
                Insert("reponses","(reponse,valeur,idQ)",(request.form.get("reponse"),"1", getidQ(question,idUtil)))
            else :
                for i in range(0,len(liste_reponses)-1,2) :
                    if (liste_reponses[i+1][1],liste_reponses[i][1]) not in getReponsesdeQ(getidQ(question,idUtil)) :
                        Insert("reponses","(reponse,valeur,idQ)",(liste_reponses[i+1][1],liste_reponses[i][1], getidQ(question,idUtil)))
            for i in range(len(liste_etiSelect)):
                if liste_etiSelect[i][1] not in liste_etiquettes_bdd :
                    Insert("etiquettes","(etiquette)",(liste_etiSelect[i][1],))
                Insert("assocQE","(idE,idQ)",(getidE(liste_etiSelect[i][1]),getidQ(question,session['connecter'])))
        return redirect(url_for("questions"))

    else:
        return render_template('ajout_question.html',titrePage= "Nouvelle question", etiquettes = get("etiquette","etiquettes") )

#
    # # Route vers la page de création d'examens
    # @app.route('/generer_fiche',methods=['GET','POST'])
    # def generer_fiche():
    #     if request.method=='POST':
    #         titre=request.form.get("titre")
    #         print(titre)
    #         print(request.form.getlist("quest"))
    #         listqueschoisi=request.form.getlist("quest")
    #         if not len(listqueschoisi)==0:
    #             print("fin")
    #             myidqlistchoisi=[]
    #             for q in listqueschoisi:
    #                 print("listeq",listqueschoisi)
    #                 print(q)
    #                 mesidq=getidQ(q,session['connecter'])
    #                 myidqlistchoisi.append(mesidq)
    #             print(myidqlistchoisi)
    #             titre=request.form.get("titre")

    #             mesreponses={}
    #             for myidq in myidqlistchoisi:
    #                 print(myidq)
    #                 myreponses=getReponsesdeQ(myidq)
    #                 myquestion=getQuestion(myidq)
    #                 print(myquestion)
    #                 print(myreponses)
    #                 reponses=[]
    #                 for res in myreponses:
    #                     reponses.append(res[0])
    #                 print(reponses)
    #                 mesreponses[myquestion[0][0]]=reponses
    #             print(mesreponses)
    #             if not titre=="":
    #                 return render_template("examen.html",titrePage= "Examen à imprimer",titre=titre,qs=listqueschoisi,reponses=mesreponses)
    #         etilist=request.form.getlist("etis")
    #         eti1list=[]
    #         for eti in etilist:
    #             eti1list.append((eti,))
    #         print(eti1list)
    #         idqlist=[]
    #         for eti1 in eti1list:
    #             print(eti1)
    #             if eti1[0] in get("etiquette","etiquettes"):
    #                 ide=getidE(eti1[0])
    #                 idqlist.append(getAssocQE(ide))
    #         print(idqlist)
    #         newidqlist=[]
    #         for idq in idqlist:
    #             for id in idq:
    #                 newidqlist.append(id)
    #         listeQuestions=[]
    #         print(newidqlist)
    #         mesreponses2={}
    #         for idq in newidqlist:
    #             print(idq)
    #             if not len(getQuestion(idq))==0:
    #                 listeQuestions.append(getQuestion(idq))
    #                 print(listeQuestions)
    #                 myreponses2=getReponsesdeQ(idq)
    #                 myquestion2=getQuestion(idq)
    #                 print(myquestion2)
    #                 print(myreponses2)
    #                 reponses2=[]
    #                 for res in myreponses2:
    #                     reponses2.append(res[0])
    #                 print(reponses2)
    #                 mesreponses2[myquestion2[0][0]]=reponses2
    #                 print(mesreponses2)
    #         print(mesreponses2)
    #         return render_template('cree_fiche.html',etiquettes=get("etiquette","etiquettes"),questions=listeQuestions,reponses=mesreponses2)
    #     print(get("etiquette","etiquettes"))
    #     return render_template('cree_fiche.html',etiquettes=get("etiquette","etiquettes"))
    # @app.route('/examen')
    # def examen():
    #     return render_template("examen.html")

# modification de ajout_question pour en faire modif_question comme etant un ajout_question prérempli
@app.route('/edit_question',methods=['POST','GET'])
def edit_question():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    liste_etiSelect = []
    liste_etiquettes_bdd=get("etiquette","etiquettes")
    idU = session['connecter']
    idQ = session['QuestionAmodifier']
    print(idQ)
    typeQ= getTypeQ(idQ)
    question = getQuestion(idQ)[0][0]
    liste_reponses = getReponsesdeQ(idQ)
    liste_etiSelect = []

    if request.method == 'POST': 
        liste_reponses = []
        for key, val in request.form.items():
            print((key,val))
        supprimer("questions","idQ",(idQ,))
        question = request.form.get('question')
        typeQ = request.form.get('typeQ')
        if (question,typeQ) not in getInfosQ(idU) :
            Insert("questions","(question,type,idU)",(question,typeQ,idU))
            for key, val in request.form.items():
                if key.startswith("item"):
                    liste_reponses.append((key,val))
                if key.startswith("etiquetteSelect"):
                    liste_etiSelect.append((key,val))
            if request.form.get("typeQ")=="Num" and (request.form.get("reponse"),"1") not in getReponsesdeQ(getidQ(question,idU)):
                Insert("reponses","(reponse,valeur,idQ)",(request.form.get("reponse"),"1", getidQ(question,idU)))
            else :
                print(liste_reponses)
                for i in range(0,len(liste_reponses)-1,2) :
                    if (liste_reponses[i+1][1],liste_reponses[i][1]) not in getReponsesdeQ(getidQ(question,idU)) : 
                        print((liste_reponses[i+1][1],liste_reponses[i][1], getidQ(question,idU)))  
                        Insert("reponses","(reponse,valeur,idQ)",(liste_reponses[i+1][1],liste_reponses[i][1], getidQ(question,idU)))
            for i in range(len(liste_etiSelect)):
                if liste_etiSelect[i][1] not in liste_etiquettes_bdd :
                    Insert("etiquettes","(etiquette)",(liste_etiSelect[i][1],))
                Insert("assocQE","(idE,idQ)",(getidE(liste_etiSelect[i][1]),getidQ(question,session['connecter'])))
        return redirect(url_for("questions"))
    for etiquette in getAssocEQ(idQ) :
        liste_etiSelect.append(getEtiq(etiquette))
    print("question :",question,"reponses :", liste_reponses,"etiquettes :", liste_etiSelect,typeQ)
    return render_template('edit_question.html',titrePage= "edition question", etiquettes = liste_etiquettes_bdd, question=question, typeQ=typeQ, liste_reponses=liste_reponses , liste_etiSelect= liste_etiSelect)

@app.route('/ajouterLesEtudiants',methods=["GET", "POST"])
def ajouterLesEtudiants():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    if request.method=='POST':
    # get the uploaded file
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            # set the file path
            uploaded_file.save(file_path)

            parseCSV(file_path)

        #ajouterlesetudiants
        etu_li_aj= getInfosEtu(session['connecter'])
        connex = mysql.connector.connect(user='root', password='password',host='localhost', database='ProjScolaire')
        curseur = connex.cursor()
        sqlnb="SELECT count(*) FROM assocEP WHERE idU="+str(session['connecter'])
        curseur.execute(sqlnb)
        nb = curseur.fetchone()[0]
        connex.close()
        print(etu_li_aj)
        return  render_template("ajouterLesEtudiants.html",titrePage= "Mes élèves",ajoutée=True,data=etu_li_aj,nb=nb)
    else:
        return render_template("ajouterLesEtudiants.html",titrePage= "Mes élèves",ajoutée=False)

@app.route('/creerSequence',methods=["GET", "POST"])
def creerSequence():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    if request.method=='POST':
        if request.form.getlist("etiquette-choisi"):
            liste_question_choisi=[] # methode de recuperation a definir (probablement json depuis js)
            # on récupère les etiquettes
            etiquette_choisi=request.form.getlist("etiquette-choisi")
            print("vos etiquettes: ",etiquette_choisi)
            # la liste des identifiant de questions de cette etiquettes
            liste_idq=[]
            for eti in etiquette_choisi:
                liste_idq.append((getAssocQE((getidE(eti),))))
            print(liste_idq)
            # la liste des questions
            liste_question={}
            for idqs in liste_idq:
                for idq in idqs:
                    liste_question[getQuestion(idq)[0]]=(getReponsesdeQ(idq))
            print(liste_question)
            # un dictionnaire qui contient question reponses
            questions_reponses=liste_question
            return render_template("creerSequence.html",quest_rep=questions_reponses,choix=liste_question_choisi!=[],quest_choix=liste_question_choisi)
        elif request.form.get("question-choisi"):
            #generer l'identifiant de la sequence
            idS=generate_id()
            print(idS)
            # la liste des questions ordonée
            ordred = request.form.get("checkedquestions")
            list_ordered=ordred.split(',')
            print(list_ordered)
            titre=request.form.get("titre")
            Insert("sequence","(idS,titre,idU)",(idS,titre,session['connecter']))
            idq_question_choisi=[]
            for question in list_ordered:
                print("coucou",question)
                idq_question_choisi.append(getidQ(question,session['connecter']))
            for idQ in idq_question_choisi:
                Insert("assocQS","(idS,idQ,Ordre)",(idS,idQ,idq_question_choisi.index(idQ)+1))
            return render_template("creerSequence.html",etiquettes=get("etiquette","etiquettes") )
    else:
        hasnoques=getQuestions(session['connecter'])==[]
        return render_template("creerSequence.html",hasNoQues=hasnoques,etiquettes=get("etiquette","etiquettes"))

@app.route("/live",methods=["GET", "POST"])
def LiveExam():
    if not(session['role']):
        return redirect(url_for('acceuil'))
    if session['role'] == 'eleve' :
        idS= session['salon']
        return render_template('LiveEtu.html',idS=idS)
    else :
        sequences = getSequences(session['connecter'])
        if request.method == "POST" :
            session['salon']= request.form.get('choicSequence')
            salon = session['salon']
            print(session)
            questions = []
            for q in getidQdeidS(salon):
                questions.append([q,getQuestion(q[1])[0][0],getReponsesdeQAvecidR(q[1]),getTypeQ(q[1])])
            print(questions)
            return render_template('LiveProfSalon.html', NumeroSalon=salon, questions=questions)
        session['salon']= ""
        return render_template('LiveProf.html', sequences=sequences)

@app.route("/live/<idS>",methods=["GET", "POST"])
def LiveExamidS(idS):
    session['salon']=idS
    return render_template('LiveEtu.html', idS=idS)

##################### TEST SOCKET.IO

@socketio.on("NewSalon")
def NewSalon(NumSession):
    join_room(NumSession)
    emit("NewSalon", "Bien recu mon gars")

@socketio.on('JoinSalon')
def JoinSalon(NumSalon):
    if NumSalon in socketio.server.manager.rooms.get('/'):
        join_room(NumSalon)
        message = session['connecter']
        emit('JoinSalon', message, to=NumSalon)

    else:
        print(socketio.server.manager.rooms)
        message = 'La salle ' + NumSalon + ' n\'existe pas'
        emit('JoinSalon', message)


@socketio.on("QuestionAfficher")
def QuestionAfficher(idQ):
    room = session['salon']
    question = getQuestion(idQ)[0][0]
    reponses = [ getTypeQ(idQ),getReponsesforEtu(idQ)]
    emit("QuestionAfficher", [question,reponses] ,to = room)

@socketio.on("StopRep")
def StopRep(arg):
    room = session['salon']
    emit("StopRep","stop", to = room )

@socketio.on("envoieRep")
def envoieRep(data):
    Insert("ReponseEtu","(NumEtu,idS,idQ,reponse,Qseule)",(session["connecter"],data[0],getidQdeR(data[1][0][0]),str(data[1]),len(getidQdeidS(data[0]))==1 ))
    emit("RecuRep", data[1] , to = data[0] )

if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=8080,debug = True)
    socketio.run(app, host='0.0.0.0',port=8080,debug = True)


