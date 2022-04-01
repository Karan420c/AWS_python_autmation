from urllib import response
import boto3
client = boto3.client('elbv2')
ec2= boto3.client('ec2')
ALB_name= input("Enter your ALB Name:- ")
Sec_grp=input("Enter your SecurityGroups Example sg-5e60b43a :- ")
HTTP_tar_grp_name = input("Enter HTTP Target Group Name:- ")
http_Port= int(input("Enter HTTP Target Group Port Number:- "))
HTTPS_tar_grp_name = input("Enter HTTPS Target Group Name:- ")
https_port= int(input("Enter HTTPS Target Group Port Number:- "))


#####################  Create Ec2 Instances #######################
print("Creating EC2 instance")

check=input("Do you want to create spot instance or Ondemand instance for spot write spot and for ondemand write ondemand:- ")
check_lower=check.lower()
check_space=check_lower.strip()
intance_type=check_space

if intance_type == 'spot':
    ct=input("For Spot Instance Enter uniq value for Client Token:-" )
    sgid_check=input("Enter security group id:- ")
    sgid=sgid_check.strip()
    insfamily_check=input("Enter Instance Family name you want to create in SPOT:- ")
    insfamily=insfamily_check.strip()
    ec2_name_check=input("Enter Ec2 instance Name:- ") # get tag name of ec2 instance from user
    ec2_name=ec2_name_check.strip() # remove space

       
    response=client.request_spot_instances(

    ClientToken=ct,
    DryRun=False,
    InstanceCount=1,
    LaunchSpecification={
        'SecurityGroupIds': [
            sgid,
        ],

        'EbsOptimized': True,
        'ImageId': 'ami-0f587da8b4e20d2c2',
        'InstanceType': insfamily,
        'KeyName': 'ubuy_admin',
        'Monitoring': {
            'Enabled': False
        },
        'Placement': {
            'AvailabilityZone': 'eu-west-1a',
        },

    },
     TagSpecifications=[
         {
             'ResourceType': 'instance',
             'Tags': [
                 {
                     
                    'Key': 'Name',
                    'Value': ec2_name,
                 },
             ],
         },
     ],
    SpotPrice='1.00',
    Type='one-time',

)
    
elif intance_type == 'ondemand':
    print("Creating Instance in Ondemand")
    ec2_ondemand= boto3.resource('ec2')
    
    sgid_check=input("Enter security group id:- ") #Get security group id from user
    sgid=sgid_check.strip() # remove space
    insfamily_check=input("Enter Instance Family name you want to create in Ondemand:- ")  # get instance family from user
    insfamily=insfamily_check.strip() # remove space
    ec2_name_check=input("Enter Ec2 instance Name:- ") # get tag name of ec2 instance from user
    ec2_name=ec2_name_check.strip() # remove space
    instances = ec2_ondemand.create_instances(
        MinCount = 1,
        MaxCount = 1,
        ImageId='ami-0f587da8b4e20d2c2',
        InstanceType=insfamily,
        KeyName='ubuy_admin',
        TagSpecifications=[    
            {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': ec2_name,
                },
            ]
        },
        ],
        NetworkInterfaces=[
            {
                'SubnetId': 'subnet-8d6881d4',
                'AssociatePublicIpAddress': True,
                'DeviceIndex': 0,
                'Groups': [sgid]}],
    )
    

else:
    print("enter valid method")

# ######################## Creating HTTP Target Group #################
print(f"Creating {HTTP_tar_grp_name} HTTP Target Group")
http_tr = client.create_target_group(
    Name=HTTP_tar_grp_name,
    Protocol='HTTP',
    ProtocolVersion='HTTP1',
    Port=http_Port,
    VpcId='vpc-b7fb3ed2',
    HealthCheckProtocol='HTTP',
    HealthCheckEnabled=True,
    HealthCheckPath='/',
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=5,
    HealthyThresholdCount=5,
    TargetType='instance',

)
http_arn=http_tr['TargetGroups'][0]['TargetGroupArn']
print(f"Created {HTTP_tar_grp_name} HTTP Target Group")

############ Create HTTPS Target Group ##########
print(f"Creating {HTTPS_tar_grp_name} HTTPS Target Group")
https_tr = client.create_target_group(
    Name=HTTPS_tar_grp_name,
    Protocol='HTTPS',
    ProtocolVersion='HTTP1',
    Port=https_port,
    VpcId='vpc-b7fb3ed2',
    HealthCheckProtocol='HTTPS',
    HealthCheckEnabled=True,
    HealthCheckPath='/',
    HealthCheckIntervalSeconds=30,
    HealthCheckTimeoutSeconds=5,
    HealthyThresholdCount=5,
    TargetType='instance',

)

https_arn=https_tr['TargetGroups'][0]['TargetGroupArn']




######################## Create ALB ######################
print(f"Creating {ALB_name} Load Balancer")
alb = client.create_load_balancer(
    Name='ALB_Name',
    Subnets=['subnet-32f55a57','subnet-8d6881d4','subnet-bb9742cc'],
    SecurityGroups=[
        Sec_grp,
    ],
    Scheme='internet-facing',
    Tags=[
        {
            'Key': 'Name',
            'Value': 'boto3'
        },
    ],
    Type='application',
    IpAddressType='ipv4',
    
)

alb_arn=alb['LoadBalancers'][0]['LoadBalancerArn']



############ Creting Port80 listener  ######################

print("Creating Port 80 Listener")

listener_80 = client.create_listener(
    LoadBalancerArn=alb_arn,
    Protocol='HTTP',
    Port=80,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': http_arn,

            },
         ],    
      )     
    
############ Creting Port 443 listener  ######################
    

print("Creating Port 443 Listener")

listener_443 = client.create_listener(
    LoadBalancerArn=alb_arn,
    Protocol='HTTPS',
    Port=443,
    DefaultActions=[
        {
            'Type': 'forward',
            'TargetGroupArn': https_arn,

            },
         ],    
      )     


    
