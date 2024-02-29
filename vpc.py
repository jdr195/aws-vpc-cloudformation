from troposphere import GetAtt, Parameter, Ref, Sub, Tags, Template, GetAZs, Select, Output
from troposphere.constants import STRING
from troposphere.ec2 import VPC, InternetGateway, VPCGatewayAttachment, Subnet, RouteTable, Route, SubnetRouteTableAssociation, EIP, NatGateway


def main():

    template = Template()
    vpc_cidr = template.add_parameter(Parameter("VpcCIDR", Description="CIDR Range for the VPC", Type=STRING, Default="10.0.0.0/16"))
    public_subnet_1_cidr = template.add_parameter(Parameter("PublicSubnet1CIDR", Description="CIDR Range for the public subnet in the first Availability Zone", Type=STRING, Default="10.0.0.0/24"))
    public_subnet_2_cidr = template.add_parameter(Parameter("PublicSubnet2CIDR", Description="CIDR Range for the public subnet in the second Availability Zone", Type=STRING, Default="10.0.1.0/24"))
    private_subnet_1_cidr = template.add_parameter(Parameter("PrivateSubnet1CIDR", Description="CIDR Range for the private subnet in the first Availability Zone", Type=STRING, Default="10.0.2.0/24"))
    private_subnet_2_cidr = template.add_parameter(Parameter("PrivateSubnet2CIDR", Description="CIDR Range for the private subnet in the second Availability Zone", Type=STRING, Default="10.0.3.0/24"))

    template.set_description("Creates a VPC with an Internet Gateway, 2 public subnets, 2 private subnets, 2 NAT Gateways, and the supporting Routes and Associations.")

    tags = Tags(
        Application=Ref(
            "AWS::StackId",
        )
    )

    vpc = template.add_resource(
        VPC(
            "VPC",
            CidrBlock=Ref(vpc_cidr),
            EnableDnsSupport=True,
            EnableDnsHostnames=True,
            Tags=tags,
        )
    )

    internet_gateway = template.add_resource(
        InternetGateway(
            "InternetGateway",
            Tags=tags,
        )
    )

    vpc_gateway_attachment = template.add_resource(
        VPCGatewayAttachment(
            "VPCGatewayAttachment",
            VpcId=Ref(vpc),
            InternetGatewayId=Ref(internet_gateway),
        )
    )
    public_subnet_1 = template.add_resource(
        Subnet(
            "PublicSubnet1",
            VpcId=Ref(vpc),
            CidrBlock=Ref(public_subnet_1_cidr),
            MapPublicIpOnLaunch=False,
            AvailabilityZone=Select(0, GetAZs()),
            Tags=tags + Tags(Name=Sub("${AWS::StackName}-PublicSubnet1")),
        )
    )
    public_subnet_2 = template.add_resource(
        Subnet(
            "PublicSubnet2",
            VpcId=Ref(vpc),
            CidrBlock=Ref(public_subnet_2_cidr),
            MapPublicIpOnLaunch=False,
            AvailabilityZone=Select(1, GetAZs()),
            Tags=tags + Tags(Name=Sub("${AWS::StackName}-PublicSubnet2")),
        )
    )
    private_subnet_1 = template.add_resource(
        Subnet(
            "PrivateSubnet1",
            VpcId=Ref(vpc),
            CidrBlock=Ref(private_subnet_1_cidr),
            MapPublicIpOnLaunch=False,
            AvailabilityZone=Select(0, GetAZs()),
            Tags=tags + Tags(Name=Sub("${AWS::StackName}-PrivateSubnet1")),
        )
    )
    private_subnet_2 = template.add_resource(
        Subnet(
            "PrivateSubnet2",
            VpcId=Ref(vpc),
            CidrBlock=Ref(private_subnet_2_cidr),
            MapPublicIpOnLaunch=False,
            AvailabilityZone=Select(1, GetAZs()),
            Tags=tags + Tags(Name=Sub("${AWS::StackName}-PrivateSubnet2")),
        )
    )
    nat_gateway_1_eip = template.add_resource(
        EIP(
            "NatGateway1EIP",
            DependsOn=vpc_gateway_attachment.title,
            Domain="vpc",
        )
    )
    nat_gateway_2_eip = template.add_resource(
        EIP(
            "NatGateway2EIP",
            DependsOn=vpc_gateway_attachment.title,
            Domain="vpc",
        )
    )
    nat_gateway_1 = template.add_resource(
        NatGateway(
            "NatGateway1",
            AllocationId=GetAtt(nat_gateway_1_eip, "AllocationId"),
            SubnetId=Ref(public_subnet_1),
        )
    )
    nat_gateway_2 = template.add_resource(
        NatGateway(
            "NatGateway2",
            AllocationId=GetAtt(nat_gateway_2_eip, "AllocationId"),
            SubnetId=Ref(public_subnet_2),
        )
    )
    public_route_table = template.add_resource(
        RouteTable(
            "PublicRouteTable",
            VpcId=Ref(vpc),
            Tags=tags + Tags(Name=Sub("${AWS::StackName} Public Routes")),
        )
    )
    default_public_route = template.add_resource(
        Route(
            "DefaultPublicRoute",
            DependsOn=vpc_gateway_attachment.title,
            RouteTableId=Ref(public_route_table),
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=Ref(internet_gateway),
        )
    )
    public_subnet_1_route_table_association = template.add_resource(
        SubnetRouteTableAssociation(
            "PublicSubnet1RouteTableAssociation",
            RouteTableId=Ref(public_route_table),
            SubnetId=Ref(public_subnet_1),
        )
    )
    public_subnet_2_route_table_association = template.add_resource(
        SubnetRouteTableAssociation(
            "PublicSubnet2RouteTableAssociation",
            RouteTableId=Ref(public_route_table),
            SubnetId=Ref(public_subnet_2),
        )
    )
    private_route_table_1 = template.add_resource(
        RouteTable(
            "PrivateRouteTable1",
            VpcId=Ref(vpc),
            Tags=tags + Tags(Name=Sub("${AWS::StackName} Private Routes (AZ1)")),
        )
    )
    default_private_route_1 = template.add_resource(
        Route(
            "DefaultPrivateRoute1",
            RouteTableId=Ref(private_route_table_1),
            DestinationCidrBlock="0.0.0.0/0",
            NatGatewayId=Ref(nat_gateway_1),
        )
    )
    private_subnet_1_route_table_association = template.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnet1RouteTableAssociation",
            RouteTableId=Ref(private_route_table_1),
            SubnetId=Ref(private_subnet_1),
        )
    )
    private_route_table_2 = template.add_resource(
        RouteTable(
            "PrivateRouteTable2",
            VpcId=Ref(vpc),
            Tags=tags + Tags(Name=Sub("${AWS::StackName} Private Routes (AZ2)")),
        )
    )
    default_private_route_2 = template.add_resource(
        Route(
            "DefaultPrivateRoute2",
            RouteTableId=Ref(private_route_table_2),
            DestinationCidrBlock="0.0.0.0/0",
            NatGatewayId=Ref(nat_gateway_2),
        )
    )
    private_subnet_2_route_table_association = template.add_resource(
        SubnetRouteTableAssociation(
            "PrivateSubnet2RouteTableAssociation",
            RouteTableId=Ref(private_route_table_2),
            SubnetId=Ref(private_subnet_2),
        )
    )

    template.add_output(
        [
            Output("VPC", Description="A reference to the created VPC", Value=Ref(vpc)),
            Output("PublicSubnets", Description="A list of the public subnets", Value=Sub(f"${{{public_subnet_1.title}}},${{{public_subnet_2.title}}}")),
            Output("PrivateSubnets", Description="A list of the private subnets", Value=Sub(f"${{{private_subnet_1.title}}},${{{private_subnet_2.title}}}")),
        ]
    )
    print(template.to_yaml(clean_up=True))
    with open("template.yml", "w") as outfile:
        outfile.writelines(template.to_yaml(clean_up=True))


if __name__ == "__main__":
    main()
