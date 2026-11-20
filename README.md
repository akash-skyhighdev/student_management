# student_management
A secure, multi-tier AWS student portal built with Flask and Gunicorn. The application runs on EC2 private subnets behind an Application Load Balancer, with MySQL on RDS, private S3 document storage, and SNS registration notifications.

## Features

- Student and administrator authentication
- Student profile and document management
- Private file uploads to Amazon S3
- Registration notifications through Amazon SNS
- Keyless EC2 administration through AWS Systems Manager Session Manager

## 🏗️ AWS Network & Security Architecture

<div align="center">
  <img width="765" height="1024" alt="architecture" src="https://github.com/user-attachments/assets/0df1ee8c-0af4-4bf2-b698-9c043cf2cfb7" />
</div>

This multi-tier AWS architecture ensures high availability, strict network isolation, and zero-trust security for the application.

## Architecture Diagram

```mermaid
flowchart TB
    %% External Entities
    Users(["👤 Students & Admin (Internet)"])
    DevOps(["🛠️ Admin / DevOps (SSM Session Manager)"])

    %% AWS Cloud Boundary
    subgraph AWS ["☁️ AWS Cloud (One Region, Two Availability Zones)"]

        %% VPC Boundary
        subgraph VPC ["VPC (10.0.0.0/16)"]
            IGW["🌐 Internet Gateway (IGW)"]

            %% Public Subnet
            subgraph PublicSubnet ["🟢 Public Subnets"]
                ALB["⚖️ Application Load Balancer (ALB)<br/>HTTP 80 / HTTPS 443<br/>Spans both Public Subnets"]
            end

            %% Private Subnet
            subgraph PrivateSubnet ["🔴 Private Subnets"]
                subgraph SG1 ["🛡️ App Server Security Group (SG1)<br/>Inbound: Port 5000 from ALB | Outbound: Port 3306 to SG2"]
                    EC2["🖥️ EC2 Instance (Flask + Gunicorn)<br/>Listening on Port 5000<br/>Keyless IAM Role + SSM (No Access Keys)"]
                end

                subgraph SG2 ["🛡️ Database Security Group (SG2)<br/>Inbound: Port 3306 from SG1 | Outbound: None"]
                    RDS[("🗄️ RDS MySQL Database<br/>Port 3306")]
                end
            end
        end

        %% AWS Managed Services
        subgraph ManagedServices ["⚙️ AWS Managed Services"]
            S3[("🪣 Amazon S3 Bucket<br/>Encrypted, Private Access<br/>(Student Documents)")]
            SNS["📧 Amazon SNS Topic<br/>Registration & Admin Emails"]
        end
    end

    %% Traffic & Data Flows
    Users -->|"1. HTTPS/HTTP Request"| IGW
    IGW -->|"Public Traffic"| ALB
    ALB -->|"2. Forward Traffic (Port 5000)"| EC2
    DevOps -.->|"Secure Shell (No SSH Keys / No Bastion)"| EC2
    EC2 -->|"3. SQL Queries (Port 3306)"| RDS
    EC2 -->|"4. Upload/Fetch Files (via IAM Role)"| S3
    EC2 -->|"5. Trigger Registration Alerts"| SNS

    %% Styling
    classDef public fill:#e6f4ea,stroke:#34a853,stroke-width:2px,color:#137333;
    classDef private fill:#fce8e6,stroke:#ea4335,stroke-width:2px,color:#c5221f;
    classDef sg fill:#fff8e1,stroke:#fbbc04,stroke-width:1.5px,stroke-dasharray: 5 5,color:#333;
    classDef managed fill:#e8f0fe,stroke:#4285f4,stroke-width:2px,color:#1967d2;
    classDef external fill:#f1f3f4,stroke:#5f6368,stroke-width:2px,color:#202124;

    class PublicSubnet public;
    class PrivateSubnet private;
    class SG1,SG2 sg;
    class ManagedServices managed;
    class Users,DevOps external;

```

## 📋 Architectural Breakdown

* **Public Subnet:** Houses the Application Load Balancer, receiving incoming traffic and routing it securely into the private network.
* **Private Subnets:** Contain your EC2 instances running the Flask application and the RDS database, completely isolated from direct public access.
* **Secure Management:** Access to the EC2 instances is managed strictly via AWS Systems Manager, eliminating the need for SSH keys or bastion hosts.
* **Storage and Notifications:** Student files are stored privately in an S3 bucket using IAM roles, while Amazon SNS automatically sends confirmation emails upon registration.

## 🔒 Security Highlights

* **Zero-Trust Access:** No bastion hosts or SSH keys are used; access is strictly controlled via IAM policies and Session Manager.
* **Network Isolation:** Database and application servers reside in private subnets, inaccessible from the public internet.
* **Principle of Least Privilege:** Fine-grained IAM roles ensure components only access the specific resources required.
```
