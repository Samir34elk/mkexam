# Module de connexion à la base de données
import mysql.connector

# Module de cryptage pour les mots de passes
import bcrypt

# Modules python pour la génération d'identifiant de session 
import random,string

#importation liée au traitement des fichiers csv
import os
import csv

#importation socket.io
from flask_socketio import SocketIO, join_room, emit,leave_room,close_room

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
                rowli = row[0].split(";")
                sqlE = "INSERT INTO Etudiants (NumEtu,Nom,Prenom,PASSWORD) VALUES (%s,%s,%s,%s)"
                sqlU="INSERT INTO assocEP (idU,NumEtu) VALUES (%s,%s)"
                valueU=(session['connecter'],rowli[0])
                code = rowli[0].encode('utf-8')
                code = bcrypt.hashpw(code,bcrypt.gensalt(12))
                valueE = (rowli[0],rowli[1],rowli[2],code)
                if not(Inscrit(rowli[0])):
                    Execute(sqlE,valueE)
                if session['connecter'] not in getAssocEP(rowli[0]):
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
def getidS(titre):
    return Execute("SELECT idS FROM sequence WHERE titre = %s", (titre,))[0][0]

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
    return Execute("SELECT valeur FROM reponses WHERE idR = %s ",(idR,))
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
def getEtiquettes(idU):
    liste = Execute("SELECT etiquette FROM etiquettes WHERE idE in (SELECT idE FROM assocQE WHERE idQ in (SELECT idQ FROM questions WHERE idU = %s ))", (idU,))
    resultat =[]
    for eti in liste : 
        resultat.append(eti[0])
    return resultat

#infosSeq
def getTitre(NumSession):
    return Execute("SELECT sequence.titre FROM sequence INNER JOIN ExamLive ON  sequence.idS = ExamLive.idS  WHERE ExamLive.NumSession = %s ", (NumSession,))[0][0]
def getSequences(idU):
    return Execute("SELECT idS,titre FROM sequence WHERE idS in (SELECT idS FROM assocQS WHERE idQ in (SELECT idQ FROM questions WHERE idU = %s ))",(idU,))
def getidQdeidS(idS):
    return Execute("SELECT ordre,idQ FROM assocQS WHERE idS = %s ORDER BY ordre ASC",(idS,))
def getinfoSession(idU):
    return Execute("SELECT sequence.titre,DATE_FORMAT(ExamLive.date,'%d-%m-%Y'),ExamLive.NbParticipants FROM sequence INNER JOIN ExamLive ON sequence.idS = ExamLive.idS WHERE sequence.idS IN (SELECT idS FROM assocQS WHERE idQ IN ( SELECT idQ FROM questions WHERE idU = %s )) ORDER BY date ASC  ",(idU,))
def getinfoSessionPeriode(idU,dateDebut,dateFin):
    return Execute("SELECT sequence.titre,DATE_FORMAT(ExamLive.date,'%d-%m-%Y'),ExamLive.NbParticipants FROM sequence INNER JOIN ExamLive ON sequence.idS = ExamLive.idS WHERE sequence.idS IN (SELECT idS FROM assocQS WHERE idQ IN ( SELECT idQ FROM questions WHERE idU = %s )) AND date >= %s AND date <= %s  ORDER BY date ASC  ",(idU, dateDebut,dateFin+"-23-59-59"))
def getTypeSeq(NumSession):
    if len(Execute("SELECT * FROM assocQS WHERE idS IN (SELECT idS FROM ExamLive WHERE NumSession = %s )", (NumSession,))) > 1 :
        return 1
    return 0

def getQliveSalon(NumSalon):
    return Execute("SELECT idQ FROM assocQliveSalon WHERE NumSalon = %s",(NumSalon,))
def updateQliveSalon(idQ,NumSalon):
    return Execute("UPDATE assocQliveSalon SET idQ = %s WHERE NumSalon = %s",(idQ,NumSalon))

#infosRepEtu
def getRepEtu(NumEtu):
    listeSession = Execute("SELECT DISTINCT NumSession, DATE_FORMAT(date,'%d-%m-%Y'),Qseule FROM ReponseEtu WHERE NumEtu = %s ORDER BY  DATE_FORMAT(date,'%d-%m-%Y') ASC ", (NumEtu,))
    maliste = []
    for session in listeSession:
        maliste.append([getTitre(session[0]),getReussiteEtuSession(session[0],NumEtu),session[1],session[2]])
    return maliste
