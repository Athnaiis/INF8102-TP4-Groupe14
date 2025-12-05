from troposphere import Template, Ref, Sub, GetAtt, Output
import troposphere.ec2 as ec2
import troposphere.iam as iam
import troposphere.cloudwatch as cw

template = Template()
template.set_description("VPC de la Q3.2 - Ajout d_instances EC2 + LabRole + CloudWatch alarm")


# ----------------------------------------------------------------------
# ------- 1. Création du VPC (Figure 1) --------------------------------
# ----------------------------------------------------------------------
vpc = template.add_resource(
    ec2.VPC(
        "VPCQ1TP4",
        CidrBlock="10.0.0.0/16",
        EnableDnsSupport=True,
        EnableDnsHostnames=True,
        Tags=[{"Key": "Name", "Value": "polystudent-vpc"}]
    )
)


# ----------------------------------------------------------------------
# ------- 2. Création de sous-réseaux (Figures 2, 3 et 4) --------------
# ----------------------------------------------------------------------
# Sous-réseau public dans l'AZ1
public_subnet_az1 = template.add_resource(
    ec2.Subnet(
        "PublicSubnetAZ1",
        VpcId=Ref(vpc),
        CidrBlock="10.0.0.0/24",
        AvailabilityZone=Sub("us-east-1a"),
        MapPublicIpOnLaunch=True,
        Tags=[{"Key": "Name", "Value": "public-az1"}]
    )
)

# Sous-réseau public dans l'AZ2
public_subnet_az2 = template.add_resource(
    ec2.Subnet(
        "PublicSubnetAZ2",
        VpcId=Ref(vpc),
        CidrBlock="10.0.16.0/24",
        AvailabilityZone=Sub("us-east-1b"),
        MapPublicIpOnLaunch=True,
        Tags=[{"Key": "Name", "Value": "public-az2"}]
    )
)

# Sous-réseau privé dans l'AZ1
private_subnet_az1 = template.add_resource(
    ec2.Subnet(
        "PrivateSubnetAZ1",
        VpcId=Ref(vpc),
        CidrBlock="10.0.128.0/24",
        AvailabilityZone=Sub("us-east-1a"),
        MapPublicIpOnLaunch=False,
        Tags=[{"Key": "Name", "Value": "private-az1"}]
    )
)

# Sous-réseau privé dans l'AZ2
private_subnet_az2 = template.add_resource(
    ec2.Subnet(
        "PrivateSubnetAZ2",
        VpcId=Ref(vpc),
        CidrBlock="10.0.144.0/24",
        AvailabilityZone=Sub("us-east-1b"),
        MapPublicIpOnLaunch=False,
        Tags=[{"Key": "Name", "Value": "private-az2"}]
    )
)


# ---------------------------------------------------------------------------------
# ------- 3. Création d'un groupe de sécurité (Figure 9) --------------------------
# ---------------------------------------------------------------------------------
security_group = template.add_resource(
    ec2.SecurityGroup(
        "polystudent14SG",
        VpcId=Ref(vpc),
        GroupDescription="Security group qui allows SSH, HTTP, etc.",
        SecurityGroupIngress=[
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=22,   ToPort=22,   CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=80,   ToPort=80,   CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=443,  ToPort=443,  CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="udp", FromPort=53,   ToPort=53,   CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=53,   ToPort=53,   CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=1433, ToPort=1433, CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=5432, ToPort=5432, CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=3306, ToPort=3306, CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=3389, ToPort=3389, CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=1514, ToPort=1514, CidrIp="0.0.0.0/0"),
            ec2.SecurityGroupRule(IpProtocol="tcp", FromPort=9200, ToPort=9300, CidrIp="0.0.0.0/0")
        ],
        Tags=[{"Key": "Name", "Value": "polystudent-sg"}]
    )
)


# ------------------------------------------------------------------------------------
# ------- 4. IAM Instance Profile pour LabRole ---------------------------------------
# ------------------------------------------------------------------------------------
lab_instance_profile = template.add_resource(
    iam.InstanceProfile(
        "LabInstanceProfile",
        Roles=["LabRole"]     # Rôle existant déjà dans AWS Academy
    )
)


# -------------------------------------------------------------------------------------
# ------- 5. Création de 4 instances EC2 (2 publiques et 2 privées) ---------------------
# -------------------------------------------------------------------------------------
AMI = "ami-0c02fb55956c7d316"   # Amazon Linux 2 (us-east-1)
InstanceType = "t3.micro"       

