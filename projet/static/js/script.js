
/************* FONCTIONS MES_QUESTIONS ****************/


function etiquetteselect(){
    valeur = document.getElementById("listeEtiquette").value;
    html = '<li  class="list-inline-item"><input type="hidden"  value="'+valeur+'">'+valeur+'<button type="button" onClick="supprimeEti1(this)"></li>'
    document.getElementById("etiquetteSelectionner").innerHTML += html;
}

function incrEtiquettesSelect1(){
    var increments = document.getElementById("etiquetteSelectionner");
    var li = increments.getElementsByTagName("input");
    var l2 = increments.getElementsByTagName("button");
    var l3 = increments.getElementsByTagName("li");
    listeEti =[]
    for (i=0;i<li.length;i++) {li[i].setAttribute("name", "etiquetteSelect".concat(i+1));l2[i].setAttribute("name", "etiquetteSelect".concat(i+1));l3[i].setAttribute("name", "etiquetteSelect".concat(i+1));listeEti.push(li[i].value)};
    cacherLignes(listeEti);
}

function cacherLignes(liste){
    table = document.getElementById("tableQ").getElementsByTagName("tr")
    if(liste.length === 0 ){
        for (j=1;j<table.length;j++){
            table[j].hidden = false;
        }
    } else {
            for (j=1;j<table.length;j++){
        table[j].hidden = true;
        for (i=0;i<liste.length;i++){
        if ( table[j].cells[3].innerText.includes(liste[i])){
            table[j].hidden = false;
        }
    }
    }
    }

}

function supprimeEti1(valeur){
    nomli = valeur.name;
    li = document.getElementById("etiquetteSelectionner").getElementsByTagName("li");
    for (i=0;i<li.length;i++) {if (li[i].attributes.name.value == nomli ){
        li[i].remove();
    };}
    incrEtiquettesSelect1();
}

/* fonction chargée à la sélection/déselection d'une checkbox dans la page question qui permet le stockage des questions sélectionnées */
function SelectionQ(checkbox){
    idQ = checkbox.value;
    var oldValue = document.getElementById("listeQchoisi").value;
    var newValue = "";
    var tableQselect = document.getElementById("tableQselect")
    let ligne = tableQselect.insertRow(-1);
    if(checkbox.checked){
        if(oldValue.indexOf(idQ + ",") == -1 && oldValue.indexOf("," + idQ) == -1 && oldValue.indexOf(idQ) != 0) {
            newValue = oldValue + idQ + ",";
            document.getElementById("listeQchoisi").value = newValue;
            afficheLigneSelect(newValue);
        }
    }else{
        newValue = oldValue.replace(idQ+",", "");
        document.getElementById("listeQchoisi").value = newValue;
        afficheLigneSelect(newValue);
    }
}

/*fonction qui permet de mettre les question dans la liste des questions sélectionnées dans la page questions */
function afficheLigneSelect(listeidQselect){
    listeidQselect = listeidQselect.split(",").map(Number);
    listeidQselect = listeidQselect.slice(0,-1);
    table = document.getElementById("tableQ").getElementsByTagName("tr")
    tableQselect = document.getElementById("tableQselect")
    while (tableQselect.rows.length > 1) {
        tableQselect.deleteRow(-1);
    }
    for(i=0; i<listeidQselect.length;i++){
        for (j=1;j<table.length;j++){
            if (listeidQselect[i] === parseInt(table[j].cells[0].firstElementChild.value)){
                let ligne = tableQselect.insertRow(-1);
                let c1 = ligne.insertCell(0);
                let c2 = ligne.insertCell(1);
                let c3 = ligne.insertCell(2);
                let c4 = ligne.insertCell(3);
                c1.innerHTML = "<input type='button' name='"+listeidQselect[i]+"' onclick=(decoche(this.name)) value='X'></input>"
                c2.innerHTML = table[j].cells[1].innerHTML
                c3.innerHTML = table[j].cells[2].innerHTML
                c4.innerHTML = table[j].cells[3].innerHTML
            }
        }
    }
}