def getRepEtuPeriode(NumEtu,dateDebut,dateFin):
    listeSession = Execute("SELECT DISTINCT NumSession, DATE_FORMAT(date,'%d-%m-%Y'),Qseule FROM ReponseEtu WHERE NumEtu = %s AND date >= %s AND date <= %s ORDER BY  DATE_FORMAT(date,'%d-%m-%Y') ASC  ", (NumEtu,dateDebut,dateFin+"23-59-59"))
    maliste = []
    for session in listeSession:
        maliste.append([getTitre(session[0]),getReussiteEtuSession(session[0],NumEtu),session[1],session[2]])
    return maliste
def getRep(idU):
    listeSession = Execute("SELECT NumSession, DATE_FORMAT(date,'%d-%m-%Y') FROM ExamLive WHERE idS IN (SELECT sequence.idS FROM sequence INNER JOIN assocQS ON sequence.idS = assocQS.idS WHERE assocQS.idQ IN (SELECT idQ FROM questions WHERE idU = %s )) ORDER BY  DATE_FORMAT(date,'%d-%m-%Y') ASC ", (idU,))
    maliste = []
    for session in listeSession:
        maliste.append([getTitre(session[0]),getReussiteSession(session[0]),session[1],getTypeSeq(session[0])])
    return maliste
def getRepPeriode(idU,dateDebut,dateFin):
    listeSession = Execute("SELECT NumSession, DATE_FORMAT(date,'%d-%m-%Y') FROM ExamLive WHERE idS IN (SELECT sequence.idS FROM sequence INNER JOIN assocQS ON sequence.idS = assocQS.idS WHERE assocQS.idQ IN (SELECT idQ FROM questions WHERE idU = %s ))  AND date >= %s AND date <= %s ORDER BY  DATE_FORMAT(date,'%d-%m-%Y') ASC ", (idU,dateDebut,dateFin+"-23-59-59"))
    maliste = []
    for session in listeSession:
        maliste.append([getTitre(session[0]),getReussiteSession(session[0]),session[1],getTypeSeq(session[0])])
    return maliste

def getReussiteSession(NumSession):
    listeRep = Execute("SELECT idQ,reponse FROM ReponseEtu WHERE NumSession = %s",(NumSession,))
    RepJuste = 0
    for GroupeRep in listeRep :
        GrpRep = eval(GroupeRep[1])
        print(getTypeQ(GroupeRep[0])=="qcm")
        if getTypeQ(GroupeRep[0])=="qcm":
            valreponse=1
            for rep in GrpRep:
                if int(rep[1])!=(getValR(rep[0])[0][0]):
                    valreponse=0
            RepJuste+=valreponse
        else:
            if float(GrpRep[0][1])==float(getReponse(GrpRep[0][0])):
                        RepJuste+=1
    if len(listeRep) == 0 : 
        return 'NonRepondu'
    return (RepJuste/len(listeRep)*100)

def getReussiteEtuSession(NumSession, NumEtu):
    listeRep = Execute("SELECT idQ,reponse FROM ReponseEtu WHERE NumSession = %s AND NumEtu = %s",(NumSession,NumEtu))
    RepJuste = 0.00
    print(listeRep)
    for GroupeRep in listeRep :
        GrpRep = eval(GroupeRep[1])

        print(getTypeQ(GroupeRep[0])=="qcm")
        if getTypeQ(GroupeRep[0])=="qcm":
            valreponse=1
            for rep in GrpRep:
                print("ici",type(rep[1]),type(getValR(rep[0])[0][0]))
                if int(rep[1])!=(getValR(rep[0])[0][0]):
                    valreponse=0
            RepJuste+=valreponse
        else:
            print( GrpRep[0][1],float(getReponse(GrpRep[0][0])))
            print( GrpRep[0][1]==float(getReponse(GrpRep[0][0])))
            if float(GrpRep[0][1])==float(getReponse(GrpRep[0][0])):
                        RepJuste+=1
    print(RepJuste)
    return (RepJuste/len(listeRep)*100)

