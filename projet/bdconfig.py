# import mysql.connector


# connex = mysql.connector.connect(user='root', password='password',host='localhost', database='ProjScolaire')
# curseur = connex.cursor()

# curseur.execute("DROP TABLE IF EXISTS ReponseEtu")
# curseur.execute("DROP TABLE IF EXISTS ExamLive")
# curseur.execute("DROP TABLE IF EXISTS assocQS")
# curseur.execute("DROP TABLE IF EXISTS sequence")
# curseur.execute("DROP TABLE IF EXISTS assocEP")
# curseur.execute("DROP TABLE IF EXISTS Etudiants")
# curseur.execute("DROP TABLE IF EXISTS assocQE")
# curseur.execute("DROP TABLE IF EXISTS etiquettes")
# curseur.execute("DROP TABLE IF EXISTS reponses")
# curseur.execute("DROP TABLE IF EXISTS questions")
# curseur.execute("DROP TABLE IF EXISTS utilisateurs")
# curseur.execute("DROP TABLE IF EXISTS assocQliveSalon")

# curseur.execute("""CREATE TABLE utilisateurs (
#     idU INT PRIMARY KEY AUTO_INCREMENT,
#     nom VARCHAR(255),
#     prenom VARCHAR(255),
#     mail VARCHAR(255),
#     `PASSWORD` VARCHAR(255))
#     """)


# curseur.execute("""CREATE TABLE questions (
#     idQ INT PRIMARY KEY AUTO_INCREMENT,
#     question TEXT,
#     type VARCHAR(20),
#     idU INT,
#     FOREIGN KEY (idU) REFERENCES utilisateurs(idU) ON DELETE CASCADE)
#     """)


# curseur.execute("""CREATE TABLE reponses (
#     idR INT PRIMARY KEY AUTO_INCREMENT,
#     reponse TEXT,
#     valeur BOOLEAN,
#     idQ INT,
#     FOREIGN KEY(idQ) REFERENCES questions(idQ) ON DELETE CASCADE)
#     """)


# curseur.execute("""CREATE TABLE etiquettes (
#     idE INT PRIMARY KEY AUTO_INCREMENT,
#     etiquette VARCHAR(255))
#     """)


# curseur.execute("""CREATE TABLE assocQE (
#     idE INT,
#     idQ INT,
#     PRIMARY KEY(idE,idQ),
#     FOREIGN KEY (idQ) REFERENCES questions(idQ) ON DELETE CASCADE,
#     FOREIGN KEY (idE) REFERENCES etiquettes(idE) ON DELETE CASCADE)
#     """)


# curseur.execute("""CREATE TABLE Etudiants (
#     NumEtu INT PRIMARY KEY,
#     Nom VARCHAR(255),
#     Prenom VARCHAR(255),
#     `PASSWORD` VARCHAR(255))
#     """)


# curseur.execute("""CREATE TABLE assocEP (
#     idU INT,
#     NumEtu INT,
#     PRIMARY KEY(NumEtu,idU),
#     FOREIGN KEY (idU) REFERENCES utilisateurs(idU) ON DELETE CASCADE,
#     FOREIGN KEY (NumEtu) REFERENCES Etudiants(NumEtu) ON DELETE CASCADE)
#     """)


# curseur.execute("""CREATE TABLE sequence (
#     idS INT AUTO_INCREMENT PRIMARY KEY,
#     titre VARCHAR(255))
#     """)

# curseur.execute("""CREATE TABLE assocQS (
#     idS INT,
#     idQ INT,
#     ordre INT,
#     PRIMARY KEY(idS,idQ),
#     FOREIGN KEY (idS) REFERENCES sequence(idS) ON DELETE CASCADE,
#     FOREIGN KEY (idQ) REFERENCES questions(idQ) ON DELETE CASCADE)
#     """)

# curseur.execute("""CREATE TABLE ExamLive (
#     NumSession CHAR(8),
#     idS INT,
#     date DATETIME DEFAULT NOW(),
#     NbParticipants INT,
#     PRIMARY KEY(NumSession,date),
#     FOREIGN KEY (idS) REFERENCES sequence(idS) ON DELETE CASCADE)
#     """)


# curseur.execute("""CREATE TABLE ReponseEtu (
#     NumEtu INT,
#     NumSession CHAR(8),
#     idQ INT,
#     reponse TEXT,
#     date DATETIME DEFAULT NOW(),
#     Qseule BOOLEAN,
#     PRIMARY KEY(NumEtu,NumSession,idQ),
#     FOREIGN KEY (NumSession) REFERENCES ExamLive(NumSession) ON DELETE CASCADE,
#     FOREIGN KEY (idQ) REFERENCES questions(idQ) ON DELETE CASCADE,
#     FOREIGN KEY (NumEtu) REFERENCES Etudiants(NumEtu) ON DELETE CASCADE
# )""")

# curseur.execute("""CREATE TABLE assocQliveSalon (
#     NumSalon char(8),
#     idQ INT,
#     PRIMARY KEY(NumSalon)
# )""")

# connex.close()