/*fonction qui permet de désélectionner une question depuis la liste des questions sélectionnées dans la page questions */
function decoche(idQ){
    table = document.getElementById("tableQ").getElementsByTagName("tr");
    for (j=1;j<table.length;j++){
        if (idQ === table[j].cells[0].firstElementChild.value){
            table[j].cells[0].firstElementChild.checked = false;
            SelectionQ(table[j].cells[0].firstElementChild);
        }
    }
}

function transformeQ(classe){
    let avant = document.getElementsByClassName(classe)[0].textContent;
    const renderer = new marked.Renderer();
    renderer.code = function (code, language) {
        if (language.match(/^mermaid/)) {
        return '<pre class="mermaid">' + code + '</pre>';
        } else {
        const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
        return `<pre><code class="hljs ${validLanguage}">${hljs.highlight(code, { language: validLanguage }).value}</code></pre>`;
        }
    };
    let html = marked.parse(avant, { renderer });
    document.getElementsByClassName(classe)[0].innerHTML = html;
}

/***************  FONCTIONS AJOUT/EDIT QUESTION **************************/

// Fonction qui permet de modifier l'affichage de l'ajout question en fonction du type de question 
function TypeQ(){
    valeur = document.getElementById("typeQ").value;
    html = '<input type="TEXT" hidden name="typeQ" value="'+valeur+'">';
    document.getElementById("typeQuest").innerHTML = html;
    if(valeur=="Num"){
        document.getElementById("listeReponse").hidden = true;
        document.getElementById("BtnAjtR").hidden = true;
        document.getElementById("listeReponse").innerHTML = "";
        textarea = document.getElementById('reponse')
        input = document.createElement('input')
        input.setAttribute('type','number')
        input.step = 0.01
        input.id = textarea.id;
        input.name = textarea.name;
        textarea.replaceWith(input)
    } else if (valeur=="qcm"){
        document.getElementById("listeReponse").hidden = false;
        document.getElementById("BtnAjtR").hidden = false;
        input = document.getElementById('reponse')
        textarea = document.createElement('textarea')
        textarea.id = input.id;
        textarea.name = input.name;
        textarea.className = "form-control"
        textarea.setAttribute('oninput',"Preview();")
        input.replaceWith(textarea)
    }
}

// fonction ajoute une reponse à la liste des reponses ainsi qu'une checkbox pour choisir sa valeur
// la reponse reste modifiable car on crée en realité une liste de textarea
function choix(){
    let html=""
    if (document.getElementById("reponse").value != ""){
    valeur=document.getElementById("reponse").value
    html +='<li><select  id="valeur"> <option value="0" <?php if($_POST["valeur"]=="0") ?> Faux </option> <option value="1" <?phpif($_POST["valeur"]=="1")?> Vrai </option> </select><textarea>'+valeur+'</textarea><button type="button" onClick="supprimeRep(this)"><img src="/static/img/logo-poubelle.ico" alt=""></button></li>' }
    document.getElementById("listeReponse").innerHTML += html
    document.getElementById("reponse").value=""
}

// fonction ajoute une etiquette dans la datalist 
function choixE(){
    let html=""
    var li= (document.getElementById("listeEtiquette").getElementsByTagName("option"))
    if (document.getElementById("SaisieEtiquette").value != "" && pasdans(document.getElementById("SaisieEtiquette").value,li)){
    html+="<option>"+document.getElementById("SaisieEtiquette").value+"</option>"}
    document.getElementById("listeEtiquette").innerHTML += html
}

// fonction qui verifie qu'un élement n'est pas dans une liste 
function pasdans(element,liste){
    valeur = true
    for (i=0;i<liste.length;i++){
        if (element==liste[i].value) valeur=false ;
    }
    return valeur;
    
}

// fonction qui permet le rendu de saisie en direct 
function Preview(){
    nouvelleQ = document.getElementById('question').value
    nouvelleR = document.getElementById('reponse').value
    document.getElementById('preview').children[1].innerHTML = nouvelleQ;
    document.getElementById('preview').children[3].innerHTML = nouvelleR;
    transforme(document.getElementById('previewR'));
    transforme(document.getElementById('previewQ'));
    mermaid.init();
    MathJax.typeset();
}