# UPDATE
def modifier_mdp_prof(idU,NewMdp):
    Execute("UPDATE utilisateurs SET PASSWORD = %s WHERE idU = %s", (NewMdp,idU))
def modifier_mdp_etu(NumEtu,NewMdp):
    Execute("UPDATE etudiants SET PASSWORD = %s WHERE NumEtu = %s", (NewMdp,NumEtu))
def modifier_nbParticipants(NumSession):
    Execute("UPDATE ExamLive SET NbParticipants = NbParticipants + 1 WHERE NumSession = %s ",(NumSession,))
# DELETE
def supprimer(table,cond,val):
    requete = f"DELETE FROM {table} WHERE {cond} = %s "
    Execute(requete,val)

#    ROUTES

# Route racine contenant la page d'acceuil
@app.route('/',methods=['POST','GET'] )
def acceuil():
    return render_template('index.html', titrePage = 'Bienvenue')

# Routes vers la page d'inscription
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

@app.route('/signup/<mail>',methods=['POST','GET'])
def sign(mail):
    return render_template('signup.html',titrePage= "Inscription", mail=mail , mailInconnu = 1 )

# Routes vers la page de connexion
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

@app.route('/login/<mail>',methods=['POST','GET'])
def log(mail):
    return render_template('login.html',titrePage= "Inscription", login=mail)

# route vers modif mdp
@app.route("/changerMdpEtu",methods=['POST','GET'])
def changerMdpEtu():
    idU=session['connecter']
    if session['role']=='eleve' :
        Identifiant=idU
        Prenom = getPrenomEtu(idU)
        Nom = getNomEtu(idU)
    else :
        Identifiant=getMailU(idU)
        Prenom = getPrenomU(idU)
        Nom = getNomU(idU)
    if request.method=='POST':
        anMdp=request.form.get("anmdp")
        nvMdp=request.form.get("nvmdp")
        nvMdpCnf=request.form.get("nvmdpcnf")
        if codeCorrect(Identifiant,anMdp) and nvMdpCnf==nvMdp:
            nvMdp = nvMdp.encode('utf-8')
            nvMdp = bcrypt.hashpw(nvMdp,bcrypt.gensalt(12))
            if session['role'] == 'eleve' :
                modifier_mdp_etu(idU,nvMdp)
            else : 
                modifier_mdp_prof(idU,nvMdp)
            return redirect(url_for('acceuil'))
        return render_template("changerMdpEtu.html", Identifiant=Identifiant, Prenom=Prenom,Nom=Nom, MsgErreur = "Vous n'avez pas entré le bon Mot de passe")
    return render_template("changerMdpEtu.html", Identifiant=Identifiant, Prenom=Prenom,Nom=Nom )

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

# Route vers la page contenant les questions et permetant la création d'examen écrit et live
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
    if  request.method == 'POST' and request.form.get("ExamLive") :
        listeidq = request.form.get('listeQchoisi')
        listeidq = list(filter(None,listeidq.split(',')))
        listeidq = [int(num) for num in listeidq]
        intitule= request.form.get('titre')
        Insert("sequence","(titre)",(intitule,))
        idS = getidS(intitule)
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
        return render_template('questions.html',titrePage= "Mes Questions", questions=questions_idU, idU=idU, etiquettes = getEtiquettes(idU), liste_reponses=liste_reponses, liste_assocQE=liste_assocQE)

# Route vers la page d'ajout de question
@app.route('/ajout_question',methods=['POST','GET'])
def ajout_question():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    liste_reponses = []
    liste_etiSelect = []
    idUtil = session['connecter']
    liste_etiquettes_bdd=getEtiquettes(session['connecter'])
    if request.method == 'POST': 
        question = request.form.get('question')
        typeQ = request.form.get('typeQ')
        if (question,typeQ) not in getInfosQ(idUtil) :
            Insert("questions","(question,type,idU)",(question,typeQ,idUtil))
            for key, val in request.form.items():
                if key.startswith("item"):
                    liste_reponses.append((key,val))
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
        return render_template('ajout_question.html',titrePage= "Nouvelle question", etiquettes = getEtiquettes(session['connecter']) )

