from troposphere import Template, Ref, Tags, Sub, GetAtt, Output
import troposphere.ec2 as ec2

# Initialisation du template CloudFormation : 
# on crée un objet Template qui contiendra toutes les ressources
template = Template()

# Cette description apparaîtra dans AWS CloudFormation lorsque la pile sera créée
template.set_description("VPC de la Q1 mis à jour pour la Q3.1 afin qu'il puisse supporter les VPC Flow Logs")


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


# --------------------------------------------------------------------------
# ------- 3. Création d'un Internet Gateway (Figure 5) ---------------------
# --------------------------------------------------------------------------
# L'IGW permet au VPC d'avoir une sortie vers Internet. 
# Il est ensuite attaché explicitement au VPC.
# Il est important car sans IGW, aucun subnet ne peut être publique
igw = template.add_resource(
    ec2.InternetGateway(
        "InternetGateway",
        Tags=[{"Key": "Name", "Value": "polystudent-14-igw"}]
    )
)

# Attachement de l'IGW au VPC
attach_igw = template.add_resource(
    ec2.VPCGatewayAttachment(
        "InternetGatewayAttachment",
        VpcId=Ref(vpc),             # VPC auquel l'IGW est attaché
        InternetGatewayId=Ref(igw)  # l'IGW créé juste au-dessus
    )
)


# --------------------------------------------------------------------------
# ------- 4. Création d'un NAT Gateway per AZ (Figure 6) -------------------
# --------------------------------------------------------------------------

# --- NAT Gateway de l'AZ1 ---
# Création de l’EIP du NAT Gateway dans l’AZ1
nat1_eip = ec2.EIP("NATEIP1", Domain="vpc")
nat1_eip.DependsOn="InternetGatewayAttachment"
template.add_resource(nat1_eip)

# Création du NAT Gateway pour l’AZ1
nat1 = template.add_resource(
    ec2.NatGateway(
        "NatGatewayAZ1",
        AllocationId=GetAtt(nat1_eip, "AllocationId"),
        SubnetId=Ref(public_subnet_az1)
    )
)


# --- NAT Gateway de l'AZ2 ---
# Création de l’EIP du NAT Gateway dans l’AZ2
nat2_eip = ec2.EIP("NATEIP2", Domain="vpc")
nat2_eip.DependsOn="InternetGatewayAttachment"
template.add_resource(nat2_eip)

# Création du NAT Gateway pour l’AZ2
nat2 = template.add_resource(
    ec2.NatGateway(
        "NatGatewayAZ2",
        AllocationId=GetAtt(nat2_eip, "AllocationId"),
        SubnetId=Ref(public_subnet_az2)
    )
)


# ---------------------------------------------------------------------------------
# ------- 5. Création de tables de routage publiques (Figure 7) -------------------
# ---------------------------------------------------------------------------------
# Création de la table de routage publique
public_route_table = template.add_resource(ec2.RouteTable("PublicRouteTable", VpcId=Ref(vpc)))

# Ajout d’une route par défaut vers l’Internet Gateway
public_route = template.add_resource(
    ec2.Route(
        "PublicRouteDefault",
        RouteTableId=Ref(public_route_table),
        DestinationCidrBlock="0.0.0.0/0",
        GatewayId=Ref(igw)
    )
)

# Association du subnet public AZ1 à la table de routage publique
template.add_resource(
    ec2.SubnetRouteTableAssociation(
        "PublicSubnet1RTAssociation",
        SubnetId=Ref(public_subnet_az1),
        RouteTableId=Ref(public_route_table)
    )
)

# Association du subnet public AZ2 à la table de routage publique
template.add_resource(
    ec2.SubnetRouteTableAssociation(
        "PublicSubnet2RTAssociation",
        SubnetId=Ref(public_subnet_az2),
        RouteTableId=Ref(public_route_table)
    )
)


# ---------------------------------------------------------------------------------
# ------- 6. Création de tables de routage privées (Figure 8) ---------------------
# ---------------------------------------------------------------------------------

# --- AZ1 ---
# Table de routage privée pour l’AZ1
private_rt_az1 = template.add_resource(
    ec2.RouteTable("PrivateRouteTableAZ1", VpcId=Ref(vpc))
)

# Route par défaut utilisant le NAT Gateway 1
template.add_resource(
    ec2.Route(
        "PrivateRoute1Default",
        RouteTableId=Ref(private_rt_az1),
        DestinationCidrBlock="0.0.0.0/0",
        NatGatewayId=Ref(nat1)
    )
)

# Association du subnet privé AZ1 à sa table de routage privée
template.add_resource(
    ec2.SubnetRouteTableAssociation(
        "PrivateSubnet1RTAssociation",
        SubnetId=Ref(private_subnet_az1),
        RouteTableId=Ref(private_rt_az1)
    )
)


# --- AZ2 ---
# Table de routage privée pour l’AZ2
private_rt_az2 = template.add_resource(
    ec2.RouteTable("PrivateRouteTableAZ2", VpcId=Ref(vpc))
)

# Route par défaut utilisant le NAT Gateway 2
template.add_resource(
    ec2.Route(
        "PrivateRoute2Default",
        RouteTableId=Ref(private_rt_az2),
        DestinationCidrBlock="0.0.0.0/0",
        NatGatewayId=Ref(nat2)
    )
)

# Association du subnet privé AZ2 à sa table de routage privée
template.add_resource(
    ec2.SubnetRouteTableAssociation(
        "PrivateSubnet2RTAssociation",
        SubnetId=Ref(private_subnet_az2),
        RouteTableId=Ref(private_rt_az2)
    )
)


# ---------------------------------------------------------------------------------
# ------- 7. Création d'un groupe de sécurité (Figure 9) --------------------------
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


# ---------------------------------------------------------------------------------
# ------- 8. Activation des VPC Flow Logs (VOIR ICI POUR LA Q2) -------------------
# ---------------------------------------------------------------------------------
# Seulement les paquests rejetés peuvent etre capturés et envoyés à notre bucket S3 
# nommée polystudent-q2-tp4 (créé dans la Q2)
flow_log = template.add_resource(
    ec2.FlowLog(
        "VPCFlowLogRejectedOnly",
        ResourceId=Ref(vpc),
        ResourceType="VPC",
        TrafficType="REJECT",
        LogDestinationType="s3",
        LogDestination="arn:aws:s3:::polystudent-q2-tp4",   # ARN du bucket S3 créé dans la Q2
        MaxAggregationInterval=600
    )
)


# ---------------------------------------------------------------------------------
# ------- Ajout des lignes du bloc Output (Figure 4) ------------------------------
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
# Objectif : Écrire dans un fichier local (vpc-Q3_1.yaml) l’intégralité du template 
#            CloudFormation construit avec Troposphere
# Ce fichier YAML sera ensuite importé manuellement dans CloudFormation pour 
# déployer réellement l'infrastructure sur AWS
with open("vpc-Q3_1.yaml", "w") as file:
    file.write(template.to_yaml())

print("Le fichier vpc-Q3_1.yaml a bien été généré!")