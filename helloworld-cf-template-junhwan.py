"""Generating CloudFormation template."""

#클라우드 포메이션 템플릿 생성#
from troposphere import (
    Base64,
    ec2,
    GetAtt,
    Join,
    Output,
    Parameter,
    Ref,
    Template,
)

#변수 정의 // 자주 변경할 값
ApplicationPort = "3000"

#Template 변수 초기화
t = Template()

# 템플릿을 여러개 동시 실행 할 예정이므로, 식별을 위한 설명 추가
t.set_description("Effective DevOps in AWS: HelloWorld web application")

# 매개변수 설정
t.add_parameter(Parameter(
    "KeyPair",
    Description="Name of an existing EC2 KeyPair to SSH",
    Type="AWS::EC2::KeyPair::KeyName",
    ConstraintDescription="must be the name of an existing EC2 KeyPair.",
))

# 리소스 추가 / 위의 ApplicationPort 3000값을 사용
t.add_resource(ec2.SecurityGroup(
    "SecurityGroup",
    GroupDescription="Allow SSH and TCP/{} access".format(ApplicationPort),
    SecurityGroupIngress=[
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort="22",
            ToPort="22",
            CidrIp="0.0.0.0/0",
        ),
        ec2.SecurityGroupRule(
            IpProtocol="tcp",
            FromPort=ApplicationPort,
            ToPort=ApplicationPort,
            CidrIp="0.0.0.0/0",
        ),
    ],
))


ud = Base64(Join('\n', [
    "#!/bin/bash",
    # nvm 설치 및 환경 설정"
    "curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.39.3/install.sh | bash",
    
    # nvm을 로드하여 사용할 수 있도록 설정 (중요!)"
    "export NVM_DIR=\"$HOME/.nvm\"",
    "[ -s \"$NVM_DIR/nvm.sh\" ] && . \"$NVM_DIR/nvm.sh\"",
    
    # node.js 설치
    "nvm install node",
    
    # helloworld.js 파일을 다운로드하고 실행"
    "wget http://bit.ly/2vESNuc -O /home/ec2-user/helloworld.js",
    
    # node.js 백그라운드 실행 (로그 파일을 남기도록 설정)"
    "nohup node /home/ec2-user/helloworld.js > /home/ec2-user/helloworld.log 2>&1 &"
]))


# UserData 는 생성 시 1번 실행되는 명령어 제공
t.add_resource(ec2.Instance(
    "instance",
    #ImageId="ami-cfe4b2b0",
    ImageId="ami-0de20b1c8590e09c5",
    InstanceType="t2.micro",
    SecurityGroups=[Ref("SecurityGroup")],
    KeyName=Ref("KeyPair"),
    UserData=ud,
))

t.add_output(Output(
    "InstancePublicIp",
    Description="Public IP of our instance.",
    Value=GetAtt("instance", "PublicIp"),
))

t.add_output(Output(
    "WebUrl",
    Description="Application endpoint",
    Value=Join("", [
        "http://", GetAtt("instance", "PublicDnsName"),
        ":", ApplicationPort
    ]),
))

# Python 3에서는 print를 함수로 사용해야 하므로, 다음과 같이 수정 
# 기존 : print t.to_json()
print(t.to_json())