# modification de ajout_question pour en faire modif_question comme etant un ajout_question prérempli
@app.route('/edit_question',methods=['POST','GET'])
def edit_question():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    liste_etiSelect = []
    liste_etiquettes_bdd=getEtiquettes(session['connecter'])
    idU = session['connecter']
    idQ = session['QuestionAmodifier']
    typeQ= getTypeQ(idQ)
    question = getQuestion(idQ)[0][0]
    liste_reponses = getReponsesdeQ(idQ)
    liste_etiSelect = []
    if request.method == 'POST': 
        liste_reponses = []
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
                for i in range(0,len(liste_reponses)-1,2) :
                    if (liste_reponses[i+1][1],liste_reponses[i][1]) not in getReponsesdeQ(getidQ(question,idU)) : 
                        Insert("reponses","(reponse,valeur,idQ)",(liste_reponses[i+1][1],liste_reponses[i][1], getidQ(question,idU)))
            for i in range(len(liste_etiSelect)):
                if liste_etiSelect[i][1] not in liste_etiquettes_bdd :
                    Insert("etiquettes","(etiquette)",(liste_etiSelect[i][1],))
                Insert("assocQE","(idE,idQ)",(getidE(liste_etiSelect[i][1]),getidQ(question,session['connecter'])))
        return redirect(url_for("questions"))
    for etiquette in getAssocEQ(idQ) :
        liste_etiSelect.append(getEtiq(etiquette))
    return render_template('edit_question.html',titrePage= "edition question", etiquettes = liste_etiquettes_bdd, question=question, typeQ=typeQ, liste_reponses=liste_reponses , liste_etiSelect= liste_etiSelect)

@app.route('/ajouterLesEtudiants',methods=["GET", "POST"])
def ajouterLesEtudiants():
    if session['role'] == 'eleve' :
        return redirect(url_for('acceuil'))
    etu_li_aj= getInfosEtu(session['connecter'])
    if request.method=='POST':
    # get the uploaded file
        uploaded_file = request.files['file']
        if uploaded_file.filename != '':
            file_path = os.path.join(app.config['UPLOAD_FOLDER'], uploaded_file.filename)
            # set the file path
            uploaded_file.save(file_path)

            parseCSV(file_path)

        #ajouterlesetudiants
        connex = mysql.connector.connect(user='root', password='password',host='localhost', database='ProjScolaire')
        curseur = connex.cursor()
        sqlnb="SELECT count(*) FROM assocEP WHERE idU="+str(session['connecter'])
        curseur.execute(sqlnb)
        nb = curseur.fetchone()[0]
        connex.close()
        return  render_template("ajouterLesEtudiants.html",titrePage= "Mes élèves", data=etu_li_aj, nb=len(etu_li_aj))
    else:
        return render_template("ajouterLesEtudiants.html",titrePage= "Mes élèves", data=etu_li_aj, nb=len(etu_li_aj))

@app.route("/live",methods=["GET", "POST"])
def LiveExam():
    if not(session['role']):
        return redirect(url_for('acceuil'))
    if session['role'] == 'eleve' :
        if 'salon' in session :
            idS= session['salon']
        else :
            idS=""
        return render_template('LiveEtu.html',idS=idS)
    else :
        sequences = getSequences(session['connecter'])
        if request.method == "POST" :
            NumSession = generate_id()
            idS = request.form.get('choicSequence')
            Insert("ExamLive","(NumSession,idS,NbParticipants)",(NumSession,idS,0))
            session['salon']= NumSession
            salon = session['salon']
            questions = []
            for q in getidQdeidS(idS):
                questions.append([q,getQuestion(q[1])[0][0],getReponsesdeQAvecidR(q[1]),getTypeQ(q[1])])
            return render_template('LiveProfSalon.html', NumeroSalon=salon, questions=questions)
        session['salon']= ""
        return render_template('LiveProf.html', sequences=sequences)

@app.route("/live/<idS>",methods=["GET", "POST"])
def LiveExamidS(idS):
    session['salon']=idS
    return render_template('LiveEtu.html', idS=idS)

@app.route("/quitterRoom/<sid>")
def quitterRoom(sid):
    #leave_room(session['salon'], sid)
    session['salon'] = ""
    return redirect(url_for('acceuil'))