# Instance publique AZ1
public_instance_az1 = template.add_resource(
    ec2.Instance(
        "PublicInstanceAZ1",
        ImageId=AMI,
        InstanceType=InstanceType,
        SubnetId=Ref(public_subnet_az1),                # Subnet public AZ1
        SecurityGroupIds=[Ref(security_group)],
        IamInstanceProfile=Ref(lab_instance_profile)    # Role IAM (LabRole)
    )
)

# Instance publique AZ2
public_instance_az2 = template.add_resource(
    ec2.Instance(
        "PublicInstanceAZ2",
        ImageId=AMI,
        InstanceType=InstanceType,
        SubnetId=Ref(public_subnet_az2),                # Subnet public AZ2
        SecurityGroupIds=[Ref(security_group)],
        IamInstanceProfile=Ref(lab_instance_profile)
    )
)

# Instance publique AZ1
private_instance_az1 = template.add_resource(
    ec2.Instance(
        "PrivateInstanceAZ1",
        ImageId=AMI,
        InstanceType=InstanceType,
        SubnetId=Ref(private_subnet_az1),               # Subnet privée AZ1
        SecurityGroupIds=[Ref(security_group)],
        IamInstanceProfile=Ref(lab_instance_profile)
    )
)

# Instance publique AZ2
private_instance_az2 = template.add_resource(
    ec2.Instance(
        "PrivateInstanceAZ2",
        ImageId=AMI,
        InstanceType=InstanceType,
        SubnetId=Ref(private_subnet_az2),               # Subnet privée AZ2
        SecurityGroupIds=[Ref(security_group)],
        IamInstanceProfile=Ref(lab_instance_profile)
    )
)


# ----------------------------------------------------------------------------------------
# ------- 6. Création d'un CloudWatch Alarm (NetworkPacketsIn > 1000 pkts/sec) -----------
# ----------------------------------------------------------------------------------------
# Objectif : Déclencher une alarme si le nombre moyen de paquets entrants (NetworkPacketsIn)
#            dépasse 1000 paquets/secondes. L'analyse se fait sur une période de 60 secondes 
#            (grâce à Average). Chaque alarme est associée à l'ID d'une instance.
def create_alarm(instance, name_suffix):
    return cw.Alarm(
        f"Alarm{name_suffix}",
        AlarmDescription=f"Alarm activated if NetworkPacketsIn > 1000 on {name_suffix}",
        Namespace="AWS/EC2",
        MetricName="NetworkPacketsIn",
        Statistic="Average",
        Period="60",
        EvaluationPeriods="1",
        Threshold="1000",
        ComparisonOperator="GreaterThanThreshold",
        Dimensions=[
            cw.MetricDimension(
                Name="InstanceId",
                Value=Ref(instance)
            )
        ]
    )

# ---- Création des 4 alarmes ----
# Un pour chaque instance publique (AZ1 & AZ2) et un pour chaque instance privée (AZ1 & AZ2).
# Cela garantit que toutes les instances du VPC sont surveillées.

alarm_public_az1 = template.add_resource(
    create_alarm(public_instance_az1, "PublicAZ1")
)

alarm_public_az2 = template.add_resource(
    create_alarm(public_instance_az2, "PublicAZ2")
)

alarm_private_az1 = template.add_resource(
    create_alarm(private_instance_az1, "PrivateAZ1")
)

alarm_private_az2 = template.add_resource(
    create_alarm(private_instance_az2, "PrivateAZ2")
)


# ---------------------------------------------------------------------------------
# ------- 7. Ajout des lignes du bloc Output (Figure 4) ---------------------------
# ---------------------------------------------------------------------------------
template.add_output([
    Output("VPCQ1TP4", Value=Ref(vpc)),
    Output("PublicSubnetAZ1", Value=Ref(public_subnet_az1)),
    Output("PublicSubnetAZ2", Value=Ref(public_subnet_az2)),
    Output("PrivateSubnetAZ1", Value=Ref(private_subnet_az1)),
    Output("PrivateSubnetAZ2", Value=Ref(private_subnet_az2)),
])


# ---------------------------------------------------------------------------------
# ------- Génération du fichier de sortie yaml ------------------------------------
# ---------------------------------------------------------------------------------
# Objectif : Écrire dans un fichier local (vpc-Q3_2.yaml) l’intégralité du template 
#            CloudFormation construit avec Troposphere
# Ce fichier YAML sera ensuite importé manuellement dans CloudFormation pour 
# déployer réellement l'infrastructure sur AWS
with open("vpc-Q3_2.yaml", "w") as f:
    f.write(template.to_yaml())

print("Le fichier vpc-Q3_2.yaml a bien été généré !")