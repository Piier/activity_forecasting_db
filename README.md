# tirocinio
<h2>creaDB</h2>
<p>
Script per creare da 0 il db e popolarlo, i file verranno prima automaticamente formattati.</br>
L'unico vincolo stretto è che il db non sia gia stato creato.

Ha due tipologie di utilizzo:</br>
<b>python3 creaDB.py </b> che crea il db</br>
<b>python3 creaDB.py percorso_cartella</b> che crea e popola il db. Vedere popolaDB per dettagli maggiori su come passare la cartella</br>


<h2>popolaDB</h2>
<p>Script per la popolazione del db già creato, i file verranno prima automaticamente formattati.</br>
I dataset per popolare il db dovranno essere all'interno della cartella unzippata , e queste cartelle unzippate devono stare dentro alla cartella passata come parametro.
In caso di nome diverso da 'hh1xx', dove xx indica il numero del dataset, la cartella non verrà presa in considerazione, quindi consiglio di unzippare tutti i file nella stessa cartella e poi passare quest'ultima come parametro.

Utilizzo: <b>python3 popolaDB.py percorso_cartella</b></br>
Il parametro passato è il percorso della cartella che contiente le cartelle coi dataset.</br></br>
Il simbolo '->' indica "contiene"</br>
es. </br>
cartellaX -> hh101 -> ann.txt + altri file</br>
cartellaX -> hh114 -> ann.txt + altri file</br>
cartellaX -> hh123 -> ann.txt + altri file</br>

python3 creaDB.py percorso_cartellaX</br>
Vengono prima formattati i file percorso_cartellaX/hh101/ann.txt, percorso_cartellaX/hh114/ann.txt e percorso_cartellaX/hh123/ann.txt e successivamente viene popolato il db attraverso i file formattati

</p>
<h2>formattazione</h2>
<p>Script per la formattazione, utilizzato da creaDB e popolaDB</p>


