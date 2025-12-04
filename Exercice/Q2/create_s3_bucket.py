from troposphere import Template
from troposphere.s3 import Bucket, PublicAccessBlockConfiguration, VersioningConfiguration, BucketEncryption, ServerSideEncryptionRule, ServerSideEncryptionByDefault

# ------------------------
# Création du template CloudFormation
# ------------------------
template = Template()
template.set_description("S3 Security")

# ------------------------
# Configuration du chiffrement KMS
# ------------------------
kms_key_id = "arn:aws:kms:us-east-1:081743453153:key/0bdfb016-9a1e-43fe-9b7c-d351fa52a535"

bucket = template.add_resource(
    Bucket(
        "PolystudentS3ImaneQ2TP4",
        BucketName="polystudent-q2-tp4",
        AccessControl="Private",

        PublicAccessBlockConfiguration=PublicAccessBlockConfiguration(
            BlockPublicAcls=True,
            IgnorePublicAcls=True,
            BlockPublicPolicy=True,
            RestrictPublicBuckets=True
        ),

        BucketEncryption=BucketEncryption(
            ServerSideEncryptionConfiguration=[
                ServerSideEncryptionRule(
                    ServerSideEncryptionByDefault=ServerSideEncryptionByDefault(
                        SSEAlgorithm="aws:kms",
                        KMSMasterKeyID=kms_key_id
                    )
                )
            ]
        ),

        VersioningConfiguration=VersioningConfiguration(
            Status="Enabled"
        )
    )
)

# ------------------------
# Export du fichier JSON
# ------------------------
with open("bucket_python.json", "w") as f:
    f.write(template.to_json())

print("Template CloudFormation généré : bucket_python.json")