// fonction qui prend du text et fait le rendu markdown combiné à mermaid, highlights puis mathJax
function transforme(element){
    let avant =element.textContent;
    const renderer = new marked.Renderer();
    renderer.code = function (code, language) {
        if (language.match(/^mermaid/)) {
        return '<pre class="mermaid">' + code + '</pre>';
        } else {
        const validLanguage = hljs.getLanguage(language) ? language : 'plaintext';
        return `<pre><code class="hljs ${validLanguage}">${hljs.highlight(code, { language: validLanguage }).value}</code></pre>`;
        }
    };
    let html = marked.parse(avant, { renderer });
    element.innerHTML = html;
    MathJax.typeset();
    mermaid.init();
}

// fonction permet de distinguer chaque reponse et sa valeur
// ca peut etre complexe a comprendre mais c'est juste pour inserer les reponses et leurs valeurs correctement dans la bdd
function incrRep(){
    var increments = document.getElementById("listeReponse");
    var li = increments.getElementsByTagName("textarea");
    var lii = increments.getElementsByTagName("select");
    var l2 = increments.getElementsByTagName("button");
    var l3 = increments.getElementsByTagName("li");
    for (i=0;i<li.length;i++) {li[i].setAttribute("name", "item".concat(2*i+1));lii[i].setAttribute("name","item".concat(2*i+2));l2[i].setAttribute("name", "item".concat(2*i+1));l3[i].setAttribute("name", "item".concat(2*i+1))}
}

function etiqselect(){
    let html=""
    var li= (document.getElementById("EtiquetteSelectionner").getElementsByTagName("li"))
    if (document.getElementById("SaisieEtiquette").value != "" && pasdans1(document.getElementById("SaisieEtiquette").value,li)){
        html+='<li><input type="hidden"  value="'+document.getElementById("SaisieEtiquette").value+'">'+document.getElementById("SaisieEtiquette").value+'<button type="button" onClick="supprimeEti(this)"><img src="/static/img/logo-poubelle.ico" alt=""></li>'}
        
    document.getElementById("EtiquetteSelectionner").innerHTML += html
}

// fonction permet de donner un attribut name aux etiquettes 
// pour ensuite les inserer dans la bdd avec la fonction qui est sur projet.py
function incrEtiquettes(){
    var increments = document.getElementById("listeEtiquette");
    var li = increments.getElementsByTagName("option");
    for (i=0;i<li.length;i++) {li[i].setAttribute("name", "etiquette".concat(i+1));}
}

function pasdans1(element,liste){
    valeur = true
    for (i=0;i<liste.length;i++){
        if (element==liste[i].textContent) valeur=false ;
    }
    return valeur;
    
}

function incrEtiquettesSelect(){
    var increments = document.getElementById("EtiquetteSelectionner");
    var li = increments.getElementsByTagName("input");
    var l2 = increments.getElementsByTagName("button");
    var l3 = increments.getElementsByTagName("li");
    for (i=0;i<li.length;i++) {li[i].setAttribute("name", "etiquetteSelect".concat(i+1));l2[i].setAttribute("name", "etiquetteSelect".concat(i+1));l3[i].setAttribute("name", "etiquetteSelect".concat(i+1))}
}

function supprimeEti(valeur){
    nomli = valeur.name;
    li = document.getElementById("EtiquetteSelectionner").getElementsByTagName("li");
    for (i=0;i<li.length;i++) {if (li[i].attributes.name.value == nomli ){
        li[i].remove();
    };}
}

function supprimeRep(valeur){
    nomli = valeur.name;
    li = document.getElementById("listeReponse").getElementsByTagName("li");
    for (i=0;i<li.length;i++) {if (li[i].attributes.name.value == nomli ){
        li[i].remove();
    };}
}

Nbconnecter = 0;
NbRepRecu = 0;
RepRecu = [];
EtuConnecter = []
typeQ = ""

