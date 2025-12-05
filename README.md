
## Étudiantes :
- Imane AHMED ROBLEH (2067952) sous le pseudonyme Athnaiis
- Ndèye Maty Ndiaye (2405114) sous le pseudonyme maty23

## Structure du TP4
```bash
  TP4/
    ├── EC2 Security/          # dossier de la section 2 - EC2 Security
    ├── Exercice/              # dossier contenant les dossiers des 4 questions de l'exercice
        ├── Q1/                # dossier contenant les scripts demandés pour la question 1
        ├── Q2/                # dossier contenant les scripts demandés pour la question 2
        ├── Q3/                # dossier contenant les scripts demandés pour la question 3
            ├── Question 3.1/  # dossier contenant le script python demandé pour la question 3.1
            ├── Question 3.2/  # dossier contenant le script python demandé pour la question 3.2
            ├── Question 3.3/  # dossier contenant le script python demandé pour la question 3.3
        ├── Q4/                # dossier contenant les scripts demandés pour la question 4
            ├── 4.1./          # dossier contenant le(s) script(s) python demandé(s) pour la question 4.1
            ├── 4.2/           # dossier contenant le(s) script(s) python demandé(s) pour la question 4.2
    ├── S3 Security/           # dossier de la section 3 - S3 Security
    ├── VPC Security/          # dossier de la section 1 - VPC Security
    ├── README.md              # Documentation de ce TP4
```

## Éxécution de la question 1 de l'exercice 
Pour exécuter la question 1, il suffit de lancer le script correspondant dans le dossier TP4/Exercice/Q1/ :
```bash
python3 Q1.py
```
Ce script génère un fichier JSON CloudFormation (**vpc_Q1.yaml**) que vous pouvez ensuite importer dans AWS CloudFormation via l’interface web.



## Éxécution de la question 2 de l'exercice 
Pour exécuter la question 1, il suffit de lancer le script correspondant dans le dossier TP4/Exercice/Q2/ :
```bash
python3 create_s3_bucket.py
```
Ce script génère un fichier JSON CloudFormation (**bucket_python.json**) que vous pouvez ensuite importer dans AWS CloudFormation via l’interface web.



## Éxécution de la question 3 de l'exercice 
Cette question est divisé en trois parties, qui requiert chacune l'éxécution d'un script python: 

#### Dans le dossier TP4/Exercice/Question 3.1/, lancez le script correspondant :
```bash
python3 Q3_1.py
```
Ce script génère un fichier JSON CloudFormation (**vpc-Q3_1.yaml**) que vous pouvez ensuite importer dans AWS CloudFormation via l’interface web.

#### Dans le dossier TP4/Exercice/Question 3.2/, lancez le script correspondant :
```bash
python3 Q3_2.py
```
Ce script génère un fichier JSON CloudFormation (**vpc-Q3_2.yaml**) que vous pouvez ensuite importer dans AWS CloudFormation via l’interface web.

#### Dans le dossier TP4/Exercice/Question 3.3/, lancez le script correspondant :
```bash
python3 Q3_3.py
```
Ce script génère un fichier JSON CloudFormation (**Q3_3.json**) que vous pouvez ensuite importer dans AWS CloudFormation via l’interface web.



## Remarques 
- On a utilisé le Lab Learner pour effectuer ce TP alors la région configuré dans notre code est 'us-east-1'.
