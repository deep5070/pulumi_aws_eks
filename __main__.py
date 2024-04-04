import pulumi
import pulumi_aws as aws
#import pulumi_eks as eks
#import pulumi_kubernetes as kubernetes
import json
from pulumi_aws import ec2

#variables

ec2_iam_cluster_role_name = 'cluster-role-pulumi'
ec2_cluster_policy = 'eks_pulumi_cluster_policy'
ec2_service_policy = 'eks_pulumi_service_policy'
ec2_vpc_controller = 'eks_pulumi_vpc_resource_controller'
ec2_iam_node_role_name = 'node-role-pulumi'
ec2_node_policy = 'eks-AmazonEKSWorkerNodePolicy'
ec2_cni_policy = 'eks-AmazonEKSCNIPolicy'
ec2_container_policy = 'eks-AmazonEC2ContainerRegistryReadOnly'
ec2_cluster_name = 'eks_pulumi_cluster'
ec2_node_name = 'eks_pulumi_node_group'


assume_role = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    effect="Allow",
    principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type="Service",
        identifiers=["eks.amazonaws.com"],
    )],
    actions=["sts:AssumeRole"],
)])

assume_role_node = aws.iam.get_policy_document(statements=[aws.iam.GetPolicyDocumentStatementArgs(
    effect="Allow",
    principals=[aws.iam.GetPolicyDocumentStatementPrincipalArgs(
        type="Service",
        identifiers=["ec2.amazonaws.com"],
    )],
    actions=["sts:AssumeRole"],
)])



eks_iam_role = aws.iam.Role("example",
    name="eks-cluster-policy",
    assume_role_policy=assume_role.json)


eks_iam_node_role = aws.iam.Role("node",
    name="eks-node-policy",
    assume_role_policy=assume_role_node.json)



ec2_cluster_policy = aws.iam.RolePolicyAttachment("ec2_cluster_policy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSClusterPolicy",
    role=eks_iam_role.name)

ec2_service_policy = aws.iam.RolePolicyAttachment("ec2_service_policy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSServicePolicy",
    role=eks_iam_role.name)

ec2_vpc_policy = aws.iam.RolePolicyAttachment("ec2_vpc_controller",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSVPCResourceController",
    role=eks_iam_role.name)


ec2_node_policy = aws.iam.RolePolicyAttachment("ec2_node_policy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKSWorkerNodePolicy",
    role=eks_iam_node_role.name)

ec2_cni_policy = aws.iam.RolePolicyAttachment("ec2_cni_policy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEKS_CNI_Policy",
    role=eks_iam_node_role.name)

ec2_container_policy = aws.iam.RolePolicyAttachment("ec2_container_policy",
    policy_arn="arn:aws:iam::aws:policy/AmazonEC2ContainerRegistryReadOnly",
    role=eks_iam_node_role.name)


default = aws.ec2.DefaultVpc("default", tags={
    "Name": "Default VPC",
})

sg = aws.ec2.SecurityGroup("pulumi_sg",
        description="Allow HTTP traffic to EC2 instance",
        ingress=[{
                "protocol": "tcp",
                "from_port": 0,
                "to_port": 65535,
                "cidr_blocks": ["0.0.0.0/0"],
            },
       
        ],
    egress=[
        {
            "protocol": "tcp",
            "from_port": 0,
            "to_port": 65535,
            "cidr_blocks": ["0.0.0.0/0"],
        }
    ],
    vpc_id=default.id
)

eks_cluster = aws.eks.Cluster("eks_pulumi",
    name="ec2_cluster_name",
    role_arn=eks_iam_role.arn,
    vpc_config=aws.eks.ClusterVpcConfigArgs(
        subnet_ids=[
            "subnet-b45e62ba",
            "subnet-750c7613",
            "subnet-6c36764d",
        ],
    ))

eks_node_group = aws.eks.NodeGroup("eks_pulumi_node_group",
    cluster_name="ec2_cluster_name",
    node_group_name="ec2_node_name",
    node_role_arn=eks_iam_node_role.arn,
    subnet_ids=[
            "subnet-b45e62ba",
            "subnet-750c7613",
            "subnet-6c36764d",
        ],
    scaling_config=aws.eks.NodeGroupScalingConfigArgs(
        desired_size=1,
        max_size=2,
        min_size=1,
    ),
    opts=pulumi.ResourceOptions(parent=eks_cluster)
    )