function creeSalon(){
    socket = io.connect();
    document.addEventListener("DOMContentLoaded", function(event) {
        socket.emit("NewSalon", document.getElementById('idS').innerHTML);
    });
    socket.on("JoinSalon", (arg) => {
        if (!(EtuConnecter.includes(arg))){
            Nbconnecter++ ;
            document.getElementById("NbConnecter").textContent = Nbconnecter;
            EtuConnecter.push(arg)
        }
    });
    socket.on("RecuRep", (reponses) => {
        NbRepRecu++;
        document.getElementById("NbReponses").textContent = NbRepRecu;
        DivRep = document.getElementById('Rafficher')
        listeRep = DivRep.children
        if(listeRep.length == 0 ){
            typeQ = "Num"
        }
        if(typeQ === "Num" && !(RepRecu.some(sousliste => sousliste.includes(reponses[0][1])))){
            RepRecu.push([reponses[0][1],0]);
            nouveauli = document.createElement('div')
            nouveauli.innerHTML = `<li id="`+reponses[0][1]+`
            " name="`+reponses[0][0] +`" class="list-group-item" >` 
            + reponses[0][1] +
            `<div id="NbVote" hidden>
            <div class="progress progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" style="width: 0%"></div>0%</div>
            </li>`;
            DivRep.appendChild(nouveauli);
        }
        for(i=0;i<reponses.length;i++){
            console.log[reponses[i]]
            for(j=0;j<RepRecu.length;j++){
                if(reponses[i][0]===RepRecu[j][0] && parseInt(reponses[i][1])===1 && typeQ === "" ){
                    RepRecu[j][1]++;
                } else if(reponses[i][1]===RepRecu[j][0] && typeQ === "Num"){
                    RepRecu[j][1]++;
                }
            }
        }
        reponses = document.getElementById('Rafficher').children
        for(i=0;i<reponses.length;i++){
                pourcentage = (RepRecu[i][1]/NbRepRecu)*100
                if(pourcentage>50){
                    reponses[i].getElementsByTagName('div')[0].innerHTML = '<div class="progress progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" style="width: '+pourcentage+'%">'+pourcentage.toFixed(0)+'%</div></div>'
                }else{
                    reponses[i].getElementsByTagName('div')[0].innerHTML = '<div class="progress progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" style="width: '+pourcentage+'%"></div>'+pourcentage.toFixed(0)+'%</div>'
                }
        }
    });
}

function RejoindreSalon(){
    socket = io.connect();
    idSalon = document.getElementById('idSequence').value;
    socket.emit("JoinSalon", idSalon )
    socket.on("JoinSalon", (arg) => {
        console.log(arg !== "La salle n'existe pas")
        if(arg === "La salle n'existe pas"){
            document.getElementById('SalleNonexistante').hidden = false;
        }else {
            document.getElementById('connexion').hidden = true;
        }
    });
    socket.on("QuestionAfficher", (data) => {
        document.getElementById('connecter').hidden = false;
        document.getElementById('envoieRep').disabled = false;
        liste = document.getElementById('listeR')
        html = ""
        question=data[0]
        typeQ = data[1][0]
        reponses = data[1][1]
        console.log(reponses)
        document.getElementById('Qafficher').textContent = question;
        transforme(document.getElementById('Qafficher'))
        if(typeQ === "qcm"){
            for(i=0;i<reponses.length;i++){
                html += '<li class="list-unstyled my-2 mx-3" id="'+reponses[i][0]+'"><input type="checkbox" name="" id="">  '+reponses[i][1]+'</li>'
            }
        } else {
            html += '<form><li class="list-unstyled m-2 w-75" id="'+reponses[0]+'"><input type="number" class="w-100" name="" id="" step=0.01 ></li>'
        }
        document.getElementById('listeR').innerHTML = html;
    });
    socket.on("StopRep", (arg) => {
        liste = document.getElementById('listeR').getElementsByTagName('input')
        for (i=0;i<liste.length;i++){
            liste[i].disabled = true;
        }
        document.getElementById('envoieRep').disabled = true;
    });
    socket.on("affichageCorrection", (liste) => {
        if (typeQ == "qcm" ){
            listeR= document.getElementById('listeR').children
            for(i=0;i<listeR.length;i++){
                for(j=0;j<liste.length;j++){
                    if(listeR[i].id == liste[j][0]){
                        if(parseInt(liste[j][1])==1){
                            listeR[i].className += " bg-success-subtle "
                        }else{
                            listeR[i].className += " bg-danger-subtle "
                        }
                    }
                }
                    
            };
            console.log(document.getElementById('listeR'),liste)
        }else{
            console.log(document.getElementById('listeR').getElementsByTagName('input')[0].value,liste)
            //if(document.getElementById('listeR').getElementsByTagName('input')[0].value == liste)
        }
    });
    socket.on("quitter", () => {
        sid = socket.id
        window.location.href = "quitterRoom/"+sid
    })

};

