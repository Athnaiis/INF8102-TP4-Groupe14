from troposphere import Template, Ref
from troposphere.s3 import (
    Bucket,
    BucketPolicy,
    VersioningConfiguration,
    ReplicationConfiguration,
    ReplicationConfigurationRules,
    ReplicationConfigurationRulesDestination
)
from troposphere.cloudtrail import Trail, EventSelector, DataResource

template = Template()
template.set_description("TP4 Q3.3 — Réplication + CloudTrail")

SOURCE_BUCKET_NAME = "polystudents-ing-groupe14-tp4-q3"
BACKUP_BUCKET_NAME = "polystudents-ing-groupe14-tp4-q3-backup"
IAM_ROLE_REPLICATION_ARN = "arn:aws:iam::625730254292:role/LabRole"

# ---------------------------------------------------------------------------------------
# ------------- 1. Création du bucket source avec la réplication activée ----------------
# ---------------------------------------------------------------------------------------
# Le versioning est activé car il est obligatoire pour pouvoir utiliser la réplication
# S3 (AWS ne permet pas la réplication sur un bucket non versionné).
# La section "ReplicationConfiguration" définit la règle de réplication qui permet
# de copier automatiquement tous les objets du bucket source vers un bucket de
# destination (BACKUP_BUCKET_NAME).
# La règle "ReplicateToBackup" copie automatiquement tous les objets du bucket
# source vers le bucket de destination (ARN du bucket backup). 
# Le rôle IAM spécifié autorise S3 à exécuter la réplication.

source_bucket = template.add_resource(
    Bucket(
        "Q3SourceBucket",
        BucketName=SOURCE_BUCKET_NAME,
        VersioningConfiguration=VersioningConfiguration(Status="Enabled"),
        ReplicationConfiguration=ReplicationConfiguration(
            Role=IAM_ROLE_REPLICATION_ARN,
            Rules=[
                ReplicationConfigurationRules(
                    Id="ReplicateToBackup",
                    Status="Enabled",
                    Prefix="",
                    Destination=ReplicationConfigurationRulesDestination(
                        Bucket=f"arn:aws:s3:::{BACKUP_BUCKET_NAME}"
                    )
                )
            ]
        )
    )
)


# ---------------------------------------------------------------------------------------
# ------------- 2. Bucket de destination (backup) ---------------------------------------
# ---------------------------------------------------------------------------------------
# Ce S3 bucket est utilisé pour recevoir les objets répliqués.
# La réplication S3 exige que le bucket cible ait aussi le versioning activé, afin de 
# conserver l’historique complet des objets répliqués.
# Ce bucket sert uniquement de backup : aucun traitement particulier n’est appliqué ici,
# il se contente de stocker les copies provenant du bucket source.

backup_bucket = template.add_resource(
    Bucket(
        "Q3BackupBucket",
        BucketName=BACKUP_BUCKET_NAME,
        VersioningConfiguration=VersioningConfiguration(Status="Enabled")
    )
)


# -----------------------------------------------------------------------------------------------
# --------- 3. Politique du bucket permettant à CloudTrail d’écrire les journaux ----------------
# -----------------------------------------------------------------------------------------------
# CloudTrail doit pouvoir lire l’ACL du bucket (GetBucketAcl) pour vérifier les permissions.
# Il doit aussi pouvoir déposer des fichiers de logs (PutObject) dans le dossier AWSLogs/.
# La condition "bucket-owner-full-control" garantit que tous les objets écrits dans le bucket
# restent entièrement contrôlés par le propriétaire du bucket.
# Sans cette politique, CloudTrail ne pourrait pas livrer les fichiers de journaux.

template.add_resource(
    BucketPolicy(
        "Q3BackupBucketPolicy",
        Bucket=Ref("Q3BackupBucket"),
        PolicyDocument={
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:GetBucketAcl",
                    "Resource": f"arn:aws:s3:::{BACKUP_BUCKET_NAME}"
                },
                {
                    "Effect": "Allow",
                    "Principal": {"Service": "cloudtrail.amazonaws.com"},
                    "Action": "s3:PutObject",
                    "Resource": f"arn:aws:s3:::{BACKUP_BUCKET_NAME}/AWSLogs/625730254292/*",
                    "Condition": {
                        "StringEquals": {
                            "s3:x-amz-acl": "bucket-owner-full-control"
                        }
                    }
                }
            ]
        }
    )
)


# -----------------------------------------------------------------------------------------------
# ------------- 4. Configuration du Trail CloudTrail --------------------------------------------
# -----------------------------------------------------------------------------------------------
# Les journaux seront stockés dans le bucket de backup (S3BucketName).
# Le trail dépend du bucket et de sa BucketPolicy pour garantir que l’écriture est autorisée.
# IncludeGlobalServiceEvents active l’enregistrement des événements AWS globaux.
# IsLogging démarre la journalisation dès la création.
# EventSelector indique à CloudTrail de capturer toutes les opérations (lecture/écriture) sur 
# les objets du bucket source.
# Cette configuration permet de suivre les modifications et suppressions du S3 d’origine.

template.add_resource(
    Trail(
        "Q3Trail",
        TrailName="groupe14-s3-trail-q3",
        DependsOn=["Q3BackupBucket", "Q3BackupBucketPolicy"],
        S3BucketName=BACKUP_BUCKET_NAME,
        IncludeGlobalServiceEvents=True,
        IsLogging=True,
        EventSelectors=[
            EventSelector(
                ReadWriteType="All",
                DataResources=[
                    DataResource(
                        Type="AWS::S3::Object",
                        Values=[f"arn:aws:s3:::{SOURCE_BUCKET_NAME}/*"]
                    )
                ]
            )
        ]
    )
)


# ---------------------------------------------------------------------------------------
# --------- 5. Génération du fichier JSON -----------------------------------------------
# ---------------------------------------------------------------------------------------
with open("Q3_3.json", "w") as f:
    f.write(template.to_json())

print("Le fichier Q3_3.json a été généré avec succès !")