@app.route("/stats",methods=['POST','GET'])
def stats():
    if request.method == "POST":
        dateDebut = request.form.get('dateDebut')
        dateFin = request.form.get('dateFin')
        liste = getinfoSessionPeriode(session['connecter'],dateDebut,dateFin)
        return render_template('stats.html', liste = liste, dateDebut=dateDebut, dateFin=dateFin )
    else :
        liste = getinfoSession(session['connecter'])
    return render_template('stats.html', liste = liste )

@app.route("/statsResultats",methods=['POST','GET'])
def statsResultats():
    idU=session['connecter']
    if request.method == "POST":
        NumEtu = request.form.get('NumEtu')
        dateDebut = request.form.get('dateDebut')
        dateFin = request.form.get('dateFin')
        if NumEtu == "" :
            if dateDebut == "" or dateFin=="" :
                liste = getRep(idU)
            else :
                liste = getRepPeriode(idU,dateDebut,dateFin)
        else:
            if dateDebut == "" or dateFin=="" :
                liste = getRepEtu(NumEtu)
            else :
                liste = getRepEtuPeriode(NumEtu,dateDebut,dateFin)
        return render_template('stats1.html',listeEtu=getInfosEtu(idU), liste = liste, dateDebut=dateDebut, dateFin=dateFin )
    else :
        liste = getRep(session['connecter'])
    return render_template('stats1.html',listeEtu=getInfosEtu(idU), liste = liste )

##################### SOCKET.IO

@socketio.on("NewSalon")
def NewSalon(NumSession):
    join_room(NumSession)
    emit("NewSalon", "Bien recu mon gars")

@socketio.on('JoinSalon')
def JoinSalon(NumSalon):
    if NumSalon in socketio.server.manager.rooms.get('/'):
        join_room(NumSalon)
        message = session['connecter']
        modifier_nbParticipants(NumSalon)
        emit('JoinSalon', message, to=NumSalon)
        idQ = getQliveSalon(NumSalon)[0][0]
        print(idQ)
        question = getQuestion(idQ)[0][0]
        if getTypeQ(idQ) == "qcm" :
            reponses = [ getTypeQ(idQ),getReponsesforEtu(idQ)]
        else :
            reponses = [ getTypeQ(idQ),[getReponsesforEtu(idQ)[0][0]]]
        emit("QuestionAfficher", [question,reponses])
    else:
        message = 'La salle n\'existe pas'
        emit('JoinSalon', message)

@socketio.on("QuestionAfficher")
def QuestionAfficher(idQ):
    room = session['salon']
    if getQliveSalon(room) == []:
        Insert("assocQliveSalon","(NumSalon,idQ)",(room,idQ))
    else:
        updateQliveSalon(idQ,room)
    question = getQuestion(idQ)[0][0]
    if getTypeQ(idQ) == "qcm" :
        reponses = [ getTypeQ(idQ),getReponsesforEtu(idQ)]
    else :
        reponses = [ getTypeQ(idQ),[getReponsesforEtu(idQ)[0][0]]]
    emit("QuestionAfficher", [question,reponses] ,to = room)

@socketio.on("StopRep")
def StopRep(arg):
    room = session['salon']
    emit("StopRep","stop", to = room )

@socketio.on("affichageCorrection")
def affichageCorrection(listeR):
    liste=[]
    print(listeR)
    if getTypeQ(getidQdeR(listeR[0][0])) == "qcm":
        liste = listeR
    else:
        liste = getValR(listeR[0][0])
    emit("affichageCorrection",liste,to = session['salon'])

@socketio.on("envoieRep")
def envoieRep(data):
    Insert("ReponseEtu","(NumEtu,NumSession,idQ,reponse,Qseule)",(session["connecter"],data[0],getidQdeR(data[1][0][0]),str(data[1]),len(getidQdeidS(data[0]))==1 ))
    emit("RecuRep", data[1] , to = data[0] )

@socketio.on("quitter")
def quitter(arg):
    room = session['salon']
    if getQliveSalon(room) != []:
        supprimer("assocQliveSalon","(NumSalon)",(session['salon'],))
    emit("quitter","bizarre", to = session['salon'])
    leave_room(session['salon'])


if __name__ == '__main__':
    # app.run(host='0.0.0.0',port=8080,debug = True)
    socketio.run(app, host='localhost',port=8080,debug = True)