function NextQ(btnNext){
    
    liste = document.getElementById('listeQ');
    QinListe = liste.getElementsByClassName('question')
    Index = parseInt(document.getElementById('IndexOrdre').textContent)+1
    console.log(Index);
    document.getElementById('IndexOrdre').textContent = Index ;
    html ="";
    RepRecu = []
    typeQ = ""
    if (Index > QinListe.length ){
        document.getElementById('IndexOrdre').textContent = Index-1 ;
        btnNext.hidden = true;
        document.getElementById('Qafficher').innerHTML = '<h2 class="w-100 text-center my-5"> Séquence Terminée<h2>';
        document.getElementById('Rafficher').innerHTML = '<h2 class="w-100 text-center my-5"> Bravo à tout les participants <h2>';
        
    }else{
        btnNext.textContent = "Next";
        for (i=0;i<QinListe.length;i++){
            if (QinListe[i].id == Index){
                transforme(QinListe[i].getElementsByTagName('textarea')[0]);
                document.getElementById('Qafficher').innerHTML = QinListe[i].getElementsByTagName('textarea')[0].textContent;
                console.log(QinListe[i].getElementsByTagName('div')[0].textContent)
                if (QinListe[i].getElementsByTagName('div')[0].textContent === 'qcm' ){
                    for (j=1;j<QinListe[i].getElementsByTagName('textarea').length;j++){
                        RepRecu.push([ QinListe[i].getElementsByTagName('textarea')[j].name , 0])
                        html +=`<li id="`+QinListe[i].getElementsByTagName("span")[j].textContent+`
                        " name="`+ QinListe[i].getElementsByTagName(`textarea`)[j].name +`" class="list-group-item" >` 
                        + QinListe[i].getElementsByTagName(`textarea`)[j].textContent + 
                        `<div id="NbVote" hidden>
                        <div class="progress progress-bar" role="progressbar" aria-valuemin="0" aria-valuemax="100" style="width: 0%"></div>0%</div>
                        </li>`
                    }
                }
                document.getElementById('Rafficher').innerHTML = html ;
                html =""
                NbRepRecu = 0;
                MathJax.typeset();
                mermaid.init();
                document.getElementById("afficheRepDirect").disabled = false;
                document.getElementById("StopRep").disabled = false;
                document.getElementById("afficheCorrection").disabled = false;
                document.getElementById("NbReponses").textContent = NbRepRecu;
                socket.emit("QuestionAfficher", QinListe[i].getElementsByTagName('span')[0].textContent)
            }
        }
    }
    socket.on("QuestionAfficher", (arg) => {
        console.log(arg);
    });
}

function affichage(){
    afficheQ = document.getElementById("afficheQ").checked;
    afficheR =document.getElementById("afficheR").checked;
    if (afficheR === true) {
        document.getElementById('Rafficher').hidden = true;
    } else {
        document.getElementById('Rafficher').hidden = false;
    }
    if (afficheQ === true) {
        document.getElementById('Qafficher').hidden = true;
    } else {
        document.getElementById('Qafficher').hidden = false;
    }
}

function afficheRepDirect(btn){
    //btn.disabled = true;
    reponses = document.getElementById('Rafficher').children
    for(i=0;i<reponses.length;i++){
        if(reponses[i].getElementsByTagName('div')[0].hidden === false){
            reponses[i].getElementsByTagName('div')[0].hidden = true;
        }else{
            reponses[i].getElementsByTagName('div')[0].hidden = false;
        }
    }
    socket.on("RecuRep", () => {
        // Sélectionnez tous les éléments parent des barres de progression
            parents = Array.from(document.querySelectorAll('.progress-bar')).map(bar => bar.parentElement.parentElement);

            // Triez les éléments parents en fonction de la largeur de leur barre de progression
            parents.sort((a, b) => {
            const barA = a.querySelector('.progress-bar');
            const barB = b.querySelector('.progress-bar');
            const widthA = parseFloat(barA.style.width);
            const widthB = parseFloat(barB.style.width);
            return widthB - widthA;
            });
    
            // Ajoutez les éléments parent triés à leur conteneur
            const container = document.getElementById('Rafficher');
            parents.forEach(parent => container.appendChild(parent));
            parents.forEach((parent, index) => {
                if (index < 4) {
                    container.appendChild(parent);
                } else {
                    parent.style.display = 'none';
                }
            }
            )})
    
}

