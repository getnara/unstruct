# unstruct Backend Architecture Design

## 1. High-Level Architecture
```
                                                            AWS Cloud
┌──────────┐     ┌─────────────┐     ┌──────────┐     ┌─────────────┐     ┌───────────────┐
│  Client  │ →   │ API Gateway │ →   │   NLB    │ →   │Target Group │ →   │ EC2 Instance  │
│ (Web/App)│     │ (Regional)  │     │(TCP/8000)│     │(port 8000)  │     │   ┌─────────┐ │
└──────────┘     └─────────────┘     └──────────┘     └─────────────┘     │   │Container│ │
                                                                           │   │(Django) │ │
                                                                           │   └─────────┘ │
                                                                           └───────────────┘
                        ↑                                                          ↑
                        │                                                          │
                  Authentication                                             Data Storage
                        │                                                          │
                 ┌──────────┐                                              ┌──────────────┐
                 │ AWS      │                                              │ SQLite DB    │
                 │ Cognito  │                                              │ (Container)  │
                 └──────────┘                                              └──────────────┘
```

## 2. Component Details

### 2.1 Client Layer
- Web Application: Next.js 14.1.1+
- Hosted on AWS Amplify
- Communicates with backend via REST API

### 2.2 API Layer
- **API Gateway**
  - Type: REST API (Regional)
  - Endpoint: `https://zwxentfg2f.execute-api.us-east-2.amazonaws.com/prod`
  - Handles routing and API management

### 2.3 Load Balancing
- **Network Load Balancer (NLB)**
  - Name: unstruct-nlb
  - Type: TCP Load Balancer
  - Port: 8000
  - Internet-facing

### 2.4 Target Group
- Name: unstruct-tg
- Protocol: TCP
- Port: 8000
- Health Check: TCP on port 8000
- Target Type: Instance

### 2.5 Compute Layer
- **EC2 Instance**
  - Type: t2.xlarge
  - OS: Amazon Linux 2
  - VPC: vpc-01aca5ade58c15403
  - Subnet: subnet-03ab6d54ac71aa273 (us-east-2a)

- **ECS Configuration**
  - Cluster: unstruct-cluster
  - Service: unstruct-service
  - Task Definition: unstruct-backend:80
  - Container Port: 8000 (static mapping)

### 2.6 Authentication
- **AWS Cognito**
  - User Pool ID: us-east-2_EPatQHp7j
  - Client ID: 1g4o8ut88sr5tdp2677mne1if8
  - Region: us-east-2
  - Token Type: ID Token

### 2.7 Storage
- **SQLite Database**
  - Location: Inside container
  - Type: File-based database
  - Persistence: ECS volume mount
  - Note: Development/Testing configuration

## 3. Network Flow
1. Client makes request to API Gateway
2. API Gateway forwards to NLB
3. NLB routes to Target Group (port 8000)
4. Target Group forwards to EC2 instance
5. EC2 routes to container on port 8000

## 4. Security
- API Gateway: Public endpoint
- NLB: Internet-facing
- EC2: In private subnet
- Authentication: Cognito JWT tokens
- Network: VPC with proper security groups

## 5. Monitoring
- ECS Service metrics
- Target Group health checks
- EC2 CloudWatch metrics
- Container logs in CloudWatch

## 6. Future Considerations
- Migration to RDS for production database
- Implementation of read replicas
- Backup and restore procedures
- High availability configuration 