function StopRep(btn){
    btn.disabled = true;
    socket.emit("StopRep","stop")
}

function afficheCorrection(btn){
    btn.disabled = true;
    reponses = document.getElementById('Rafficher').children
    liste = []
    listeQ = document.getElementById('listeQ').getElementsByTagName('textarea')
    for(i=0;i<reponses.length;i++){
        if (typeQ !== "Num"){
            liste.push([reponses[i].attributes.name.value,reponses[i].id])
            if ( parseInt(reponses[i].id) === 1 ){
                reponses[i].className += " list-group-item-success"
            } else {
                reponses[i].className += " list-group-item-danger"
            }
        }else{
            for(j=0;j<listeQ.length;j++){
                    if(listeQ[j].attributes.length !== 0 && listeQ[j].attributes.name.value === reponses[i].firstElementChild.attributes.name.value){
                        console.log(parseFloat(reponses[i].id),parseFloat(listeQ[j].textContent))
                        if ( parseFloat(reponses[i].firstElementChild.id) === parseFloat(listeQ[j].textContent) ){
                            reponses[i].firstElementChild.className += " list-group-item-success"
                        } else {
                            reponses[i].firstElementChild.className += " list-group-item-danger"
                        }
                    }
            }
        }

    };
    socket.emit("affichageCorrection",liste)
}

function quitterRoom(){
    socket.emit("quitter", "quitter")
    socket.on("quitter", () => {
        sid = socket.id
        window.location.href = "quitterRoom/"+sid
    })
}

function envoieRep(btn){
    btn.disabled = true;
    // if num (input.type = number) recup value, sinon for liste, recupe idr+ 1 if checked
    listeRep = document.getElementById('listeR')
    liste = listeRep.getElementsByTagName('input')
    mesreponses = []
    console.log([liste[0].parentNode.id,liste[0].checked])
    if (liste[0].type === "number"){
        liste[0].disabled = true;
        mesreponses = [[liste[0].parentNode.id,parseFloat(liste[0].value).toFixed(2)]]
        console.log(mesreponses)
    } else {
        for (i=0;i<liste.length;i++){
            liste[i].disabled = true;
            valeur=""
            if (liste[i].checked === true){
                valeur="1"
            }else{
                valeur="0"
            }
            mesreponses.push([liste[i].parentNode.id,valeur])
        }
        console.log(mesreponses)
    }
    socket.emit("envoieRep", [document.getElementById('idSequence').value, mesreponses])
}

function imprimer(){
    table = document.getElementById('tableQselect');
    liste = document.getElementById('divAimprimer').children[1];
    for(i=1;i<table.rows.length;i++){
        if (table.rows[i].cells[2].children.length <= 2 ){
            liste.innerHTML += '<li class="list-group-item">'+table.rows[i].cells[1].innerHTML+'<li><br><br><br><br>';
        }else{
            liste.innerHTML += '<li class="list-group-item"  >'+table.rows[i].cells[1].innerHTML+'<li><ul class="reponseImprimer" >'+table.rows[i].cells[2].innerHTML+'</ul>';
        }
    }
    repimp = document.getElementsByClassName('reponseImprimer')
    for(i=0;i<repimp.length;i++){
        for(j=0;j<repimp[i].children.length;j++){
            repimp[i].children[j].innerHTML = '<input class="position-absolute" type="checkbox"> <div class="ms-4">'+ repimp[i].children[j].innerHTML+'</div>'
        }
    }
    document.getElementById('aCacher').hidden=true;
    document.getElementById('divAimprimer').hidden=false;
    document.getElementsByClassName('navbar')[0].hidden = true;
    document.getElementsByTagName('footer')[0].hidden = true;
    window.print();
    liste.innerHTML = ""
    document.getElementsByTagName('footer')[0].hidden = false;
    document.getElementsByClassName('navbar')[0].hidden = false;
    document.getElementById('aCacher').hidden=false;
    document.getElementById('divAimprimer').hidden=true;

}